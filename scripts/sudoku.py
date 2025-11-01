#!/usr/bin/env python3
"""Main entry point for Sudoku game with hidden chat."""

import sys
import os

# Add parent directory to path so we can import from sudoku/, chat/, etc.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from sudoku.gui import SudokuGUI


def main():
    """Launch Sudoku game with integrated hidden chat system."""
    root = tk.Tk()
    game = SudokuGUI(root)
    game.run()


if __name__ == "__main__":
    main()
