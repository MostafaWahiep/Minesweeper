# minesweeper/ui/tk_gui.py

import tkinter as tk
from typing import Dict, List, Tuple
from queue import SimpleQueue
from agents import MoveType

from core   import CellState, BoardView
from engine import EventBus, Event, GameState

# Defualt visual constants for Minesweeper
CELL_PX = 28
FONT    = ("Consolas", 12, "bold")
NUMBER_COLOURS = {1:"#0000FF",2:"#008200",3:"#FF0000",4:"#000084",
                  5:"#840000",6:"#008284",7:"#000000",8:"#808080"}
HIDDEN_FILL, REVEALED_FILL, FLAG_FILL = "#BDBDBD", "#D0D0D0", "#BDBDBD"
GRID_OUTLINE, MINE_FILL               = "#7B7B7B", "#FA5858"
FLASH_MS, BLINK_MS, BLINK_CYCLES      = 160, 120, 4


class TkUI(tk.Canvas):
    """Incremental-patch GUI; enqueues clicks *only* when the agent requests."""

    def __init__(
        self,
        master:   tk.Misc,
        rows:     int,
        cols:     int,
        cell_px:  int,
        bus:      EventBus,
        click_q:  SimpleQueue[tuple[int, int]],
    ) -> None:
        super().__init__(
            master,
            width=cols * cell_px,
            height=rows * cell_px,
            highlightthickness=0,
            bg="black",
        )

        self.rows, self.cols, self.cpx = rows, cols, cell_px
        self.bus  = bus
        self._click_q            = click_q
        self._awaiting_guess     = False
        self._rect: Dict[Tuple[int, int], int] = {}
        self._text: Dict[Tuple[int, int], int] = {}
        self._view: BoardView | None = None

        # ── subscribe to engine events ─────────────────────────────────
        bus.subscribe(Event.GAME_START,   self._init_grid)
        bus.subscribe(Event.REVEAL_TILES, self._update_tiles)
        bus.subscribe(Event.FLAG_TILES,   self._update_tiles)
        bus.subscribe(Event.UNFLAG_TILES, self._update_tiles)
        bus.subscribe(Event.GAME_OVER,    self._on_game_over)
        bus.subscribe(Event.NEED_GUESS,   self._enable_clicks)
        bus.subscribe(Event.GUESS_DONE,   self._disable_clicks)

        self.bind("<Button-1>", self._on_left)
        self.bind("<Button-3>", self._on_right)      # Windows/Linux flag
        self.bind("<Button-2>", self._on_right)      # macOS flag
        self.pack()

        # if controller started first, draw immediately
        first_view = getattr(bus, "last_view", None)
        if first_view:
            self._init_grid(first_view)

    # ── click-gate helpers ────────────────────────────────────────────
    def _enable_clicks(self, *_):
        self._awaiting_guess = True
        self.config(cursor="hand2")        # visual cue

    def _disable_clicks(self, *_):
        self._awaiting_guess = False
        self.config(cursor="")             # default arrow

    def _on_left(self, ev: tk.Event) -> None:
        """Queue a coordinate only while a guess is required."""
        if not self._awaiting_guess:
            return
        r, c = ev.y // self.cpx, ev.x // self.cpx
        if 0 <= r < self.rows and 0 <= c < self.cols:   # ← fixed test
            self._click_q.put((MoveType.REVEAL, r, c))
            self.bus.publish(Event.GUESS_DONE)          # lock out more
    
    def _on_right(self, ev: tk.Event) -> None:
        """Queue a coordinate only while a guess is required."""
        if not self._awaiting_guess:
            return
        r, c = ev.y // self.cpx, ev.x // self.cpx
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self._click_q.put((MoveType.FLAG, r, c))
            self.bus.publish(Event.GUESS_DONE)          # lock out more

    # ── drawing helpers ───────────────────────────────────────────────
    def _xy(self, r: int, c: int) -> tuple[int, int, int, int]:
        x0, y0 = c * self.cpx, r * self.cpx
        return x0, y0, x0 + self.cpx, y0 + self.cpx

    def _init_grid(self, view: BoardView, *_):
        """Draw hidden grid once. Safe to call many times."""
        if self._rect:                         # already drawn
            return
        self._view = view
        for r in range(self.rows):
            for c in range(self.cols):
                rid = self.create_rectangle(
                    *self._xy(r, c),
                    fill=HIDDEN_FILL,
                    outline=GRID_OUTLINE,
                )
                self._rect[(r, c)] = rid

    def _update_tiles(
        self,
        view: BoardView,
        changed: List[Tuple[int, int]],
        *_,
    ):
        if not self._rect:
            self._init_grid(view)

        self._view = view
        for r, c in changed:
            if (r, c) not in self._rect:
                continue
            rect_id = self._rect[(r, c)]

            # wipe previous text
            tid = self._text.pop((r, c), None)
            if tid:
                self.delete(tid)

            state, num = view[r, c]
            if state is CellState.REVEALED:
                self.itemconfig(rect_id, fill=REVEALED_FILL)
                if num:
                    colour = NUMBER_COLOURS.get(num, "black")
                    tid = self.create_text(
                        c * self.cpx + self.cpx // 2,
                        r * self.cpx + self.cpx // 2,
                        text=str(num),
                        font=FONT,
                        fill=colour,
                    )
                    self._text[(r, c)] = tid
                # flash outline
                self.itemconfig(rect_id, width=3, outline="gold")
                self.after(
                    FLASH_MS,
                    lambda rid=rect_id: self.itemconfig(
                        rid, width=1, outline=GRID_OUTLINE
                    ),
                )

            elif state is CellState.FLAGGED:
                self.itemconfig(rect_id, fill=FLAG_FILL)
                tid = self.create_text(
                    c * self.cpx + self.cpx // 2,
                    r * self.cpx + self.cpx // 2,
                    text="⚑",
                    font=FONT,
                    fill="red",
                )
                self._text[(r, c)] = tid
                self._blink(tid, BLINK_CYCLES)

            else:  # hidden again
                self.itemconfig(rect_id, fill=HIDDEN_FILL, width=1,
                                outline=GRID_OUTLINE)

    def _blink(self, tid: int, cycles: int):
        if cycles == 0:
            self.itemconfig(tid, fill="red")
            return
        self.itemconfig(
            tid,
            fill="yellow" if self.itemcget(tid, "fill") == "red" else "red",
        )
        self.after(
            BLINK_MS,
            lambda t=tid, c=cycles - 1: self._blink(t, c),
        )

    # game-over fireworks
    def _on_game_over(self, outcome: GameState, *_):
        banner_colour = "green" if outcome is GameState.WON else "red"
        self.create_text(
            self.winfo_reqwidth() // 2,
            self.winfo_reqheight() // 2,
            text=f"Game {outcome.name}!",
            font=("Consolas", 20, "bold"),
            fill=banner_colour,
        )