import time
from typing import List
from Syntax import Syntax

class MemoryZone:
    def __init__(self):
        self.pool: List[Syntax] = []
        self.timestamps = {}

    def store(self, syntax: Syntax):
        self.pool.append(syntax)
        self.timestamps[syntax.sid] = time.time()

    def reactivate_candidates(self, trigger_tags: List[str], threshold=0.3) -> List[Syntax]:
        return [
            s for s in self.pool
            if len(set(s.tags) & set(trigger_tags)) / max(len(set(s.tags) | set(trigger_tags)), 1) >= threshold
        ]

    # 🔴 スコア淘汰
    def prune_by_score(self, min_score=0.3):
        self.pool = [s for s in self.pool if s.score >= min_score]

    # 🔵 時間淘汰（60秒より古い構文を削除：デバッグ用）
    def prune_by_age(self, age_limit=60):
        now = time.time()
        self.pool = [s for s in self.pool if (now - self.timestamps.get(s.sid, now)) < age_limit]

    # 🟢 類似構文淘汰（Jaccard 類似が高すぎる構文は間引く）
    def prune_by_similarity(self, threshold=0.9):
        unique = []
        for s in self.pool:
            if all(len(set(s.tags) & set(u.tags)) / max(len(set(s.tags) | set(u.tags)), 1) < threshold for u in unique):
                unique.append(s)
        self.pool = unique

    def auto_optimize(self, score_thresh=0.3, age_limit=60, similarity_thresh=0.9):
        before_count = len(self.pool)
        
        self.prune_by_score(min_score=score_thresh)
        self.prune_by_age(age_limit=age_limit)
        self.prune_by_similarity(threshold=similarity_thresh)

        after_count = len(self.pool)
        print(f"[記憶圏最適化] 構文数: {before_count} → {after_count}")


