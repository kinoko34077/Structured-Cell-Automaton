from typing import List
from Syntax import Syntax
from Cell import Cell

def linearize_syntax(syntax: Syntax, cell_dict: dict) -> str:
    cells = [cell_dict.get(cid) for cid in syntax.cell_ids if cid in cell_dict]
    if not cells:
        return "(構文情報なし)"

    # 意味タグの優先順（名詞→動詞→助詞）
    tag_order = ["名詞", "動物", "動詞", "移動", "助詞"]

    # タグの重み付けによる並び順決定
    def tag_priority(cell: Cell):
        for i, tag in enumerate(tag_order):
            if tag in cell.meaning_tags:
                return i
        return len(tag_order)

    sorted_cells = sorted(cells, key=tag_priority)

    # 出力フォーマット例：「動物が 移動する」
    elements = []
    for c in sorted_cells:
        tags = "・".join(c.meaning_tags)
        elements.append(f"[{c.id}:{tags}]")

    return "→ " + " ".join(elements)
