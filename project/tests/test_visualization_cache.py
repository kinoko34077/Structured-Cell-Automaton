import unittest


class DummySyntax:
    def __init__(self, sid, tags, score=0.0, parent_sid=None):
        self.sid = sid
        self.tags = tags
        self.score = score
        self.parent_sid = parent_sid


class VisualizationCacheTests(unittest.TestCase):
    def test_same_signature_reuses_render_and_changed_state_rebuilds(self):
        from project.ui_visualization_cache import get_cached_visualization, syntax_visual_signature

        syntaxes = [DummySyntax("s1", ["都市", "移動"], score=0.5)]
        cache = {}
        calls = []

        def build():
            calls.append("build")
            return b"png-v1"

        signature = syntax_visual_signature(syntaxes)
        first = get_cached_visualization(cache, "cluster", signature, build)
        second = get_cached_visualization(cache, "cluster", signature, build)

        self.assertEqual(first, b"png-v1")
        self.assertEqual(second, b"png-v1")
        self.assertEqual(calls, ["build"])
        self.assertEqual(cache["cluster"]["build_count"], 1)

        syntaxes[0].score = 0.75
        changed_signature = syntax_visual_signature(syntaxes)
        third = get_cached_visualization(cache, "cluster", changed_signature, lambda: b"png-v2")

        self.assertEqual(third, b"png-v2")
        self.assertEqual(cache["cluster"]["build_count"], 2)

    def test_signature_tracks_genealogy_and_tag_changes(self):
        from project.ui_visualization_cache import syntax_visual_signature

        syntax = DummySyntax("s1", ["都市"], score=0.5, parent_sid="p1")
        original = syntax_visual_signature([syntax])
        syntax.parent_sid = "p2"
        self.assertNotEqual(original, syntax_visual_signature([syntax]))
        syntax.parent_sid = "p1"
        syntax.tags = ["都市", "移動"]
        self.assertNotEqual(original, syntax_visual_signature([syntax]))


if __name__ == "__main__":
    unittest.main()
