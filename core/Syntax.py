"""
Syntax.py

構文（Syntax）構造体を定義するモジュール。

構文は、構成セル列、意味タグ、スコア、進化系譜（親SID）などを保持し、
進化・再活性・淘汰・整形出力の基本単位をなす。
"""

from typing import List, Optional
from dataclasses import dataclass, field
import time
import uuid
from random import shuffle

@dataclass
class Syntax:
    """
    構文構造体クラス。

    Attributes:
        sid (str): 構文ID（UUIDベース）
        cell_ids (List[str]): セルID列（構成するセルの順序列）
        score (float): 評価スコア
        meaning_cluster (Optional[str]): クラスタ分類（未使用またはSemantic Cluster Map用）
        created_at (float): 生成時刻（UNIX時間）
        parent_sid (Optional[str]): 親構文ID（進化元）
        tags (List[str]): 意味タグのリスト（構成セルからの総和）
        generation_stamp (int): 生成世代スタンプ（記憶圏管理用）
    """
    sid: str
    cell_ids: List[str]
    score: float = 0.0
    meaning_cluster: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    parent_sid: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    generation_stamp: int = 0

    def update_score(self, new_score: float):
        """
        構文のスコアを更新する。

        Args:
            new_score (float): 新しいスコア値
        """
        self.score = new_score

    def mutate(self) -> 'Syntax':
        """
        構文を変異（セル順序をシャッフル）して新構文を生成。

        Returns:
            Syntax: 新しい構文インスタンス（親SIDを継承）
        """
        new_cell_ids = self.cell_ids.copy()
        shuffle(new_cell_ids)
        new_sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, ''.join(new_cell_ids) + str(time.time())))
        return Syntax(
            sid=new_sid,
            cell_ids=new_cell_ids,
            parent_sid=self.sid,
            tags=self.tags
        )

    def __repr__(self) -> str:
        """
        構文の簡易表示（スコアと長さ）。

        Returns:
            str: 簡易構文情報
        """
        return f"Syntax(sid={self.sid[:8]}, score={self.score:.2f}, len={len(self.cell_ids)})"
