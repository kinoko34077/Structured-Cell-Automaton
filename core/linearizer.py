"""
linearizer.py

構文（Syntax）を自然言語風の整形文字列に変換するモジュール。
主にGUIでの発話表示や、ログ出力に用いられる。
"""

from typing import List
from core import Syntax, Cell

def linearize_syntax(syntax: Syntax, cell_dict: dict[str, Cell]) -> str:
    """
    構文オブジェクトを人間可読なフォーマットに変換する。

    Args:
        syntax (Syntax): 構文オブジェクト（SID・タグ列等含む）
        cell_dict (dict[str, Cell]): 全セル辞書（ID → Cell）

    Returns:
        str: 整形された構文表示文字列（例：[c01:名詞] [c02:動詞] ...）
    """
    cells = [cell_dict.get(cid) for cid in syntax.cell_ids if cid in cell_dict]
    if not cells:
        return "(構文情報なし)"

    # タグの出現優先順位（先頭に並ぶほど左側に寄せる）
    tag_order = ["名詞", "動物", "動詞", "移動", "助詞"]

    def tag_priority(cell: Cell) -> int:
        for i, tag in enumerate(tag_order):
            if tag in cell.meaning_tags:
                return i
        return len(tag_order)

    sorted_cells = sorted(cells, key=tag_priority)

    elements = [
        f"[{c.id}:{'・'.join(c.meaning_tags)}]"
        for c in sorted_cells
    ]
    return "→ " + " ".join(elements)
