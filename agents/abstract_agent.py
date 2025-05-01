from abc import ABC, abstractmethod
from core import BoardView
from .move import Move

class AbstractAgent(ABC):
    @abstractmethod
    def choose_action(self, view: BoardView) -> Move: ...
