"""
output_zone.py

構文の出力管理ゾーン。意味密度・スコアに応じて発話タイミングを制御する。
"""

from typing import List
from core import Syntax

class OutputZone:
    """
    出力ゾーンクラス：発話構文バッファとその制御。
    """

    def __init__(self, capacity=5, activation_threshold=0.6):
        self.buffer: List[Syntax] = []
        self.capacity = capacity
        self.activation_threshold = activation_threshold

    def add_syntax(self, syntax: Syntax):
        """
        バッファに構文を追加（スコア順に整列・容量制限あり）。

        Args:
            syntax (Syntax): 追加対象の構文
        """
        if syntax.score >= self.activation_threshold:
            self.buffer.append(syntax)
            self.buffer = sorted(self.buffer, key=lambda s: -s.score)
            self.buffer = self.buffer[:self.capacity]

    def should_emit(self) -> bool:
        """
        発話実行すべきか判定（現在はバッファ満杯基準）

        Returns:
            bool: True = 発話すべき
        """
        return len(self.buffer) >= self.capacity

    def emit(self) -> List[Syntax]:
        """
        バッファ内構文を発話として出力し、バッファをクリア。

        Returns:
            List[Syntax]: 発話対象構文群
        """
        output = self.buffer.copy()
        self.buffer.clear()
        return output
