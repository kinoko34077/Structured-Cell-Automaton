"""
engine: SCA構文セル・オートマトン 処理系モジュール集
────────────────────────────
- 構文抽出・評価・進化処理     (engine.syntax_extractor, engine.scoring, engine.evolver)
- セル生成                     (engine.sca_data)
- タグクラスタ構築             (engine.clustering)
- 思考ループ処理               (engine.think_loop)
"""

from .syntax_extractor import extract_syntax_from_cells
from .scoring import evaluate_syntax
from .evolver import evolve_generation_with_tags, evolve_generation
from .sca_data import generate_balanced_cells
from .clustering import cluster_syntaxes_by_tags
from .think_loop import simulate_thought_cycle

__all__ = [
    "extract_syntax_from_cells",
    "evaluate_syntax",
    "evolve_generation_with_tags",
    "evolve_generation",
    "generate_balanced_cells",
    "cluster_syntaxes_by_tags",
    "simulate_thought_cycle",
]
