import math
from typing import List
from Cell import Cell
from Syntax import Syntax

def evaluate_syntax(syntax: Syntax, cell_dict: dict, memory_pool: List[Syntax] = []) -> float:
    cells = [cell_dict[cid] for cid in syntax.cell_ids if cid in cell_dict]
    if not cells:
        return 0.0

    activation_score = sum(c.activation for c in cells) / len(cells)
    unique_tags = {tag for c in cells for tag in c.meaning_tags}
    diversity_score = len(unique_tags) / max(len(cells), 1)
    length_score = math.exp(-((len(cells) - 5) ** 2) / 4.0)

    # 創造性: 過去構文との差分（タグ重複率の反転）
    if memory_pool:
        max_overlap = max(
            len(set(s.tags).intersection(unique_tags)) / max(len(set(s.tags).union(unique_tags)), 1)
            for s in memory_pool
        )
        creativity_score = 1.0 - max_overlap  # 類似構文が多いと低評価
    else:
        creativity_score = 1.0

    total_score = (
        0.4 * activation_score +
        0.3 * diversity_score +
        0.2 * length_score +
        0.1 * creativity_score
    )

    syntax.update_score(total_score)
    return total_score
