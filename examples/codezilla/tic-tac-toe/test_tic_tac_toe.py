import unittest
from tic_tac_toe import initialize_board, display_board, is_valid_input, update_board, check_win_draw

class TestTicTacToe(unittest.TestCase):

    def test_initialize_board(self):
        board = initialize_board()
        self.assertEqual(len(board), 3)
        self.assertEqual(len(board[0]), 3)
        for row in board:
            for cell in row:
                self.assertEqual(cell, ' ')

    def test_is_valid_input(self):
        board = initialize_board()
        self.assertTrue(is_valid_input('1', board))
        self.assertFalse(is_valid_input('0', board))
        self.assertFalse(is_valid_input('10', board))
        self.assertFalse(is_valid_input('a', board))
        board[0][0] = 'X'
        self.assertFalse(is_valid_input('1', board))

    def test_update_board(self):
        board = initialize_board()
        update_board(board, '1', 'X')
        self.assertEqual(board[0][0], 'X')

    def test_check_win_draw(self):
        board = [['X', 'X', 'X'],
                 [' ', ' ', ' '],
                 [' ', ' ', ' ']]
        self.assertEqual(check_win_draw(board), 'X')
        board = [['X', ' ', ' '],
                 [' ', 'X', ' '],
                 [' ', ' ', 'X']]
        self.assertEqual(check_win_draw(board), 'X')
        board = [['X', 'O', 'X'],
                 ['O', 'X', 'O'],
                 ['O', 'X', 'O']]
        self.assertEqual(check_win_draw(board), 'Draw')
        board = [['X', 'O', 'X'],
                 ['O', 'X', 'O'],
                 ['O', 'X', ' ']]
        self.assertIsNone(check_win_draw(board))

if __name__ == '__main__':
    unittest.main()