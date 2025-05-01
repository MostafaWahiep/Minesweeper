from dataclasses import dataclass
from enum import Enum, auto


class CellState(Enum):
    """Represents the possible states of a Minesweeper cell."""
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()


@dataclass(slots=True)
class Cell:
    """
    A class representing a single cell in a Minesweeper grid.

    Attributes:
        has_mine (bool): Whether the cell contains a mine.
        adjacent_mines (int): Number of mines in adjacent cells.
        state (CellState): Current state of the cell (hidden, revealed, flagged).
    """
    has_mine: bool = False
    adjacent_mines: int = 0
    state: CellState = CellState.HIDDEN