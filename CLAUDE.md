# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Game
```bash
# GUI mode (default)
python3 main.py

# Or explicitly
python3 main.py --gui
python3 gui_main.py

# CLI mode
python3 main.py --cli
```

### Running Tests
```bash
# Run all tests with pytest
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_board.py -v

# Run with unittest (alternative)
python3 -m unittest discover tests/
```

### Running Individual Tests
```bash
# Run single test class
python3 -m pytest tests/test_solver.py::TestSudokuSolver -v

# Run single test method
python3 -m pytest tests/test_solver.py::TestSudokuSolver::test_solve_puzzle -v
```

## Architecture Overview

This is a Sudoku game with clean separation between game logic, solving algorithms, and user interface.

### Core Components

**sudoku/board.py** - `SudokuBoard` class
- Represents the 9x9 game board as a 2D list (0 for empty cells)
- Validates moves according to Sudoku rules (row, column, 3x3 subgrid)
- Methods: `is_valid_move()`, `find_empty()`, `is_valid()`, `is_complete()`
- Board uses 0-indexed internally but CLI uses 1-indexed for user input

**sudoku/solver.py** - `SudokuSolver` class
- Implements backtracking algorithm to solve puzzles
- Key method: `solve(board)` - solves in-place, returns bool
- `has_unique_solution()` - checks if puzzle has exactly one solution (important for generation)
- `get_solution()` - returns solved copy without modifying original

**sudoku/generator.py** - `SudokuGenerator` class
- Generates valid puzzles with difficulty levels (Easy: 35, Medium: 45, Hard: 52, Expert: 58 cells removed)
- Algorithm: Fill diagonal boxes → solve complete board → remove cells while maintaining uniqueness
- `from_string()` - loads puzzles from 81-character strings (0/. for empty)

**sudoku/game.py** - `SudokuGame` class
- CLI interface with command loop
- Tracks initial cells (cannot be modified during play)
- Commands: new, show, move, clear, hint, check, solve, quit
- Uses ANSI codes for formatting (bold for initial cells, red for errors)

**sudoku/gui.py** - `SudokuGUI` class
- Tkinter-based graphical interface
- Grid rendered on Canvas with cell rectangles and text
- Click cells to select, keyboard (1-9, 0/Delete) to enter values
- Color coding: gray for initial cells, blue for user entries, red for errors
- Buttons for game controls (New Game, Hint, Check, etc.)
- Visual feedback for selected cells and errors

### Key Design Decisions

1. **Separation of Concerns**: Board representation, solving, generation, and UI are in separate modules for testability and maintainability.

2. **Immutability**: Solver methods that shouldn't modify input create copies (e.g., `get_solution()`).

3. **Validation Layers**:
   - Board-level validation (`is_valid()` - checks entire board state)
   - Move-level validation (`is_valid_move()` - checks if specific move is legal)

4. **Puzzle Generation**: For performance, uniqueness checking is only enforced on harder puzzles (≥50 empty cells) as easier puzzles are more likely to have unique solutions naturally.

5. **Index Convention**: Internal representation uses 0-indexed arrays, but CLI accepts 1-indexed input for user friendliness.

6. **Dual Interface**: Main entry point (main.py) supports both GUI (default) and CLI modes. GUI falls back to CLI if tkinter is unavailable.

## Testing Strategy

- **test_board.py**: Board representation, validation, and utility methods
- **test_solver.py**: Solving algorithm correctness, uniqueness checking
- **test_generator.py**: Puzzle generation and string parsing

When adding new features:
- Add tests for new validation logic in test_board.py
- Test solver changes with known puzzles and solutions in test_solver.py
- Verify puzzle generation produces solvable puzzles in test_generator.py

## Common Modifications

### Adding a New Difficulty Level
1. Add enum value to `Difficulty` in sudoku/generator.py (specify cells to remove)
2. Update CLI command parser in sudoku/game.py `run()` method
3. Update GUI difficulty combobox values in sudoku/gui.py `setup_ui()` and `new_game()` methods
4. Update README.md with new difficulty option

### Changing Board Display
- **CLI**: Modify `SudokuBoard.__str__()` for non-interactive display, or `SudokuGame.display_board()` for interactive display
- **GUI**: Modify `SudokuGUI.update_board_display()` and color constants at top of class

### Adding New Validation Rules
- Implement in `SudokuBoard.is_valid_move()` for pre-placement validation
- Implement in `SudokuBoard.is_valid()` for post-state validation
- Add corresponding tests

## GUI Implementation Details

### Cell Rendering (sudoku/gui.py:139-180)
- Each cell is a canvas rectangle + text element stored in `self.cells` dict
- Cells are bound to click events for selection
- Thick lines (width=3) drawn every 3 cells for 3x3 subgrid borders

### Color System
Constants at top of SudokuGUI class define color scheme:
- `INITIAL_CELL_COLOR` - Gray background for puzzle clues
- `SELECTED_CELL_COLOR` - Light blue for selected cell
- `ERROR_CELL_COLOR` - Red background for incorrect entries (when Show Errors enabled)
- `USER_TEXT_COLOR` - Blue text for user-entered numbers
- `ERROR_TEXT_COLOR` - Red text for incorrect entries

### Event Handling
- **Mouse**: `on_cell_click()` - selects cell, updates `self.selected_cell`
- **Keyboard**: `on_key_press()` - handles 1-9 for input, 0/Delete/Backspace to clear

## Dependencies

None - uses only Python standard library (random, copy, enum, typing, sys, argparse, tkinter, unittest).
