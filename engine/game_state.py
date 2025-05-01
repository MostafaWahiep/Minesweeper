from enum import Enum, auto

class GameState(Enum):
    IDLE = auto()
    RUNNING = auto()
    WON = auto()
    LOST = auto()
