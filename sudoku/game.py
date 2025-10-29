"""CLI interface for playing Sudoku."""

import sys
from typing import Optional, Set, Tuple
from sudoku.board import SudokuBoard
from sudoku.solver import SudokuSolver
from sudoku.generator import SudokuGenerator, Difficulty


class SudokuGame:
    """Interactive Sudoku game with CLI interface."""

    def __init__(self):
        self.puzzle: Optional[SudokuBoard] = None
        self.current: Optional[SudokuBoard] = None
        self.solution: Optional[SudokuBoard] = None
        self.initial_cells: Set[Tuple[int, int]] = set()

    def start_new_game(self, difficulty: Difficulty = Difficulty.MEDIUM):
        """Start a new game with specified difficulty."""
        print(f"\nGenerating {difficulty.name} puzzle...")
        self.puzzle, self.solution = SudokuGenerator.generate(difficulty)
        self.current = self.puzzle.copy()

        # Track which cells were initially filled
        self.initial_cells = set()
        for row in range(self.puzzle.SIZE):
            for col in range(self.puzzle.SIZE):
                if not self.puzzle.is_empty(row, col):
                    self.initial_cells.add((row, col))

        print("Puzzle generated!\n")

    def load_puzzle(self, puzzle_str: str):
        """Load a puzzle from string."""
        self.puzzle = SudokuGenerator.from_string(puzzle_str)
        self.current = self.puzzle.copy()
        self.solution = SudokuSolver.get_solution(self.puzzle)

        if self.solution is None:
            raise ValueError("Puzzle has no solution!")

        # Track initial cells
        self.initial_cells = set()
        for row in range(self.puzzle.SIZE):
            for col in range(self.puzzle.SIZE):
                if not self.puzzle.is_empty(row, col):
                    self.initial_cells.add((row, col))

    def display_board(self, show_errors: bool = False):
        """Display the current board state."""
        if self.current is None:
            print("No active game. Start a new game first!")
            return

        print("\n    1 2 3   4 5 6   7 8 9")
        print("  " + "─" * 25)

        for i in range(self.current.SIZE):
            if i > 0 and i % 3 == 0:
                print("  " + "─" * 25)

            row_str = f"{i + 1} │ "
            for j in range(self.current.SIZE):
                if j > 0 and j % 3 == 0:
                    row_str += "│ "

                val = self.current.get(i, j)

                # Highlight errors if requested
                if show_errors and val != 0 and (i, j) not in self.initial_cells:
                    if self.solution and val != self.solution.get(i, j):
                        row_str += f"\033[91m{val}\033[0m "  # Red for errors
                    else:
                        row_str += f"{val} "
                elif val == 0:
                    row_str += ". "
                elif (i, j) in self.initial_cells:
                    row_str += f"\033[1m{val}\033[0m "  # Bold for initial cells
                else:
                    row_str += f"{val} "

            print(row_str + "│")

        print("  " + "─" * 25)
        print()

    def make_move(self, row: int, col: int, value: int) -> bool:
        """Make a move on the board.

        Args:
            row: Row (1-9)
            col: Column (1-9)
            value: Value to place (0-9, where 0 clears the cell)

        Returns:
            True if move was successful
        """
        if self.current is None:
            print("No active game!")
            return False

        # Convert to 0-indexed
        row -= 1
        col -= 1

        # Validate indices
        if not (0 <= row < 9 and 0 <= col < 9):
            print("Invalid position! Row and column must be 1-9.")
            return False

        # Check if cell is modifiable
        if (row, col) in self.initial_cells:
            print("Cannot modify initial puzzle cells!")
            return False

        # Validate value
        if not (0 <= value <= 9):
            print("Invalid value! Must be 0-9 (0 to clear).")
            return False

        self.current.set(row, col, value)
        return True

    def get_hint(self) -> Optional[Tuple[int, int, int]]:
        """Get a hint for an empty cell.

        Returns:
            Tuple of (row, col, value) or None if board is complete
        """
        if self.current is None or self.solution is None:
            return None

        # Find an empty cell
        for row in range(self.current.SIZE):
            for col in range(self.current.SIZE):
                if self.current.is_empty(row, col):
                    value = self.solution.get(row, col)
                    return (row + 1, col + 1, value)  # Convert to 1-indexed

        return None

    def check_solution(self) -> bool:
        """Check if current board matches solution."""
        if self.current is None or self.solution is None:
            return False

        for row in range(self.current.SIZE):
            for col in range(self.current.SIZE):
                if self.current.get(row, col) != self.solution.get(row, col):
                    return False

        return True

    def is_complete(self) -> bool:
        """Check if board is completely filled."""
        return self.current is not None and self.current.is_complete()

    def run(self):
        """Run the main game loop."""
        print("=" * 50)
        print("         SUDOKU GAME")
        print("=" * 50)

        while True:
            print("\nCommands:")
            print("  new [easy|medium|hard|expert] - Start new game")
            print("  show [errors]                  - Display board")
            print("  move <row> <col> <value>       - Make a move (1-9)")
            print("  clear <row> <col>              - Clear a cell")
            print("  hint                           - Get a hint")
            print("  check                          - Check solution")
            print("  solve                          - Show solution")
            print("  quit                           - Exit game")

            try:
                command = input("\n> ").strip().lower().split()

                if not command:
                    continue

                cmd = command[0]

                if cmd == "quit" or cmd == "exit":
                    print("Thanks for playing!")
                    break

                elif cmd == "new":
                    difficulty = Difficulty.MEDIUM
                    if len(command) > 1:
                        diff_map = {
                            "easy": Difficulty.EASY,
                            "medium": Difficulty.MEDIUM,
                            "hard": Difficulty.HARD,
                            "expert": Difficulty.EXPERT
                        }
                        difficulty = diff_map.get(command[1], Difficulty.MEDIUM)

                    self.start_new_game(difficulty)
                    self.display_board()

                elif cmd == "show":
                    show_errors = len(command) > 1 and command[1] == "errors"
                    self.display_board(show_errors)

                elif cmd == "move":
                    if len(command) != 4:
                        print("Usage: move <row> <col> <value>")
                        continue

                    try:
                        row, col, value = map(int, command[1:4])
                        if self.make_move(row, col, value):
                            self.display_board()

                            if self.is_complete():
                                if self.check_solution():
                                    print("🎉 Congratulations! You solved the puzzle!")
                                else:
                                    print("Board is complete but incorrect. Use 'show errors' to see mistakes.")
                    except ValueError:
                        print("Invalid input! Use numbers only.")

                elif cmd == "clear":
                    if len(command) != 3:
                        print("Usage: clear <row> <col>")
                        continue

                    try:
                        row, col = map(int, command[1:3])
                        if self.make_move(row, col, 0):
                            self.display_board()
                    except ValueError:
                        print("Invalid input! Use numbers only.")

                elif cmd == "hint":
                    hint = self.get_hint()
                    if hint:
                        row, col, value = hint
                        print(f"Hint: Try placing {value} at row {row}, column {col}")
                    else:
                        print("No hints available - board is complete!")

                elif cmd == "check":
                    if self.current is None:
                        print("No active game!")
                    elif self.check_solution():
                        print("✓ Perfect! All cells are correct!")
                    else:
                        print("✗ Some cells are incorrect. Use 'show errors' to highlight them.")

                elif cmd == "solve":
                    if self.solution:
                        print("\nSolution:")
                        print(self.solution)
                    else:
                        print("No active game!")

                else:
                    print(f"Unknown command: {cmd}")

            except KeyboardInterrupt:
                print("\n\nThanks for playing!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Entry point for the game."""
    game = SudokuGame()
    game.run()


if __name__ == "__main__":
    main()
