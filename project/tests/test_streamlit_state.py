import unittest

from streamlit.testing.v1 import AppTest


class StreamlitStateRegressionTests(unittest.TestCase):
    def _button(self, app, label):
        for button in app.button:
            if button.label == label:
                return button
        self.fail(f"button not found: {label}")

    def _assert_no_app_exception(self, app):
        messages = [str(exc.value) for exc in app.exception]
        self.assertEqual(messages, [], "\n".join(messages))

    def test_memory_and_emitted_state_survive_sequential_button_reruns(self):
        app = AppTest.from_file("sca_gui.py", default_timeout=30).run()
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
        app = AppTest.from_file("sca_gui.py", default_timeout=30).run()
        self._button(app, "初回進化・発話").click().run()
        self._assert_no_app_exception(app)

        memory_before = len(app.session_state["sca_memory_zone"].pool)
        self.assertGreater(memory_before, 0)

        app.text_input[0].set_value("昨日、都市を歩いた").run()
        self._button(app, "意味タグに変換").click().run()
        self._assert_no_app_exception(app)
        self.assertEqual(len(app.session_state["sca_memory_zone"].pool), memory_before)


if __name__ == "__main__":
    unittest.main()
