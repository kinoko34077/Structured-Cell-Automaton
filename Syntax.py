
from typing import List, Optional
from dataclasses import dataclass, field
import time
import uuid
from random import shuffle

@dataclass
class Syntax:
    sid: str
    cell_ids: List[str]
    score: float = 0.0
    meaning_cluster: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    parent_sid: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def update_score(self, new_score: float):
        self.score = new_score

    def mutate(self) -> 'Syntax':
        new_cell_ids = self.cell_ids.copy()
        shuffle(new_cell_ids)
        new_sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, ''.join(new_cell_ids) + str(time.time())))
        return Syntax(sid=new_sid, cell_ids=new_cell_ids, parent_sid=self.sid, tags=self.tags)

    def __repr__(self):
        return f"Syntax(sid={self.sid[:8]}, score={self.score:.2f}, len={len(self.cell_ids)})"
