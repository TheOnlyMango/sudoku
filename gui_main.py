#!/usr/bin/env python3
"""Direct entry point for GUI version of Sudoku game."""

import tkinter as tk
from sudoku.gui import SudokuGUI


def main():
    """Start the GUI version."""
    root = tk.Tk()
    game = SudokuGUI(root)
    game.run()


if __name__ == "__main__":
    main()
