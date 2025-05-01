import unittest
from core import Board, GameConfig

class TestBoard(unittest.TestCase):
    
    def setUp(self):
        self.cfg = GameConfig(rows=5, cols=5, mines=3, first_click_safe=True)
        self.board = Board(self.cfg)

    def test_initial_state(self):
        self.assertFalse(self.board.lost())
        self.assertEqual(len(self.board.view()._grid), 5)

    def test_flag_toggle(self):
        result = self.board.flag(0, 0)
        self.assertTrue(result)
        result = self.board.flag(0, 0)
        self.assertFalse(result)

    def test_invalid_flag(self):
        result = self.board.flag(-1, 0)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
