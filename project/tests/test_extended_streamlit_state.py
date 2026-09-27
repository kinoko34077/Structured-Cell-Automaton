import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "sca_gui_extended.py"
SAVE_DIR = ROOT / "save"
SAVE_NAME = "issue3_extended_state_test"


class ExtendedStreamlitStateRegressionTests(unittest.TestCase):
    def setUp(self):
        self._cleanup_save_files()

    def tearDown(self):
        self._cleanup_save_files()

    def _cleanup_save_files(self):
        for suffix in ("_cells.jsonl", "_syntax.jsonl", "_meta.json"):
            path = SAVE_DIR / f"{SAVE_NAME}{suffix}"
            if path.exists():
                path.unlink()

    def _new_app(self):
        return AppTest.from_file(str(APP_PATH), default_timeout=90).run()

    def _button(self, app, label):
        for button in app.button:
            if button.label == label:
                return button
        self.fail(f"button not found: {label}")

    def _slider(self, app, label):
        for slider in app.slider:
            if slider.label == label:
                return slider
        self.fail(f"slider not found: {label}")

    def _text_input(self, app, label):
        for text_input in app.text_input:
            if text_input.label == label:
                return text_input
        self.fail(f"text input not found: {label}")

    def _assert_no_app_exception(self, app):
        messages = [str(exc.value) for exc in app.exception]
        self.assertEqual(messages, [], "\n".join(messages))

    def _state(self, app, key):
        try:
            return app.session_state[key]
        except KeyError:
            self.fail(f"extended GUI state is not persisted: {key}")

    def _cell_signature(self, cells):
        return tuple(
            (cell.id, tuple(cell.position), cell.activation, tuple(cell.meaning_tags))
            for cell in cells
        )

    def _syntax_signature(self, syntaxes):
        return tuple(
            (syn.sid, getattr(syn, "parent_sid", None), tuple(syn.tags), syn.score)
            for syn in syntaxes
        )

    def test_extended_experiment_state_survives_unrelated_rerun(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        cells_before = self._cell_signature(self._state(app, "sca_ext_initial_cells"))
        syntaxes_before = self._syntax_signature(self._state(app, "sca_ext_syntax_pool"))
        memory_before = self._state(app, "sca_ext_memory_zone")
        output_before = self._state(app, "sca_ext_output_zone")

        self._button(app, "スコア淘汰（<0.3）").click().run()
        self._assert_no_app_exception(app)

        self.assertEqual(
            self._cell_signature(self._state(app, "sca_ext_initial_cells")),
            cells_before,
        )
        self.assertEqual(
            self._syntax_signature(self._state(app, "sca_ext_syntax_pool")),
            syntaxes_before,
        )
        self.assertIs(self._state(app, "sca_ext_memory_zone"), memory_before)
        self.assertIs(self._state(app, "sca_ext_output_zone"), output_before)

    def test_cell_count_change_reinitializes_once_then_stays_stable(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        self._slider(app, "セル数").set_value(30).run()
        self._assert_no_app_exception(app)

        cells_after_change = self._state(app, "sca_ext_initial_cells")
        self.assertEqual(len(cells_after_change), 30)
        signature_after_change = self._cell_signature(cells_after_change)

        self._button(app, "類似構文淘汰（閾値=0.9）").click().run()
        self._assert_no_app_exception(app)
        self.assertEqual(
            self._cell_signature(self._state(app, "sca_ext_initial_cells")),
            signature_after_change,
        )

    def test_saved_cells_and_syntaxes_remain_loaded_after_followup_rerun(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        original_cells = self._cell_signature(self._state(app, "sca_ext_initial_cells"))
        original_syntaxes = self._syntax_signature(self._state(app, "sca_ext_syntax_pool"))

        self._text_input(app, "保存ファイル名（例：save_001）").set_value(SAVE_NAME).run()
        self._button(app, "📥 保存").click().run()
        self._assert_no_app_exception(app)

        self._slider(app, "セル数").set_value(30).run()
        self._assert_no_app_exception(app)
        self.assertEqual(len(self._state(app, "sca_ext_initial_cells")), 30)

        self._button(app, "📤 読込").click().run()
        self._assert_no_app_exception(app)
        self.assertEqual(
            self._cell_signature(self._state(app, "sca_ext_initial_cells")),
            original_cells,
        )
        self.assertEqual(
            self._syntax_signature(self._state(app, "sca_ext_syntax_pool")),
            original_syntaxes,
        )

        self._button(app, "スコア淘汰（<0.3）").click().run()
        self._assert_no_app_exception(app)
        self.assertEqual(
            self._cell_signature(self._state(app, "sca_ext_initial_cells")),
            original_cells,
        )
        self.assertEqual(
            self._syntax_signature(self._state(app, "sca_ext_syntax_pool")),
            original_syntaxes,
        )

    def test_evolution_persists_memory_without_duplicate_emitted_sids(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        self._button(app, "▶ 構文進化→評価→発話").click().run()
        self._assert_no_app_exception(app)

        memory_zone = self._state(app, "sca_ext_memory_zone")
        self.assertGreater(len(memory_zone.pool), 0)

        emitted = self._state(app, "sca_ext_emitted")
        emitted_sids = [syn.sid for syn in emitted]
        self.assertEqual(emitted_sids, list(dict.fromkeys(emitted_sids)))

    def test_extended_visualization_cache_and_operation_feedback(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        cluster_before = self._state(app, "sca_ext_cluster_figure")
        genealogy_before = self._state(app, "sca_ext_genealogy_figure")
        cooccurrence_before = self._state(app, "sca_ext_cooccurrence_figure")

        self._button(app, "スコア淘汰（<0.3）").click().run()
        self._assert_no_app_exception(app)

        self.assertIs(self._state(app, "sca_ext_cluster_figure")["figure"], cluster_before["figure"])
        self.assertIs(self._state(app, "sca_ext_genealogy_figure")["figure"], genealogy_before["figure"])
        self.assertIs(self._state(app, "sca_ext_cooccurrence_figure")["figure"], cooccurrence_before["figure"])

        feedback = [
            str(item.value)
            for item in (*app.success, *app.info, *app.warning)
        ]
        self.assertTrue(
            any("件" in message or "変化なし" in message for message in feedback),
            feedback,
        )


if __name__ == "__main__":
    unittest.main()
