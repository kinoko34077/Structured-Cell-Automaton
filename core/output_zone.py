from typing import List
from core import Syntax

class OutputZone:
    def __init__(self, capacity=5, activation_threshold=0.6):
        self.buffer: List[Syntax] = []
        self.capacity = capacity
        self.activation_threshold = activation_threshold

    def add_syntax(self, syntax: Syntax):
        """スコアが高ければ追加（優先挿入）"""
        if syntax.score >= self.activation_threshold:
            self.buffer.append(syntax)
            self.buffer = sorted(self.buffer, key=lambda s: -s.score)
            self.buffer = self.buffer[:self.capacity]

    def should_emit(self) -> bool:
        """意味タグ密度や平均スコアで発話タイミング判断（仮に容量到達で）"""
        return len(self.buffer) >= self.capacity

    def emit(self) -> List[Syntax]:
        """現在のバッファを発話出力"""
        output = self.buffer.copy()
        self.buffer.clear()
        return output
