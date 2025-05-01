from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameConfig:
    """
    Immutable configuration for Minesweeper game.

    Attributes:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
        mines (int): Number of mines to place.
        first_click_safe (bool): Whether the first click is guaranteed to be safe (default: True).
    """
    rows: int
    cols: int
    mines: int
    first_click_safe: bool = True

    def __post_init__(self):
        """Validate mine count after initialization."""
        max_mines = self.max_allowed_mines()
        if self.mines > max_mines:
            raise ValueError(
                f"Too many mines: {self.mines}. "
                f"Maximum allowed is {max_mines} for a {self.rows}x{self.cols} board with first-click safety: {self.first_click_safe}."
            )

    def max_allowed_mines(self) -> int:
        """
        Returns the maximum number of mines allowed based on board size
        and the safety buffer if first-click safety is enabled.
        """
        return self.rows * self.cols - (9 if self.first_click_safe else 0)
