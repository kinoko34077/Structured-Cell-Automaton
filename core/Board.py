"""
Board.py

構文セル（Cell）を2次元グリッド上に配置・操作するための盤面クラス。

本モジュールは「構文の空間的配置」や「局所構造（近傍セル）」を抽出する目的で使用される。
現段階では構文抽出への応用は限定的だが、空間的構文処理やグラフ進化モデル等に発展可能。
"""

from typing import Dict, Tuple
from core import Cell

class Board:
    """
    セルを2次元グリッドに配置・管理する盤面クラス。

    Attributes:
        width (int): 盤面の幅（セル単位）
        height (int): 盤面の高さ（セル単位）
        grid (Dict[Tuple[int, int], Cell]): 座標 → セルのマッピング辞書
    """

    def __init__(self, width: int, height: int):
        """
        ボードの初期化。

        Args:
            width (int): 横幅
            height (int): 高さ
        """
        self.width = width
        self.height = height
        self.grid: Dict[Tuple[int, int], Cell] = {}

    def place_cell(self, cell: Cell):
        """
        指定したセルをボード上に配置する。

        Args:
            cell (Cell): 配置対象のセル（.position 属性を持つこと）
        """
        self.grid[cell.position] = cell

    def get_cell(self, x: int, y: int) -> Cell:
        """
        指定座標のセルを取得する。

        Args:
            x (int): X座標
            y (int): Y座標

        Returns:
            Cell: 指定位置に存在するセル、存在しない場合は None
        """
        return self.grid.get((x, y))

    def get_neighbors(self, x: int, y: int) -> list:
        """
        指定セルの上下左右の隣接セルを取得する。

        Args:
            x (int): 対象セルのX座標
            y (int): 対象セルのY座標

        Returns:
            list: 隣接セルのリスト（存在しないセルは含まれない）
        """
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return [
            self.grid.get((x + dx, y + dy))
            for dx, dy in offsets
            if (x + dx, y + dy) in self.grid
        ]

    def __repr__(self) -> str:
        """
        現在の盤面状態を文字列として返す。

        Returns:
            str: 各セルの座標と内容の一覧文字列
        """
        return "\n".join(
            f"({pos}): {cell}"
            for pos, cell in self.grid.items()
        )
