# ◆memory_zone.py
import time
from typing import List, Optional
from core import Syntax

class MemoryZone:
    def __init__(self):
        self.pool: dict[str, Syntax] = {}  # ← SyntaxをSIDで一意管理
        # self.timestamps = {}  # 使用せずとも created_at に内包可能

    def store(self, syntax: Syntax, current_gen: Optional[int] = None):
        if current_gen is not None:
            syntax.generation_stamp = current_gen
        self.pool[syntax.sid] = syntax
    def reactivate_candidates(self, trigger_tags: List[str], threshold=0.3) -> List[Syntax]:
        return [
            s for s in self.pool.values()
            if len(set(s.tags) & set(trigger_tags)) / max(len(set(s.tags) | set(trigger_tags)), 1) >= threshold
        ]

    # 🔴 スコア淘汰
    def prune_by_score(self, min_score=0.3):
        self.pool = {
            sid: s for sid, s in self.pool.items()
            if s.score >= min_score
        }

    # 🔵 世代スタンプによる世代淘汰
    def prune_by_generation(self, current_gen: int, max_age: int = 60):
        self.pool = {
            sid: s for sid, s in self.pool.items()
            if hasattr(s, "generation_stamp") and (current_gen - s.generation_stamp) <= max_age
        }

    # 🟡 時間淘汰（旧方式・廃止済み）
    # def prune_by_age(self, age_limit: int = 60):
    #     now = time.time()
    #     self.pool = {
    #         sid: s for sid, s in self.pool.items()
    #         if (now - s.created_at) <= age_limit
    #     }

    # 🟢 類似構文の圧縮
    def prune_by_similarity(self, threshold=0.9):
        unique = {}
        for sid, s in self.pool.items():
            if all(
                len(set(s.tags) & set(u.tags)) / max(len(set(s.tags) | set(u.tags)), 1) < threshold
                for u in unique.values()
            ):
                unique[sid] = s
        self.pool = unique

    def auto_optimize(self, score_thresh=0.3, age_limit=60, similarity_thresh=0.9, current_gen=0):
        before_count = len(self.pool)
        self.prune_by_score(min_score=score_thresh)
        self.prune_by_generation(current_gen=current_gen, max_age=age_limit)
        self.prune_by_similarity(threshold=similarity_thresh)
        after_count = len(self.pool)
        print(f"[記憶圏最適化] 構文数: {before_count} → {after_count}")
