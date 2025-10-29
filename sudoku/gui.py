"""GUI interface for Sudoku game using tkinter."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Set, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageTk
from sudoku.board import SudokuBoard
from sudoku.solver import SudokuSolver
from sudoku.generator import SudokuGenerator, Difficulty


class DraculaDialog:
    """Custom dialog box with Dracula theme."""

    @staticmethod
    def show_info(parent, title, message):
        """Show an info dialog."""
        return DraculaDialog._create_dialog(parent, title, message, "info")

    @staticmethod
    def show_warning(parent, title, message):
        """Show a warning dialog."""
        return DraculaDialog._create_dialog(parent, title, message, "warning")

    @staticmethod
    def ask_yesno(parent, title, message):
        """Show a yes/no dialog."""
        return DraculaDialog._create_dialog(parent, title, message, "yesno")

    @staticmethod
    def _create_dialog(parent, title, message, dialog_type):
        """Create a custom styled dialog."""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.configure(bg="#282a36")  # Dracula background
        dialog.resizable(False, False)

        # Set size first
        dialog.geometry("450x220")

        # Update to get actual sizes
        dialog.update_idletasks()

        # Center on parent
        parent.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        dialog_w = 450
        dialog_h = 220

        x = parent_x + (parent_w // 2) - (dialog_w // 2)
        y = parent_y + (parent_h // 2) - (dialog_h // 2)

        # Ensure it's on screen
        x = max(0, x)
        y = max(0, y)

        dialog.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")

        # Make modal
        dialog.transient(parent)
        dialog.grab_set()
        dialog.focus_set()

        # Main container with border
        main_frame = tk.Frame(dialog, bg="#282a36", relief=tk.RIDGE, bd=4,
                             highlightbackground="#bd93f9", highlightthickness=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title bar
        title_frame = tk.Frame(main_frame, bg="#44475a", relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, padx=5, pady=5)

        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Courier", 14, "bold"),
            bg="#44475a",
            fg="#8be9fd",  # Cyan
            pady=5
        )
        title_label.pack()

        # Message area
        message_frame = tk.Frame(main_frame, bg="#282a36")
        message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        message_label = tk.Label(
            message_frame,
            text=message,
            font=("Courier", 11),
            bg="#282a36",
            fg="#f8f8f2",  # Foreground
            wraplength=350,
            justify=tk.CENTER
        )
        message_label.pack(expand=True)

        # Button frame
        button_frame = tk.Frame(main_frame, bg="#282a36")
        button_frame.pack(pady=10)

        result = [None]  # Use list to store result from nested function

        def on_yes():
            result[0] = True
            dialog.destroy()

        def on_no():
            result[0] = False
            dialog.destroy()

        def on_ok():
            result[0] = True
            dialog.destroy()

        if dialog_type == "yesno":
            # Yes button
            yes_btn = tk.Button(
                button_frame,
                text="▶ YES",
                command=on_yes,
                font=("Courier", 10, "bold"),
                bg="#50fa7b",  # Green
                fg="#282a36",
                activebackground="#69ff94",
                activeforeground="#282a36",
                padx=20,
                pady=8,
                relief=tk.RAISED,
                bd=3,
                cursor="hand2"
            )
            yes_btn.pack(side=tk.LEFT, padx=10)

            # No button
            no_btn = tk.Button(
                button_frame,
                text="✖ NO",
                command=on_no,
                font=("Courier", 10, "bold"),
                bg="#ff5555",  # Red
                fg="#282a36",
                activebackground="#ff6e6e",
                activeforeground="#282a36",
                padx=20,
                pady=8,
                relief=tk.RAISED,
                bd=3,
                cursor="hand2"
            )
            no_btn.pack(side=tk.LEFT, padx=10)

        else:
            # OK button
            ok_btn = tk.Button(
                button_frame,
                text="✓ OK",
                command=on_ok,
                font=("Courier", 10, "bold"),
                bg="#bd93f9",  # Purple
                fg="#282a36",
                activebackground="#d4aeff",
                activeforeground="#282a36",
                padx=30,
                pady=8,
                relief=tk.RAISED,
                bd=3,
                cursor="hand2"
            )
            ok_btn.pack()

        # Bind Escape key to close
        dialog.bind('<Escape>', lambda e: dialog.destroy())

        # Bind Enter key for OK/YES
        if dialog_type == "yesno":
            dialog.bind('<Return>', lambda e: on_yes())
        else:
            dialog.bind('<Return>', lambda e: on_ok())

        # Wait for dialog to close
        dialog.wait_window()
        return result[0] if result[0] is not None else False


class SudokuGUI:
    """Graphical interface for Sudoku game."""

    CELL_SIZE = 56  # Reduced from 64
    GRID_SIZE = 9
    SUBGRID_SIZE = 3

    # Dracula Color Scheme
    BG_COLOR = "#282a36"           # Dracula background
    GRID_COLOR = "#6272a4"         # Dracula comment (subtle grid)
    SUBGRID_COLOR = "#bd93f9"      # Dracula purple (bold subgrid)
    INITIAL_CELL_COLOR = "#44475a" # Dracula current line
    SELECTED_CELL_COLOR = "#6272a4" # Dracula comment
    ERROR_CELL_COLOR = "#ff5555"   # Dracula red
    INITIAL_TEXT_COLOR = "#f8f8f2" # Dracula foreground
    USER_TEXT_COLOR = "#50fa7b"    # Dracula green
    ERROR_TEXT_COLOR = "#ff79c6"   # Dracula pink
    HINT_COLOR = "#ffb86c"         # Dracula orange
    BUTTON_BG = "#bd93f9"          # Dracula purple
    BUTTON_HOVER = "#ff79c6"       # Dracula pink
    TITLE_COLOR = "#8be9fd"        # Dracula cyan

    def __init__(self, root: tk.Tk):
        """Initialize the GUI.

        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Sudoku Game")
        self.root.resizable(False, False)

        # Game state
        self.puzzle: Optional[SudokuBoard] = None
        self.current: Optional[SudokuBoard] = None
        self.solution: Optional[SudokuBoard] = None
        self.initial_cells: Set[Tuple[int, int]] = set()
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.show_errors = False

        # UI elements
        self.cells = {}  # Dictionary to store cell widgets
        self.setup_ui()

        # Bind keyboard events
        self.root.bind('<Key>', self.on_key_press)

    def setup_ui(self):
        """Set up the user interface."""
        # Set window background
        self.root.configure(bg=self.BG_COLOR)

        # Main container with reduced padding
        main_frame = tk.Frame(self.root, bg=self.BG_COLOR, padx=15, pady=15)
        main_frame.pack()

        # Contra-style title with big S and small udoku
        title_frame = tk.Frame(main_frame, bg=self.BG_COLOR, width=600, height=180)
        title_frame.pack(pady=(0, 5))
        title_frame.pack_propagate(False)

        # Top decorative bar
        top_bar = tk.Label(
            title_frame,
            text="▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg="#FF4500"
        )
        top_bar.place(relx=0.5, rely=0.0, anchor="n")

        # Create the logo using PIL for proper gradients and textures
        self._create_logo(title_frame)

        # Contra-style subtitle
        subtitle = tk.Label(
            title_frame,
            text="- PUZZLE WARRIOR -",
            font=("Courier", 12, "bold"),
            bg=self.BG_COLOR,
            fg="#FFFF00"
        )
        subtitle.place(relx=0.5, rely=0.92, anchor="center")

        # Bottom decorative bar
        bottom_bar = tk.Label(
            main_frame,
            text="▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg="#FF0000"  # Contra red
        )
        bottom_bar.pack(pady=(0, 10))

        # Game board
        self.board_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        self.board_frame.pack(pady=10)
        self.create_board()

        # Control panel
        control_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        control_frame.pack(pady=8)

        # Difficulty selection with 8-bit style
        difficulty_frame = tk.Frame(control_frame, bg=self.BG_COLOR, relief=tk.RIDGE, bd=3,
                                    highlightbackground=self.SUBGRID_COLOR, highlightthickness=2)
        difficulty_frame.pack(side=tk.LEFT, padx=8)

        tk.Label(
            difficulty_frame,
            text="▶ LEVEL:",
            font=("Courier", 10, "bold"),
            bg=self.BG_COLOR,
            fg=self.HINT_COLOR
        ).pack(side=tk.LEFT, padx=5, pady=3)

        self.difficulty_var = tk.StringVar(value="Medium")

        # Style the combobox
        style = ttk.Style()
        style.theme_use('clam')

        # Slightly lighter than BG_COLOR (#282a36)
        combo_bg = "#3a3c4e"  # Lighter shade

        style.configure('Dracula.TCombobox',
                       fieldbackground=combo_bg,
                       background=self.BUTTON_BG,
                       foreground=self.HINT_COLOR,  # Same yellow/orange as "LEVEL:"
                       arrowcolor=self.HINT_COLOR,
                       borderwidth=2,
                       relief=tk.RIDGE)

        # Style for dropdown list
        style.map('Dracula.TCombobox',
                 fieldbackground=[('readonly', combo_bg)],
                 selectbackground=[('readonly', self.SELECTED_CELL_COLOR)],
                 selectforeground=[('readonly', self.HINT_COLOR)])

        difficulty_combo = ttk.Combobox(
            difficulty_frame,
            textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Hard", "Expert"],
            state="readonly",
            width=10,
            style='Dracula.TCombobox',
            font=("Courier", 10, "bold")
        )
        difficulty_combo.pack(side=tk.LEFT, padx=5, pady=3)

        # Configure the dropdown listbox colors
        self.root.option_add('*TCombobox*Listbox.background', combo_bg)
        self.root.option_add('*TCombobox*Listbox.foreground', self.HINT_COLOR)
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.SELECTED_CELL_COLOR)
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.HINT_COLOR)
        self.root.option_add('*TCombobox*Listbox.font', ('Courier', 10, 'bold'))

        # Buttons with 8-bit pixel style
        button_frame = tk.Frame(control_frame, bg=self.BG_COLOR)
        button_frame.pack(side=tk.LEFT, padx=5)

        buttons = [
            ("▶ NEW", self.new_game),
            ("✖ CLR", self.clear_cell),
            ("? HINT", self.get_hint),
            ("✓ CHK", self.check_solution),
            ("◈ ERR", self.toggle_errors),
            ("★ SOL", self.show_solution)
        ]

        for text, command in buttons:
            # Create a frame for each button to add border effect
            btn_container = tk.Frame(button_frame, bg=self.BG_COLOR)
            btn_container.pack(side=tk.LEFT, padx=2)

            btn = tk.Button(
                btn_container,
                text=text,
                command=command,
                font=("Courier", 9, "bold"),
                bg=self.BUTTON_BG,
                fg=self.BG_COLOR,
                activebackground=self.BUTTON_HOVER,
                activeforeground=self.BG_COLOR,
                padx=8,
                pady=6,
                relief=tk.RAISED,
                bd=3,
                cursor="hand2",
                highlightbackground=self.SUBGRID_COLOR,
                highlightthickness=1
            )
            btn.pack()

            # Add hover effect
            def on_enter(e, b=btn):
                b.config(bg=self.BUTTON_HOVER)
            def on_leave(e, b=btn):
                b.config(bg=self.BUTTON_BG)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        # Status bar with 8-bit style
        status_container = tk.Frame(main_frame, bg=self.INITIAL_CELL_COLOR, relief=tk.RIDGE, bd=3)
        status_container.pack(pady=(15, 5), fill=tk.X)

        self.status_var = tk.StringVar(value="▶ Press 'NEW' to start!")
        status_label = tk.Label(
            status_container,
            textvariable=self.status_var,
            font=("Courier", 10, "bold"),
            bg=self.INITIAL_CELL_COLOR,
            fg=self.USER_TEXT_COLOR,
            pady=5
        )
        status_label.pack()

        # Instructions with pixel style
        instructions = "━━━ [CLICK] + [1-9] or [0/DEL] ━━━"
        tk.Label(
            main_frame,
            text=instructions,
            font=("Courier", 9),
            bg=self.BG_COLOR,
            fg=self.GRID_COLOR
        ).pack(pady=(5, 0))

        # Retro footer
        footer = tk.Label(
            main_frame,
            text="░░ INSERT COIN TO CONTINUE ░░",
            font=("Courier", 8),
            bg=self.BG_COLOR,
            fg=self.HINT_COLOR
        )
        footer.pack(pady=(3, 0))

    def _create_logo(self, parent):
        """Create the Sudoku logo with gradient on S and texture on UDOKU using PIL."""
        # Reduced size to fit screen better
        img_width, img_height = 580, 160
        img = Image.new('RGBA', (img_width, img_height), (40, 42, 54, 0))  # Transparent BG
        draw = ImageDraw.Draw(img)

        try:
            # Slightly smaller fonts
            font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 140)
            font_udoku = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 56)
        except:
            font_s = ImageFont.load_default()
            font_udoku = ImageFont.load_default()

        # Calculate positions to center "Sudoku" as one word
        # Position S and udoku right next to each other, then center the whole thing
        s_x = 70  # Start position for S
        s_y = 10
        udoku_x = s_x + 95  # Right next to S (S width adjusted)
        udoku_y = 50  # Vertically aligned to come out of S

        # Create gradient effect for S by drawing it multiple times with different colors
        gradient_colors = [
            (139, 0, 0),      # Dark red (bottom)
            (178, 34, 34),    # Firebrick
            (220, 20, 60),    # Crimson
            (255, 69, 0),     # Orange-red
            (255, 140, 0),    # Dark orange
            (255, 165, 0),    # Orange
            (255, 215, 0),    # Gold (top)
        ]

        # Draw S with gradient by slicing it into horizontal bands
        s_height = 140
        band_height = s_height // len(gradient_colors)

        for i, color in enumerate(gradient_colors):
            # Create a copy to draw each band
            temp_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text((s_x, s_y), "S", font=font_s, fill=color + (255,))

            # Mask to only show this band
            mask = Image.new('L', (img_width, img_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            y_start = s_y + (i * band_height)
            y_end = s_y + ((i + 1) * band_height)
            mask_draw.rectangle([(0, y_start), (img_width, y_end)], fill=255)

            # Composite this band onto main image
            img = Image.alpha_composite(img, Image.composite(temp_img, Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0)), mask))

        # Draw "UDOKU" with metallic texture effect - right next to S

        # Shadow layer
        draw.text((udoku_x+4, udoku_y+4), "UDOKU", font=font_udoku, fill=(30, 30, 30, 255))

        # Base metal layer
        draw.text((udoku_x+2, udoku_y+2), "UDOKU", font=font_udoku, fill=(80, 80, 80, 255))

        # Create stippled texture effect by drawing small dots
        temp_texture = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        texture_draw = ImageDraw.Draw(temp_texture)
        texture_draw.text((udoku_x, udoku_y), "UDOKU", font=font_udoku, fill=(120, 120, 120, 255))

        # Add noise/texture - now more visible at 2x size
        pixels = temp_texture.load()
        import random
        for y in range(udoku_y, min(udoku_y + 80, img_height)):
            for x in range(udoku_x, min(udoku_x + 350, img_width)):
                if pixels[x, y][3] > 0:  # If pixel is not transparent
                    noise = random.randint(-40, 40)  # More noise for visibility
                    r, g, b, a = pixels[x, y]
                    pixels[x, y] = (max(0, min(255, r + noise)),
                                   max(0, min(255, g + noise)),
                                   max(0, min(255, b + noise)), a)

        img = Image.alpha_composite(img, temp_texture)

        # Top highlight for metallic shine
        draw = ImageDraw.Draw(img)
        draw.text((udoku_x-2, udoku_y-2), "UDOKU", font=font_udoku, fill=(200, 200, 200, 255))

        # Very bright highlight on top edge
        draw.text((udoku_x-4, udoku_y-4), "UDOKU", font=font_udoku, fill=(240, 240, 240, 200))

        # Convert to PhotoImage and display - centered
        self.logo_photo = ImageTk.PhotoImage(img)
        logo_label = tk.Label(parent, image=self.logo_photo, bg=self.BG_COLOR)
        logo_label.place(relx=0.5, rely=0.40, anchor="center")

    def create_board(self):
        """Create the Sudoku board grid with rounded corners."""
        canvas_size = self.CELL_SIZE * self.GRID_SIZE + 8  # +8 for borders and padding

        # Create container with border
        border_frame = tk.Frame(self.board_frame, bg=self.SUBGRID_COLOR, relief=tk.RIDGE, bd=4)
        border_frame.pack()

        self.canvas = tk.Canvas(
            border_frame,
            width=canvas_size,
            height=canvas_size,
            bg=self.BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(padx=2, pady=2)

        # Create cells with rounded corners
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                x1 = col * self.CELL_SIZE + 4
                y1 = row * self.CELL_SIZE + 4
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                # Create rounded rectangle for cell
                rect = self._create_rounded_rectangle(
                    x1, y1, x2, y2,
                    radius=8,
                    fill=self.BG_COLOR,
                    outline=self.GRID_COLOR,
                    width=2
                )

                # Create text with pixel font
                text = self.canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text="",
                    font=("Courier", 24, "bold"),
                    fill=self.INITIAL_TEXT_COLOR
                )

                self.cells[(row, col)] = {'rect': rect, 'text': text}

                # Bind click events to all parts of the rounded rect
                for item in rect:
                    self.canvas.tag_bind(item, '<Button-1>', lambda e, r=row, c=col: self.on_cell_click(r, c))
                self.canvas.tag_bind(text, '<Button-1>', lambda e, r=row, c=col: self.on_cell_click(r, c))

        # Draw thick lines for 3x3 subgrids with pixel style
        for i in range(0, self.GRID_SIZE + 1, self.SUBGRID_SIZE):
            # Vertical lines
            x = i * self.CELL_SIZE + 4
            self.canvas.create_line(
                x, 4,
                x, canvas_size - 4,
                fill=self.SUBGRID_COLOR,
                width=4
            )

            # Horizontal lines
            y = i * self.CELL_SIZE + 4
            self.canvas.create_line(
                4, y,
                canvas_size - 4, y,
                fill=self.SUBGRID_COLOR,
                width=4
            )

    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Create a rounded rectangle on canvas.

        Returns:
            List of canvas items that make up the rounded rectangle
        """
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]

        # Create the rounded rectangle as a polygon
        rect_id = self.canvas.create_polygon(points, smooth=True, **kwargs)
        return [rect_id]

    def update_board_display(self):
        """Update the visual display of the board."""
        if self.current is None:
            return

        # Check if canvas exists and is valid
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            return

        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                value = self.current.get(row, col)
                cell = self.cells[(row, col)]

                # Update text
                text_value = str(value) if value != 0 else ""
                try:
                    self.canvas.itemconfig(cell['text'], text=text_value)
                except:
                    return  # Canvas no longer valid

                # Determine colors
                is_initial = (row, col) in self.initial_cells
                is_selected = (row, col) == self.selected_cell
                has_error = False

                if self.show_errors and value != 0 and not is_initial and self.solution:
                    has_error = value != self.solution.get(row, col)

                # Set background color
                if is_selected:
                    bg_color = self.SELECTED_CELL_COLOR
                    outline_color = self.HINT_COLOR
                    outline_width = 3
                elif has_error:
                    bg_color = self.ERROR_CELL_COLOR
                    outline_color = self.ERROR_TEXT_COLOR
                    outline_width = 2
                elif is_initial:
                    bg_color = self.INITIAL_CELL_COLOR
                    outline_color = self.GRID_COLOR
                    outline_width = 2
                else:
                    bg_color = self.BG_COLOR
                    outline_color = self.GRID_COLOR
                    outline_width = 2

                # Update all rect items (rounded rectangle parts)
                try:
                    for rect_item in cell['rect']:
                        self.canvas.itemconfig(rect_item, fill=bg_color, outline=outline_color, width=outline_width)

                    # Set text color
                    if has_error:
                        text_color = self.ERROR_TEXT_COLOR
                    elif is_initial:
                        text_color = self.INITIAL_TEXT_COLOR
                    else:
                        text_color = self.USER_TEXT_COLOR

                    self.canvas.itemconfig(cell['text'], fill=text_color)
                except:
                    return  # Canvas no longer valid

    def on_cell_click(self, row: int, col: int):
        """Handle cell click event.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)
        """
        if self.current is None:
            return

        if (row, col) in self.initial_cells:
            self.status_var.set("Cannot modify initial puzzle cells!")
            return

        self.selected_cell = (row, col)
        self.update_board_display()
        self.status_var.set(f"▶ Cell [{row + 1},{col + 1}] selected!")

    def on_key_press(self, event):
        """Handle keyboard input.

        Args:
            event: Keyboard event
        """
        if self.current is None or self.selected_cell is None:
            return

        row, col = self.selected_cell

        if (row, col) in self.initial_cells:
            return

        # Handle number keys
        if event.char in '123456789':
            value = int(event.char)
            self.current.set(row, col, value)
            self.update_board_display()
            self.status_var.set(f"▶ Placed [{value}] at [{row + 1},{col + 1}]")
            self.check_completion()

        # Handle clear (0, Delete, Backspace)
        elif event.char == '0' or event.keysym in ('Delete', 'BackSpace'):
            self.current.set(row, col, 0)
            self.update_board_display()
            self.status_var.set(f"✖ Cleared [{row + 1},{col + 1}]")

    def new_game(self):
        """Start a new game."""
        difficulty_map = {
            "Easy": Difficulty.EASY,
            "Medium": Difficulty.MEDIUM,
            "Hard": Difficulty.HARD,
            "Expert": Difficulty.EXPERT
        }

        difficulty = difficulty_map[self.difficulty_var.get()]
        self.status_var.set(f"▶ Generating {difficulty.name.upper()} puzzle...")
        self.root.update()

        self.puzzle, self.solution = SudokuGenerator.generate(difficulty)
        self.current = self.puzzle.copy()
        self.show_errors = False

        # Track initial cells
        self.initial_cells = set()
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if not self.puzzle.is_empty(row, col):
                    self.initial_cells.add((row, col))

        self.selected_cell = None
        self.update_board_display()
        self.status_var.set(f"★ {difficulty.name.upper()} puzzle loaded! Good luck!")

    def clear_cell(self):
        """Clear the selected cell."""
        if self.selected_cell is None:
            self.status_var.set("✖ No cell selected!")
            return

        row, col = self.selected_cell

        if (row, col) in self.initial_cells:
            self.status_var.set("✖ Cannot modify puzzle clues!")
            return

        self.current.set(row, col, 0)
        self.update_board_display()
        self.status_var.set(f"✖ Cleared [{row + 1},{col + 1}]")

    def get_hint(self):
        """Get a hint for an empty cell."""
        if self.current is None or self.solution is None:
            self.status_var.set("✖ No active game!")
            return

        # Find first empty cell
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.current.is_empty(row, col):
                    value = self.solution.get(row, col)
                    self.status_var.set(f"? HINT: Place [{value}] at [{row + 1},{col + 1}]")
                    self.selected_cell = (row, col)
                    self.update_board_display()
                    return

        self.status_var.set("✓ No hints needed - board complete!")

    def check_solution(self):
        """Check if the current solution is correct."""
        if self.current is None or self.solution is None:
            self.status_var.set("✖ No active game!")
            return

        is_correct = True
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.current.get(row, col) != self.solution.get(row, col):
                    is_correct = False
                    break
            if not is_correct:
                break

        if is_correct:
            DraculaDialog.show_info(self.root, "★ VICTORY! ★",
                                   "Perfect! All cells are correct!\n\n▄▄▄▄▄▄▄▄▄▄▄▄▄\n█ YOU WIN! █\n▀▀▀▀▀▀▀▀▀▀▀▀▀")
            self.status_var.set("★ PUZZLE SOLVED! ★")
        else:
            DraculaDialog.show_warning(self.root, "✖ Not Yet!",
                                      "Some cells are incorrect.\nTry '◈ ERR' button to highlight mistakes!")
            self.status_var.set("✖ Keep trying...")

    def check_completion(self):
        """Check if puzzle is complete and correct."""
        if self.current.is_complete():
            is_correct = True
            for row in range(self.GRID_SIZE):
                for col in range(self.GRID_SIZE):
                    if self.current.get(row, col) != self.solution.get(row, col):
                        is_correct = False
                        break
                if not is_correct:
                    break

            if is_correct:
                DraculaDialog.show_info(self.root, "★ CONGRATULATIONS! ★",
                                       "YOU SOLVED THE PUZZLE!\n\n████████████\n█ WINNER! █\n████████████\n\nPress ▶ NEW for another!")
                self.status_var.set("★★★ VICTORY! ★★★")

    def toggle_errors(self):
        """Toggle error highlighting."""
        self.show_errors = not self.show_errors
        self.update_board_display()

        if self.show_errors:
            self.status_var.set("◈ Error highlighting: ON")
        else:
            self.status_var.set("◈ Error highlighting: OFF")

    def show_solution(self):
        """Show the solution."""
        if self.solution is None:
            self.status_var.set("✖ No active game!")
            return

        result = DraculaDialog.ask_yesno(
            self.root,
            "★ Show Solution?",
            "Are you sure?\n\nThis will reveal the complete solution\nand end the current game."
        )

        if result:
            self.current = self.solution.copy()
            self.update_board_display()
            self.status_var.set("★ Solution revealed!")

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Entry point for GUI version."""
    root = tk.Tk()
    game = SudokuGUI(root)
    game.run()


if __name__ == "__main__":
    main()
