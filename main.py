#!/usr/bin/env python3
"""Main entry point for Sudoku game."""

import sys
import argparse


def main():
    """Main entry point with mode selection."""
    parser = argparse.ArgumentParser(
        description="Sudoku Game - CLI or GUI mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py           # Launch GUI (default)
  python3 main.py --gui     # Launch GUI explicitly
  python3 main.py --cli     # Launch CLI mode
        """
    )

    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run in CLI (command-line) mode'
    )

    parser.add_argument(
        '--gui',
        action='store_true',
        help='Run in GUI mode (default)'
    )

    args = parser.parse_args()

    # Default to GUI if neither specified
    if args.cli:
        from sudoku.game import main as cli_main
        cli_main()
    else:
        try:
            import tkinter as tk
            from sudoku.gui import SudokuGUI

            root = tk.Tk()
            game = SudokuGUI(root)
            game.run()
        except ImportError:
            print("Error: tkinter is not available on this system.")
            print("Falling back to CLI mode...\n")
            from sudoku.game import main as cli_main
            cli_main()
        except Exception as e:
            print(f"Error starting GUI: {e}")
            print("Falling back to CLI mode...\n")
            from sudoku.game import main as cli_main
            cli_main()


if __name__ == "__main__":
    main()
