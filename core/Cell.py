"""
Cell.py

構文セル（Cell）クラス定義モジュール。

各セルは意味タグ・活性度・構文IDなどを保持し、盤面上で構文構造を形成する要素単位。
"""

from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class Cell:
    """
    セルの構造体。

    Attributes:
        id (str): 一意なセルID
        position (tuple): セルの位置情報（x, y）
        syntax_id (Optional[str]): 所属する構文ID（任意）
        activation (float): 活性度（0.0～1.0）
        meaning_tags (List[str]): 意味タグのリスト（例：名詞、時間、動作など）
        history (List[str]): 操作・活性履歴（任意拡張用）
    """
    id: str
    position: tuple
    syntax_id: Optional[str] = None
    activation: float = 0.0
    meaning_tags: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

    def update_activation(self, delta: float):
        """
        セルの活性度を変化させる。0未満にはならない。

        Args:
            delta (float): 活性変化量（±）
        """
        self.activation = max(0.0, self.activation + delta)

    def add_meaning_tag(self, tag: str):
        """
        セルに意味タグを追加（重複不可）。

        Args:
            tag (str): 追加する意味タグ（例：動詞）
        """
        if tag not in self.meaning_tags:
            self.meaning_tags.append(tag)

    def __repr__(self) -> str:
        """
        セルの簡易表示（デバッグ用）。

        Returns:
            str: 活性度とタグを含む短縮表記
        """
        return f"Cell(id={self.id}, act={self.activation:.2f}, tags={self.meaning_tags})"
