import unittest

from project.ui_helpers import get_cached_figure


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


if __name__ == "__main__":
    unittest.main()
