from ..abstract_agent import AbstractAgent
from collections import deque
from ..move import Move, MoveType
from core import BoardView, CellState
from engine import EventBus, Event
import random
from .engine import PrologEngine
from ..human_cli import HumanCLI
from queue import SimpleQueue


class PrologAgent(AbstractAgent):
    def __init__(
            self,
            view: BoardView,
            bus: EventBus, 
            click_q: SimpleQueue[tuple[int,int]],
            engine: PrologEngine | None = None
            ):
        self._moves: deque[Move] = deque()
        self._new_reveals: list[tuple[int, int, int]] = []
        self._click_q = click_q

        self._engine: PrologEngine = PrologEngine("kb.pl") if engine is None else engine
        self._engine.reset()
        self._engine.initialize_dimensions(view.rows, view.cols)

        self._bus: EventBus = bus
        self._bus.subscribe(Event.REVEAL_TILES, self._on_reveal_tiles)
        self._bus.subscribe(Event.FLAG_TILES, self._on_flagged_cell)
        self._bus.subscribe(Event.UNFLAG_TILES, self._on_unflagged_cell)

        row = random.randrange(view.rows)
        col = random.randrange(view.cols)
        first_move = Move(MoveType.REVEAL, row, col)
        self._moves.append(first_move)
    
    def choose_action(self, view: BoardView) -> Move:
        if not self._moves:
            # deduce new moves
            self._engine.feed_revealed_cells(self._new_reveals)
            self._new_reveals.clear()
            moves = self._engine.deduce()
            self._pack_moves(moves)

            if not moves:
                return self._handle_by_human_agent(view)
        
        move = self._moves.popleft()
        return move


    def _on_reveal_tiles(self, view: BoardView, changed: list[tuple[int, int]]) -> None:
        for row, col in changed:
            state, number = view[row, col]

            # Skip anything not revealed
            if state is not CellState.REVEALED:
                continue

            self._new_reveals.append((row, col, number))
            

    def _pack_moves(self, moves: list[tuple[int, int, str]]) -> None:
        """Converts (row, col, type_str) tuples into Move objects and stores them."""
        for row, col, kind in moves:
            if kind == "r":
                move_type = MoveType.REVEAL
            elif kind == "f":
                move_type = MoveType.FLAG
            else:
                raise ValueError(f"Unknown move type: {kind!r}")

            move = Move(move_type, row, col)
            self._moves.append(move)

    def _handle_by_human_agent(self, view: BoardView) -> Move:
        print("No logical move – please click a cell in the GUI…")
        self._bus.publish(Event.NEED_GUESS)

        # empty any stale clicks
        while not self._click_q.empty():
            self._click_q.get_nowait()

        move_type, row, col = self._click_q.get()                # blocks here
        self._bus.publish(Event.GUESS_DONE)           # (UI also triggers it)

        return Move(move_type, row, col)        # or FLAG if you prefer

    def _on_flagged_cell(self, view: BoardView, changed: list[tuple[int, int]]) -> None:
        for row, col in changed:
            self._engine.add_flagged_cell(row, col)

    def _on_unflagged_cell(self, view: BoardView, changed: list[tuple[int, int]]) -> None:
        for row, col in changed:
            self._engine.remove_flagged_cell(row, col)

    def reset(self):
        self._engine.reset()