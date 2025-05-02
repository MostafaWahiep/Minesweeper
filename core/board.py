from .config import GameConfig
from .cell import Cell, CellState
import random
from .board_view import BoardView

class Board:
    """
    Core game logic for a Minesweeper board.

    This class manages the grid of cells, mine placement, cell revealing,
    flag toggling, and win/loss state evaluation. It supports first-click
    safety and exposes a read-only board view for UI or AI purposes.
    """

    def __init__(self, cfg: GameConfig):
        """
        Initialize the board with a given configuration.

        Args:
            cfg (GameConfig): Configuration for the board (dimensions, mines, etc.).
        """
        self._grid: list[list[Cell]] = [
            [Cell() for _ in range(cfg.cols)]
            for _ in range(cfg.rows)
        ]
        self._cfg:  GameConfig = cfg
        self._mines_placed: bool = False
        self._safe_left: int = cfg.rows * cfg.cols - cfg.mines
        self._lost: bool = False
        self._flags: int = 0

        if not cfg.first_click_safe:
            self._place_mines(exclude=None) 

    def reveal(self, row: int, col: int) -> list[tuple[int, int]]:
        """
        Reveal the cell at (row, col) and any connected empty cells.

        If the selected cell contains a mine, the game is lost.
        If it's empty (zero adjacent mines), adjacent empty cells are also revealed recursively.

        Args:
            row (int): Row index of the cell to reveal.
            col (int): Column index of the cell to reveal.

        Returns:
            list[tuple[int, int]]: List of coordinates of cells that were revealed.
        """
        if not self._validate_coord(row, col):
            return []

        if not self._mines_placed:
            self._place_mines(exclude=(row, col))
            self._mines_placed = True

        cell = self._grid[row][col]

        if cell.state == CellState.FLAGGED or cell.state == CellState.REVEALED:
            return []

        if cell.has_mine:
            cell.state = CellState.REVEALED
            self._lost = True
            return [(row, col)]

        cell.state = CellState.REVEALED
        self._safe_left -= 1

        visited: set[tuple[int, int]] = {(row, col)}
        if cell.adjacent_mines == 0:
            self._flood(row, col, visited)

        return list(visited)


    def _flood(self, row, col, visited: set[tuple[int, int]]) -> None:
        """
        Recursively reveal all connected empty cells with zero adjacent mines.

        This is flood-fill algorithm that reveals safe areas when a 
        cell with no adjacent mines is clicked.

        Args:
            row (int): Row index.
            col (int): Column index.
            visited (set[tuple[int, int]]): Set of already revealed cell coordinates.
        """
        for n_row, n_col in self._neighbors(row, col):
            if (n_row, n_col) in visited:
                continue

            cell = self._grid[n_row][n_col]
            if cell.state != CellState.HIDDEN:
                continue

            visited.add((n_row, n_col))
            self._safe_left -= 1
            cell.state = CellState.REVEALED

            if cell.adjacent_mines == 0 and not cell.has_mine:
                self._flood(n_row, n_col, visited)


    def flag(self, row: int, col: int) -> bool | None:
        """
        Toggles a flag on a hidden cell. If the cell is hidden, it becomes flagged.
        If it's already flagged, the flag is removed.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.

        Returns:
            bool | None:
                - True if the cell was flagged,
                - False if the flag was removed,
                - None if the coordinates are invalid or the cell is not flaggable.
        """
        if not self._validate_coord(row, col):
            return None

        cell = self._grid[row][col]

        if cell.state == CellState.REVEALED:
            raise ValueError("Invalid move; flagging a revealed cell!")

        if cell.state == CellState.HIDDEN:
            cell.state = CellState.FLAGGED
            self._flags += 1
            return True
        elif cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN
            self._flags -= 1
            return False

        return None  # Explicitly return None if cell is revealed or not toggleable


    def is_finished(self) -> tuple[bool, list[tuple[int,int]]]:
        """
        Check if the game is successfully completed.

        The game is considered finished when all non-mine cells have been revealed. 
        At that point, all remaining hidden cells must contain mines. This method 
        flags any remaining hidden cells and returns their coordinates.

        Returns:
            tuple[bool, list[tuple[int, int]]]:
                - A boolean indicating if the game is won.
                - A list of coordinates for newly flagged cells.
        """
        if self._safe_left != 0:
            return False, []

        changed_coords: list[tuple[int, int]] = []

        for row_idx, row in enumerate(self._grid):
            for col_idx, cell in enumerate(row):
                if cell.state == CellState.HIDDEN:
                    cell.state = CellState.FLAGGED
                    changed_coords.append((row_idx, col_idx))

        return True, changed_coords

    def lost(self) -> bool:
        """
        Checks if the game has been lost due to revealing a mine.

        Returns:
            bool: True if the game has been lost, False otherwise.
        """
        return self._lost

    def view(self) -> BoardView:
        """
        Return a read-only snapshot of the current board state.

        O(1) Operation and provides a safe view for UI rendering or AI agents. 
        The returned view does not expose hidden mines or allow mutation.

        Returns:
            BoardView: An immutable representation of the grid, revealing only visible information.
        """
        return BoardView(self._grid)
        
    def _place_mines(self, exclude: tuple[int, int] | None) -> None:
        """
        Randomly place mines on the board and update adjacent mine counts.

        Mines are placed with uniform randomness, excluding the first-clicked cell 
        and its neighbors (for first-click safety). After placement, the adjacent 
        mine count is updated for each non-mine cell.

        Args:
            exclude (tuple[int, int] | None): Coordinates of the first-clicked cell 
                to exclude from mine placement, along with its neighbors.
        """
        coords = [
            (row, col)
            for row in range(self._cfg.rows)
            for col in range(self._cfg.cols)
        ]

        if exclude:
            coords.remove(exclude)
        
            for neighbor in self._neighbors(*exclude):
                coords.remove(neighbor)

        mines_coord = random.Random().sample(coords, k=self._cfg.mines)

        for row, col in mines_coord:
            self._grid[row][col].has_mine = True

        for row, col in mines_coord:
            for new_row, new_col in self._neighbors(row, col):
                if not self._grid[new_row][new_col].has_mine:
                    self._grid[new_row][new_col].adjacent_mines += 1
    
    def _neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        """
        Yield coordinates of all valid neighboring cells.

        A neighbor is any adjacent cell in the 8 surrounding directions
        within the grid bounds.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.

        Yields:
            tuple[int, int]: Coordinates (row, col) of each valid neighbor.
        """
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue

                new_row = row + d_row
                new_col = col + d_col

                if self._validate_coord(new_row, new_col):
                    yield (new_row, new_col)


    def _validate_coord(self, row: int, col: int) -> bool:
        """
        Check if given coordinates are within the boundaries of the board.

        Returns:
            bool: True if coordinates are valid, False otherwise.
        """
        if row < 0 or row >= self._cfg.rows or col < 0 or col >= self._cfg.cols:
            return False

        return True
