# ui/console.py
from __future__ import annotations

from typing import Iterable, List, Tuple

from rich.console import Console
from rich.table import Table

from core import CellState, BoardView
from engine import EventBus, Event, GameState   # Outcome = RUNNING / WON / LOST


class ConsoleUI:
    """
    Simple Rich-based text renderer.
    Listens to the EventBus and redraws the board whenever something changes.
    """

    def __init__(self, bus: EventBus) -> None:
        self._bus: EventBus = bus
        self._con: Console = Console()
        self._last_view: BoardView | None = None   # updated on every event

        # Event subscriptions
        bus.subscribe(Event.GAME_START,   self._on_new_view)
        bus.subscribe(Event.REVEAL_TILES, self._on_new_view)
        bus.subscribe(Event.FLAG_TILES,   self._on_new_view)
        bus.subscribe(Event.GAME_OVER,    self._on_game_over)

    def _on_new_view(self, view: BoardView, *_ignore) -> None:
        """Called for GAME_START, REVEAL_TILES, FLAG_TILES."""
        self._last_view = view
        self._draw_full(view)

    def _on_game_over(self, outcome: GameState, *_ignore) -> None:
        colour = {"WON": "green", "LOST": "red", "IDLE": "yellow"}[outcome.name]
        self._con.print(f"[bold {colour}]Game {outcome.name}![/]")

    def _draw_full(self, view: BoardView) -> None:
        self._con.clear()
        self._con.print(self._render(view))


    def _render(self, view: BoardView) -> Table:
        tbl = Table.grid(padding=0)
        symbols = {
            CellState.HIDDEN: "■",
            CellState.FLAGGED: "⚑"
        }

        header = [' ']*2
        for c in range(view.cols):
            header.extend([str(c), ' '])
        tbl.add_row(*header)

        for r in range(view.rows):
            row: List[str] = [str(r), ' ']
            for c in range(view.cols):
                state, num = view[r, c]
                if state is CellState.REVEALED and not view._grid[r][c].has_mine:
                    row.append(str(num or " "))
                elif state is CellState.REVEALED and view._grid[r][c].has_mine:
                        row.append("💣")
                else:
                    row.append(symbols[state])
                row.append(' ')
            tbl.add_row(*row)
        return tbl