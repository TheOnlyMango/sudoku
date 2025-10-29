"""Secret Chat Client - 90s Hacker mIRC Style"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading
import time
from datetime import datetime


class ChatClient:
    """90s style chat client with Dracula theme."""

    def __init__(self, root, server_host='100.115.233.16', server_port=7331):
        self.root = root
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.username = None
        self.running = False
        self.users = set()

        # Dracula colors with 90s hacker twist
        self.BG_COLOR = "#282a36"
        self.PANEL_COLOR = "#1a1c24"  # Darker for panels
        self.TEXT_COLOR = "#50fa7b"  # Green terminal text
        self.USER_COLOR = "#8be9fd"  # Cyan for usernames
        self.SYSTEM_COLOR = "#ffb86c"  # Orange for system messages
        self.DM_COLOR = "#ff79c6"  # Pink for DMs
        self.INPUT_BG = "#44475a"
        self.BUTTON_COLOR = "#bd93f9"

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

        # Header with 90s ASCII art
        header = tk.Label(
            main_frame,
            text="░▒▓█ SECURE CHAT █▓▒░\n>> ENCRYPTED TUNNEL ESTABLISHED <<",
            font=("Courier", 10, "bold"),
            bg=self.BG_COLOR,
            fg=self.SYSTEM_COLOR
        )
        header.pack(pady=(0, 10))

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

        # User listbox
        self.user_listbox = tk.Listbox(
            user_panel,
            font=("Courier", 9),
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

        # Chat display - ScrolledText for auto-scroll
        self.chat_display = scrolledtext.ScrolledText(
            chat_panel,
            font=("Courier", 9),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.chat_display.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Configure text tags for colors
        self.chat_display.tag_config("system", foreground=self.SYSTEM_COLOR)
        self.chat_display.tag_config("user", foreground=self.USER_COLOR)
        self.chat_display.tag_config("dm", foreground=self.DM_COLOR)
        self.chat_display.tag_config("text", foreground=self.TEXT_COLOR)

        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        input_frame.pack(fill=tk.X, pady=(10, 0))

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

        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.INPUT_BG, relief=tk.RIDGE, bd=2)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = tk.Label(
            status_frame,
            text=">> Connecting...",
            font=("Courier", 8),
            bg=self.INPUT_BG,
            fg=self.SYSTEM_COLOR,
            anchor=tk.W,
            padx=5,
            pady=3
        )
        self.status_label.pack(fill=tk.X)

        # Focus on input
        self.message_entry.focus()

    def display_message(self, message, tag="text"):
        """Display message in chat window."""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.chat_display.insert(tk.END, f"[{timestamp}] ", "system")
        self.chat_display.insert(tk.END, f"{message}\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def update_user_list(self, users):
        """Update the user list."""
        self.user_listbox.delete(0, tk.END)
        self.users = set(users)

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
                    self.display_message("Usage: /msg username message", "system")
            else:
                # Group message
                self.socket.send(f'MSG:{message}\n'.encode('utf-8'))
                self.display_message(f"<{self.username}> {message}", "user")

            self.message_entry.delete(0, tk.END)

        except Exception as e:
            self.display_message(f"Error sending message: {e}", "system")

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
                    self.display_message(f"Connection error: {e}", "system")
                break

        if self.running:
            self.display_message(">> Disconnected from server", "system")
            self.status_label.config(text=">> Disconnected")

    def process_message(self, message):
        """Process incoming message from server."""
        if message.startswith('WELCOME:'):
            self.display_message(f">> Connected as {message[8:]}", "system")
            self.status_label.config(text=f">> Connected as {self.username}")

        elif message.startswith('USERLIST:'):
            users = message[9:].split(',')
            self.update_user_list(users)

        elif message.startswith('JOIN:'):
            username = message[5:]
            self.display_message(f">> {username} has joined", "system")

        elif message.startswith('LEAVE:'):
            username = message[6:]
            self.display_message(f">> {username} has left", "system")

        elif message.startswith('MSG:'):
            # Format: MSG:username:message
            parts = message[4:].split(':', 1)
            if len(parts) == 2:
                username, msg = parts
                self.display_message(f"<{username}> {msg}", "user")

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
            self.display_message(f">> {message[5:]}", "system")

    def connect(self, username):
        """Connect to the chat server."""
        self.username = username

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.running = True

            # Wait for username prompt
            data = self.socket.recv(1024).decode('utf-8')

            # Send username
            self.socket.send((username + '\n').encode('utf-8'))

            # Check if accepted
            response = self.socket.recv(1024).decode('utf-8')
            if 'USERNAME_TAKEN' in response:
                self.socket.close()
                return False

            # Start receive thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            return True

        except Exception as e:
            self.display_message(f">> Connection failed: {e}", "system")
            self.status_label.config(text=">> Connection failed")
            return False

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
