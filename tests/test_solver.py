"""Tests for SudokuSolver class."""

import unittest
from sudoku.board import SudokuBoard
from sudoku.solver import SudokuSolver


class TestSudokuSolver(unittest.TestCase):
    """Test cases for SudokuSolver."""

    def setUp(self):
        """Set up test fixtures."""
        # A solvable puzzle
        self.solvable_puzzle = SudokuBoard([
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

        # Expected solution
        self.expected_solution = SudokuBoard([
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

    def test_solve_puzzle(self):
        """Test solving a valid puzzle."""
        board = self.solvable_puzzle.copy()
        result = SudokuSolver.solve(board)

        self.assertTrue(result)
        self.assertTrue(board.is_complete())
        self.assertTrue(board.is_valid())

        # Check against expected solution
        for row in range(9):
            for col in range(9):
                self.assertEqual(
                    board.get(row, col),
                    self.expected_solution.get(row, col)
                )

    def test_solve_already_solved(self):
        """Test solving an already solved puzzle."""
        board = self.expected_solution.copy()
        result = SudokuSolver.solve(board)

        self.assertTrue(result)
        self.assertTrue(board.is_complete())

    def test_get_solution(self):
        """Test getting solution without modifying original."""
        original = self.solvable_puzzle.copy()
        solution = SudokuSolver.get_solution(self.solvable_puzzle)

        self.assertIsNotNone(solution)
        self.assertTrue(solution.is_complete())

        # Original should not be modified
        self.assertFalse(self.solvable_puzzle.is_complete())

    def test_has_unique_solution(self):
        """Test unique solution checking."""
        # This puzzle should have unique solution
        self.assertTrue(SudokuSolver.has_unique_solution(self.solvable_puzzle.copy()))

        # Empty board has multiple solutions
        empty = SudokuBoard()
        self.assertFalse(SudokuSolver.has_unique_solution(empty))


if __name__ == '__main__':
    unittest.main()
