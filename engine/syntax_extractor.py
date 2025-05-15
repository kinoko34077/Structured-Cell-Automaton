from typing import List
from core import Cell, Syntax
import uuid
import time

def extract_syntax_from_cells(cells: List[Cell], min_activation=0.5, min_tag_count=2) -> List[Syntax]:
    """
    活性スコアと意味タグ数に基づいて構文候補列を抽出
    """
    syntax_list = []
    current_group = []

    for cell in cells:
        if cell.activation >= min_activation and len(cell.meaning_tags) >= min_tag_count:
            current_group.append(cell)
        else:
            if len(current_group) >= 2:
                sid = str(uuid.uuid4())
                syntax_list.append(
                    Syntax(
                        sid=sid,
                        cell_ids=[c.id for c in current_group],
                        tags=list({t for c in current_group for t in c.meaning_tags})
                    )
                )
            current_group = []

    # 残りを処理
    if len(current_group) >= 2:
        sid = str(uuid.uuid4())
        syntax_list.append(
            Syntax(
                sid=sid,
                cell_ids=[c.id for c in current_group],
                tags=list({t for c in current_group for t in c.meaning_tags})
            )
        )

    return syntax_list
