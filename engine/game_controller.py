from .game_state import GameState
from core import Board, CellState, BoardView
from .event_bus import EventBus
from .events import Event
from agents import MoveType, AbstractAgent
import time

class GameController:
    def __init__(self, board: Board, bus: EventBus, agent: AbstractAgent):
        self.board = board
        self.state = GameState.RUNNING
        self.bus = bus
        self.agent = agent
        self.bus.publish(Event.GAME_START, board.view())
        self.start = time.perf_counter()

    def step(self) -> GameState:
        if self.state is not GameState.RUNNING:
            return self.state

        move = self.agent.choose_action(self.board.view())

        if move.type == MoveType.OUT_OF_MOVES:
            self.state = GameState.IDLE
            self.bus.publish(Event.GAME_OVER, self.state)
            return GameState.IDLE

        if move.type == MoveType.REVEAL:
            changed = self.board.reveal(move.r, move.c)
            self.bus.publish(Event.REVEAL_TILES, self.board.view(), changed)
        else:
            try:
                was_flagged = self.board.flag(move.r, move.c)
                event = Event.FLAG_TILES if was_flagged else Event.UNFLAG_TILES
                self.bus.publish(event, self.board.view(), [(move.r, move.c)])
            except ValueError:
                pass

        if self.board.lost():
            self.state = GameState.LOST
            self.bus.publish(Event.GAME_OVER, self.state)
        else:
            finished, auto_flagged = self.board.is_finished()
            if finished:
                if auto_flagged:
                    self.bus.publish(Event.FLAG_TILES, self.board.view(), auto_flagged)
                self.state = GameState.WON
                self.bus.publish(Event.GAME_OVER, self.state)

        return self.state