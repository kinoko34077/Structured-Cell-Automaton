import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from core import Cell, Syntax
from save import quicksave


class QuicksaveIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.cells_a = [Cell(id="c1", position=(0, 0), activation=0.25)]
        self.syntax_a = [Syntax(sid="s1", cell_ids=["c1"], score=0.5)]
        self.meta_a = {"total_generations": 3}
        self.cells_b = [Cell(id="c2", position=(1, 0), activation=0.75)]
        self.syntax_b = [Syntax(sid="s2", cell_ids=["c2"], score=0.8)]
        self.meta_b = {"total_generations": 9}

    def tearDown(self):
        self.temp_dir.cleanup()

    def _save_a(self):
        quicksave.save_snapshot(self.root, "save_001", self.cells_a, self.syntax_a, self.meta_a)
    def _loaded_ids(self):
        cells, syntaxes, meta = quicksave.load_snapshot(self.root, "save_001")
        return [cell.id for cell in cells], [syn.sid for syn in syntaxes], meta

    def test_save_name_is_a_logical_identifier_not_a_path(self):
        self.assertEqual(quicksave.validate_save_name("save_001"), "save_001")
        for value in ("../escape", "a/b", r"a\b", ".", "..", "C:drive", "/abs", ""):
            with self.subTest(value=value):
                with self.assertRaises(quicksave.InvalidSaveNameError):
                    quicksave.validate_save_name(value)

    def test_successful_snapshot_round_trip_uses_one_generation(self):
        result = quicksave.save_snapshot(
            self.root, "save_001", self.cells_a, self.syntax_a, self.meta_a
        )
        self.assertEqual(self._loaded_ids(), (["c1"], ["s1"], self.meta_a))
        manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "sca-quicksave-v1")
        self.assertTrue(manifest["generation"])
        self.assertEqual(set(manifest["sha256"]), {"cells", "syntax", "meta"})

    def test_legacy_save_001_remains_loadable_without_manifest(self):
        repo_save = Path(__file__).resolve().parents[2] / "save"
        cells, syntaxes, meta = quicksave.load_snapshot(repo_save, "save_001")
        self.assertGreater(len(cells), 0)
        self.assertGreater(len(syntaxes), 0)
        self.assertIn("total_generations", meta)
    def test_component_write_failures_leave_previous_snapshot_authoritative(self):
        self._save_a()
        original_manifest = quicksave.manifest_path(self.root, "save_001").read_bytes()
        original_writer = quicksave._write_generation_file

        for fail_call in (1, 2, 3):
            calls = 0

            def failing_writer(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == fail_call:
                    raise OSError(f"injected component failure {fail_call}")
                return original_writer(*args, **kwargs)

            with self.subTest(fail_call=fail_call):
                with mock.patch.object(quicksave, "_write_generation_file", side_effect=failing_writer):
                    with self.assertRaises(OSError):
                        quicksave.save_snapshot(
                            self.root, "save_001", self.cells_b, self.syntax_b, self.meta_b
                        )
                self.assertEqual(
                    quicksave.manifest_path(self.root, "save_001").read_bytes(),
                    original_manifest,
                )
                self.assertEqual(self._loaded_ids(), (["c1"], ["s1"], self.meta_a))
    def test_manifest_publish_failure_leaves_previous_snapshot_authoritative(self):
        self._save_a()
        original_manifest = quicksave.manifest_path(self.root, "save_001").read_bytes()
        with mock.patch.object(
            quicksave, "_publish_manifest", side_effect=OSError("injected publish failure")
        ):
            with self.assertRaises(OSError):
                quicksave.save_snapshot(
                    self.root, "save_001", self.cells_b, self.syntax_b, self.meta_b
                )
        self.assertEqual(
            quicksave.manifest_path(self.root, "save_001").read_bytes(), original_manifest
        )
        self.assertEqual(self._loaded_ids(), (["c1"], ["s1"], self.meta_a))

    def test_hash_mismatch_rejects_tampered_or_mixed_generation(self):
        result_a = quicksave.save_snapshot(
            self.root, "save_001", self.cells_a, self.syntax_a, self.meta_a
        )
        result_b = quicksave.save_snapshot(
            self.root, "save_001", self.cells_b, self.syntax_b, self.meta_b
        )
        old_cells = quicksave.generation_paths(
            self.root, "save_001", result_a.generation
        )["cells"].read_bytes()
        current_cells = quicksave.generation_paths(
            self.root, "save_001", result_b.generation
        )["cells"]
        current_cells.write_bytes(old_cells)
        with self.assertRaises(quicksave.SnapshotIntegrityError):
            quicksave.load_snapshot(self.root, "save_001")


if __name__ == "__main__":
    unittest.main()
