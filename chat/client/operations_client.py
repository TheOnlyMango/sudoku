"""Operations Wiki Client - Retro Cyberpunk Theme"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import socket
import json
import threading
from typing import Optional, Callable


class OperationsClient:
    """Operations wiki/forum client with retro cyberpunk theme."""

    def __init__(self, root, message_router, username, exit_callback=None, chat_callback=None, inbox_callback=None):
        self.root = root
        self.message_router = message_router  # Use MessageRouter instead of raw socket
        self.socket = message_router.socket if message_router else None  # Keep for compatibility checks
        self.username = username
        self.exit_callback = exit_callback
        self.chat_callback = chat_callback  # Callback to return to chat
        self.inbox_callback = inbox_callback  # Callback to return to inbox
        self.current_view = "list"  # list, thread
        self.current_operation = None
        self.operations_data = {}  # Initialize operations data dict

        # Match chat client colors (90s hacker Dracula theme)
        self.BG_COLOR = "#282a36"
        self.PANEL_COLOR = "#0a0e14"  # Darker for terminal feel with CRT glow
        self.TEXT_COLOR = "#f8f8f2"  # White/light gray for message text (terminal style)
        self.USER_COLOR = "#8be9fd"  # Cyan for usernames
        self.SYSTEM_COLOR = "#ffb86c"  # Orange for system messages
        self.INPUT_BG = "#1a1f2e"  # Darker input with subtle glow
        self.BUTTON_COLOR = "#bd93f9"
        self.PROMPT_COLOR = "#6272a4"  # Muted blue for prompt symbols
        self.ACCENT_COLOR = "#50fa7b"  # Green for highlights
        self.SECONDARY_COLOR = "#ff79c6"  # Pink for special items
        self.ERROR_COLOR = "#ff5555"  # Red for errors
        self.SUCCESS_COLOR = "#50fa7b"  # Green for success

        # Status indicator label reference
        self.status_label = None

    def create_ui(self):
        """Create the operations interface."""
        # Configure root
        if isinstance(self.root, tk.Tk):
            self.root.configure(bg=self.BG_COLOR)
            self.root.geometry("700x600")
            self.root.resizable(False, False)
        else:
            self.root.configure(bg=self.BG_COLOR)

        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.BG_COLOR, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Show operations list by default
        self.show_operations_list()

    def show_operations_list(self):
        """Show list of all operations."""
        self.current_view = "list"
        self.clear_main_frame()

        # Retro ASCII art title bar (match chat style)
        title_bar = tk.Label(
            self.main_frame,
            text="╔═══════════════════════════════════════════════════════════╗\n"
                 "║  ░▒▓█ S H N E T  S E C U R E  T E R M I N A L █▓▒░  ║\n"
                 "╚═══════════════════════════════════════════════════════════╝",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg=self.BUTTON_COLOR,
            justify=tk.CENTER
        )
        title_bar.pack(pady=(0, 2))

        # Tunnel status message (match chat style)
        tunnel_label = tk.Label(
            self.main_frame,
            text=">> OPERATIONS DATABASE ACCESSED <<",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg=self.SYSTEM_COLOR
        )
        tunnel_label.pack(pady=(0, 5))

        # Header with buttons (match chat style - left and right aligned)
        header_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        header_frame.pack(pady=(0, 10), fill=tk.X)

        # ABORT button - red circle with 3D effect in top left (match chat)
        abort_btn = tk.Button(
            header_frame,
            text="ABORT",
            command=self._on_abort,
            font=("Courier", 8, "bold"),
            bg="#8b0000",  # Dark red
            fg="#ffffff",
            activebackground="#ff0000",
            activeforeground="#ffffff",
            width=8,
            height=1,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )
        abort_btn.pack(side=tk.LEFT, padx=5)

        # Add 3D shading effect with hover
        def on_abort_enter(e):
            abort_btn.config(bg="#ff0000", relief=tk.RAISED)
        def on_abort_leave(e):
            abort_btn.config(bg="#8b0000", relief=tk.RAISED)
        abort_btn.bind("<Enter>", on_abort_enter)
        abort_btn.bind("<Leave>", on_abort_leave)

        # CHAT button - on RIGHT side to match chat layout
        if self.chat_callback:
            chat_btn = tk.Button(
                header_frame,
                text="CHAT",
                command=self.chat_callback,
                font=("Courier", 8, "bold"),
                bg="#00b4d8",  # Cyan blue
                fg="#00ff41",  # Matrix green
                activebackground="#00ff41",
                activeforeground="#00b4d8",
                width=10,
                height=1,
                relief=tk.RAISED,
                bd=4,
                cursor="hand2"
            )
            chat_btn.pack(side=tk.RIGHT, padx=5)

            # Add hover effect
            def on_chat_enter(e):
                chat_btn.config(bg="#00ff41", fg="#00b4d8", relief=tk.RAISED)
            def on_chat_leave(e):
                chat_btn.config(bg="#00b4d8", fg="#00ff41", relief=tk.RAISED)
            chat_btn.bind("<Enter>", on_chat_enter)
            chat_btn.bind("<Leave>", on_chat_leave)

        # INBOX button - on RIGHT side
        if self.inbox_callback:
            inbox_btn = tk.Button(
                header_frame,
                text="INBOX",
                command=self.inbox_callback,
                font=("Courier", 8, "bold"),
                bg="#00b4d8",  # Cyan blue like chat button
                fg="#00ff41",  # Matrix green
                activebackground="#00ff41",
                activeforeground="#00b4d8",
                width=10,
                height=1,
                relief=tk.RAISED,
                bd=4,
                cursor="hand2"
            )
            inbox_btn.pack(side=tk.RIGHT, padx=5)

            # Add hover effect
            def on_inbox_enter(e):
                inbox_btn.config(bg="#00ff41", fg="#00b4d8", relief=tk.RAISED)
            def on_inbox_leave(e):
                inbox_btn.config(bg="#00b4d8", fg="#00ff41", relief=tk.RAISED)
            inbox_btn.bind("<Enter>", on_inbox_enter)
            inbox_btn.bind("<Leave>", on_inbox_leave)
        else:
            # Show disabled button if no callback
            inbox_btn = tk.Button(
                header_frame,
                text="INBOX",
                command=None,
                font=("Courier", 8, "bold"),
                bg="#6272a4",  # Muted/disabled color
                fg="#44475a",
                width=10,
                height=1,
                relief=tk.RAISED,
                bd=4,
                state=tk.DISABLED
            )
            inbox_btn.pack(side=tk.RIGHT, padx=5)

        # OPERATIONS button (current - highlighted) - on RIGHT side
        ops_btn = tk.Button(
            header_frame,
            text="OPERATIONS",
            command=None,
            font=("Courier", 8, "bold"),
            bg="#7b2cbf",  # Purple - highlighted as current
            fg="#00ff41",  # Matrix green
            width=12,
            height=1,
            relief=tk.SUNKEN,  # Sunken to show it's active
            bd=4,
            cursor="hand2"
        )
        ops_btn.pack(side=tk.RIGHT, padx=5)

        # Create new operation form
        form_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                              highlightbackground=self.ACCENT_COLOR, highlightthickness=2)
        form_frame.pack(pady=10, fill=tk.X)

        tk.Label(
            form_frame,
            text="[ CREATE NEW OPERATION ]",
            font=("Courier", 10, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.SECONDARY_COLOR
        ).pack(pady=5)

        # Operation name
        name_frame = tk.Frame(form_frame, bg=self.PANEL_COLOR)
        name_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(name_frame, text="OP NAME:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.op_name_entry = tk.Entry(name_frame, font=("Courier", 9), bg=self.INPUT_BG,
                                       fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, relief=tk.FLAT)
        self.op_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Password
        pass_frame = tk.Frame(form_frame, bg=self.PANEL_COLOR)
        pass_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(pass_frame, text="PASSWORD:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.op_pass_entry = tk.Entry(pass_frame, font=("Courier", 9), bg=self.INPUT_BG,
                                       fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, show="*", relief=tk.FLAT)
        self.op_pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Description
        desc_frame = tk.Frame(form_frame, bg=self.PANEL_COLOR)
        desc_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(desc_frame, text="DESCRIPTION:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.op_desc_entry = tk.Entry(desc_frame, font=("Courier", 9), bg=self.INPUT_BG,
                                       fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, relief=tk.FLAT)
        self.op_desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Create button
        create_btn = self._create_button(
            form_frame, "[ CREATE ]", self._create_operation,
            bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR
        )
        create_btn.pack(pady=10)

        # Password requirements label
        req_label = tk.Label(
            form_frame,
            text="* Password: 8+ chars, 1 uppercase, 1 special char",
            font=("Courier", 7),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        )
        req_label.pack(pady=(0, 5))

        # Operations list
        list_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                              highlightbackground=self.TEXT_COLOR, highlightthickness=2)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Header with title and status indicator
        list_header_frame = tk.Frame(list_frame, bg=self.PANEL_COLOR)
        list_header_frame.pack(pady=5, fill=tk.X)

        tk.Label(
            list_header_frame,
            text="[ AVAILABLE OPERATIONS ]",
            font=("Courier", 10, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        ).pack(side=tk.LEFT, padx=10)

        # Status indicator in top-right
        self.status_label = tk.Label(
            list_header_frame,
            text="",
            font=("Courier", 8, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Scrollable list (no visible scrollbar - mousewheel/touchpad still works)
        list_container = tk.Frame(list_frame, bg=self.PANEL_COLOR)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.ops_listbox = tk.Listbox(
            list_container,
            font=("Courier", 9),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            selectbackground=self.BUTTON_COLOR,
            selectforeground=self.ACCENT_COLOR,
            relief=tk.FLAT,
            highlightthickness=0,
            bd=0
        )
        self.ops_listbox.pack(fill=tk.BOTH, expand=True)

        # Button frame for Access and Refresh buttons - full width like form
        button_frame = tk.Frame(list_frame, bg=self.PANEL_COLOR)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        # Access button - equal width, expand to fill
        access_btn = self._create_button(
            button_frame, "[ ACCESS OPERATION ]", self._access_operation,
            bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR
        )
        access_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Refresh button - equal width, expand to fill
        refresh_btn = self._create_button(
            button_frame, "[ REFRESH ]", self._load_operations,
            bg=self.SUCCESS_COLOR, fg=self.BG_COLOR
        )
        refresh_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def show_operation_thread(self, op_name, op_info):
        """Show operation thread/forum page."""
        self.current_view = "thread"
        self.current_operation = op_name
        self.clear_main_frame()

        # Retro ASCII art title bar (match chat style)
        title_bar = tk.Label(
            self.main_frame,
            text="╔═══════════════════════════════════════════════════════════╗\n"
                 "║  ░▒▓█ S H N E T  S E C U R E  T E R M I N A L █▓▒░  ║\n"
                 "╚═══════════════════════════════════════════════════════════╝",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg=self.BUTTON_COLOR,
            justify=tk.CENTER
        )
        title_bar.pack(pady=(0, 2))

        # Tunnel status message (match chat style)
        tunnel_label = tk.Label(
            self.main_frame,
            text=f">> OPERATION: {op_name.upper()} <<",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg=self.SYSTEM_COLOR
        )
        tunnel_label.pack(pady=(0, 5))

        # Header with buttons (match chat style)
        header_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        header_frame.pack(pady=(0, 10), fill=tk.X)

        # ABORT button on LEFT
        abort_btn = tk.Button(
            header_frame,
            text="ABORT",
            command=self._on_abort,
            font=("Courier", 8, "bold"),
            bg="#8b0000",
            fg="#ffffff",
            activebackground="#ff0000",
            activeforeground="#ffffff",
            width=8,
            height=1,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )
        abort_btn.pack(side=tk.LEFT, padx=5)

        # Add hover effect
        def on_abort_enter(e):
            abort_btn.config(bg="#ff0000", relief=tk.RAISED)
        def on_abort_leave(e):
            abort_btn.config(bg="#8b0000", relief=tk.RAISED)
        abort_btn.bind("<Enter>", on_abort_enter)
        abort_btn.bind("<Leave>", on_abort_leave)

        # CHAT button on RIGHT
        if self.chat_callback:
            chat_btn = tk.Button(
                header_frame,
                text="CHAT",
                command=self.chat_callback,
                font=("Courier", 8, "bold"),
                bg="#00b4d8",
                fg="#00ff41",
                activebackground="#00ff41",
                activeforeground="#00b4d8",
                width=10,
                height=1,
                relief=tk.RAISED,
                bd=4,
                cursor="hand2"
            )
            chat_btn.pack(side=tk.RIGHT, padx=5)

            def on_chat_enter(e):
                chat_btn.config(bg="#00ff41", fg="#00b4d8", relief=tk.RAISED)
            def on_chat_leave(e):
                chat_btn.config(bg="#00b4d8", fg="#00ff41", relief=tk.RAISED)
            chat_btn.bind("<Enter>", on_chat_enter)
            chat_btn.bind("<Leave>", on_chat_leave)

        # INBOX button on RIGHT
        if self.inbox_callback:
            inbox_btn = tk.Button(
                header_frame,
                text="INBOX",
                command=self.inbox_callback,
                font=("Courier", 8, "bold"),
                bg="#00b4d8",  # Cyan blue like chat button
                fg="#00ff41",  # Matrix green
                activebackground="#00ff41",
                activeforeground="#00b4d8",
                width=10,
                height=1,
                relief=tk.RAISED,
                bd=4,
                cursor="hand2"
            )
            inbox_btn.pack(side=tk.RIGHT, padx=5)

            # Add hover effect
            def on_inbox_enter(e):
                inbox_btn.config(bg="#00ff41", fg="#00b4d8", relief=tk.RAISED)
            def on_inbox_leave(e):
                inbox_btn.config(bg="#00b4d8", fg="#00ff41", relief=tk.RAISED)
            inbox_btn.bind("<Enter>", on_inbox_enter)
            inbox_btn.bind("<Leave>", on_inbox_leave)
        else:
            # Show disabled button if no callback
            inbox_btn = tk.Button(
                header_frame,
                text="INBOX",
                command=None,
                font=("Courier", 8, "bold"),
                bg="#6272a4",
                fg="#44475a",
                width=10,
                height=1,
                relief=tk.RAISED,
                bd=4,
                state=tk.DISABLED
            )
            inbox_btn.pack(side=tk.RIGHT, padx=5)

        # OPERATIONS button on RIGHT (can click to go back to list)
        ops_btn = tk.Button(
            header_frame,
            text="OPERATIONS",
            command=self.show_operations_list,
            font=("Courier", 8, "bold"),
            bg="#7b2cbf",
            fg="#00ff41",
            width=12,
            height=1,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )
        ops_btn.pack(side=tk.RIGHT, padx=5)

        def on_ops_enter(e):
            ops_btn.config(bg="#00ff41", fg="#7b2cbf", relief=tk.RAISED)
        def on_ops_leave(e):
            ops_btn.config(bg="#7b2cbf", fg="#00ff41", relief=tk.RAISED)
        ops_btn.bind("<Enter>", on_ops_enter)
        ops_btn.bind("<Leave>", on_ops_leave)

        # Operation title
        title_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                               highlightbackground=self.SECONDARY_COLOR, highlightthickness=2)
        title_frame.pack(pady=5, fill=tk.X)

        tk.Label(
            title_frame,
            text="operation",
            font=("Courier", 8),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        ).pack(pady=(10, 0))

        tk.Label(
            title_frame,
            text=op_name.upper(),
            font=("Courier", 16, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.ACCENT_COLOR
        ).pack(pady=(0, 5))

        if op_info and op_info.get('description'):
            tk.Label(
                title_frame,
                text=f">> {op_info['description']}",
                font=("Courier", 8),
                bg=self.PANEL_COLOR,
                fg=self.TEXT_COLOR
            ).pack(pady=(0, 10))

        # Form toggle buttons
        toggle_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        toggle_frame.pack(pady=5, fill=tk.X)

        self.form_mode = "post"  # "post" or "iir"

        post_toggle_btn = tk.Button(
            toggle_frame,
            text="[ NEW POST ]",
            command=lambda: self._toggle_form("post"),
            font=("Courier", 9, "bold"),
            bg=self.BUTTON_COLOR,
            fg=self.ACCENT_COLOR,
            activebackground=self.ACCENT_COLOR,
            activeforeground=self.BG_COLOR,
            relief=tk.SUNKEN,
            bd=4,
            cursor="hand2"
        )
        post_toggle_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.post_toggle_btn = post_toggle_btn

        iir_toggle_btn = tk.Button(
            toggle_frame,
            text="[ NEW IIR ]",
            command=lambda: self._toggle_form("iir"),
            font=("Courier", 9, "bold"),
            bg=self.SYSTEM_COLOR,  # Orange - more visible
            fg=self.BG_COLOR,
            activebackground=self.ACCENT_COLOR,
            activeforeground=self.BG_COLOR,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )
        iir_toggle_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.iir_toggle_btn = iir_toggle_btn

        # Post form
        self.post_form_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                                         highlightbackground=self.ACCENT_COLOR, highlightthickness=2)
        self.post_form_frame.pack(pady=5, fill=tk.X)

        tk.Label(
            self.post_form_frame,
            text="[ NEW POST ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.SECONDARY_COLOR
        ).pack(pady=5)

        # Comment
        comment_frame = tk.Frame(self.post_form_frame, bg=self.PANEL_COLOR)
        comment_frame.pack(pady=5, padx=10, fill=tk.BOTH)
        tk.Label(comment_frame, text="COMMENT:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR).pack(anchor=tk.W)
        self.comment_text = tk.Text(comment_frame, font=("Courier", 9), bg=self.INPUT_BG,
                                     fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR,
                                     height=3, wrap=tk.WORD, relief=tk.FLAT)
        self.comment_text.pack(fill=tk.BOTH, expand=True)

        # File upload
        file_frame = tk.Frame(self.post_form_frame, bg=self.PANEL_COLOR)
        file_frame.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(file_frame, text="FILE:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=12, anchor=tk.W).pack(side=tk.LEFT)

        self.selected_file = None
        self.file_label = tk.Label(file_frame, text="No file selected", font=("Courier", 8),
                                    bg=self.PANEL_COLOR, fg=self.TEXT_COLOR)
        self.file_label.pack(side=tk.LEFT, padx=5)

        upload_btn = self._create_button(
            file_frame, "[ BROWSE ]", self._browse_file,
            bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=10
        )
        upload_btn.pack(side=tk.LEFT, padx=5)

        # Post button
        post_btn = self._create_button(
            self.post_form_frame, "[ POST ]", self._add_post,
            bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR
        )
        post_btn.pack(pady=10)

        # IIR form (initially hidden)
        self.iir_form_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                                        highlightbackground=self.ACCENT_COLOR, highlightthickness=2)

        tk.Label(
            self.iir_form_frame,
            text="[ NEW INTELLIGENCE INFORMATION REPORT ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.SECONDARY_COLOR
        ).pack(pady=5)

        # Priority dropdown
        priority_frame = tk.Frame(self.iir_form_frame, bg=self.PANEL_COLOR)
        priority_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(priority_frame, text="PRIORITY:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=15, anchor=tk.W).pack(side=tk.LEFT)

        from tkinter import ttk
        self.iir_priority_var = tk.StringVar(value="routine")
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.iir_priority_var,
                                       values=["routine", "urgent", "priority", "flash"],
                                       state="readonly", font=("Courier", 9), width=15)
        priority_combo.pack(side=tk.LEFT, padx=5)

        # DATE OF INFO (LCD ticker tape style)
        dtg_info_frame = tk.Frame(self.iir_form_frame, bg=self.PANEL_COLOR)
        dtg_info_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(dtg_info_frame, text="DATE OF INFO:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=15, anchor=tk.W).pack(side=tk.LEFT)

        # Container for ticker(s) and [END] button
        self.dtg_info_container = tk.Frame(dtg_info_frame, bg=self.PANEL_COLOR)
        self.dtg_info_container.pack(side=tk.LEFT, padx=5)

        # First ticker (always visible)
        ticker1_container, self.dtg_info_ticker1_labels, dtg1_btn = self._create_dtg_ticker(
            self.dtg_info_container,
            on_dtg_click=lambda: self._show_dtg_calendar_for_ticker(self.dtg_info_ticker1_labels, 1)
        )
        ticker1_container.pack(side=tk.LEFT)

        # Store DTG values
        self.dtg_info_value1 = ""
        self.dtg_info_value2 = ""

        # [END] button (initially hidden) - appears after first date is set
        self.dtg_info_end_btn = tk.Button(
            self.dtg_info_container,
            text="[END]",
            font=("Courier", 8, "bold"),
            bg=self.SYSTEM_COLOR,
            fg=self.PANEL_COLOR,
            command=self._add_second_dtg_info,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        # Don't pack yet - will show after first date is set

        # Second ticker (initially hidden)
        self.dtg_info_ticker2_container = None
        self.dtg_info_ticker2_labels = None

        # CUTOFF (LCD ticker tape style - single date only)
        dtg_cutoff_frame = tk.Frame(self.iir_form_frame, bg=self.PANEL_COLOR)
        dtg_cutoff_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(dtg_cutoff_frame, text="CUTOFF:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=15, anchor=tk.W).pack(side=tk.LEFT)

        cutoff_ticker_container, self.dtg_cutoff_ticker_labels, cutoff_dtg_btn = self._create_dtg_ticker(
            dtg_cutoff_frame,
            on_dtg_click=lambda: self._show_dtg_calendar_for_ticker(self.dtg_cutoff_ticker_labels, 'cutoff')
        )
        cutoff_ticker_container.pack(side=tk.LEFT, padx=5)

        self.dtg_cutoff_value = ""

        # Target
        target_frame = tk.Frame(self.iir_form_frame, bg=self.PANEL_COLOR)
        target_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(target_frame, text="TARGET:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.iir_target_entry = tk.Entry(target_frame, font=("Courier", 9), bg=self.INPUT_BG,
                                          fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, relief=tk.FLAT)
        self.iir_target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Title
        title_frame = tk.Frame(self.iir_form_frame, bg=self.PANEL_COLOR)
        title_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(title_frame, text="TITLE:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.iir_title_entry = tk.Entry(title_frame, font=("Courier", 9), bg=self.INPUT_BG,
                                         fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, relief=tk.FLAT)
        self.iir_title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Information text block
        info_frame = tk.Frame(self.iir_form_frame, bg=self.PANEL_COLOR)
        info_frame.pack(pady=5, padx=10, fill=tk.BOTH)
        tk.Label(info_frame, text="INFORMATION:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR).pack(anchor=tk.W)
        self.iir_information_text = tk.Text(info_frame, font=("Courier", 9), bg=self.INPUT_BG,
                                             fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR,
                                             height=5, wrap=tk.WORD, relief=tk.FLAT)
        self.iir_information_text.pack(fill=tk.BOTH, expand=True)

        # IIR File upload
        iir_file_frame = tk.Frame(self.iir_form_frame, bg=self.PANEL_COLOR)
        iir_file_frame.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(iir_file_frame, text="FILE:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=15, anchor=tk.W).pack(side=tk.LEFT)

        self.iir_selected_file = None
        self.iir_file_label = tk.Label(iir_file_frame, text="No file selected", font=("Courier", 8),
                                        bg=self.PANEL_COLOR, fg=self.TEXT_COLOR)
        self.iir_file_label.pack(side=tk.LEFT, padx=5)

        iir_upload_btn = self._create_button(
            iir_file_frame, "[ BROWSE ]", self._browse_iir_file,
            bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=10
        )
        iir_upload_btn.pack(side=tk.LEFT, padx=5)

        # Submit IIR button
        submit_iir_btn = self._create_button(
            self.iir_form_frame, "[ SUBMIT IIR ]", self._submit_iir,
            bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR
        )
        submit_iir_btn.pack(pady=10)

        # Posts display
        self.posts_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                                     highlightbackground=self.TEXT_COLOR, highlightthickness=2)
        self.posts_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        tk.Label(
            self.posts_frame,
            text="[ THREAD POSTS ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        ).pack(pady=5)

        # Use regular Text widget without scrollbar for cleaner look
        self.posts_display = tk.Text(
            self.posts_frame,
            font=("Courier", 9),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            insertbackground=self.ACCENT_COLOR,
            state=tk.DISABLED,
            wrap=tk.WORD,  # Word wrapping for natural text flow
            width=75,  # Set width to accommodate 70-char borders plus margin
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.posts_display.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Configure text tags
        self.posts_display.tag_config("user", foreground=self.SECONDARY_COLOR, font=("Courier", 9, "bold"))
        self.posts_display.tag_config("time", foreground=self.TEXT_COLOR, font=("Courier", 7))
        self.posts_display.tag_config("text", foreground=self.ACCENT_COLOR)
        self.posts_display.tag_config("iir_header", foreground=self.ERROR_COLOR, font=("Courier", 9, "bold"))
        self.posts_display.tag_config("iir_label", foreground=self.SYSTEM_COLOR, font=("Courier", 8, "bold"))
        self.posts_display.tag_config("iir_value", foreground=self.ACCENT_COLOR, font=("Courier", 8))

        # Load posts and IIRs
        self._load_posts()

    def clear_main_frame(self):
        """Clear all widgets from main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _create_button(self, parent, text, command, bg=None, fg=None, width=None):
        """Create a styled button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Courier", 8, "bold"),
            bg=bg or self.BUTTON_COLOR,
            fg=fg or self.TEXT_COLOR,
            activebackground=self.ACCENT_COLOR,
            activeforeground=self.BG_COLOR,
            width=width,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )

        # Hover effects
        def on_enter(e):
            btn.config(bg=self.ACCENT_COLOR, fg=self.BG_COLOR)
        def on_leave(e):
            btn.config(bg=bg or self.BUTTON_COLOR, fg=fg or self.TEXT_COLOR)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def _create_dtg_ticker(self, parent, on_dtg_click=None):
        """Create LCD-style DTG ticker tape display.

        Returns: (ticker_frame, ticker_labels, dtg_button)
        """
        # Main ticker container
        ticker_container = tk.Frame(parent, bg=self.PANEL_COLOR)

        # Ticker display frame (holds all character labels)
        ticker_frame = tk.Frame(ticker_container, bg=self.PANEL_COLOR, relief=tk.SUNKEN, bd=2,
                                highlightbackground=self.ACCENT_COLOR, highlightthickness=1)
        ticker_frame.pack(side=tk.LEFT, padx=(0, 2))

        # Create 14 character labels for DTG format: DD HH MM Z MON YY
        ticker_labels = []
        char_groups = [2, 2, 2, 1, 3, 2]  # Character counts for each group
        group_names = ['DD', 'HH', 'MM', 'Z', 'MON', 'YY']

        char_index = 0
        for group_idx, char_count in enumerate(char_groups):
            # Add spacing between groups
            if group_idx > 0:
                tk.Frame(ticker_frame, width=2, bg=self.PANEL_COLOR).pack(side=tk.LEFT)

            # Group frame for this DTG component
            group_frame = tk.Frame(ticker_frame, bg=self.PANEL_COLOR)
            group_frame.pack(side=tk.LEFT)

            # Create character labels for this group
            for i in range(char_count):
                char_label = tk.Label(
                    group_frame,
                    text='─',  # Placeholder character
                    font=("Courier", 10, "bold"),
                    bg="#0a0e14",  # Dark LCD background
                    fg=self.ACCENT_COLOR,  # Green glow
                    width=1,
                    height=1,
                    relief=tk.FLAT,
                    bd=1,
                    highlightbackground=self.ACCENT_COLOR,  # Glow effect
                    highlightthickness=1
                )
                char_label.pack(side=tk.LEFT, padx=0, pady=2)
                ticker_labels.append(char_label)
                char_index += 1

        # DTG button - seamless integration with ticker
        dtg_button = tk.Button(
            ticker_container,
            text="DTG",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.ACCENT_COLOR,
            activebackground=self.ACCENT_COLOR,
            activeforeground=self.PANEL_COLOR,
            command=on_dtg_click,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            highlightbackground=self.ACCENT_COLOR,
            highlightthickness=1
        )
        dtg_button.pack(side=tk.LEFT)

        # Hover effect for button
        def on_enter(e):
            dtg_button.config(bg=self.ACCENT_COLOR, fg=self.PANEL_COLOR)
        def on_leave(e):
            dtg_button.config(bg=self.PANEL_COLOR, fg=self.ACCENT_COLOR)
        dtg_button.bind("<Enter>", on_enter)
        dtg_button.bind("<Leave>", on_leave)

        return ticker_container, ticker_labels, dtg_button

    def _update_dtg_ticker(self, ticker_labels, dtg_string):
        """Update ticker tape display with DTG string.

        Args:
            ticker_labels: List of 14 character labels
            dtg_string: DTG in format DDHHMM(Z)MONYY or empty
        """
        if not dtg_string or dtg_string == '':
            # Clear display
            for label in ticker_labels:
                label.config(text='─')
        else:
            # Remove Z and parentheses, parse DTG
            dtg_clean = dtg_string.replace('(', '').replace(')', '')
            # Format: DDHHMMZMONYY (13 chars) but we display with Z separate
            # Parse: DD HH MM Z MON YY
            try:
                if len(dtg_clean) >= 12:
                    chars = list(dtg_clean)
                    # Update each label
                    for i, label in enumerate(ticker_labels):
                        if i < len(chars):
                            label.config(text=chars[i])
                        else:
                            label.config(text='─')
            except:
                # If parsing fails, show dashes
                for label in ticker_labels:
                    label.config(text='─')

    def _format_timestamp_to_dtg(self, timestamp_str):
        """Convert database timestamp to military DTG format (DDHHMM(Z)MONYY).

        Args:
            timestamp_str: Timestamp string from database (e.g., "2025-01-15 14:30:45")

        Returns:
            DTG format string (e.g., "151430ZJAN25") or original if parsing fails
        """
        try:
            from datetime import datetime

            # Parse timestamp (handle various formats)
            if isinstance(timestamp_str, str):
                # Try ISO format first
                try:
                    dt = datetime.fromisoformat(timestamp_str)
                except:
                    # Try other common formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(timestamp_str, fmt)
                            break
                        except:
                            continue
                    else:
                        return timestamp_str  # Return original if can't parse
            else:
                return str(timestamp_str)

            # Format as DDHHMM(Z)MONYY (drop seconds)
            month_abbr = dt.strftime("%b").upper()
            dtg = f"{dt.day:02d}{dt.hour:02d}{dt.minute:02d}Z{month_abbr}{dt.strftime('%y')}"
            return dtg

        except Exception:
            return timestamp_str  # Return original if any error

    def _load_operations(self):
        """Load operations list from server (runs in background thread)."""
        # Run in separate thread to avoid UI freezing
        thread = threading.Thread(target=self._load_operations_thread, daemon=True)
        thread.start()

    def _load_operations_thread(self):
        """Background thread for loading operations with retry logic."""
        # Show loading status (thread-safe UI update)
        self.root.after(0, lambda: self._update_status("[ LOADING... ]", self.TEXT_COLOR))

        # Try twice - first attempt often times out due to buffer issues
        for attempt in range(2):
            try:
                # Aggressive buffer clearing before each attempt
                self._clear_socket_buffer()

                # Small delay between attempts
                if attempt > 0:
                    import time
                    time.sleep(0.5)

                self.message_router.send('OP_LIST:')

                # Receive response with timeout using MessageRouter
                response = self.message_router.get_operation_response(timeout=5.0)

                if response.startswith('OP_LIST:'):
                    data = response[8:]
                    operations = json.loads(data)

                    # Thread-safe UI updates
                    def update_ui():
                        self.ops_listbox.delete(0, tk.END)
                        self.operations_data = {}

                        for op in operations:
                            display = f">> {op['name'].upper():20s} | by {op['creator']:10s} | {op['created_at'][:10]}"
                            self.ops_listbox.insert(tk.END, display)
                            self.operations_data[display] = op

                        # Show success status briefly
                        self._update_status("[ REFRESHED ]", self.SUCCESS_COLOR)
                        self.root.after(2000, lambda: self._update_status("", self.TEXT_COLOR))

                    self.root.after(0, update_ui)
                    return  # Success, exit retry loop

                else:
                    if attempt == 1:  # Last attempt failed
                        self.root.after(0, lambda: self._update_status("[ ERROR ]", self.ERROR_COLOR))
                        self.root.after(0, lambda: self._show_message("No response from server", self.ERROR_COLOR))

            except socket.timeout:
                if attempt == 1:  # Last attempt timed out
                    pass  # Timeout handled by MessageRouter
                    self.root.after(0, lambda: self._update_status("[ ERROR ]", self.ERROR_COLOR))
                    self.root.after(0, lambda: self._show_message("Server timeout - click refresh again", self.ERROR_COLOR))
                # If first attempt, continue to retry
                self.socket.settimeout(None)

            except Exception as e:
                if attempt == 1:  # Last attempt failed
                    error_msg = str(e).lower()
                    print(f"Error loading operations: {e}")

                    def show_error():
                        self._update_status("[ ERROR ]", self.ERROR_COLOR)
                        if "operations.db" in error_msg or "database" in error_msg or "no such table" in error_msg:
                            self._show_message(
                                "Database not found on server.\nServer may be running on a different machine.\nCreate a new operation to initialize database!",
                                self.ERROR_COLOR
                            )
                        elif "connection" in error_msg:
                            self._show_message("Connection lost to server", self.ERROR_COLOR)
                        else:
                            self._show_message(f"Error: {e}", self.ERROR_COLOR)

                    self.root.after(0, show_error)

    def _create_operation(self):
        """Create new operation."""
        op_name = self.op_name_entry.get().strip()
        op_pass = self.op_pass_entry.get()
        op_desc = self.op_desc_entry.get().strip()

        if not op_name or not op_pass:
            self._show_message("Operation name and password required", self.ERROR_COLOR)
            return

        try:
            message = f'OP_CREATE:{op_name}:{op_pass}:{op_desc}'
            self.message_router.send(message)
            response = self.message_router.get_operation_response(timeout=5.0)

            if response.startswith('OP_CREATE_RESULT:'):
                parts = response[17:].split(':', 1)
                success = parts[0] == 'True'
                msg = parts[1] if len(parts) > 1 else ""

                if success:
                    self._show_message(f"✓ {msg}", self.SUCCESS_COLOR)
                    self.op_name_entry.delete(0, tk.END)
                    self.op_pass_entry.delete(0, tk.END)
                    self.op_desc_entry.delete(0, tk.END)
                    self._load_operations()
                else:
                    self._show_message(f"✗ {msg}", self.ERROR_COLOR)

        except TimeoutError:
            self._show_message("Server timeout", self.ERROR_COLOR)
        except Exception as e:
            self._show_message(f"Error: {e}", self.ERROR_COLOR)

    def _access_operation(self):
        """Access selected operation with password."""
        selection = self.ops_listbox.curselection()
        if not selection:
            self._show_message("Select an operation first", self.ERROR_COLOR)
            return

        op_display = self.ops_listbox.get(selection[0])
        op = self.operations_data.get(op_display)

        if not op:
            return

        # Password dialog
        password = self._ask_password(op['name'])
        if not password:
            return

        # Verify password
        try:
            message = f'OP_VERIFY:{op["name"]}:{password}'
            self.message_router.send(message)
            response = self.message_router.get_operation_response(timeout=5.0)

            if response.startswith('OP_VERIFY_RESULT:'):
                valid = response[17:] == 'True'

                if valid:
                    # Get operation info
                    self.message_router.send(f'OP_INFO:{op["name"]}')
                    response = self.message_router.get_operation_response(timeout=5.0)

                    op_info = None
                    if response.startswith('OP_INFO:'):
                        data = response[8:]
                        op_info = json.loads(data) if data != "null" else None

                    self.show_operation_thread(op['name'], op_info)
                else:
                    pass  # Timeout handled by MessageRouter
                    self._show_message("✗ Invalid password", self.ERROR_COLOR)

        except TimeoutError:
            self._show_message("Server timeout", self.ERROR_COLOR)
        except Exception as e:
            self._show_message(f"Error: {e}", self.ERROR_COLOR)

    def _load_posts(self):
        """Load posts and IIRs for current operation."""
        if not self.current_operation:
            return

        try:
            # Load posts
            self.message_router.send(f'OP_POSTS:{self.current_operation}')
            response = self.message_router.get_operation_response(timeout=5.0)

            posts = []
            if response.startswith('OP_POSTS:'):
                data = response[9:]
                posts = json.loads(data)
                # Tag posts for sorting
                for post in posts:
                    post['type'] = 'post'

            # Load IIRs
            iirs = self._load_iirs()
            for iir in iirs:
                iir['type'] = 'iir'

            # Combine and sort by timestamp
            all_items = posts + iirs
            if all_items:
                # Sort by timestamp (use created_at for posts, dtg_submitted for IIRs)
                all_items.sort(key=lambda x: x.get('created_at') if x['type'] == 'post' else x.get('dtg_submitted', ''))

            self.posts_display.config(state=tk.NORMAL)
            self.posts_display.delete('1.0', tk.END)

            if not all_items:
                self.posts_display.insert(tk.END, "No posts or IIRs yet. Be the first to contribute!\n", "text")
            else:
                # Define display width for borders (characters) - reduced for better fit
                BOX_WIDTH = 70

                for item in all_items:
                    if item['type'] == 'post':
                        # Display post with DTG format timestamp
                        dtg_timestamp = self._format_timestamp_to_dtg(item['created_at'])
                        self.posts_display.insert(tk.END, f">> {item['username']}", "user")
                        self.posts_display.insert(tk.END, f" [{dtg_timestamp}]\n", "time")
                        self.posts_display.insert(tk.END, f"{item['comment']}\n", "text")
                        # Filename if present with download link
                        if item.get('filename'):
                            file_tag = f"file_{item['id']}"
                            self.posts_display.insert(tk.END, f"📎 FILE: ", "time")
                            self.posts_display.insert(tk.END, f"{item['filename']}", file_tag)
                            self.posts_display.insert(tk.END, f" [click to download]\n", "time")

                            # Make filename clickable
                            self.posts_display.tag_config(file_tag, foreground=self.SECONDARY_COLOR, underline=1)
                            self.posts_display.tag_bind(file_tag, "<Button-1>",
                                                        lambda e, p=item: self._download_file(p))
                            self.posts_display.tag_bind(file_tag, "<Enter>",
                                                        lambda e, t=file_tag: self.posts_display.config(cursor="hand2"))
                            self.posts_display.tag_bind(file_tag, "<Leave>",
                                                        lambda e: self.posts_display.config(cursor=""))

                        # Full-width separator
                        self.posts_display.insert(tk.END, "\n" + "─" * BOX_WIDTH + "\n", "time")

                    else:  # IIR
                        # Display IIR with simple 3/4 box (top/bottom borders only)
                        report_title = f"INTELLIGENCE REPORT {item['report_number']}"
                        # Calculate padding for centered title
                        total_padding = BOX_WIDTH - len(report_title) - 2 - 2  # -2 for corners, -2 for spaces
                        left_padding = total_padding // 2
                        right_padding = total_padding - left_padding
                        top_border = f"╔{'═' * left_padding} {report_title} {'═' * right_padding}╗\n"
                        self.posts_display.insert(tk.END, top_border, "iir_header")

                        # Convert timestamps to DTG format
                        dtg_submitted = self._format_timestamp_to_dtg(item['dtg_submitted'])
                        dtg_info = item['dtg_info_date'].upper() if item.get('dtg_info_date') else ''
                        dtg_cutoff_val = item['dtg_cutoff'].upper() if item.get('dtg_cutoff') else ''

                        # Simple indented fields (no vertical borders)
                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "SUBMITTED:", "iir_label")
                        self.posts_display.insert(tk.END, f" {dtg_submitted}\n", "iir_value")

                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "SUBMITTER:", "iir_label")
                        self.posts_display.insert(tk.END, f" {item['submitter'].upper()}\n", "iir_value")

                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "PRIORITY:", "iir_label")
                        self.posts_display.insert(tk.END, f" {item['priority'].upper()}\n", "iir_value")

                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "DATE OF INFO:", "iir_label")
                        self.posts_display.insert(tk.END, f" {dtg_info}\n", "iir_value")

                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "CUTOFF:", "iir_label")
                        self.posts_display.insert(tk.END, f" {dtg_cutoff_val}\n", "iir_value")

                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "TARGET:", "iir_label")
                        self.posts_display.insert(tk.END, f" {item['target'].upper()}\n", "iir_value")

                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "TITLE:", "iir_label")
                        self.posts_display.insert(tk.END, f" {item['title'].upper()}\n", "iir_value")

                        # INFORMATION field with simple indentation
                        self.posts_display.insert(tk.END, "  ", "text")
                        self.posts_display.insert(tk.END, "INFORMATION:\n", "iir_label")
                        # Simple word wrap with 4-space indentation
                        info_caps = item['information'].upper()
                        self.posts_display.insert(tk.END, f"    {info_caps}\n", "iir_value")

                        # Filename if present
                        if item.get('filename'):
                            file_tag = f"iir_file_{item['id']}"
                            self.posts_display.insert(tk.END, "  ", "text")
                            self.posts_display.insert(tk.END, "📎 ATTACHMENT: ", "iir_label")
                            self.posts_display.insert(tk.END, f"{item['filename']}", file_tag)
                            self.posts_display.insert(tk.END, " [click to download]\n", "iir_label")

                            # Make filename clickable
                            self.posts_display.tag_config(file_tag, foreground=self.SECONDARY_COLOR, underline=1)
                            self.posts_display.tag_bind(file_tag, "<Button-1>",
                                                        lambda e, i=item: self._download_iir_file(i))
                            self.posts_display.tag_bind(file_tag, "<Enter>",
                                                        lambda e, t=file_tag: self.posts_display.config(cursor="hand2"))
                            self.posts_display.tag_bind(file_tag, "<Leave>",
                                                        lambda e: self.posts_display.config(cursor=""))

                        # Bottom border
                        self.posts_display.insert(tk.END, f"╚{'═' * (BOX_WIDTH - 2)}╝\n", "iir_header")
                        # Separator
                        self.posts_display.insert(tk.END, "─" * BOX_WIDTH + "\n", "time")

            self.posts_display.config(state=tk.DISABLED)

        except socket.timeout:
            self.posts_display.config(state=tk.NORMAL)
            self.posts_display.insert(tk.END, "Server timeout loading posts\n", "text")
            self.posts_display.config(state=tk.DISABLED)
            self.socket.settimeout(None)
        except Exception as e:
            print(f"Error loading posts: {e}")
            self.socket.settimeout(None)

    def _browse_file(self):
        """Browse for a file to upload."""
        filename = filedialog.askopenfilename(
            title="Select file to upload",
            filetypes=[("All files", "*.*")]
        )

        if filename:
            self.selected_file = filename
            import os
            basename = os.path.basename(filename)
            self.file_label.config(text=f"✓ {basename}", fg=self.SUCCESS_COLOR)
        else:
            self.selected_file = None
            self.file_label.config(text="No file selected", fg=self.TEXT_COLOR)

    def _add_post(self):
        """Add a new post to the operation."""
        comment = self.comment_text.get('1.0', tk.END).strip()

        if not comment:
            self._show_message("Comment cannot be empty", self.ERROR_COLOR)
            return

        try:
            import os
            import base64

            filename = None
            file_data = None

            # Read and encode file if selected
            if self.selected_file:
                try:
                    with open(self.selected_file, 'rb') as f:
                        file_data = base64.b64encode(f.read()).decode('utf-8')
                    filename = os.path.basename(self.selected_file)
                except Exception as e:
                    self._show_message(f"✗ Error reading file: {e}", self.ERROR_COLOR)
                    return

            # Send post with optional file data
            if file_data:
                message = f'OP_POST:{self.current_operation}:{comment}:{filename}:{file_data}'
                print(f"CLIENT DEBUG: Sending with file - op={self.current_operation}, comment_len={len(comment)}, filename={filename}, file_data_len={len(file_data)}")
            else:
                message = f'OP_POST:{self.current_operation}:{comment}::'
                print(f"CLIENT DEBUG: Sending without file - op={self.current_operation}, comment_len={len(comment)}")

            self.message_router.send(message)
            response = self.message_router.get_operation_response(timeout=10.0)  # Longer timeout for file uploads

            if response.startswith('OP_POST_RESULT:'):
                parts = response[15:].split(':', 1)
                success = parts[0] == 'True'

                if success:
                    self._show_message("✓ Post added", self.SUCCESS_COLOR)
                    self.comment_text.delete('1.0', tk.END)
                    self.selected_file = None
                    self.file_label.config(text="No file selected", fg=self.TEXT_COLOR)
                    self._load_posts()
                else:
                    self._show_message(f"✗ Failed to add post", self.ERROR_COLOR)

        except TimeoutError:
            self._show_message("Server timeout - post may be too large", self.ERROR_COLOR)
        except Exception as e:
            self._show_message(f"Error: {e}", self.ERROR_COLOR)

    def _download_file(self, post):
        """Download file from post."""
        try:
            import os
            import base64
            from tkinter import filedialog

            # Request file data from server
            self.message_router.send(f'OP_FILE:{post["id"]}')

            # Longer timeout for large files
            response = self.message_router.get_operation_response(timeout=30.0)

            if response.startswith('OP_FILE:'):
                file_data_b64 = response[8:]
                if file_data_b64 and file_data_b64 != "null":
                    # Ask where to save
                    save_path = filedialog.asksaveasfilename(
                        defaultextension="",
                        initialfile=post['filename'],
                        title="Save file as"
                    )

                    if save_path:
                        # Decode and save file
                        file_data = base64.b64decode(file_data_b64)
                        with open(save_path, 'wb') as f:
                            f.write(file_data)
                        self._show_message(f"✓ File saved: {os.path.basename(save_path)}", self.SUCCESS_COLOR)
                else:
                    self._show_message("✗ File not found", self.ERROR_COLOR)
            else:
                self._show_message("✗ Failed to download file", self.ERROR_COLOR)

        except TimeoutError:
            self._show_message("Server timeout downloading file", self.ERROR_COLOR)
        except Exception as e:
            self._show_message(f"✗ Error: {e}", self.ERROR_COLOR)

    def _ask_password(self, op_name):
        """Show password dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"◆ Access {op_name} ◆")
        dialog.configure(bg=self.BG_COLOR)
        dialog.geometry("400x200")  # Increased height to show button
        dialog.resizable(False, False)

        # Center dialog relative to parent window
        # Update both dialog and parent to ensure accurate positioning
        self.root.update_idletasks()
        dialog.update_idletasks()

        # Get parent window position and size
        parent_x = self.root.winfo_rootx()  # Use rootx/rooty for absolute screen position
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        dialog_width = 400
        dialog_height = 200

        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.grab_set()

        # Retro-style header
        tk.Label(
            dialog,
            text="▼▼▼ ACCESSING MAINFRAME ▼▼▼",
            font=("Courier", 9, "bold"),
            bg=self.BG_COLOR,
            fg=self.ERROR_COLOR
        ).pack(pady=(10, 5))

        tk.Label(
            dialog,
            text=f"Enter password for:\n{op_name.upper()}",
            font=("Courier", 10, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR
        ).pack(pady=10)

        pass_entry = tk.Entry(
            dialog,
            font=("Courier", 11),
            bg=self.PANEL_COLOR,
            fg=self.ACCENT_COLOR,
            insertbackground=self.ACCENT_COLOR,
            show="*",
            width=30
        )
        pass_entry.pack(pady=10)
        pass_entry.focus()

        result = [None]

        def on_ok():
            result[0] = pass_entry.get()
            dialog.destroy()

        pass_entry.bind('<Return>', lambda e: on_ok())

        btn = tk.Button(
            dialog,
            text="[ ACCESS ]",
            command=on_ok,
            font=("Courier", 10, "bold"),
            bg=self.BUTTON_COLOR,
            fg=self.ACCENT_COLOR,
            activebackground=self.ACCENT_COLOR,
            activeforeground=self.BG_COLOR,
            padx=20,
            pady=5,
            relief=tk.RAISED,
            bd=3
        )
        btn.pack(pady=15)  # Increased padding to ensure visibility

        self.root.wait_window(dialog)
        return result[0]

    def _clear_socket_buffer(self):
        """No-op: MessageRouter handles all buffering and message routing."""
        pass  # MessageRouter eliminates the need for manual buffer clearing

    def _update_status(self, message, color):
        """Update the status indicator label."""
        if self.status_label:
            self.status_label.config(text=message, fg=color)

    def _show_message(self, message, color):
        """Show temporary message."""
        # Create a temporary label that fades
        msg_label = tk.Label(
            self.main_frame,
            text=message,
            font=("Courier", 9, "bold"),
            bg=self.BG_COLOR,
            fg=color
        )
        msg_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # Remove after 3 seconds
        self.root.after(3000, msg_label.destroy)

    def _toggle_form(self, mode):
        """Toggle between post form and IIR form."""
        self.form_mode = mode

        if mode == "post":
            # Show post form and posts display, hide IIR form
            self.post_form_frame.pack(pady=5, fill=tk.X)
            self.iir_form_frame.pack_forget()
            self.posts_frame.pack(pady=5, fill=tk.BOTH, expand=True)
            # Update button states
            self.post_toggle_btn.config(relief=tk.SUNKEN, bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR)
            self.iir_toggle_btn.config(relief=tk.RAISED, bg=self.SYSTEM_COLOR, fg=self.BG_COLOR)
        else:  # mode == "iir"
            # Hide post form and posts display, show IIR form taking all space
            self.post_form_frame.pack_forget()
            self.posts_frame.pack_forget()
            self.iir_form_frame.pack(pady=5, fill=tk.BOTH, expand=True)
            # Update button states
            self.post_toggle_btn.config(relief=tk.RAISED, bg=self.SYSTEM_COLOR, fg=self.BG_COLOR)
            self.iir_toggle_btn.config(relief=tk.SUNKEN, bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR)

    def _browse_iir_file(self):
        """Browse for a file to attach to IIR."""
        filename = filedialog.askopenfilename(
            title="Select file to attach to IIR",
            filetypes=[("All files", "*.*")]
        )

        if filename:
            self.iir_selected_file = filename
            import os
            basename = os.path.basename(filename)
            self.iir_file_label.config(text=f"✓ {basename}", fg=self.SUCCESS_COLOR)
        else:
            self.iir_selected_file = None
            self.iir_file_label.config(text="No file selected", fg=self.TEXT_COLOR)

    def _submit_iir(self):
        """Submit an Intelligence Information Report."""
        # Get all field values
        priority = self.iir_priority_var.get()

        # Build DTG info date (single or range)
        if self.dtg_info_value2:
            dtg_info_date = f"{self.dtg_info_value1} - {self.dtg_info_value2}"
        else:
            dtg_info_date = self.dtg_info_value1

        dtg_cutoff = self.dtg_cutoff_value
        target = self.iir_target_entry.get().strip()
        title = self.iir_title_entry.get().strip()
        information = self.iir_information_text.get('1.0', tk.END).strip()

        # Validate required fields
        if not all([dtg_info_date, dtg_cutoff, target, title, information]):
            self._show_message("All fields required except file attachment", self.ERROR_COLOR)
            return

        try:
            import os
            import base64

            filename = None
            file_data = None

            # Read and encode file if selected
            if self.iir_selected_file:
                try:
                    with open(self.iir_selected_file, 'rb') as f:
                        file_data = base64.b64encode(f.read()).decode('utf-8')
                    filename = os.path.basename(self.iir_selected_file)
                except Exception as e:
                    self._show_message(f"✗ Error reading file: {e}", self.ERROR_COLOR)
                    return

            # Build message using JSON to avoid colon conflicts
            iir_data = {
                'operation': self.current_operation,
                'priority': priority,
                'dtg_info_date': dtg_info_date,
                'dtg_cutoff': dtg_cutoff,
                'target': target,
                'title': title,
                'information': information,
                'filename': filename or '',
                'file_data': file_data or ''
            }
            message = f'OP_IIR_SUBMIT:{json.dumps(iir_data)}'

            self.message_router.send(message)
            response = self.message_router.get_operation_response(timeout=10.0)

            # Debug: print response to see what we actually got
            print(f"IIR SUBMIT DEBUG: Received response: {repr(response)}")

            if response and response.startswith('IIR_SUBMIT_RESULT:'):
                parts = response[18:].split(':', 1)
                success = parts[0] == 'True'
                result = parts[1] if len(parts) > 1 else ""

                if success:
                    # result is the IR number
                    self._show_message(f"✓ IIR submitted: {result}", self.SUCCESS_COLOR)
                    # Clear form
                    self.iir_priority_var.set("routine")

                    # Clear DTG tickers
                    self.dtg_info_value1 = ""
                    self.dtg_info_value2 = ""
                    self.dtg_cutoff_value = ""
                    self._update_dtg_ticker(self.dtg_info_ticker1_labels, "")
                    self._update_dtg_ticker(self.dtg_cutoff_ticker_labels, "")

                    # Remove second ticker if it exists
                    if self.dtg_info_ticker2_container is not None:
                        self.dtg_info_ticker2_container.destroy()
                        self.dtg_info_ticker2_container = None
                        self.dtg_info_ticker2_labels = None

                    # Hide [END] button
                    self.dtg_info_end_btn.pack_forget()

                    self.iir_target_entry.delete(0, tk.END)
                    self.iir_title_entry.delete(0, tk.END)
                    self.iir_information_text.delete('1.0', tk.END)
                    self.iir_selected_file = None
                    self.iir_file_label.config(text="No file selected", fg=self.TEXT_COLOR)
                    # Reload posts and IIRs
                    self._load_posts()
                else:
                    self._show_message(f"✗ {result}", self.ERROR_COLOR)
            else:
                # Unexpected response format
                print(f"IIR SUBMIT ERROR: Unexpected response format: {repr(response)}")
                self._show_message(f"✗ Unexpected server response", self.ERROR_COLOR)

        except TimeoutError:
            print("IIR SUBMIT ERROR: Timeout waiting for server response")
            self._show_message("Server timeout - IIR may be too large", self.ERROR_COLOR)
        except Exception as e:
            print(f"IIR SUBMIT ERROR: Exception occurred: {e}")
            self._show_message(f"Error: {e}", self.ERROR_COLOR)

    def _load_iirs(self):
        """Load IIRs for current operation."""
        if not self.current_operation:
            return []

        try:
            self.message_router.send(f'OP_IIR_LIST:{self.current_operation}')
            response = self.message_router.get_operation_response(timeout=5.0)

            if response.startswith('IIR_LIST:'):
                data = response[9:]
                iirs = json.loads(data)
                return iirs
            return []

        except Exception as e:
            print(f"Error loading IIRs: {e}")
            return []

    def _download_iir_file(self, iir):
        """Download file from IIR."""
        try:
            import os
            import base64
            from tkinter import filedialog

            # Request file data from server
            self.message_router.send(f'OP_IIR_FILE:{iir["id"]}')

            # Longer timeout for large files
            response = self.message_router.get_operation_response(timeout=30.0)

            if response.startswith('IIR_FILE:'):
                file_data_b64 = response[9:]
                if file_data_b64 and file_data_b64 != "null":
                    # Ask where to save
                    save_path = filedialog.asksaveasfilename(
                        defaultextension="",
                        initialfile=iir['filename'],
                        title="Save file as"
                    )

                    if save_path:
                        # Decode and save file
                        file_data = base64.b64decode(file_data_b64)
                        with open(save_path, 'wb') as f:
                            f.write(file_data)
                        self._show_message(f"✓ File saved: {os.path.basename(save_path)}", self.SUCCESS_COLOR)
                else:
                    self._show_message("✗ File not found", self.ERROR_COLOR)
            else:
                self._show_message("✗ Failed to download file", self.ERROR_COLOR)

        except TimeoutError:
            self._show_message("Server timeout downloading file", self.ERROR_COLOR)
        except Exception as e:
            self._show_message(f"✗ Error: {e}", self.ERROR_COLOR)

    def _show_dtg_calendar_for_ticker(self, ticker_labels, ticker_id):
        """Show calendar and update ticker display.

        Args:
            ticker_labels: List of character labels for the ticker
            ticker_id: 1, 2, or 'cutoff' to identify which ticker
        """
        from datetime import datetime
        import calendar

        dialog = tk.Toplevel(self.root)
        dialog.title("Select Date/Time")
        dialog.configure(bg=self.BG_COLOR)
        dialog.geometry("350x400")
        dialog.resizable(False, False)

        # Center dialog
        self.root.update_idletasks()
        dialog.update_idletasks()
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width - 350) // 2
        y = parent_y + (parent_height - 400) // 2
        dialog.geometry(f"350x400+{x}+{y}")
        dialog.grab_set()

        # Current date/time
        now = datetime.now()
        selected_date = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        selected_hour = tk.StringVar(value=now.strftime("%H"))
        selected_minute = tk.StringVar(value=now.strftime("%M"))

        # Header
        tk.Label(dialog, text="SELECT DATE & TIME", font=("Courier", 10, "bold"),
                bg=self.BG_COLOR, fg=self.SYSTEM_COLOR).pack(pady=10)

        # Calendar frame
        cal_frame = tk.Frame(dialog, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=2)
        cal_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Month/Year selector
        nav_frame = tk.Frame(cal_frame, bg=self.PANEL_COLOR)
        nav_frame.pack(pady=5)

        current_month = tk.IntVar(value=now.month)
        current_year = tk.IntVar(value=now.year)

        def update_calendar():
            # Clear existing calendar
            for widget in days_frame.winfo_children():
                widget.destroy()

            # Get calendar for selected month/year
            month = current_month.get()
            year = current_year.get()
            cal = calendar.monthcalendar(year, month)

            # Day headers
            for i, day in enumerate(['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']):
                tk.Label(days_frame, text=day, font=("Courier", 8, "bold"),
                        bg=self.PANEL_COLOR, fg=self.SYSTEM_COLOR, width=4).grid(row=0, column=i)

            # Days
            for week_num, week in enumerate(cal, start=1):
                for day_num, day in enumerate(week):
                    if day == 0:
                        tk.Label(days_frame, text="", bg=self.PANEL_COLOR, width=4).grid(row=week_num, column=day_num)
                    else:
                        day_str = f"{year}-{month:02d}-{day:02d}"
                        btn = tk.Button(days_frame, text=str(day), font=("Courier", 8),
                                       bg=self.INPUT_BG, fg=self.TEXT_COLOR,
                                       command=lambda d=day_str: selected_date.set(d),
                                       width=4, cursor="hand2")
                        btn.grid(row=week_num, column=day_num, padx=1, pady=1)

        def prev_month():
            month = current_month.get()
            year = current_year.get()
            if month == 1:
                current_month.set(12)
                current_year.set(year - 1)
            else:
                current_month.set(month - 1)
            month_label.config(text=f"{calendar.month_name[current_month.get()]} {current_year.get()}")
            update_calendar()

        def next_month():
            month = current_month.get()
            year = current_year.get()
            if month == 12:
                current_month.set(1)
                current_year.set(year + 1)
            else:
                current_month.set(month + 1)
            month_label.config(text=f"{calendar.month_name[current_month.get()]} {current_year.get()}")
            update_calendar()

        tk.Button(nav_frame, text="<", command=prev_month, font=("Courier", 9, "bold"),
                 bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=3).pack(side=tk.LEFT, padx=5)

        month_label = tk.Label(nav_frame, text=f"{calendar.month_name[now.month]} {now.year}",
                              font=("Courier", 9, "bold"), bg=self.PANEL_COLOR, fg=self.ACCENT_COLOR, width=20)
        month_label.pack(side=tk.LEFT, padx=5)

        tk.Button(nav_frame, text=">", command=next_month, font=("Courier", 9, "bold"),
                 bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=3).pack(side=tk.LEFT, padx=5)

        # Days frame
        days_frame = tk.Frame(cal_frame, bg=self.PANEL_COLOR)
        days_frame.pack(pady=5)
        update_calendar()

        # Time selector
        time_frame = tk.Frame(dialog, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=2)
        time_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(time_frame, text="TIME (UTC):", font=("Courier", 9, "bold"),
                bg=self.PANEL_COLOR, fg=self.TEXT_COLOR).pack(pady=5)

        time_input_frame = tk.Frame(time_frame, bg=self.PANEL_COLOR)
        time_input_frame.pack(pady=5)

        tk.Label(time_input_frame, text="Hour:", font=("Courier", 8),
                bg=self.PANEL_COLOR, fg=self.TEXT_COLOR).pack(side=tk.LEFT, padx=5)

        from tkinter import ttk
        hour_combo = ttk.Combobox(time_input_frame, textvariable=selected_hour,
                                   values=[f"{h:02d}" for h in range(24)],
                                   state="readonly", font=("Courier", 9), width=4)
        hour_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(time_input_frame, text="Min:", font=("Courier", 8),
                bg=self.PANEL_COLOR, fg=self.TEXT_COLOR).pack(side=tk.LEFT, padx=5)

        min_combo = ttk.Combobox(time_input_frame, textvariable=selected_minute,
                                  values=[f"{m:02d}" for m in range(0, 60, 5)],
                                  state="readonly", font=("Courier", 9), width=4)
        min_combo.pack(side=tk.LEFT, padx=5)

        # OK button
        def on_ok():
            # Format: DDHHMM(Z)MONYY
            date = datetime.strptime(selected_date.get(), "%Y-%m-%d")
            hour = selected_hour.get()
            minute = selected_minute.get()

            # DTG format: DDHHMMZMONYY
            month_abbr = date.strftime("%b").upper()
            dtg = f"{date.day:02d}{hour}{minute}Z{month_abbr}{date.strftime('%y')}"

            # Update the appropriate ticker
            if ticker_id == 1:
                self.dtg_info_value1 = dtg
                self._update_dtg_ticker(ticker_labels, dtg)
                # Show [END] button after first date is set
                if not self.dtg_info_end_btn.winfo_ismapped():
                    self.dtg_info_end_btn.pack(side=tk.LEFT, padx=5)
            elif ticker_id == 2:
                self.dtg_info_value2 = dtg
                self._update_dtg_ticker(ticker_labels, dtg)
            elif ticker_id == 'cutoff':
                self.dtg_cutoff_value = dtg
                self._update_dtg_ticker(ticker_labels, dtg)

            dialog.destroy()

        btn = tk.Button(dialog, text="[ OK ]", command=on_ok, font=("Courier", 10, "bold"),
                       bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR, padx=20, pady=5)
        btn.pack(pady=10)

        self.root.wait_window(dialog)

    def _add_second_dtg_info(self):
        """Add second ticker for date range."""
        if self.dtg_info_ticker2_container is not None:
            return  # Already added

        # Create second ticker
        ticker2_container, self.dtg_info_ticker2_labels, dtg2_btn = self._create_dtg_ticker(
            self.dtg_info_container,
            on_dtg_click=lambda: self._show_dtg_calendar_for_ticker(self.dtg_info_ticker2_labels, 2)
        )
        ticker2_container.pack(side=tk.LEFT, padx=(10, 0))
        self.dtg_info_ticker2_container = ticker2_container

        # Hide [END] button after second ticker is added
        self.dtg_info_end_btn.pack_forget()

    def _show_dtg_calendar(self, entry_widget):
        """Show calendar widget to select date/time in DTG format."""
        from datetime import datetime
        import calendar

        dialog = tk.Toplevel(self.root)
        dialog.title("Select Date/Time")
        dialog.configure(bg=self.BG_COLOR)
        dialog.geometry("350x400")
        dialog.resizable(False, False)

        # Center dialog
        self.root.update_idletasks()
        dialog.update_idletasks()
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width - 350) // 2
        y = parent_y + (parent_height - 400) // 2
        dialog.geometry(f"350x400+{x}+{y}")
        dialog.grab_set()

        # Current date/time
        now = datetime.now()
        selected_date = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        selected_hour = tk.StringVar(value=now.strftime("%H"))
        selected_minute = tk.StringVar(value=now.strftime("%M"))

        # Header
        tk.Label(dialog, text="SELECT DATE & TIME", font=("Courier", 10, "bold"),
                bg=self.BG_COLOR, fg=self.SYSTEM_COLOR).pack(pady=10)

        # Calendar frame
        cal_frame = tk.Frame(dialog, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=2)
        cal_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Month/Year selector
        nav_frame = tk.Frame(cal_frame, bg=self.PANEL_COLOR)
        nav_frame.pack(pady=5)

        current_month = tk.IntVar(value=now.month)
        current_year = tk.IntVar(value=now.year)

        def update_calendar():
            # Clear existing calendar
            for widget in days_frame.winfo_children():
                widget.destroy()

            # Get calendar for selected month/year
            month = current_month.get()
            year = current_year.get()
            cal = calendar.monthcalendar(year, month)

            # Day headers
            for i, day in enumerate(['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']):
                tk.Label(days_frame, text=day, font=("Courier", 8, "bold"),
                        bg=self.PANEL_COLOR, fg=self.SYSTEM_COLOR, width=4).grid(row=0, column=i)

            # Days
            for week_num, week in enumerate(cal, start=1):
                for day_num, day in enumerate(week):
                    if day == 0:
                        tk.Label(days_frame, text="", bg=self.PANEL_COLOR, width=4).grid(row=week_num, column=day_num)
                    else:
                        day_str = f"{year}-{month:02d}-{day:02d}"
                        btn = tk.Button(days_frame, text=str(day), font=("Courier", 8),
                                       bg=self.INPUT_BG, fg=self.TEXT_COLOR,
                                       command=lambda d=day_str: selected_date.set(d),
                                       width=4, cursor="hand2")
                        btn.grid(row=week_num, column=day_num, padx=1, pady=1)

        def prev_month():
            month = current_month.get()
            year = current_year.get()
            if month == 1:
                current_month.set(12)
                current_year.set(year - 1)
            else:
                current_month.set(month - 1)
            month_label.config(text=f"{calendar.month_name[current_month.get()]} {current_year.get()}")
            update_calendar()

        def next_month():
            month = current_month.get()
            year = current_year.get()
            if month == 12:
                current_month.set(1)
                current_year.set(year + 1)
            else:
                current_month.set(month + 1)
            month_label.config(text=f"{calendar.month_name[current_month.get()]} {current_year.get()}")
            update_calendar()

        tk.Button(nav_frame, text="<", command=prev_month, font=("Courier", 9, "bold"),
                 bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=3).pack(side=tk.LEFT, padx=5)

        month_label = tk.Label(nav_frame, text=f"{calendar.month_name[now.month]} {now.year}",
                              font=("Courier", 9, "bold"), bg=self.PANEL_COLOR, fg=self.ACCENT_COLOR, width=20)
        month_label.pack(side=tk.LEFT, padx=5)

        tk.Button(nav_frame, text=">", command=next_month, font=("Courier", 9, "bold"),
                 bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=3).pack(side=tk.LEFT, padx=5)

        # Days frame
        days_frame = tk.Frame(cal_frame, bg=self.PANEL_COLOR)
        days_frame.pack(pady=5)
        update_calendar()

        # Time selector
        time_frame = tk.Frame(dialog, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=2)
        time_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(time_frame, text="TIME (UTC):", font=("Courier", 9, "bold"),
                bg=self.PANEL_COLOR, fg=self.TEXT_COLOR).pack(pady=5)

        time_input_frame = tk.Frame(time_frame, bg=self.PANEL_COLOR)
        time_input_frame.pack(pady=5)

        tk.Label(time_input_frame, text="Hour:", font=("Courier", 8),
                bg=self.PANEL_COLOR, fg=self.TEXT_COLOR).pack(side=tk.LEFT, padx=5)

        from tkinter import ttk
        hour_combo = ttk.Combobox(time_input_frame, textvariable=selected_hour,
                                   values=[f"{h:02d}" for h in range(24)],
                                   state="readonly", font=("Courier", 9), width=4)
        hour_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(time_input_frame, text="Min:", font=("Courier", 8),
                bg=self.PANEL_COLOR, fg=self.TEXT_COLOR).pack(side=tk.LEFT, padx=5)

        min_combo = ttk.Combobox(time_input_frame, textvariable=selected_minute,
                                  values=[f"{m:02d}" for m in range(0, 60, 5)],
                                  state="readonly", font=("Courier", 9), width=4)
        min_combo.pack(side=tk.LEFT, padx=5)

        # OK button
        def on_ok():
            # Format: DDHHMM(Z)MONYY
            date = datetime.strptime(selected_date.get(), "%Y-%m-%d")
            hour = selected_hour.get()
            minute = selected_minute.get()

            # DTG format: DDHHMM(Z)MONYY
            month_abbr = date.strftime("%b").upper()
            dtg = f"{date.day:02d}{hour}{minute}Z{month_abbr}{date.strftime('%y')}"

            # Check if entry already has a DTG (for range)
            current = entry_widget.get().strip()
            if current and not current.endswith('[END]'):
                # Add as second date
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, f"{current} - {dtg} [END]")
            else:
                # Set as first date
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, dtg)

            dialog.destroy()

        btn = tk.Button(dialog, text="[ OK ]", command=on_ok, font=("Courier", 10, "bold"),
                       bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR, padx=20, pady=5)
        btn.pack(pady=10)

        self.root.wait_window(dialog)

    def _on_abort(self):
        """Handle abort button."""
        if self.exit_callback:
            self.exit_callback()
