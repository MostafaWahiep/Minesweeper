import threading, queue
from core import Board, GameConfig
from engine import GameController, EventBus
from agents import PrologAgent
from ui.tkinter import TkUI
import tkinter as tk
import time
from queue import SimpleQueue

# choose which mode or customize
beginer = GameConfig(9, 9, 10)
Normal = GameConfig(16, 16, 40)
Hard = GameConfig(24, 16, 70) 
expert = GameConfig(30, 16, 99)

cfg = expert

counter = 0
while counter < 1:
    counter += 1
    board = Board(cfg)
    bus   = EventBus()
    q     = queue.SimpleQueue()

    click_q = SimpleQueue()

    root = tk.Tk()
    root.title("Minesweeper")
    CELL_PX = 20
    ui   = TkUI(root, cfg.rows, cfg.cols, CELL_PX, bus, click_q)
    agent = PrologAgent(board.view(), bus, click_q)
    gc    = GameController(board, bus, agent)

    def loop():
        while gc.step().name == "RUNNING":
            time.sleep(0.)
    t1= threading.Thread(target=loop, daemon=True)
    t1.start()
    root.mainloop()
    t1.join()