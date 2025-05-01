from .abstract_agent import AbstractAgent
from core import BoardView
from .move import Move, MoveType

class HumanCLI(AbstractAgent):
    def choose_action(self, view: BoardView) -> Move:
        while True:
            try:
                r = int(input("row > "))
                c = int(input("col > "))
                break
            except ValueError:
                print("Please enter valid integers for row and column.")

        t = input("Enter move type — 'r' to reveal a cell, 'f' to flag a mine: ").strip().lower()
        while t not in ("r", "f"):
            t = input("Invalid move type. Enter 'r' to reveal or 'f' to flag > ").strip().lower()

        move_type = MoveType.FLAG if t == "f" else MoveType.REVEAL
        return Move(move_type, r, c)