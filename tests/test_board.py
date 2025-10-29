"""Tests for SudokuBoard class."""

import unittest
from sudoku.board import SudokuBoard


class TestSudokuBoard(unittest.TestCase):
    """Test cases for SudokuBoard."""

    def setUp(self):
        """Set up test fixtures."""
        self.empty_board = SudokuBoard()

        # A valid partial board
        self.partial_board = SudokuBoard([
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ])

    def test_initialization_empty(self):
        """Test empty board initialization."""
        board = SudokuBoard()
        for row in range(9):
            for col in range(9):
                self.assertEqual(board.get(row, col), 0)

    def test_initialization_with_data(self):
        """Test board initialization with data."""
        self.assertEqual(self.partial_board.get(0, 0), 5)
        self.assertEqual(self.partial_board.get(0, 2), 0)

    def test_set_and_get(self):
        """Test setting and getting values."""
        board = SudokuBoard()
        board.set(0, 0, 5)
        self.assertEqual(board.get(0, 0), 5)

    def test_is_empty(self):
        """Test empty cell detection."""
        self.assertTrue(self.empty_board.is_empty(0, 0))
        self.assertFalse(self.partial_board.is_empty(0, 0))

    def test_is_valid_move_row(self):
        """Test row validation."""
        # Row 0 has 5, so placing 5 elsewhere should fail
        self.assertFalse(self.partial_board.is_valid_move(0, 2, 5))
        # Placing 1 should be fine (not in row)
        self.assertTrue(self.partial_board.is_valid_move(0, 2, 1))

    def test_is_valid_move_column(self):
        """Test column validation."""
        # Column 0 has 5, 6, 8, 4, 7 - placing any should fail
        self.assertFalse(self.partial_board.is_valid_move(2, 0, 5))

    def test_is_valid_move_subgrid(self):
        """Test 3x3 subgrid validation."""
        # Top-left subgrid has 5, 3, 6, 9, 8
        # Position (0, 2) is in this subgrid
        self.assertFalse(self.partial_board.is_valid_move(0, 2, 5))
        self.assertFalse(self.partial_board.is_valid_move(0, 2, 9))

    def test_find_empty(self):
        """Test finding empty cells."""
        pos = self.partial_board.find_empty()
        self.assertIsNotNone(pos)
        row, col = pos
        self.assertEqual(self.partial_board.get(row, col), 0)

    def test_find_empty_full_board(self):
        """Test find_empty on full board."""
        board = SudokuBoard([
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ])
        self.assertIsNone(board.find_empty())

    def test_is_complete(self):
        """Test board completion check."""
        self.assertFalse(self.partial_board.is_complete())

    def test_is_valid(self):
        """Test board validity check."""
        self.assertTrue(self.partial_board.is_valid())

        # Create invalid board (duplicate in row)
        invalid_board = SudokuBoard([
            [5, 5, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ])
        self.assertFalse(invalid_board.is_valid())

    def test_copy(self):
        """Test board copying."""
        copy = self.partial_board.copy()
        self.assertEqual(copy.get(0, 0), self.partial_board.get(0, 0))

        # Modify copy shouldn't affect original
        copy.set(0, 0, 9)
        self.assertNotEqual(copy.get(0, 0), self.partial_board.get(0, 0))


if __name__ == '__main__':
    unittest.main()
