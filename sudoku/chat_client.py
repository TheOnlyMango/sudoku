"""Secret Chat Client - 90s Hacker mIRC Style"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading
import time
import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import config reader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat_config_reader import get_config
from auth_ui import AuthUI
from inbox_ui import InboxUI


class ChatClient:
    """90s style chat client with Dracula theme."""

    def __init__(self, root, server_host=None, server_port=None, exit_callback=None, operations_callback=None):
        """Initialize chat client.

        Args:
            root: Tkinter root window
            server_host: Server address (None = read from config)
            server_port: Server port (None = read from config)
            exit_callback: Callback when exiting chat
            operations_callback: Callback to switch to operations view
        """
        self.root = root

        # Load config
        config = get_config()
        config_host, config_port = config.get_client_config()

        # Use provided values or config values
        self.server_host = server_host if server_host is not None else config_host
        self.server_port = server_port if server_port is not None else config_port
        self.socket = None
        self.username = None
        self.password = None  # Store password for authentication
        self.is_anon = False  # Track if user is anonymous
        self.token = None  # Auth token from server
        self.running = False
        self.users = {}  # {username: is_anon} - track anon status
        self.exit_callback = exit_callback
        self.operations_callback = operations_callback
        self.is_hidden = False  # Track if chat is just hidden (not disconnected)

        # Request/response system for DM operations
        self.pending_responses = {}  # {request_id: response_data}
        self.response_lock = threading.Lock()
        self.request_counter = 0

        # Typing indicator state
        self.typing_users = {}  # {username: timestamp}
        self.typing_timer = None
        self.last_typing_sent = 0
        self.blink_state = 0  # For blinking dots animation

        # Dracula colors with 90s hacker twist
        self.BG_COLOR = "#282a36"
        self.PANEL_COLOR = "#0a0e14"  # Darker for terminal feel with CRT glow
        self.TEXT_COLOR = "#f8f8f2"  # White/light gray for message text (terminal style)
        self.USER_COLOR = "#8be9fd"  # Cyan for usernames
        self.ANON_COLOR = "#ff5555"  # RED for anonymous users
        self.SYSTEM_COLOR = "#ffb86c"  # Orange for system messages
        self.DM_COLOR = "#ff79c6"  # Pink for DMs
        self.INPUT_BG = "#1a1f2e"  # Darker input with subtle glow
        self.BUTTON_COLOR = "#bd93f9"
        self.PROMPT_COLOR = "#6272a4"  # Muted blue for prompt symbols

        # Per-user color palette (90s hacker style)
        self.USER_COLORS = [
            "#50fa7b",  # Green
            "#8be9fd",  # Cyan
            "#ff79c6",  # Pink
            "#ffb86c",  # Orange
            "#bd93f9",  # Purple
            "#f1fa8c",  # Yellow
            "#ff5555",  # Red
            "#6272a4",  # Blue-gray
            "#44fa7b",  # Lime
            "#ff6ac1",  # Magenta
        ]

    def create_ui(self):
        """Create the chat interface."""
        # Configure root (handle both Tk and Frame parents)
        if isinstance(self.root, tk.Tk):
            self.root.title("░▒▓█ SECURE CHAT █▓▒░")
            self.root.configure(bg=self.BG_COLOR)
            self.root.geometry("700x600")
            self.root.resizable(False, False)
        else:
            self.root.configure(bg=self.BG_COLOR)

        # Main container
        main_frame = tk.Frame(self.root, bg=self.BG_COLOR, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Retro ASCII art title bar
        title_bar = tk.Label(
            main_frame,
            text="╔═══════════════════════════════════════════════════════════╗\n"
                 "║  ░▒▓█ S H N E T  S E C U R E  T E R M I N A L █▓▒░  ║\n"
                 "╚═══════════════════════════════════════════════════════════╝",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg=self.BUTTON_COLOR,
            justify=tk.CENTER
        )
        title_bar.pack(pady=(0, 2))

        # Blinking tunnel status message
        self.tunnel_label = tk.Label(
            main_frame,
            text=">> ENCRYPTED TUNNEL ESTABLISHED <<",
            font=("Courier", 8, "bold"),
            bg=self.BG_COLOR,
            fg=self.SYSTEM_COLOR
        )
        self.tunnel_label.pack(pady=(0, 5))
        self._start_tunnel_blink()

        # Header with 90s ASCII art and buttons
        header_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        header_frame.pack(pady=(0, 10), fill=tk.X)

        # ABORT button - red circle with 3D effect in top left
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

        # INBOX button - pink with cyberpunk style - pack on RIGHT side
        # Store reference so we can hide it for anon users
        self.inbox_btn = tk.Button(
            header_frame,
            text="INBOX",
            command=self.show_inbox,
            font=("Courier", 8, "bold"),
            bg="#ff006e",  # Hot pink
            fg="#00ff41",  # Matrix green
            activebackground="#00ff41",
            activeforeground="#ff006e",
            width=10,
            height=1,
            relief=tk.RAISED,
            bd=4,
            cursor="hand2"
        )
        self.inbox_btn.pack(side=tk.RIGHT, padx=5)

        # Add hover effect
        def on_inbox_enter(e):
            self.inbox_btn.config(bg="#00ff41", fg="#ff006e", relief=tk.RAISED)
        def on_inbox_leave(e):
            self.inbox_btn.config(bg="#ff006e", fg="#00ff41", relief=tk.RAISED)
        self.inbox_btn.bind("<Enter>", on_inbox_enter)
        self.inbox_btn.bind("<Leave>", on_inbox_leave)

        # OPERATIONS button - purple with cyberpunk style - pack on RIGHT side for visibility
        if self.operations_callback:
            ops_btn = tk.Button(
                header_frame,
                text="OPERATIONS",
                command=self.operations_callback,
                font=("Courier", 8, "bold"),
                bg="#7b2cbf",  # Purple
                fg="#00ff41",  # Matrix green
                activebackground="#00ff41",
                activeforeground="#7b2cbf",
                width=12,
                height=1,
                relief=tk.RAISED,
                bd=4,
                cursor="hand2"
            )
            ops_btn.pack(side=tk.RIGHT, padx=5)

            # Add hover effect
            def on_ops_enter(e):
                ops_btn.config(bg="#00ff41", fg="#7b2cbf", relief=tk.RAISED)
            def on_ops_leave(e):
                ops_btn.config(bg="#7b2cbf", fg="#00ff41", relief=tk.RAISED)
            ops_btn.bind("<Enter>", on_ops_enter)
            ops_btn.bind("<Leave>", on_ops_leave)

        # Content frame (users + chat)
        content_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - User list
        user_panel = tk.Frame(content_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                             highlightbackground=self.BUTTON_COLOR, highlightthickness=2)
        user_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))

        user_label = tk.Label(
            user_panel,
            text="[ USERS ONLINE ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.USER_COLOR
        )
        user_label.pack(pady=5)

        # User listbox (increased font size)
        self.user_listbox = tk.Listbox(
            user_panel,
            font=("Courier", 11),  # Increased from 9 to 11
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR,
            selectbackground=self.BUTTON_COLOR,
            selectforeground=self.BG_COLOR,
            width=18,
            height=25,
            relief=tk.FLAT,
            highlightthickness=0,
            bd=0
        )
        self.user_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Right panel - Chat area
        chat_panel = tk.Frame(content_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                             highlightbackground=self.BUTTON_COLOR, highlightthickness=2)
        chat_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chat_label = tk.Label(
            chat_panel,
            text="[ GROUP CHAT ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        )
        chat_label.pack(pady=5)

        # Chat display - ScrolledText for auto-scroll (increased font size)
        self.chat_display = scrolledtext.ScrolledText(
            chat_panel,
            font=("Courier", 11),  # Increased from 9 to 11
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.chat_display.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Configure text tags for colors (oh-my-zsh terminal style)
        self.chat_display.tag_config("system", foreground=self.SYSTEM_COLOR)
        self.chat_display.tag_config("prompt", foreground=self.PROMPT_COLOR)  # Terminal prompt symbols
        self.chat_display.tag_config("time", foreground=self.PROMPT_COLOR)  # Same as prompt [@shnet]
        self.chat_display.tag_config("dm", foreground=self.DM_COLOR)
        self.chat_display.tag_config("text", foreground=self.TEXT_COLOR)  # White for message text

        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        # Terminal-style prompt label
        prompt_label = tk.Label(
            input_frame,
            text=">>>",
            font=("Courier", 12, "bold"),
            bg=self.BG_COLOR,
            fg=self.PROMPT_COLOR
        )
        prompt_label.pack(side=tk.LEFT, padx=(0, 5))

        # Message input
        self.message_entry = tk.Entry(
            input_frame,
            font=("Courier", 10),
            bg=self.INPUT_BG,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief=tk.RIDGE,
            bd=2
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.bind('<KeyPress>', self.on_typing)

        # Send button
        send_btn = tk.Button(
            input_frame,
            text="[ SEND ]",
            command=self.send_message,
            font=("Courier", 10, "bold"),
            bg=self.BUTTON_COLOR,
            fg=self.BG_COLOR,
            activebackground=self.DM_COLOR,
            activeforeground=self.BG_COLOR,
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
            width=10
        )
        send_btn.pack(side=tk.LEFT)

        # Status indicator with LED circle
        status_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        # LED indicator
        self.led_indicator = tk.Label(
            status_frame,
            text="●",
            font=("Courier", 16, "bold"),
            bg=self.BG_COLOR,
            fg="#ffb86c"  # Yellow for connecting
        )
        self.led_indicator.pack(side=tk.LEFT, padx=5)

        # Status text
        self.status_label = tk.Label(
            status_frame,
            text="CONNECTING...",
            font=("Courier", 9, "bold"),
            bg=self.BG_COLOR,
            fg=self.SYSTEM_COLOR,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Focus on input
        self.message_entry.focus()

    def get_user_color(self, username):
        """Get consistent color for a username based on hash.

        Args:
            username: The username to get color for

        Returns:
            Hex color string
        """
        # Hash the username to get consistent color
        hash_value = sum(ord(c) for c in username)
        return self.USER_COLORS[hash_value % len(self.USER_COLORS)]

    def _start_tunnel_blink(self):
        """Start slow blinking animation for tunnel status."""
        def blink():
            if hasattr(self, 'tunnel_label'):
                current_fg = self.tunnel_label.cget("fg")
                # Toggle between visible (orange) and hidden (background color)
                new_fg = self.BG_COLOR if current_fg == self.SYSTEM_COLOR else self.SYSTEM_COLOR
                self.tunnel_label.config(fg=new_fg)
                # Slow blink: 1000ms (1 second) interval
                self.root.after(1000, blink)
        blink()

    def update_status(self, text, led_color):
        """Update status text and LED indicator.

        Args:
            text: Status text to display
            led_color: LED color - 'red', 'yellow', or 'green'
        """
        led_colors = {
            'red': '#ff5555',
            'yellow': '#ffb86c',
            'green': '#50fa7b'
        }
        self.led_indicator.config(fg=led_colors.get(led_color, '#ffb86c'))
        self.status_label.config(text=text)

    def on_typing(self, event):
        """Handle typing event - send typing notification to server."""
        if not self.socket or not self.username:
            return

        # Rate limit: only send every 3 seconds
        current_time = time.time()
        if current_time - self.last_typing_sent < 3:
            return

        try:
            self.socket.sendall(f"TYPING:{self.username}\n".encode())
            self.last_typing_sent = current_time
        except:
            pass

    def update_typing_display(self):
        """Update typing indicator with blinking animation."""
        current_time = time.time()

        # Remove expired typing indicators (>5 seconds old)
        expired = [user for user, timestamp in self.typing_users.items()
                   if current_time - timestamp > 5]
        for user in expired:
            del self.typing_users[user]

        # Update status bar with typing users
        if self.typing_users:
            # Cycle through blink states: 0=".", 1="..", 2="..."
            self.blink_state = (self.blink_state + 1) % 3
            dots = "." * (self.blink_state + 1)

            typing_list = list(self.typing_users.keys())
            if len(typing_list) == 1:
                status_text = f"{typing_list[0]} IS TYPING{dots}"
            elif len(typing_list) == 2:
                status_text = f"{typing_list[0]} AND {typing_list[1]} ARE TYPING{dots}"
            else:
                status_text = f"{len(typing_list)} USERS ARE TYPING{dots}"

            self.update_status(status_text, 'yellow')
        else:
            self.update_status("CONNECTED", 'green')

        # Schedule next update
        if self.running:
            self.typing_timer = self.root.after(500, self.update_typing_display)

    def display_message(self, message, tag="text", username=None, is_history=False):
        """Display message in chat window with right-aligned timestamp.

        Args:
            message: The message text
            tag: Color tag for the message
            username: Username to display (if None, extracts from message or uses "SYSTEM")
            is_history: True if this is a history message (don't update timestamp)
        """
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")  # Remove seconds

        # Calculate padding for right-aligned timestamp
        # Target width: 70 characters (fits nicely in 700px window with Courier 9)
        timestamp_str = f"[{timestamp}]"
        target_width = 70

        if username:
            # Oh-my-zsh terminal style: ┌─[username@shnet][HH:MM]
            #                            ~$ message goes here

            # Check if user is anonymous - use RED color if they are
            is_anon = self.users.get(username, False)
            if is_anon:
                user_color = self.ANON_COLOR
            else:
                user_color = self.get_user_color(username)

            user_tag = f"user_{username}"
            if user_tag not in self.chat_display.tag_names():
                self.chat_display.tag_config(user_tag, foreground=user_color)
            else:
                # Update color in case anon status changed
                self.chat_display.tag_config(user_tag, foreground=user_color)

            # First line: ┌─[username@shnet][HH:MM]
            self.chat_display.insert(tk.END, "┌─[", "prompt")
            self.chat_display.insert(tk.END, f"{username}", user_tag)
            self.chat_display.insert(tk.END, "@shnet", "prompt")
            self.chat_display.insert(tk.END, "]", "prompt")
            self.chat_display.insert(tk.END, f"[{timestamp}]\n", "time")

            # Second line: ~$ message
            self.chat_display.insert(tk.END, "~$ ", "prompt")
            self.chat_display.insert(tk.END, f"{message}\n", "text")
        else:
            # System message format with retro symbols
            # Add retro prefix: ►►►
            prefix = "►►► "
            content = prefix + message
            content_length = len(content)
            padding_needed = target_width - content_length - len(timestamp_str)

            # Ensure at least 2 spaces before timestamp
            if padding_needed < 2:
                padding_needed = 2

            padding = " " * padding_needed

            self.chat_display.insert(tk.END, "►►► ", "prompt")
            self.chat_display.insert(tk.END, message, tag)
            self.chat_display.insert(tk.END, padding, "text")
            self.chat_display.insert(tk.END, f"{timestamp_str}\n", "time")

        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def update_user_list(self, users):
        """Update the user list."""
        self.user_listbox.delete(0, tk.END)
        # Don't overwrite self.users dict - it contains anon status info
        # Just update the display

        for user in sorted(users):
            prefix = ">" if user == self.username else " "
            self.user_listbox.insert(tk.END, f" {prefix} {user}")

    def send_message(self):
        """Send a message."""
        message = self.message_entry.get().strip()
        if not message or not self.socket:
            return

        try:
            # Check if it's a DM (/msg username message)
            if message.startswith('/msg '):
                parts = message[5:].split(' ', 1)
                if len(parts) == 2:
                    recipient, dm_message = parts
                    self.socket.send(f'DM:{recipient}:{dm_message}\n'.encode('utf-8'))
                    self.display_message(f"[DM to {recipient}] {dm_message}", "dm")
                else:
                    self.display_message(">> Usage: /msg username message", "system")
            else:
                # Group message
                self.socket.send(f'MSG:{message}\n'.encode('utf-8'))
                self.display_message(message, "text", username=self.username)

            self.message_entry.delete(0, tk.END)

        except Exception as e:
            # Don't display errors in chat window - only in status bar
            self.status_label.config(text=f">> Error: {e}")

    def receive_messages(self):
        """Receive messages from server."""
        buffer = ""

        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.process_message(line.strip())

            except Exception as e:
                if self.running:
                    # Show connection errors in status bar only, not chat window
                    self.update_status("CONNECTION ERROR", 'red')
                break

        if self.running and not self.is_hidden:
            # Only show disconnect message if we're not just hidden
            self.display_message("SYSTEM: Disconnected from server", "system")
            self.update_status("DISCONNECTED", 'red')

    def process_message(self, message):
        """Process incoming message from server."""
        if message.startswith('WELCOME:'):
            # Don't show in chat, only update status bar
            self.update_status(f"CONNECTED AS {self.username.upper()}", 'green')

        elif message.startswith('USERLIST:'):
            # Format: USERLIST:user1:0,user2:1,user3:0  (0=normal, 1=anon)
            user_data = message[9:].split(',')
            users_dict = {}
            for item in user_data:
                if ':' in item:
                    user, is_anon = item.split(':', 1)
                    users_dict[user] = (is_anon == '1')
                else:
                    users_dict[item] = False  # Fallback for old format
            self.users = users_dict
            self.update_user_list(list(users_dict.keys()))

        elif message.startswith('JOIN:'):
            # Format: JOIN:username:is_anon
            parts = message[5:].split(':')
            username = parts[0]
            is_anon = (parts[1] == '1') if len(parts) > 1 else False
            self.users[username] = is_anon
            anon_label = " (ANON)" if is_anon else ""
            self.display_message(f"SYSTEM: {username}{anon_label} has joined", "system")

        elif message.startswith('HISTORY:'):
            # Format: HISTORY:username:timestamp:message
            parts = message[8:].split(':', 2)
            if len(parts) == 3:
                username, timestamp, msg = parts
                self.display_message(msg, "text", username=username, is_history=True)

        elif message.startswith('LEAVE:'):
            username = message[6:]
            self.display_message(f"SYSTEM: {username} has left", "system")

        elif message.startswith('MSG:'):
            # Format: MSG:username:message
            parts = message[4:].split(':', 1)
            if len(parts) == 2:
                username, msg = parts
                self.display_message(msg, "text", username=username)

        elif message.startswith('DM:'):
            # Format: DM:sender:message
            parts = message[3:].split(':', 1)
            if len(parts) == 2:
                sender, msg = parts
                self.display_message(f"[DM from {sender}] {msg}", "dm")

        elif message.startswith('OFFLINE:'):
            # Format: OFFLINE:sender:timestamp:message
            parts = message[8:].split(':', 2)
            if len(parts) == 3:
                sender, timestamp, msg = parts
                self.display_message(f"[OFFLINE MSG from {sender}] {msg}", "dm")

        elif message.startswith('INFO:'):
            # Show INFO messages in status bar, not chat window
            self.update_status(message[5:].upper(), 'yellow')

        elif message.startswith('ERROR:'):
            # Show ERROR messages in status bar only, not chat window
            self.update_status(f"ERROR: {message[6:].upper()}", 'red')

        elif message.startswith('TYPING:'):
            # Format: TYPING:username
            username = message[7:]
            # Don't show our own typing indicator
            if username != self.username:
                self.typing_users[username] = time.time()

        elif message.startswith('DM_INBOX:'):
            # Store response for inbox UI
            with self.response_lock:
                self.pending_responses['DM_INBOX'] = message[9:]

        elif message.startswith('DM_CONVERSATION:'):
            # Store response for inbox UI
            with self.response_lock:
                self.pending_responses['DM_CONVERSATION'] = message[16:]

        elif message.startswith('DM_MARKED_READ:'):
            # Acknowledge read status update
            with self.response_lock:
                self.pending_responses['DM_MARKED_READ'] = True

        elif message.startswith('DM_SENT:'):
            # DM sent confirmation
            self.update_status(message[8:], 'green')

    def connect(self, username, password, is_anon):
        """Connect to the chat server with authentication."""
        self.username = username
        self.password = password
        self.is_anon = is_anon

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.running = True

            # Wait for auth request
            data = self.socket.recv(1024).decode('utf-8')

            if 'AUTH_REQUIRED' not in data:
                self.socket.close()
                return False, "Server error: No auth request"

            # Send authentication
            if is_anon:
                auth_msg = f'AUTH_ANON:{username}\n'
            else:
                auth_msg = f'AUTH:{username}:{password}\n'

            self.socket.send(auth_msg.encode('utf-8'))

            # Check response
            response = self.socket.recv(1024).decode('utf-8')

            if 'AUTH_FAILED' in response:
                self.socket.close()
                error_msg = response.split(':', 1)[1] if ':' in response else "Authentication failed"
                return False, error_msg

            if 'WELCOME' in response:
                # Parse: WELCOME:username:token:is_anon
                parts = response.split(':')
                if len(parts) >= 4:
                    self.token = parts[2]
                    self.is_anon = parts[3].strip() == 'True'

                # Hide inbox button for anonymous users
                if self.is_anon and hasattr(self, 'inbox_btn'):
                    self.inbox_btn.pack_forget()

            # Start receive thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            # Start typing indicator update loop
            self.update_typing_display()

            return True, "Connected"

        except Exception as e:
            # Show connection error in status bar only
            self.update_status(f"CONNECTION FAILED", 'red')
            return False, str(e)

    def request_inbox(self):
        """Request inbox data from server."""
        if not self.socket:
            return None

        # Clear previous response
        with self.response_lock:
            self.pending_responses.pop('DM_INBOX', None)

        # Send request
        try:
            self.socket.send(b'DM_INBOX:\n')
        except:
            return None

        # Wait for response (with timeout)
        for _ in range(20):  # Wait up to 2 seconds
            time.sleep(0.1)
            with self.response_lock:
                if 'DM_INBOX' in self.pending_responses:
                    data = self.pending_responses.pop('DM_INBOX')
                    return json.loads(data) if data else []

        return None

    def request_conversation(self, other_user):
        """Request conversation with another user."""
        if not self.socket:
            return None

        # Clear previous response
        with self.response_lock:
            self.pending_responses.pop('DM_CONVERSATION', None)

        # Send request
        try:
            self.socket.send(f'DM_CONVERSATION:{other_user}\n'.encode('utf-8'))
        except:
            return None

        # Wait for response
        for _ in range(20):
            time.sleep(0.1)
            with self.response_lock:
                if 'DM_CONVERSATION' in self.pending_responses:
                    data = self.pending_responses.pop('DM_CONVERSATION')
                    return json.loads(data) if data else []

        return None

    def mark_conversation_read(self, other_user):
        """Mark conversation as read."""
        if not self.socket:
            return

        try:
            self.socket.send(f'DM_MARK_READ:{other_user}\n'.encode('utf-8'))
        except:
            pass

    def send_dm(self, recipient, message):
        """Send a direct message."""
        if not self.socket:
            return False

        try:
            self.socket.send(f'DM:{recipient}:{message}\n'.encode('utf-8'))
            return True
        except:
            return False

    def show_inbox(self):
        """Show DM inbox."""
        inbox = InboxUI(self.root, self)
        inbox.show_inbox()

    def _on_abort(self):
        """Handle ABORT button click."""
        if self.exit_callback:
            self.exit_callback()
        else:
            self.disconnect()

    def hide(self):
        """Hide chat (when switching to operations) but keep connection alive."""
        self.is_hidden = True

    def show(self):
        """Show chat again (when returning from operations)."""
        self.is_hidden = False

    def disconnect(self):
        """Disconnect from server."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        # Only destroy if root is a Toplevel/Tk window
        if isinstance(self.root, (tk.Tk, tk.Toplevel)):
            self.root.destroy()


def show_login_dialog(parent):
    """Show login dialog to get username."""
    dialog = tk.Toplevel(parent)
    dialog.title("Enter Chat")
    dialog.configure(bg="#282a36")
    dialog.geometry("350x180")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    # Center dialog
    parent.update_idletasks()
    dialog.update_idletasks()

    try:
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 175
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 90
        dialog.geometry(f"350x180+{x}+{y}")
    except:
        # If centering fails, just show at default position
        pass

    # Content
    tk.Label(
        dialog,
        text="░▒▓█ SECURE CHAT █▓▒░",
        font=("Courier", 12, "bold"),
        bg="#282a36",
        fg="#8be9fd"
    ).pack(pady=(20, 10))

    tk.Label(
        dialog,
        text="Enter your handle:",
        font=("Courier", 10),
        bg="#282a36",
        fg="#50fa7b"
    ).pack(pady=5)

    username_entry = tk.Entry(
        dialog,
        font=("Courier", 11),
        bg="#44475a",
        fg="#f8f8f2",
        insertbackground="#f8f8f2",
        width=25
    )
    username_entry.pack(pady=10)
    username_entry.focus()

    result = [None]

    def on_ok():
        username = username_entry.get().strip()
        if username:
            result[0] = username
            dialog.destroy()

    username_entry.bind('<Return>', lambda e: on_ok())

    btn = tk.Button(
        dialog,
        text="[ CONNECT ]",
        command=on_ok,
        font=("Courier", 10, "bold"),
        bg="#bd93f9",
        fg="#282a36",
        activebackground="#ff79c6",
        padx=20,
        pady=5,
        relief=tk.RAISED,
        bd=3
    )
    btn.pack(pady=10)

    parent.wait_window(dialog)
    return result[0]
