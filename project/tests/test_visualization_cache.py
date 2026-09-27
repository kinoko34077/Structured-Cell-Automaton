import unittest

from project.ui_helpers import get_cached_figure, syntax_signature


class VisualizationCacheTests(unittest.TestCase):
    def test_same_signature_reuses_figure_and_changed_signature_rebuilds(self):
        cache = {}
        calls = []

        def build():
            calls.append(len(calls) + 1)
            return object()

        first = get_cached_figure(cache, "cluster", ("syntax-a",), build)
        same = get_cached_figure(cache, "cluster", ("syntax-a",), build)
        changed = get_cached_figure(cache, "cluster", ("syntax-b",), build)

        self.assertIs(first, same)
        self.assertIsNot(first, changed)
        self.assertEqual(calls, [1, 2])

    def test_renderer_signature_can_ignore_score_when_renderer_does_not_consume_it(self):
        first = type("Syntax", (), {"sid": "s1", "parent_sid": None, "tags": ["city"], "score": 0.1})()
        changed_score = type("Syntax", (), {"sid": "s1", "parent_sid": None, "tags": ["city"], "score": 0.9})()

        self.assertEqual(
            syntax_signature([first], include_score=False),
            syntax_signature([changed_score], include_score=False),
        )
        self.assertNotEqual(
            syntax_signature([first], include_score=True),
            syntax_signature([changed_score], include_score=True),
        )


if __name__ == "__main__":
    unittest.main()
