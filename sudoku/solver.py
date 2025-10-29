"""Sudoku solver using backtracking algorithm."""

from typing import Optional
from sudoku.board import SudokuBoard


class SudokuSolver:
    """Solves Sudoku puzzles using backtracking."""

    @staticmethod
    def solve(board: SudokuBoard) -> bool:
        """Solve the Sudoku puzzle in place using backtracking.

        Args:
            board: SudokuBoard instance to solve

        Returns:
            True if puzzle was solved, False if no solution exists
        """
        empty = board.find_empty()

        # Base case: no empty cells means puzzle is solved
        if empty is None:
            return True

        row, col = empty

        # Try numbers 1-9
        for num in range(1, board.SIZE + 1):
            if board.is_valid_move(row, col, num):
                board.set(row, col, num)

                # Recursively try to solve
                if SudokuSolver.solve(board):
                    return True

                # Backtrack if this doesn't lead to solution
                board.set(row, col, board.EMPTY)

        # No valid number found, trigger backtracking
        return False

    @staticmethod
    def has_unique_solution(board: SudokuBoard) -> bool:
        """Check if puzzle has exactly one solution.

        Args:
            board: SudokuBoard instance to check

        Returns:
            True if puzzle has exactly one unique solution
        """
        solutions = []

        def count_solutions(b: SudokuBoard, limit: int = 2) -> None:
            """Count solutions up to limit."""
            if len(solutions) >= limit:
                return

            empty = b.find_empty()
            if empty is None:
                solutions.append(b.copy())
                return

            row, col = empty

            for num in range(1, b.SIZE + 1):
                if b.is_valid_move(row, col, num):
                    b.set(row, col, num)
                    count_solutions(b, limit)
                    b.set(row, col, b.EMPTY)

        count_solutions(board.copy(), limit=2)
        return len(solutions) == 1

    @staticmethod
    def get_solution(board: SudokuBoard) -> Optional[SudokuBoard]:
        """Get a solved copy of the board.

        Args:
            board: SudokuBoard instance to solve

        Returns:
            Solved SudokuBoard or None if no solution exists
        """
        solved = board.copy()
        if SudokuSolver.solve(solved):
            return solved
        return None
