"""
core: SCA構文セル・オートマトン 中核構造モジュール集
────────────────────────────
- Cell / Syntax 定義           (core.Cell, core.Syntax)
- 線形化モジュール             (core.linearizer)
- 出力ゾーン・記憶ゾーン       (core.output_zone, core.memory_zone)
- 構文盤面構造（任意）         (core.Board)
"""

from .Cell import Cell
from .Syntax import Syntax
from .linearizer import linearize_syntax
from .output_zone import OutputZone
from .memory_zone import MemoryZone
from .Board import Board

__all__ = [
    "Cell",
    "Syntax",
    "linearize_syntax",
    "OutputZone",
    "MemoryZone",
    "Board",
]
