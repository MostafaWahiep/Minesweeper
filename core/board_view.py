from typing import Sequence
from .cell import Cell, CellState


class BoardView:
    """
    Immutable, read-only view of the Minesweeper board.

    Designed for use by UI or AI agents, providing access to only
    the visible, legitimate information a player would know:
    
    - Cell state (HIDDEN, FLAGGED, REVEALED)
    - Adjacent mine counts (for revealed non-mine cells only)
    
    This class performs no copying and does not expose any mutation methods.
    Internally, it shares the original Cell objects for performance (O(1) to create).
    """

    __slots__ = ("_grid", "_rows", "_cols")

    def __init__(self, grid: Sequence[Sequence[Cell]]):
        """
        Initialize a read-only view over the game grid.

        Args:
            grid (Sequence[Sequence[Cell]]): The original game board.
        """
        self._grid = grid
        self._rows = len(grid)
        self._cols = len(grid[0]) if grid else 0

    @property
    def rows(self) -> int:
        """
        Get the number of rows in the board.

        Returns:
            int: Row count.
        """
        return self._rows

    @property
    def cols(self) -> int:
        """
        Get the number of columns in the board.

        Returns:
            int: Column count.
        """
        return self._cols

    def state(self, r: int, c: int) -> CellState:
        """
        Get the visible state of the cell at (r, c).

        Args:
            r (int): Row index.
            c (int): Column index.

        Returns:
            CellState: The current state of the cell.
        """
        return self._grid[r][c].state

    def number(self, r: int, c: int) -> int:
        """
        Get the adjacent mine count for a revealed non-mine cell.

        Raises:
            ValueError: If the cell is hidden, flagged, or contains a mine.

        Args:
            r (int): Row index.
            c (int): Column index.

        Returns:
            int: Number of adjacent mines (0–8).
        """
        cell = self._grid[r][c]
        if cell.state is CellState.REVEALED and not cell.has_mine:
            return cell.adjacent_mines
        raise ValueError("Cell is not a visible number square")

    def __getitem__(self, rc: tuple[int, int]) -> tuple[CellState, int | None]:
        """
        Access cell data via indexing: view[r, c].

        Args:
            rc (tuple[int, int]): Tuple of (row, column).

        Returns:
            tuple[CellState, int | None]: Cell state and number if revealed, else None.
        """
        r, c = rc
        cell = self._grid[r][c]
        return (
            cell.state,
            cell.adjacent_mines if cell.state is CellState.REVEALED else None,
        )

    def __iter__(self):
        """
        Iterate over the board in row-major order.

        Yields:
            tuple[int, int, CellState, int | None]: Row, column, cell state,
                and adjacent mine count (if revealed).
        """
        for r in range(self._rows):
            for c in range(self._cols):
                s, n = self[r, c]
                yield r, c, s, n
