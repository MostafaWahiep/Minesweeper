from enum import Enum, auto

class Event(Enum):
    FLAG_TILES = auto()
    UNFLAG_TILES = auto()
    REVEAL_TILES = auto()
    GAME_OVER = auto()
    GAME_START = auto()
    NEED_GUESS  = auto()    # UI should start accepting clicks
    GUESS_DONE  = auto()    # UI should ignore clicks again
    REVEAL_MINE = auto()