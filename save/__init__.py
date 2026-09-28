"""
save: SCA構文セル・オートマトン 保存／読込モジュール集
────────────────────────────
- セル・構文・メタデータの保存と復元       (save.quicksave)
"""

from .quicksave import (
    InvalidSaveNameError,
    QuicksaveError,
    SnapshotIntegrityError,
    SnapshotSaveResult,
    load_cells_from_jsonl,
    load_metadata,
    load_snapshot,
    load_syntaxes_from_jsonl,
    save_cells_to_jsonl,
    save_metadata,
    save_snapshot,
    save_syntaxes_to_jsonl,
    validate_save_name,
)

__all__ = [
    "InvalidSaveNameError",
    "QuicksaveError",
    "SnapshotIntegrityError",
    "SnapshotSaveResult",
    "load_cells_from_jsonl",
    "load_metadata",
    "load_snapshot",
    "load_syntaxes_from_jsonl",
    "save_cells_to_jsonl",
    "save_metadata",
    "save_snapshot",
    "save_syntaxes_to_jsonl",
    "validate_save_name",
]
