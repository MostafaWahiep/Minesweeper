from enum import Enum, auto
from dataclasses import dataclass

class MoveType(Enum):
    REVEAL = auto()
    FLAG   = auto()
    OUT_OF_MOVES = auto()

@dataclass(frozen=True, slots=True)
class Move:
    type: MoveType
    r: int
    c: int
