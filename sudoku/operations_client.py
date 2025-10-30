"""Operations Wiki Client - Retro Cyberpunk Theme"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import socket
import json
from typing import Optional, Callable


class OperationsClient:
    """Operations wiki/forum client with retro cyberpunk theme."""

    def __init__(self, root, chat_socket, username, exit_callback=None, chat_callback=None):
        self.root = root
        self.socket = chat_socket  # Reuse chat socket
        self.username = username
        self.exit_callback = exit_callback
        self.chat_callback = chat_callback  # Callback to return to chat
        self.current_view = "list"  # list, thread
        self.current_operation = None

        # Retro Cyberpunk colors
        self.BG_COLOR = "#0a0e27"  # Dark blue-black
        self.PANEL_COLOR = "#1a1f3a"  # Slightly lighter panel
        self.ACCENT_COLOR = "#00ff41"  # Matrix green
        self.SECONDARY_COLOR = "#ff006e"  # Cyberpunk pink
        self.TEXT_COLOR = "#00d9ff"  # Cyan text
        self.BUTTON_COLOR = "#7b2cbf"  # Purple button
        self.ERROR_COLOR = "#ff006e"  # Pink for errors
        self.SUCCESS_COLOR = "#00ff41"  # Green for success

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

        # Header with buttons
        header_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        header_frame.pack(pady=(0, 10), fill=tk.X)

        # ABORT button
        abort_btn = self._create_button(
            header_frame, "ABORT", self._on_abort,
            bg="#8b0000", fg="#ffffff", width=8
        )
        abort_btn.pack(side=tk.LEFT, padx=5)

        # OPERATIONS button (current - highlighted)
        ops_btn = self._create_button(
            header_frame, "OPERATIONS", None,
            bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR, width=12
        )
        ops_btn.pack(side=tk.LEFT, padx=5)

        # CHAT button
        if self.chat_callback:
            chat_btn = self._create_button(
                header_frame, "CHAT", self.chat_callback,
                bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=8
            )
            chat_btn.pack(side=tk.LEFT, padx=5)

        # Title
        title = tk.Label(
            header_frame,
            text="░▒▓█ OPERATIONS DATABASE █▓▒░",
            font=("Courier", 12, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR
        )
        title.pack(side=tk.LEFT, expand=True)

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
        self.op_name_entry = tk.Entry(name_frame, font=("Courier", 9), bg=self.BG_COLOR,
                                       fg=self.ACCENT_COLOR, insertbackground=self.ACCENT_COLOR)
        self.op_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Password
        pass_frame = tk.Frame(form_frame, bg=self.PANEL_COLOR)
        pass_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(pass_frame, text="PASSWORD:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.op_pass_entry = tk.Entry(pass_frame, font=("Courier", 9), bg=self.BG_COLOR,
                                       fg=self.ACCENT_COLOR, insertbackground=self.ACCENT_COLOR, show="*")
        self.op_pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Description
        desc_frame = tk.Frame(form_frame, bg=self.PANEL_COLOR)
        desc_frame.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(desc_frame, text="DESCRIPTION:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR, width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.op_desc_entry = tk.Entry(desc_frame, font=("Courier", 9), bg=self.BG_COLOR,
                                       fg=self.ACCENT_COLOR, insertbackground=self.ACCENT_COLOR)
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

        tk.Label(
            list_frame,
            text="[ AVAILABLE OPERATIONS ]",
            font=("Courier", 10, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        ).pack(pady=5)

        # Scrollable list
        list_container = tk.Frame(list_frame, bg=self.PANEL_COLOR)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.ops_listbox = tk.Listbox(
            list_container,
            font=("Courier", 9),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            selectbackground=self.BUTTON_COLOR,
            selectforeground=self.ACCENT_COLOR,
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT,
            highlightthickness=0,
            bd=0
        )
        self.ops_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.ops_listbox.yview)

        # Access button
        access_btn = self._create_button(
            list_frame, "[ ACCESS OPERATION ]", self._access_operation,
            bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR
        )
        access_btn.pack(pady=10)

        # Load operations
        self._load_operations()

    def show_operation_thread(self, op_name, op_info):
        """Show operation thread/forum page."""
        self.current_view = "thread"
        self.current_operation = op_name
        self.clear_main_frame()

        # Header with buttons
        header_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        header_frame.pack(pady=(0, 10), fill=tk.X)

        # ABORT button
        abort_btn = self._create_button(
            header_frame, "ABORT", self._on_abort,
            bg="#8b0000", fg="#ffffff", width=8
        )
        abort_btn.pack(side=tk.LEFT, padx=5)

        # OPERATIONS button
        ops_btn = self._create_button(
            header_frame, "OPERATIONS", self.show_operations_list,
            bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=12
        )
        ops_btn.pack(side=tk.LEFT, padx=5)

        # CHAT button
        if self.chat_callback:
            chat_btn = self._create_button(
                header_frame, "CHAT", self.chat_callback,
                bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, width=8
            )
            chat_btn.pack(side=tk.LEFT, padx=5)

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

        # Post form
        form_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                              highlightbackground=self.ACCENT_COLOR, highlightthickness=2)
        form_frame.pack(pady=5, fill=tk.X)

        tk.Label(
            form_frame,
            text="[ NEW POST ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.SECONDARY_COLOR
        ).pack(pady=5)

        # Comment
        comment_frame = tk.Frame(form_frame, bg=self.PANEL_COLOR)
        comment_frame.pack(pady=5, padx=10, fill=tk.BOTH)
        tk.Label(comment_frame, text="COMMENT:", font=("Courier", 9), bg=self.PANEL_COLOR,
                 fg=self.TEXT_COLOR).pack(anchor=tk.W)
        self.comment_text = tk.Text(comment_frame, font=("Courier", 9), bg=self.BG_COLOR,
                                     fg=self.ACCENT_COLOR, insertbackground=self.ACCENT_COLOR,
                                     height=3, wrap=tk.WORD)
        self.comment_text.pack(fill=tk.BOTH, expand=True)

        # File upload
        file_frame = tk.Frame(form_frame, bg=self.PANEL_COLOR)
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
            form_frame, "[ POST ]", self._add_post,
            bg=self.BUTTON_COLOR, fg=self.ACCENT_COLOR
        )
        post_btn.pack(pady=10)

        # Posts display
        posts_frame = tk.Frame(self.main_frame, bg=self.PANEL_COLOR, relief=tk.RIDGE, bd=3,
                               highlightbackground=self.TEXT_COLOR, highlightthickness=2)
        posts_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        tk.Label(
            posts_frame,
            text="[ THREAD POSTS ]",
            font=("Courier", 9, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.TEXT_COLOR
        ).pack(pady=5)

        self.posts_display = scrolledtext.ScrolledText(
            posts_frame,
            font=("Courier", 9),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            insertbackground=self.ACCENT_COLOR,
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.posts_display.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Configure text tags
        self.posts_display.tag_config("user", foreground=self.SECONDARY_COLOR, font=("Courier", 9, "bold"))
        self.posts_display.tag_config("time", foreground=self.TEXT_COLOR, font=("Courier", 7))
        self.posts_display.tag_config("text", foreground=self.ACCENT_COLOR)

        # Load posts
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

    def _load_operations(self):
        """Load operations list from server."""
        try:
            self.socket.send(b'OP_LIST:\n')

            # Set a timeout to prevent freezing
            self.socket.settimeout(5.0)

            # Receive response with timeout
            response = self.socket.recv(8192).decode('utf-8').strip()

            # Reset to blocking
            self.socket.settimeout(None)

            if response.startswith('OP_LIST:'):
                data = response[8:]
                operations = json.loads(data)

                self.ops_listbox.delete(0, tk.END)
                self.operations_data = {}

                for op in operations:
                    display = f">> {op['name'].upper():20s} | by {op['creator']:10s} | {op['created_at'][:10]}"
                    self.ops_listbox.insert(tk.END, display)
                    self.operations_data[display] = op
            else:
                self._show_message("No response from server", self.ERROR_COLOR)

        except socket.timeout:
            self._show_message("Server timeout - is server running?", self.ERROR_COLOR)
            self.socket.settimeout(None)
        except Exception as e:
            print(f"Error loading operations: {e}")
            self._show_message(f"Error: {e}", self.ERROR_COLOR)

    def _create_operation(self):
        """Create new operation."""
        op_name = self.op_name_entry.get().strip()
        op_pass = self.op_pass_entry.get()
        op_desc = self.op_desc_entry.get().strip()

        if not op_name or not op_pass:
            self._show_message("Operation name and password required", self.ERROR_COLOR)
            return

        try:
            message = f'OP_CREATE:{op_name}:{op_pass}:{op_desc}\n'
            self.socket.settimeout(5.0)
            self.socket.send(message.encode('utf-8'))
            response = self.socket.recv(1024).decode('utf-8').strip()
            self.socket.settimeout(None)

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

        except socket.timeout:
            self._show_message("Server timeout", self.ERROR_COLOR)
            self.socket.settimeout(None)
        except Exception as e:
            self._show_message(f"Error: {e}", self.ERROR_COLOR)
            self.socket.settimeout(None)

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
            message = f'OP_VERIFY:{op["name"]}:{password}\n'
            self.socket.settimeout(5.0)
            self.socket.send(message.encode('utf-8'))
            response = self.socket.recv(1024).decode('utf-8').strip()

            if response.startswith('OP_VERIFY_RESULT:'):
                valid = response[17:] == 'True'

                if valid:
                    # Get operation info
                    self.socket.send(f'OP_INFO:{op["name"]}\n'.encode('utf-8'))
                    response = self.socket.recv(1024).decode('utf-8').strip()
                    self.socket.settimeout(None)

                    op_info = None
                    if response.startswith('OP_INFO:'):
                        data = response[8:]
                        op_info = json.loads(data) if data != "null" else None

                    self.show_operation_thread(op['name'], op_info)
                else:
                    self.socket.settimeout(None)
                    self._show_message("✗ Invalid password", self.ERROR_COLOR)

        except socket.timeout:
            self._show_message("Server timeout", self.ERROR_COLOR)
            self.socket.settimeout(None)
        except Exception as e:
            self._show_message(f"Error: {e}", self.ERROR_COLOR)
            self.socket.settimeout(None)

    def _load_posts(self):
        """Load posts for current operation."""
        if not self.current_operation:
            return

        try:
            self.socket.settimeout(5.0)
            self.socket.send(f'OP_POSTS:{self.current_operation}\n'.encode('utf-8'))
            response = self.socket.recv(8192).decode('utf-8').strip()
            self.socket.settimeout(None)

            if response.startswith('OP_POSTS:'):
                data = response[9:]
                posts = json.loads(data)

                self.posts_display.config(state=tk.NORMAL)
                self.posts_display.delete('1.0', tk.END)

                if not posts:
                    self.posts_display.insert(tk.END, "No posts yet. Be the first to contribute!\n", "text")
                else:
                    for post in posts:
                        # User and timestamp
                        self.posts_display.insert(tk.END, f">> {post['username']}", "user")
                        self.posts_display.insert(tk.END, f" [{post['created_at']}]\n", "time")
                        # Comment
                        self.posts_display.insert(tk.END, f"{post['comment']}\n", "text")
                        # Filename if present with download link
                        if post.get('filename'):
                            file_tag = f"file_{post['id']}"
                            self.posts_display.insert(tk.END, f"📎 FILE: ", "time")
                            self.posts_display.insert(tk.END, f"{post['filename']}", file_tag)
                            self.posts_display.insert(tk.END, f" [click to download]\n", "time")

                            # Make filename clickable
                            self.posts_display.tag_config(file_tag, foreground=self.SECONDARY_COLOR, underline=1)
                            self.posts_display.tag_bind(file_tag, "<Button-1>",
                                                        lambda e, p=post: self._download_file(p))
                            self.posts_display.tag_bind(file_tag, "<Enter>",
                                                        lambda e, t=file_tag: self.posts_display.config(cursor="hand2"))
                            self.posts_display.tag_bind(file_tag, "<Leave>",
                                                        lambda e: self.posts_display.config(cursor=""))

                        self.posts_display.insert(tk.END, "─" * 70 + "\n", "time")

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
                message = f'OP_POST:{self.current_operation}:{comment}:{filename}:{file_data}\n'
                print(f"CLIENT DEBUG: Sending with file - op={self.current_operation}, comment_len={len(comment)}, filename={filename}, file_data_len={len(file_data)}")
            else:
                message = f'OP_POST:{self.current_operation}:{comment}::\n'
                print(f"CLIENT DEBUG: Sending without file - op={self.current_operation}, comment_len={len(comment)}")

            self.socket.settimeout(10.0)  # Longer timeout for file uploads
            self.socket.sendall(message.encode('utf-8'))  # Use sendall to ensure all data is sent
            response = self.socket.recv(1024).decode('utf-8').strip()
            self.socket.settimeout(None)

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

        except socket.timeout:
            self._show_message("Server timeout - post may be too large", self.ERROR_COLOR)
            self.socket.settimeout(None)
        except Exception as e:
            self._show_message(f"Error: {e}", self.ERROR_COLOR)
            self.socket.settimeout(None)

    def _download_file(self, post):
        """Download file from post."""
        try:
            import os
            import base64
            from tkinter import filedialog

            # Request file data from server
            self.socket.settimeout(30.0)  # Longer timeout for large files
            self.socket.sendall(f'OP_FILE:{post["id"]}\n'.encode('utf-8'))

            # Read response in chunks until we get the complete message
            buffer = b''
            while b'\n' not in buffer:
                chunk = self.socket.recv(65536)
                if not chunk:
                    break
                buffer += chunk

            response = buffer.decode('utf-8').strip()
            self.socket.settimeout(None)

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

        except socket.timeout:
            self._show_message("Server timeout downloading file", self.ERROR_COLOR)
            self.socket.settimeout(None)
        except Exception as e:
            self._show_message(f"✗ Error: {e}", self.ERROR_COLOR)
            self.socket.settimeout(None)

    def _ask_password(self, op_name):
        """Show password dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Access {op_name}")
        dialog.configure(bg=self.BG_COLOR)
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=f"Enter password for:\n{op_name.upper()}",
            font=("Courier", 10, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR
        ).pack(pady=20)

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
        btn.pack(pady=10)

        self.root.wait_window(dialog)
        return result[0]

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

    def _on_abort(self):
        """Handle abort button."""
        if self.exit_callback:
            self.exit_callback()
