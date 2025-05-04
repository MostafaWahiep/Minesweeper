from pyswip import Prolog, Atom, Variable, registerForeign
from enum import Enum


class Predicates(Enum):
    REVEALED = "revealed"
    FLAGGED = "flagged"
    ROWS = "rows"
    COLS = "cols"

    def __str__(self) -> str:
        return self.value

class PrologEngine:
    def __init__(self, kb_file: str) -> None:
        self._prolog = Prolog()
        self._prolog.consult(kb_file)
        self.reset()
        self._prolog.query("retractall(_).")

    def deduce(self) -> list[tuple[int, int, str]]:
        mines = list(self._prolog.query("single_sure_mine(X, Y)."))
        reveals = list(self._prolog.query("single_can_reveal(X, Y)."))

        if not mines and not reveals:
            mines = list(self._prolog.query("subset_mine(X, Y).", maxresult=1))
            reveals = list(self._prolog.query("subset_safe(X, Y).", maxresult=1))

        if not mines and not reveals:
            mines = list(self._prolog.query("diff_mine(X, Y).", maxresult=1))
            reveals = list(self._prolog.query("diff_safe(X, Y).", maxresult=1))

        unique_mines = {(d["X"], d["Y"]) for d in mines}
        unique_reveals = {(d["X"], d["Y"]) for d in reveals}

        moves = []

        for row, col in unique_mines:
            moves.append((row, col, 'f'))

        for row, col in unique_reveals:
            moves.append((row, col, 'r'))

        return moves
        
    def feed_revealed_cell(self, row: int, col: int, val: int) -> None:
        predicate = str(Predicates.REVEALED)
        fact = f"{predicate}({row}, {col}, {val})"
        self._prolog.assertz(fact)


    def initialize_dimensions(self, rows:int , cols:int ) -> None:
        self._prolog.query(f"retractall({str(Predicates.ROWS)}(_)).")
        self._prolog.query(f"retractall({str(Predicates.COLS)}(_)).")
        
        self._prolog.assertz(f"{str(Predicates.ROWS)}({rows})")
        self._prolog.assertz(f"{str(Predicates.COLS)}({cols})")


    def add_flagged_cell(self, row: int, col: int) -> None:
        predicate = str(Predicates.FLAGGED)
        fact = f"{predicate}({row}, {col})"
        self._prolog.assertz(fact)

    def remove_flagged_cell(self, row: int, col: int) -> None:
        predicate = str(Predicates.FLAGGED)
        fact = f"{predicate}({row}, {col})"
        self._prolog.retract(fact)

    def reset(self):
        patterns = {
            Predicates.REVEALED: "(_,_,_)",
            Predicates.FLAGGED: "(_,_)",
            Predicates.ROWS: "(_)",
            Predicates.COLS: "(_)",
        }
        
        for pred, pattern in patterns.items():
            self._prolog.retractall(f"{pred.value}{pattern}")
