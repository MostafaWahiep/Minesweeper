#!/usr/bin/env python3

import time, statistics as stats
from collections import defaultdict
from queue import SimpleQueue

from core   import Board, GameConfig, CellState, BoardView
from engine import EventBus, Event, GameState, GameController
from agents import PrologAgent, Move, MoveType, PrologEngine


GLOBAL_PE = PrologEngine("kb.pl")
# ──────────────────────────────────────────────────────────────────────
class AbortGuess(Exception):
    """Raised when the agent would require a human guess."""


class HeadlessPrologAgent(PrologAgent):
    """PrologAgent variant that aborts instead of waiting for a user click."""
    def __init__(self, view, bus, *_):
        super().__init__(view, bus, click_q:=SimpleQueue(), engine=GLOBAL_PE)
        # keep click_q but we will never use it

    def _handle_by_human_agent(self, view: BoardView) -> Move:
        # Immediately abort the current game; outer loop will retry.
        raise AbortGuess


# ──────────────────────────────────────────────────────────────────────
def play_until_done(cfg: GameConfig):
    """Run one game; return dict with keys {win, coverage, moves, latency}.

    If the solver needs to guess, AbortGuess is propagated to caller.
    """
    board = Board(cfg)
    bus   = EventBus()
    agent = HeadlessPrologAgent(board.view(), bus)
    gc    = GameController(board, bus, agent)

    # simple metric collectors
    safe_total = cfg.rows * cfg.cols - cfg.mines
    safe_revealed = moves = 0
    start = time.perf_counter()
    latencies = []

    # Update counters inside the step loop for simplicity
    while True:
        try:
            status = gc.step()
        except AbortGuess:
            status = None
        moves += 1
        now = time.perf_counter()
        latencies.append(now - start)
        start = now
        if status is GameState.RUNNING:
            continue
        # count safe squares revealed
        break

    safe_revealed = sum(
            1
            for r in range(cfg.rows)
            for c in range(cfg.cols)
            if board._grid[r][c].state is CellState.REVEALED and not board._grid[r][c].has_mine
        )

    return {
        "win":            int(status is GameState.WON),
        "coverage":       safe_revealed / safe_total,
        "moves":          moves,
        "ms_per_move":    stats.mean(latencies) * 1_0 if latencies else 0,
    }


def suite(cfg: GameConfig, completed_games: int = 100) -> None:
    """Run until <completed_games> boards finish without NEED_GUESS."""
    agg = defaultdict(list)
    attempts = 0
    success = 0
    while success < completed_games:
        attempts += 1
        try:
            res = play_until_done(cfg)
        except AbortGuess:
            continue  # discarded, start a new board
        for k, v in res.items():
            agg[k].append(v)
        if res['win']:
            success += 1

    print(f"\n{cfg.rows}×{cfg.cols} / {cfg.mines} mines"
          f"  —  finished {completed_games} boards "
          f"after {attempts} attempts")
    print(f"  Win rate             : {completed_games/attempts*100:6.2f}%")
    print(f"  forced-move coverage : {stats.mean(agg['coverage'])*100:6.2f}%")
    print(f"  avg moves per board  : {stats.mean(agg['moves']):6.1f}")
    print(f"  latency per move     : {stats.mean(agg['ms_per_move']):6.2f} ms")


# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    presets = {
        "Beginner"     : GameConfig(9, 9, 10),
        "Normal"       : GameConfig(16, 16, 40),
        "Hard"         : GameConfig(24, 16, 70)    
    }
    for name, cfg in presets.items():
        print(f"\n### {name}")
        suite(cfg, completed_games=50)    