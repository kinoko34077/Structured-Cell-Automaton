"""
memory_zone.py

構文の記憶・再活性・圧縮・淘汰を担当する記憶ゾーンクラス。
構文をSIDで一意管理し、進化ループや再出力に用いる。
"""

import time
from typing import List, Optional
from core import Syntax

DEFAULT_MAX_AGE_GENERATIONS = 60

def prune_memory_by_generation(memory_zone, current_generation: int, max_age_generations: int = DEFAULT_MAX_AGE_GENERATIONS):
    """世代差による記憶淘汰を設定値から実行する。"""
    return memory_zone.prune_by_generation(current_gen=current_generation, max_age=max_age_generations)

class MemoryZone:
    """
    記憶圏クラス。構文を辞書で管理し、再活性や世代淘汰を提供する。
    """

    def __init__(self):
        self.pool: dict[str, Syntax] = {}

    def store(self, syntax: Syntax, current_gen: Optional[int] = None):
        """
        構文を記憶圏に保存。

        Args:
            syntax (Syntax): 保存する構文
            current_gen (Optional[int]): 世代スタンプ（進化ループ用）
        """
        if current_gen is not None:
            syntax.generation_stamp = current_gen
        self.pool[syntax.sid] = syntax

    def reactivate_candidates(self, trigger_tags: List[str], threshold=0.3) -> List[Syntax]:
        """
        タグに基づいて再活性可能な構文候補を返す。

        Args:
            trigger_tags (List[str]): 発話構文などから得たトリガータグ群
            threshold (float): 類似度しきい値（Jaccard係数）

        Returns:
            List[Syntax]: 条件を満たす構文リスト
        """
        return [
            s for s in self.pool.values()
            if len(set(s.tags) & set(trigger_tags)) / max(len(set(s.tags) | set(trigger_tags)), 1) >= threshold
        ]

    def prune_by_score(self, min_score=0.3):
        """スコアが一定未満の構文を淘汰"""
        before_count = len(self.pool)
        self.pool = {
            sid: s for sid, s in self.pool.items()
            if s.score >= min_score
        }
        return before_count - len(self.pool)

    def prune_by_generation(self, current_gen: int, max_age: int = 60):
        """世代差がmax_age以上の構文を淘汰"""
        before_count = len(self.pool)
        self.pool = {
            sid: s for sid, s in self.pool.items()
            if hasattr(s, "generation_stamp") and (current_gen - s.generation_stamp) <= max_age
        }
        return before_count - len(self.pool)

    def prune_by_similarity(self, threshold=0.9):
        """類似タグをもつ冗長構文を圧縮（タグのJaccard類似）"""
        before_count = len(self.pool)
        unique = {}
        for sid, s in self.pool.items():
            if all(
                len(set(s.tags) & set(u.tags)) / max(len(set(s.tags) | set(u.tags)), 1) < threshold
                for u in unique.values()
            ):
                unique[sid] = s
        self.pool = unique
        return before_count - len(self.pool)

    def auto_optimize(self, score_thresh=0.3, age_limit=60, similarity_thresh=0.9, current_gen=0):
        """
        スコア・世代・類似性に基づく複合最適化を実施。

        Args:
            score_thresh (float): 最小スコア閾値
            age_limit (int): 最大保持世代数
            similarity_thresh (float): 類似タグしきい値
            current_gen (int): 現在の世代数（世代差計算用）
        """
        before_count = len(self.pool)
        self.prune_by_score(min_score=score_thresh)
        self.prune_by_generation(current_gen=current_gen, max_age=age_limit)
        self.prune_by_similarity(threshold=similarity_thresh)
        after_count = len(self.pool)
        print(f"[記憶圏最適化] 構文数: {before_count} → {after_count}")
