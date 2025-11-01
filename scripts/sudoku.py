#!/usr/bin/env python3
"""Main entry point for Sudoku game with hidden chat."""

import tkinter as tk
from sudoku.gui import SudokuGUI


def main():
    """Launch Sudoku game with integrated hidden chat system."""
    root = tk.Tk()
    game = SudokuGUI(root)
    game.run()


if __name__ == "__main__":
    main()
