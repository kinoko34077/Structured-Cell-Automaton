import ast
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[2] / "sca_gui_extended.py"
EVOLVE_LABEL = "▶ 構文進化→評価→発話"
PRUNE_LABEL = "世代淘汰（60世代前まで）"
LOAD_LABEL = "📤 読込"


class ExtendedGuiStateTests(unittest.TestCase):
    def _new_app(self):
        return AppTest.from_file(str(APP_PATH), default_timeout=90).run()

    def _button(self, app, label):
        for button in app.button:
            if button.label == label:
                return button
        self.fail(f"button not found: {label}")

    def _assert_no_app_exception(self, app):
        messages = [str(exc.value) for exc in app.exception]
        self.assertEqual(messages, [], "\n".join(messages))

    def test_experiment_state_survives_unrelated_rerun(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        expected_keys = {
            "sca_initial_cells",
            "sca_syntax_pool",
            "sca_emitted",
            "sca_memory_zone",
            "sca_output_zone",
            "sca_visualization_cache",
        }
        self.assertTrue(expected_keys.issubset(set(app.session_state.filtered_state)))

        initial_cells = app.session_state["sca_initial_cells"]
        syntax_pool = app.session_state["sca_syntax_pool"]
        memory_zone = app.session_state["sca_memory_zone"]
        output_zone = app.session_state["sca_output_zone"]
        emitted = app.session_state["sca_emitted"]

        self._button(app, PRUNE_LABEL).click().run()
        self._assert_no_app_exception(app)

        self.assertIs(app.session_state["sca_initial_cells"], initial_cells)
        self.assertIs(app.session_state["sca_syntax_pool"], syntax_pool)
        self.assertIs(app.session_state["sca_memory_zone"], memory_zone)
        self.assertIs(app.session_state["sca_output_zone"], output_zone)
        self.assertIs(app.session_state["sca_emitted"], emitted)

    def test_load_control_updates_session_owned_values(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        app.text_input[0].set_value("save_001")
        self._button(app, LOAD_LABEL).click().run()
        self._assert_no_app_exception(app)

        self.assertGreater(len(app.session_state["sca_initial_cells"]), 0)
        self.assertGreater(len(app.session_state["sca_syntax_pool"]), 0)

        loaded_cells = app.session_state["sca_initial_cells"]
        loaded_syntaxes = app.session_state["sca_syntax_pool"]
        self._button(app, PRUNE_LABEL).click().run()
        self._assert_no_app_exception(app)
        self.assertIs(app.session_state["sca_initial_cells"], loaded_cells)
        self.assertIs(app.session_state["sca_syntax_pool"], loaded_syntaxes)

    def test_visualization_figures_reuse_cache_on_unrelated_rerun(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        cache = app.session_state["sca_visualization_cache"]
        expected_keys = {"cluster", "genealogy", "cooccurrence", "heatmap"}
        self.assertEqual(set(cache), expected_keys)
        figures = {key: cache[key]["figure"] for key in expected_keys}

        self._button(app, PRUNE_LABEL).click().run()
        self._assert_no_app_exception(app)

        for key, figure in figures.items():
            self.assertIs(app.session_state["sca_visualization_cache"][key]["figure"], figure)

    def test_evolution_does_not_use_augmented_session_emitted_append(self):
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        augmented_targets = []
        for node in ast.walk(tree):
            if isinstance(node, ast.AugAssign):
                target = ast.unparse(node.target)
                if target in {"st.session_state.emitted", "st.session_state.sca_emitted"}:
                    augmented_targets.append(target)

        self.assertEqual(augmented_targets, [])


if __name__ == "__main__":
    unittest.main()
