from core      import GameConfig, Board
from engine    import EventBus, GameController
from ui.console import ConsoleUI
from agents     import HumanCLI
from agents.prolog.prolog_agent import PrologAgent
import time

beginer = GameConfig(9, 9, 10)
Normal = GameConfig(16, 16, 40)
Hard = GameConfig(24, 16, 70) 
expert = GameConfig(30, 16, 99)

cfg = expert

board = Board(cfg)
bus   = EventBus()
ui    = ConsoleUI(bus)
agent = PrologAgent(board.view(), bus)

gc = GameController(board, bus, agent)
while gc.step().name == "RUNNING":
    pass