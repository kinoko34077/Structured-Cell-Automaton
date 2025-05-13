import math
from typing import List
from Cell import Cell
from Syntax import Syntax

def evaluate_syntax(syntax: Syntax, cell_dict: dict) -> float:
    cells: List[Cell] = [cell_dict[cid] for cid in syntax.cell_ids if cid in cell_dict]

    if not cells:
        return 0.0

    # 1. 活性度の平均
    activation_score = sum(c.activation for c in cells) / len(cells)

    # 2. タグ多様性スコア（ユニーク数）
    unique_tags = {tag for c in cells for tag in c.meaning_tags}
    diversity_score = len(unique_tags) / max(len(cells), 1)

    # 3. 構文長スコア（5セル程度を理想として正規分布）
    ideal_len = 5
    length_score = math.exp(-((len(cells) - ideal_len) ** 2) / 4.0)

    # 総合スコア（重みは仮）
    total_score = (
        0.4 * activation_score +
        0.3 * diversity_score +
        0.3 * length_score
    )

    syntax.update_score(total_score)
    return total_score
