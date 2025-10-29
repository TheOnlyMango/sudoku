"""Sudoku game implementation."""

from sudoku.board import SudokuBoard
from sudoku.solver import SudokuSolver
from sudoku.generator import SudokuGenerator

try:
    from sudoku.gui import SudokuGUI
    __all__ = ['SudokuBoard', 'SudokuSolver', 'SudokuGenerator', 'SudokuGUI']
except ImportError:
    # tkinter not available
    __all__ = ['SudokuBoard', 'SudokuSolver', 'SudokuGenerator']
