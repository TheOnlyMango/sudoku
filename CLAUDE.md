# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This repository contains two main projects:
1. **Sudoku Game** - A puzzle game with GUI and CLI interfaces
2. **SHNet Chat System** - A secure chat application with operations/wiki features

```
sudoku/  (root)
├── main.py                      # Sudoku game entry point
├── gui_main.py                  # Sudoku GUI launcher
│
├── sudoku/                      # Sudoku game module
│   ├── board.py                 # Board representation & validation
│   ├── solver.py                # Backtracking solver
│   ├── generator.py             # Puzzle generator
│   ├── game.py                  # CLI interface
│   └── gui.py                   # GUI interface
│
├── chat/                        # Chat system module
│   ├── server/                  # Server components
│   │   ├── chat_server.py       # Main chat server
│   │   ├── server_gui.py        # Server GUI
│   │   └── logging.py           # Server logging
│   ├── client/                  # Client components
│   │   ├── chat_client.py       # Chat client logic
│   │   ├── operations_client.py # Operations/wiki client
│   │   ├── message_router.py    # Message multiplexer
│   │   ├── auth_ui.py           # Authentication UI
│   │   └── inbox_ui.py          # Direct messaging UI
│   ├── database/                # Database layer
│   │   ├── auth_db.py           # User authentication
│   │   ├── operations_db.py     # Operations/wiki data
│   │   └── db_pool.py           # Connection pooling
│   ├── network/                 # Networking
│   │   └── encryption.py        # Socket encryption
│   └── config/                  # Configuration
│       ├── security.py          # Security policies
│       └── reader.py            # Config file reader
│
├── utils/                       # Shared utilities
│   ├── spy_names.py             # Name generator
│   └── diagnostics.py           # Network diagnostics
│
├── scripts/                     # Helper scripts
│   ├── chat_client.py           # Launch chat client
│   ├── chat_server.py           # Launch chat server
│   └── set_server.py            # Update server config
│
├── tests/                       # Test suite
│   ├── test_board.py
│   ├── test_solver.py
│   ├── test_generator.py
│   └── test_security_features.py
│
└── logs/                        # Application logs
```

## Development Commands

### Running the Sudoku Game
```bash
# GUI mode (default)
python3 main.py

# Or explicitly
python3 main.py --gui
python3 gui_main.py

# CLI mode
python3 main.py --cli
```

### Running the Chat System
```bash
# Launch chat server
python3 scripts/chat_server.py

# Launch chat client
python3 scripts/chat_client.py

# Update server address
python3 scripts/set_server.py <server_address>
```

### Running Tests
```bash
# Run all tests with pytest
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_board.py -v

# Run security tests
python3 tests/test_security_features.py

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

## Sudoku Game Architecture

Clean separation between game logic, solving algorithms, and user interface.

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

**Sudoku**: None - uses only Python standard library (random, copy, enum, typing, sys, argparse, tkinter, unittest).

**Chat System**: Python standard library (sqlite3, threading, socket, json, tkinter) + optional cryptography for encryption.

## Chat System Architecture

The chat system is organized into distinct layers for maintainability and security.

### Server Components (chat/server/)

**chat_server.py** - `ImprovedChatServer` class
- Main server handling chat messages, DMs, and operations
- Token-based authentication with rate limiting
- File upload validation (size limits, MIME type checking)
- Database connection pooling for performance
- Optional socket encryption support

**server_gui.py** - `ServerGUI` class
- Tkinter-based server console with terminal styling
- Real-time log display with color-coded messages
- Graceful shutdown handling (background thread to prevent GUI freeze)
- Start/stop controls and log clearing

**logging.py** - Server logging framework
- Separate loggers: chat_logger, ops_logger, security_logger
- File rotation and console output
- Formatted timestamps and log levels

### Client Components (chat/client/)

**chat_client.py** - `ChatClient` class
- Main chat client with 90s hacker aesthetic
- Integrates MessageRouter for clean message handling
- Manages authentication, inbox, and operations UIs
- Real-time message display and user list updates

**message_router.py** - `MessageRouter` class
- **Critical component**: Solves socket race condition
- Single receiver thread reads ALL messages from socket
- Routes messages to appropriate queues based on prefix:
  - `OP_*` → operations_queue
  - `DM_INBOX:`, `DM_CONVERSATION:`, `DM_MARKED_READ:` → chat_queue
  - Everything else → chat_queue
- Eliminates race conditions from multiple recv() calls on same socket

**auth_ui.py** - `AuthUI` class
- Login, registration, and anonymous mode
- Password hashing and validation
- Random spy name generation

**inbox_ui.py** - `InboxUI` class
- Direct messaging interface
- Auto-refresh every 1 second for live updates
- Smart scroll handling (auto-scroll on new messages)
- Unread message indicators (star icons)

**operations_client.py** - `OperationsClient` class
- Operations/wiki system for collaborative content
- File upload/download with progress tracking
- Message threading per operation

### Database Layer (chat/database/)

**auth_db.py** - User authentication database
- User registration with password hashing (SHA-256)
- Token generation and validation
- Message history storage and retrieval

**operations_db.py** - Operations/wiki database
- Operation creation and management
- File storage and retrieval
- Message threading

**db_pool.py** - Database connection pooling
- Thread-safe connection management
- Automatic cleanup and resource management

### Network Layer (chat/network/)

**encryption.py** - Socket encryption
- Optional TLS-like encryption for socket communications
- Requires cryptography library

### Configuration (chat/config/)

**security.py** - Security policies
- TokenManager: Session token generation and validation
- RateLimiter: Per-user rate limiting for messages and uploads
- File validation: Size limits, MIME type checking, filename sanitization
- Constants: MAX_FILE_SIZE, MAX_MESSAGE_LENGTH, MAX_BUFFER_SIZE

**reader.py** - Configuration file reader
- Loads chat_config.json for server/client settings
- Tailscale integration support
- Auto-detection of server addresses

### Key Design Decisions

1. **MessageRouter Pattern**: Prevents socket race conditions by having a single receiver thread that routes messages to appropriate queues. This was critical fix for DM inbox functionality.

2. **Thread Safety**: Background threads for server operations (shutdown, file transfers) to prevent GUI freezing. Thread-safe GUI updates using `root.after()`.

3. **Security Layers**:
   - Token-based authentication (not just username/password)
   - Rate limiting per user
   - File upload validation (size, type, sanitized names)
   - SQL injection protection via parameterized queries

4. **Live Updates**: Auto-refresh mechanisms in inbox (1s intervals) and operations for real-time collaboration without polling overhead.

5. **Graceful Shutdown**: Proper cleanup of connections, threads, and resources with timeout mechanisms.

### Common Chat System Tasks

**Adding a new message type**:
1. Define message prefix in message_router.py routing logic
2. Add handler in chat_server.py
3. Add client-side processing in chat_client.py or operations_client.py
4. Update logging in server/logging.py if needed

**Changing refresh rates**:
- inbox_ui.py: `start_auto_refresh()` - currently 1000ms (1 second)
- operations_client.py: Similar pattern for operations updates

**Modifying security policies**:
- chat/config/security.py: Update constants like MAX_FILE_SIZE, rate limits
- Restart server for changes to take effect
