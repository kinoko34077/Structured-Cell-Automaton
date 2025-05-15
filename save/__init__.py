"""
save: SCA構文セル・オートマトン 保存／読込モジュール集
────────────────────────────
- セル・構文・メタデータの保存と復元       (save.quicksave)
"""

from .quicksave import (
    save_cells_to_jsonl,
    load_cells_from_jsonl,
    save_syntaxes_to_jsonl,
    load_syntaxes_from_jsonl,
    save_metadata,
    load_metadata,
)

__all__ = [
    "save_cells_to_jsonl",
    "load_cells_from_jsonl",
    "save_syntaxes_to_jsonl",
    "load_syntaxes_from_jsonl",
    "save_metadata",
    "load_metadata",
]
