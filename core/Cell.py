
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class Cell:
    id: str
    position: tuple
    syntax_id: Optional[str] = None
    activation: float = 0.0
    meaning_tags: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

    def update_activation(self, delta: float):
        self.activation = max(0.0, self.activation + delta)

    def add_meaning_tag(self, tag: str):
        if tag not in self.meaning_tags:
            self.meaning_tags.append(tag)

    def __repr__(self):
        return f"Cell(id={self.id}, act={self.activation:.2f}, tags={self.meaning_tags})"
