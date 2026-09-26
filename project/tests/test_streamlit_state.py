import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[2] / "sca_gui.py"


class StreamlitStateRegressionTests(unittest.TestCase):
    def _button(self, app, label):
        for button in app.button:
            if button.label == label:
                return button
        self.fail(f"button not found: {label}")

    def _assert_no_app_exception(self, app):
        messages = [str(exc.value) for exc in app.exception]
        self.assertEqual(messages, [], "\n".join(messages))

    def _new_app(self):
        return AppTest.from_file(str(APP_PATH), default_timeout=90).run()

    def test_memory_and_emitted_state_survive_sequential_button_reruns(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        self._button(app, "初回進化・発話").click().run()
        self._assert_no_app_exception(app)

        try:
            memory_zone = app.session_state["sca_memory_zone"]
        except KeyError:
            self.fail("MemoryZone is not persisted in Streamlit session state")
        self.assertGreater(len(memory_zone.pool), 0)

        self._button(app, "内的思考ループ実行").click().run()
        self._assert_no_app_exception(app)
        self.assertGreater(len(app.session_state["sca_memory_zone"].pool), 0)

    def test_natural_language_reactivation_keeps_prior_memory(self):
        app = self._new_app()
        self._button(app, "初回進化・発話").click().run()
        self._assert_no_app_exception(app)

        memory_before = len(app.session_state["sca_memory_zone"].pool)
        self.assertGreater(memory_before, 0)

        app.text_input[0].set_value("昨日、都市を歩いた").run()
        self._button(app, "意味タグに変換").click().run()
        self._assert_no_app_exception(app)
        self.assertEqual(len(app.session_state["sca_memory_zone"].pool), memory_before)

    def test_last_natural_language_analysis_survives_unrelated_rerun(self):
        app = self._new_app()
        self._button(app, "初回進化・発話").click().run()
        self._assert_no_app_exception(app)

        original_input = "昨日、都市を歩いた"
        app.text_input[0].set_value(original_input).run()
        self._button(app, "意味タグに変換").click().run()
        self._assert_no_app_exception(app)

        try:
            analysis = app.session_state["sca_last_analysis"]
        except KeyError:
            self.fail("last natural-language analysis is not persisted in Streamlit session state")

        self.assertEqual(analysis["input"], original_input)
        self.assertIn("inferred_tags", analysis)
        self.assertIn("expanded_tags", analysis)
        self.assertIn("reactivated_lines", analysis)

        # Trigger a rerun unrelated to the analysis result.
        self._button(app, "世代淘汰（60世代超）").click().run()
        self._assert_no_app_exception(app)

        persisted = app.session_state["sca_last_analysis"]
        self.assertEqual(persisted, analysis)
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn(original_input, rendered)
        self.assertIn("抽出された意味タグ", rendered)
        self.assertIn("拡張されたトリガータグ", rendered)

    def test_generation_pruning_control_uses_persistent_generation_state(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        try:
            initial_generation = app.session_state["sca_generation"]
        except KeyError:
            self.fail("current generation is not persisted in Streamlit session state")
        self.assertEqual(initial_generation, 0)

        self._button(app, "初回進化・発話").click().run()
        self._assert_no_app_exception(app)
        self.assertGreater(app.session_state["sca_generation"], initial_generation)

        self._button(app, "世代淘汰（60世代超）").click().run()
        self._assert_no_app_exception(app)

    def test_unrelated_analysis_rerun_reuses_visualization_cache(self):
        app = self._new_app()
        self._assert_no_app_exception(app)

        try:
            cache = app.session_state["sca_visualization_cache"]
        except KeyError:
            self.fail("visualization cache is not persisted in Streamlit session state")
        initial_counts = {name: entry["build_count"] for name, entry in cache.items()}
        self.assertGreaterEqual(len(initial_counts), 3)

        app.text_input[0].set_value("昨日、都市を歩いた").run()
        self._button(app, "意味タグに変換").click().run()
        self._assert_no_app_exception(app)

        after = app.session_state["sca_visualization_cache"]
        after_counts = {name: entry["build_count"] for name, entry in after.items()}
        self.assertEqual(after_counts, initial_counts)

    def test_pruning_reports_removed_count_and_pool_transition(self):
        app = self._new_app()
        self._button(app, "初回進化・発話").click().run()
        self._assert_no_app_exception(app)

        self._button(app, "スコア淘汰（<0.3）").click().run()
        self._assert_no_app_exception(app)

        status = app.session_state.get("sca_last_operation_status")
        self.assertIsInstance(status, str)
        self.assertIn("削除", status)
        self.assertIn("→", status)
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn(status, rendered)

    def test_evolution_reports_emission_count_even_when_zero(self):
        app = self._new_app()
        self._button(app, "進化 → 評価 → 発話チェック").click().run()
        self._assert_no_app_exception(app)

        status = app.session_state.get("sca_last_operation_status")
        self.assertIsInstance(status, str)
        self.assertIn("発話件数", status)
        self.assertRegex(status, r"発話件数: \d+件")


if __name__ == "__main__":
    unittest.main()
