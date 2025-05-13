import time
from typing import List, Dict
from Syntax import Syntax

class MemoryZone:
    def __init__(self, lambda_decay=0.01):
        self.memory: Dict[str, Dict] = {}  # SID → {syntax, timestamp, score}
        self.lambda_decay = lambda_decay

    def store(self, syntax: Syntax):
        self.memory[syntax.sid] = {
            "syntax": syntax,
            "timestamp": time.time(),
            "score": syntax.score
        }

    def decay_score(self, entry):
        delta_t = time.time() - entry["timestamp"]
        return entry["score"] * (2.718 ** (-self.lambda_decay * delta_t))

    def reactivate_candidates(self, current_tags: List[str], threshold=0.3) -> List[Syntax]:
        candidates = []
        for sid, entry in self.memory.items():
            syn = entry["syntax"]
            if any(tag in current_tags for tag in syn.tags):
                score = self.decay_score(entry)
                if score >= threshold:
                    syn.score = score  # 更新
                    candidates.append(syn)
        return candidates
