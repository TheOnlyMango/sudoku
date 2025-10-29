"""Tests for SudokuGenerator class."""

import unittest
from sudoku.generator import SudokuGenerator, Difficulty
from sudoku.solver import SudokuSolver


class TestSudokuGenerator(unittest.TestCase):
    """Test cases for SudokuGenerator."""

    def test_generate_puzzle(self):
        """Test basic puzzle generation."""
        puzzle, solution = SudokuGenerator.generate(Difficulty.EASY)

        # Puzzle should have empty cells
        self.assertFalse(puzzle.is_complete())

        # Solution should be complete
        self.assertTrue(solution.is_complete())
        self.assertTrue(solution.is_valid())

        # Puzzle should be solvable
        solved = SudokuSolver.get_solution(puzzle)
        self.assertIsNotNone(solved)

    def test_generate_different_difficulties(self):
        """Test generating puzzles of different difficulties."""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

        for diff in difficulties:
            puzzle, solution = SudokuGenerator.generate(diff)

            # Count empty cells
            empty_count = sum(
                1 for r in range(9) for c in range(9)
                if puzzle.get(r, c) == 0
            )

            # Check difficulty roughly matches
            # (allowing some variance due to uniqueness constraint)
            self.assertGreater(empty_count, diff.value - 10)
            self.assertLess(empty_count, diff.value + 10)

    def test_from_string(self):
        """Test loading puzzle from string."""
        puzzle_str = """
            003020600
            900305001
            001806400
            008102900
            700000008
            006708200
            002609500
            800203009
            005010300
        """

        board = SudokuGenerator.from_string(puzzle_str)

        # Check some values
        self.assertEqual(board.get(0, 2), 3)
        self.assertEqual(board.get(0, 3), 0)
        self.assertEqual(board.get(1, 0), 9)

    def test_from_string_with_dots(self):
        """Test loading puzzle with dots for empty cells."""
        puzzle_str = "..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3.."

        board = SudokuGenerator.from_string(puzzle_str)
        self.assertEqual(board.get(0, 0), 0)
        self.assertEqual(board.get(0, 2), 3)

    def test_from_string_invalid_length(self):
        """Test error on invalid string length."""
        with self.assertRaises(ValueError):
            SudokuGenerator.from_string("123")

    def test_from_string_invalid_characters(self):
        """Test error on invalid characters."""
        with self.assertRaises(ValueError):
            SudokuGenerator.from_string("a" * 81)


if __name__ == '__main__':
    unittest.main()
