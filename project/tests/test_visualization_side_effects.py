import unittest
from unittest.mock import patch

import matplotlib.pyplot as plt

from core import Syntax
from viz.cluster_map import visualize_syntax_clusters
from viz.cooccurrence_net import draw_tag_cooccurrence_network
from viz.genealogy_plot import draw_syntax_genealogy
from viz.score_heatmap import draw_score_heatmap


class VisualizationSideEffectTests(unittest.TestCase):
    def test_side_effect_free_renderers_do_not_open_matplotlib_windows(self):
        syntaxes = [
            Syntax(
                sid="sid-001",
                cell_ids=["cell-001"],
                tags=["tag-a", "tag-b"],
                score=0.5,
            )
        ]

        with patch.object(plt, "show") as show:
            figures = [
                visualize_syntax_clusters(
                    syntaxes, {"tag-a": 0, "tag-b": 1}, show=False
                ),
                draw_syntax_genealogy(syntaxes, show=False),
                draw_tag_cooccurrence_network(syntaxes, show=False),
                draw_score_heatmap([], ["tag-a"], show=False),
            ]

        self.assertTrue(all(figure is not None for figure in figures))
        show.assert_not_called()
        for figure in figures:
            plt.close(figure)


if __name__ == "__main__":
    unittest.main()
