"""Inbox UI - 90s Hacker Style DM Interface"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from datetime import datetime
import json
import time


class InboxUI:
    """90s hacker style inbox interface for direct messages."""

    def __init__(self, root, chat_client):
        """Initialize inbox UI.

        Args:
            root: Parent tkinter window
            chat_client: ChatClient instance for sending DM requests
        """
        self.root = root
        self.chat_client = chat_client
        self.inbox_window = None
        self.conversations = []
        self.current_conversation = None

        # Dracula colors with 90s hacker twist
        self.BG_COLOR = "#282a36"
        self.PANEL_COLOR = "#0a0e14"
        self.TEXT_COLOR = "#f8f8f2"
        self.UNREAD_COLOR = "#ff79c6"  # Pink for unread
        self.READ_COLOR = "#6272a4"  # Muted blue for read
        self.SYSTEM_COLOR = "#ffb86c"
        self.INPUT_BG = "#1a1f2e"
        self.BUTTON_COLOR = "#bd93f9"
        self.PROMPT_COLOR = "#6272a4"

    def show_inbox(self):
        """Display the inbox window."""
        # Create modal window
        self.inbox_window = tk.Toplevel(self.root)
        self.inbox_window.title("░▒▓█ INBOX █▓▒░")
        self.inbox_window.geometry("800x600")
        self.inbox_window.configure(bg=self.BG_COLOR)
        self.inbox_window.resizable(False, False)

        # Center the window
        self.inbox_window.update_idletasks()
        x = (self.inbox_window.winfo_screenwidth() // 2) - 400
        y = (self.inbox_window.winfo_screenheight() // 2) - 300
        self.inbox_window.geometry(f"800x600+{x}+{y}")

        # Header
        header_frame = tk.Frame(self.inbox_window, bg=self.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        title = tk.Label(
            header_frame,
            text="╔════════════════════════════════════════════════════════╗\n"
                 "║  ░▒▓█ D I R E C T  M E S S A G E  I N B O X █▓▒░  ║\n"
                 "╚════════════════════════════════════════════════════════╝",
            font=("Courier", 9, "bold"),
            bg=self.BG_COLOR,
            fg="#50fa7b",
            justify=tk.CENTER
        )
        title.pack()

        # Status line
        status_label = tk.Label(
            header_frame,
            text=f">> USER: {self.chat_client.username.upper()} | SECURE CONNECTION ESTABLISHED <<",
            font=("Courier", 8),
            bg=self.BG_COLOR,
            fg=self.PROMPT_COLOR
        )
        status_label.pack(pady=5)

        # Main content area
        content_frame = tk.Frame(self.inbox_window, bg=self.BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel - Conversations list
        left_frame = tk.Frame(content_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_frame.config(width=250)

        conv_header = tk.Label(
            left_frame,
            text="[ CONVERSATIONS ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg="#50fa7b"
        )
        conv_header.pack(pady=5)

        # Conversations listbox with scrollbar
        conv_scroll_frame = tk.Frame(left_frame, bg=self.PANEL_COLOR)
        conv_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        conv_scrollbar = tk.Scrollbar(conv_scroll_frame)
        conv_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.conv_listbox = tk.Listbox(
            conv_scroll_frame,
            font=("Courier", 9),
            bg="#1a1f2e",
            fg=self.TEXT_COLOR,
            selectbackground="#44475a",
            selectforeground="#f8f8f2",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            yscrollcommand=conv_scrollbar.set
        )
        self.conv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        conv_scrollbar.config(command=self.conv_listbox.yview)

        # Bind selection event
        self.conv_listbox.bind('<<ListboxSelect>>', self.on_conversation_select)

        # New message button
        new_msg_btn = tk.Button(
            left_frame,
            text="[ NEW MESSAGE ]",
            command=self.new_message,
            font=("Courier", 9, "bold"),
            bg="#7b2cbf",
            fg="#00ff41",
            activebackground="#00ff41",
            activeforeground="#7b2cbf",
            relief=tk.RAISED,
            bd=3,
            cursor="hand2"
        )
        new_msg_btn.pack(pady=5, padx=5, fill=tk.X)

        # Right panel - Message view
        right_frame = tk.Frame(content_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        msg_header = tk.Label(
            right_frame,
            text="[ MESSAGE THREAD ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg="#50fa7b"
        )
        msg_header.pack(pady=5)

        # Message display area
        self.message_display = scrolledtext.ScrolledText(
            right_frame,
            font=("Courier", 9),
            bg="#1a1f2e",
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.message_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure tags for message display
        self.message_display.tag_config("sent", foreground="#8be9fd")  # Cyan for sent
        self.message_display.tag_config("received", foreground="#ff79c6")  # Pink for received
        self.message_display.tag_config("time", foreground=self.PROMPT_COLOR)
        self.message_display.tag_config("prompt", foreground=self.PROMPT_COLOR)

        # Reply input area
        reply_frame = tk.Frame(right_frame, bg=self.PANEL_COLOR)
        reply_frame.pack(fill=tk.X, padx=5, pady=5)

        reply_label = tk.Label(
            reply_frame,
            text="REPLY >>>",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.PROMPT_COLOR
        )
        reply_label.pack(side=tk.LEFT, padx=5)

        self.reply_entry = tk.Entry(
            reply_frame,
            font=("Courier", 9),
            bg=self.INPUT_BG,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief=tk.FLAT,
            bd=2
        )
        self.reply_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.reply_entry.bind('<Return>', lambda e: self.send_reply())

        send_btn = tk.Button(
            reply_frame,
            text="[ SEND ]",
            command=self.send_reply,
            font=("Courier", 9, "bold"),
            bg="#50fa7b",
            fg="#282a36",
            activebackground="#00ff41",
            activeforeground="#282a36",
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
            width=10
        )
        send_btn.pack(side=tk.LEFT, padx=5)

        # Bottom buttons
        button_frame = tk.Frame(self.inbox_window, bg=self.BG_COLOR)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        refresh_btn = tk.Button(
            button_frame,
            text="[ REFRESH ]",
            command=self.load_inbox,
            font=("Courier", 9, "bold"),
            bg="#44475a",
            fg="#f8f8f2",
            activebackground="#6272a4",
            relief=tk.RAISED,
            bd=3,
            width=15
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(
            button_frame,
            text="[ CLOSE ]",
            command=self.inbox_window.destroy,
            font=("Courier", 9, "bold"),
            bg="#8b0000",
            fg="#f8f8f2",
            activebackground="#ff0000",
            relief=tk.RAISED,
            bd=3,
            width=15
        )
        close_btn.pack(side=tk.RIGHT, padx=5)

        # Footer
        footer = tk.Label(
            self.inbox_window,
            text="[ ENCRYPTED • SECURE • PRIVATE ]",
            font=("Courier", 8),
            bg=self.BG_COLOR,
            fg=self.PROMPT_COLOR
        )
        footer.pack(side=tk.BOTTOM, pady=5)

        # Load inbox data
        self.load_inbox()

    def load_inbox(self):
        """Request inbox data from server."""
        conversations = self.chat_client.request_inbox()

        if conversations is not None:
            self.conversations = conversations
            self.update_conversation_list()
        else:
            messagebox.showerror("Error", "Failed to load inbox")

    def update_conversation_list(self):
        """Update the conversations listbox."""
        self.conv_listbox.delete(0, tk.END)

        for conv in self.conversations:
            user = conv['user']
            unread = conv['unread']
            preview = conv['preview']

            # Format: [!] username (3) - preview
            if unread > 0:
                display = f"[!] {user} ({unread}) - {preview}"
                self.conv_listbox.insert(tk.END, display)
                # Make unread items appear bold by using a different foreground color
                self.conv_listbox.itemconfig(tk.END, fg=self.UNREAD_COLOR)
            else:
                display = f"    {user} - {preview}"
                self.conv_listbox.insert(tk.END, display)
                self.conv_listbox.itemconfig(tk.END, fg=self.READ_COLOR)

    def on_conversation_select(self, event):
        """Handle conversation selection."""
        selection = self.conv_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        conv = self.conversations[idx]
        self.current_conversation = conv['user']

        # Load conversation
        self.load_conversation(self.current_conversation)

        # Mark as read
        self.mark_conversation_read(self.current_conversation)

    def load_conversation(self, other_user):
        """Load conversation with another user."""
        messages = self.chat_client.request_conversation(other_user)

        if messages is not None:
            self.display_conversation(messages, other_user)
        else:
            messagebox.showerror("Error", "Failed to load conversation")

    def display_conversation(self, messages, other_user):
        """Display conversation messages."""
        self.message_display.config(state=tk.NORMAL)
        self.message_display.delete(1.0, tk.END)

        # Header
        self.message_display.insert(tk.END, "═" * 80 + "\n", "prompt")
        self.message_display.insert(tk.END, f"  CONVERSATION WITH: {other_user.upper()}\n", "received")
        self.message_display.insert(tk.END, "═" * 80 + "\n\n", "prompt")

        for msg in messages:
            sender = msg['sender']
            message = msg['message']
            timestamp = msg['timestamp']

            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M")
            except:
                time_str = timestamp[:5] if len(timestamp) >= 5 else timestamp

            # Determine if sent or received
            if sender == self.chat_client.username:
                # Sent message - align right-ish with prompt
                self.message_display.insert(tk.END, f"[{time_str}] ", "time")
                self.message_display.insert(tk.END, ">>> ", "prompt")
                self.message_display.insert(tk.END, f"{message}\n\n", "sent")
            else:
                # Received message
                self.message_display.insert(tk.END, f"[{time_str}] ", "time")
                self.message_display.insert(tk.END, f"[{sender}] ", "received")
                self.message_display.insert(tk.END, f"{message}\n\n", "text")

        self.message_display.see(tk.END)
        self.message_display.config(state=tk.DISABLED)

    def mark_conversation_read(self, other_user):
        """Mark conversation as read."""
        self.chat_client.mark_conversation_read(other_user)

        # Update local conversation list
        for conv in self.conversations:
            if conv['user'] == other_user:
                conv['unread'] = 0
        self.update_conversation_list()

    def send_reply(self):
        """Send a reply in the current conversation."""
        if not self.current_conversation:
            messagebox.showwarning("No Conversation", "Please select a conversation first")
            return

        message = self.reply_entry.get().strip()
        if not message:
            return

        if self.chat_client.send_dm(self.current_conversation, message):
            # Clear input
            self.reply_entry.delete(0, tk.END)

            # Reload conversation to show new message
            time.sleep(0.2)  # Brief delay for DB write
            self.load_conversation(self.current_conversation)
        else:
            messagebox.showerror("Error", "Failed to send message")

    def new_message(self):
        """Open dialog to send a new message to a user."""
        # Create new message dialog
        dialog = tk.Toplevel(self.inbox_window)
        dialog.title("New Message")
        dialog.geometry("400x250")
        dialog.configure(bg=self.BG_COLOR)
        dialog.resizable(False, False)
        dialog.transient(self.inbox_window)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 125
        dialog.geometry(f"400x250+{x}+{y}")

        # Header
        tk.Label(
            dialog,
            text="[ NEW MESSAGE ]",
            font=("Courier", 12, "bold"),
            bg=self.BG_COLOR,
            fg="#50fa7b"
        ).pack(pady=10)

        # Recipient field with autocomplete
        tk.Label(
            dialog,
            text="TO: @username",
            font=("Courier", 10),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        ).pack(anchor=tk.W, padx=20)

        # Get list of all registered users (non-anon)
        registered_users = [u for u, is_anon in self.chat_client.users.items() if not is_anon and u != self.chat_client.username]

        # Use Combobox for autocomplete
        recipient_entry = ttk.Combobox(
            dialog,
            values=sorted(registered_users),
            font=("Courier", 10),
            width=37
        )
        recipient_entry.pack(fill=tk.X, padx=20, pady=5)
        recipient_entry.focus()

        # Message field
        tk.Label(
            dialog,
            text="MESSAGE:",
            font=("Courier", 10),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        ).pack(anchor=tk.W, padx=20, pady=(10, 0))

        message_entry = tk.Text(
            dialog,
            font=("Courier", 10),
            bg=self.INPUT_BG,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief=tk.FLAT,
            bd=2,
            height=5,
            wrap=tk.WORD
        )
        message_entry.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.BG_COLOR)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        def send_new_message():
            recipient = recipient_entry.get().strip()
            message = message_entry.get(1.0, tk.END).strip()

            if not recipient or not message:
                messagebox.showwarning("Missing Info", "Please enter recipient and message")
                return

            if self.chat_client.send_dm(recipient, message):
                dialog.destroy()
                # Refresh inbox after brief delay
                time.sleep(0.2)
                self.load_inbox()
            else:
                messagebox.showerror("Error", "Failed to send message")

        send_btn = tk.Button(
            btn_frame,
            text="[ SEND ]",
            command=send_new_message,
            font=("Courier", 10, "bold"),
            bg="#50fa7b",
            fg="#282a36",
            activebackground="#00ff41",
            relief=tk.RAISED,
            bd=3,
            width=12
        )
        send_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            btn_frame,
            text="[ CANCEL ]",
            command=dialog.destroy,
            font=("Courier", 10, "bold"),
            bg="#8b0000",
            fg="#f8f8f2",
            activebackground="#ff0000",
            relief=tk.RAISED,
            bd=3,
            width=12
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
