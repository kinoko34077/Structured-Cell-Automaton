# ◆Board.py
from typing import Dict, Tuple
from Cell import Cell

class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: Dict[Tuple[int, int], Cell] = {}

    def place_cell(self, cell: Cell):
        self.grid[cell.position] = cell

    def get_cell(self, x: int, y: int) -> Cell:
        return self.grid.get((x, y))

    def get_neighbors(self, x: int, y: int) -> list:
        offsets = [(-1,0), (1,0), (0,-1), (0,1)]
        return [
            self.grid.get((x+dx, y+dy))
            for dx, dy in offsets
            if (x+dx, y+dy) in self.grid
        ]

    def __repr__(self):
        return "\n".join(
            f"({pos}): {cell}"
            for pos, cell in self.grid.items()
        )
