"""Sudoku puzzle generator with difficulty levels."""

import random
from enum import Enum
from typing import List, Tuple
from sudoku.board import SudokuBoard
from sudoku.solver import SudokuSolver


class Difficulty(Enum):
    """Difficulty levels for Sudoku puzzles."""
    EASY = 35      # Number of cells to remove
    MEDIUM = 45
    HARD = 52
    EXPERT = 58


class SudokuGenerator:
    """Generates valid Sudoku puzzles."""

    @staticmethod
    def generate(difficulty: Difficulty = Difficulty.MEDIUM) -> Tuple[SudokuBoard, SudokuBoard]:
        """Generate a new Sudoku puzzle.

        Args:
            difficulty: Difficulty level (affects number of empty cells)

        Returns:
            Tuple of (puzzle, solution) boards
        """
        # Create a complete valid board
        solution = SudokuGenerator._generate_complete_board()

        # Create puzzle by removing numbers
        puzzle = SudokuGenerator._create_puzzle(solution, difficulty.value)

        return puzzle, solution

    @staticmethod
    def _generate_complete_board() -> SudokuBoard:
        """Generate a complete valid Sudoku board.

        Returns:
            A completely filled valid SudokuBoard
        """
        board = SudokuBoard()

        # Fill diagonal 3x3 boxes first (they're independent)
        SudokuGenerator._fill_diagonal_boxes(board)

        # Solve the rest
        SudokuSolver.solve(board)

        return board

    @staticmethod
    def _fill_diagonal_boxes(board: SudokuBoard) -> None:
        """Fill the three diagonal 3x3 boxes with random valid numbers.

        These boxes don't interact with each other, so we can fill them
        independently with random permutations.
        """
        for box in range(0, board.SIZE, board.SUBGRID_SIZE):
            numbers = list(range(1, board.SIZE + 1))
            random.shuffle(numbers)

            idx = 0
            for row in range(box, box + board.SUBGRID_SIZE):
                for col in range(box, box + board.SUBGRID_SIZE):
                    board.set(row, col, numbers[idx])
                    idx += 1

    @staticmethod
    def _create_puzzle(solution: SudokuBoard, cells_to_remove: int) -> SudokuBoard:
        """Create a puzzle by removing numbers from a complete board.

        Args:
            solution: Complete valid board
            cells_to_remove: Number of cells to empty

        Returns:
            Puzzle board with cells removed
        """
        puzzle = solution.copy()

        # Get all positions
        positions = [(r, c) for r in range(puzzle.SIZE) for c in range(puzzle.SIZE)]
        random.shuffle(positions)

        removed = 0
        attempts = 0
        max_attempts = cells_to_remove * 3  # Limit attempts to avoid infinite loops

        while removed < cells_to_remove and attempts < max_attempts:
            if not positions:
                break

            row, col = positions.pop()
            attempts += 1

            # Save the current value
            backup = puzzle.get(row, col)

            # Try removing it
            puzzle.set(row, col, puzzle.EMPTY)

            # Check if puzzle still has unique solution
            # For performance, we only check uniqueness for harder puzzles
            if cells_to_remove < 50 or SudokuSolver.has_unique_solution(puzzle):
                removed += 1
            else:
                # Restore the value if removing it creates multiple solutions
                puzzle.set(row, col, backup)

        return puzzle

    @staticmethod
    def from_string(puzzle_str: str) -> SudokuBoard:
        """Create a board from a string representation.

        Args:
            puzzle_str: String of 81 digits (0 or . for empty)

        Returns:
            SudokuBoard instance

        Example:
            "003020600900305001001806400..."
        """
        # Remove whitespace and newlines
        cleaned = ''.join(puzzle_str.split())

        if len(cleaned) != 81:
            raise ValueError("Puzzle string must contain exactly 81 characters")

        board = SudokuBoard()
        for i, char in enumerate(cleaned):
            row = i // 9
            col = i % 9

            if char == '.' or char == '0':
                board.set(row, col, 0)
            elif char.isdigit() and '1' <= char <= '9':
                board.set(row, col, int(char))
            else:
                raise ValueError(f"Invalid character '{char}' in puzzle string")

        return board
