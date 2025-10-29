"""Sudoku board representation and validation."""

from typing import List, Optional, Tuple
import copy


class SudokuBoard:
    """Represents a Sudoku board with validation capabilities."""

    SIZE = 9
    SUBGRID_SIZE = 3
    EMPTY = 0

    def __init__(self, board: Optional[List[List[int]]] = None):
        """Initialize a Sudoku board.

        Args:
            board: 9x9 list of integers (0 for empty cells, 1-9 for filled)
        """
        if board is None:
            self.board = [[self.EMPTY for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        else:
            if len(board) != self.SIZE or any(len(row) != self.SIZE for row in board):
                raise ValueError(f"Board must be {self.SIZE}x{self.SIZE}")
            self.board = copy.deepcopy(board)

    def get(self, row: int, col: int) -> int:
        """Get value at position."""
        return self.board[row][col]

    def set(self, row: int, col: int, value: int) -> None:
        """Set value at position."""
        if not (0 <= value <= self.SIZE):
            raise ValueError(f"Value must be between 0 and {self.SIZE}")
        self.board[row][col] = value

    def is_empty(self, row: int, col: int) -> bool:
        """Check if cell is empty."""
        return self.board[row][col] == self.EMPTY

    def is_valid_move(self, row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)

        Returns:
            True if the move is valid according to Sudoku rules
        """
        # Check row
        if num in self.board[row]:
            return False

        # Check column
        if num in [self.board[r][col] for r in range(self.SIZE)]:
            return False

        # Check 3x3 subgrid
        subgrid_row = (row // self.SUBGRID_SIZE) * self.SUBGRID_SIZE
        subgrid_col = (col // self.SUBGRID_SIZE) * self.SUBGRID_SIZE

        for r in range(subgrid_row, subgrid_row + self.SUBGRID_SIZE):
            for c in range(subgrid_col, subgrid_col + self.SUBGRID_SIZE):
                if self.board[r][c] == num:
                    return False

        return True

    def find_empty(self) -> Optional[Tuple[int, int]]:
        """Find an empty cell.

        Returns:
            (row, col) tuple of first empty cell, or None if board is full
        """
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if self.is_empty(row, col):
                    return (row, col)
        return None

    def is_complete(self) -> bool:
        """Check if board is completely filled."""
        return self.find_empty() is None

    def is_valid(self) -> bool:
        """Check if current board state is valid (no conflicts)."""
        # Check all rows
        for row in range(self.SIZE):
            nums = [n for n in self.board[row] if n != self.EMPTY]
            if len(nums) != len(set(nums)):
                return False

        # Check all columns
        for col in range(self.SIZE):
            nums = [self.board[row][col] for row in range(self.SIZE) if self.board[row][col] != self.EMPTY]
            if len(nums) != len(set(nums)):
                return False

        # Check all 3x3 subgrids
        for box_row in range(0, self.SIZE, self.SUBGRID_SIZE):
            for box_col in range(0, self.SIZE, self.SUBGRID_SIZE):
                nums = []
                for r in range(box_row, box_row + self.SUBGRID_SIZE):
                    for c in range(box_col, box_col + self.SUBGRID_SIZE):
                        if self.board[r][c] != self.EMPTY:
                            nums.append(self.board[r][c])
                if len(nums) != len(set(nums)):
                    return False

        return True

    def copy(self) -> 'SudokuBoard':
        """Create a deep copy of the board."""
        return SudokuBoard(self.board)

    def __str__(self) -> str:
        """String representation of the board."""
        lines = []
        for i, row in enumerate(self.board):
            if i % 3 == 0 and i != 0:
                lines.append("------+-------+------")

            row_str = ""
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                row_str += (str(val) if val != self.EMPTY else ".") + " "
            lines.append(row_str.rstrip())

        return "\n".join(lines)
