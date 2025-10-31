#!/usr/bin/env python3
"""
Chat Server GUI - Terminal-style interface with graceful shutdown
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
from io import StringIO
from datetime import datetime
from chat_server_improved import ImprovedChatServer


class ServerGUI:
    """Terminal-style GUI for chat server management."""

    def __init__(self):
        """Initialize server GUI."""
        self.root = tk.Tk()
        self.root.title("SHNet Secure Terminal - Server Console")
        self.root.geometry("900x600")
        self.root.configure(bg='#1e1e1e')

        self.server = None
        self.server_thread = None
        self.running = False

        # Redirect stdout to capture server logs
        self.original_stdout = sys.stdout
        self.log_buffer = StringIO()

        self.setup_ui()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Set up the user interface."""
        # Header
        header_frame = tk.Frame(self.root, bg='#1e1e1e')
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        title = tk.Label(
            header_frame,
            text="┌─[ SHNet Secure Terminal - Server Console ]─┐",
            font=('Courier New', 14, 'bold'),
            fg='#50fa7b',
            bg='#1e1e1e'
        )
        title.pack()

        # Server status
        self.status_label = tk.Label(
            header_frame,
            text="[ SERVER OFFLINE ]",
            font=('Courier New', 10),
            fg='#ff5555',
            bg='#1e1e1e'
        )
        self.status_label.pack(pady=5)

        # Terminal output
        terminal_frame = tk.Frame(self.root, bg='#1e1e1e')
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        terminal_label = tk.Label(
            terminal_frame,
            text="[ SERVER LOG ]",
            font=('Courier New', 9),
            fg='#6272a4',
            bg='#1e1e1e',
            anchor='w'
        )
        terminal_label.pack(fill=tk.X)

        self.terminal = scrolledtext.ScrolledText(
            terminal_frame,
            font=('Courier New', 9),
            bg='#282a36',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            relief=tk.SUNKEN,
            bd=2,
            wrap=tk.WORD
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)
        self.terminal.config(state=tk.DISABLED)

        # Control buttons
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_btn = tk.Button(
            button_frame,
            text="START SERVER",
            command=self.start_server,
            font=('Courier New', 11, 'bold'),
            bg='#44475a',
            fg='#50fa7b',
            activebackground='#6272a4',
            activeforeground='#50fa7b',
            relief=tk.RAISED,
            bd=2,
            width=20,
            height=2
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.stop_btn = tk.Button(
            button_frame,
            text="SHUTDOWN SERVER",
            command=self.stop_server,
            font=('Courier New', 11, 'bold'),
            bg='#44475a',
            fg='#ff5555',
            activebackground='#6272a4',
            activeforeground='#ff5555',
            relief=tk.RAISED,
            bd=2,
            width=20,
            height=2,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        clear_btn = tk.Button(
            button_frame,
            text="CLEAR LOG",
            command=self.clear_log,
            font=('Courier New', 11, 'bold'),
            bg='#44475a',
            fg='#f8f8f2',
            activebackground='#6272a4',
            activeforeground='#f8f8f2',
            relief=tk.RAISED,
            bd=2,
            width=15,
            height=2
        )
        clear_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Footer
        footer = tk.Label(
            self.root,
            text="[ Encrypted Connection • 90s Hacker Edition ]",
            font=('Courier New', 8),
            fg='#6272a4',
            bg='#1e1e1e'
        )
        footer.pack(side=tk.BOTTOM, pady=5)

        # Start log update loop
        self.update_log()

    def log_message(self, message: str, color: str = '#f8f8f2'):
        """Add message to terminal output."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, f'[{timestamp}] ', 'timestamp')
        self.terminal.insert(tk.END, f'{message}\n', 'message')
        self.terminal.tag_config('timestamp', foreground='#6272a4')
        self.terminal.tag_config('message', foreground=color)
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)

    def update_log(self):
        """Periodically check for new log messages."""
        # This will be called every 100ms to update the log
        self.root.after(100, self.update_log)

    def start_server(self):
        """Start the chat server in a background thread."""
        if self.running:
            return

        self.log_message("=== INITIALIZING SERVER ===", '#50fa7b')
        self.log_message("Starting SHNet Secure Terminal Server...", '#8be9fd')

        try:
            self.server = ImprovedChatServer()
            self.running = True

            # Start server in background thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()

            # Update UI
            self.status_label.config(text="[ SERVER ONLINE ]", fg='#50fa7b')
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            self.log_message("Server started successfully", '#50fa7b')
            self.log_message("Waiting for client connections...", '#8be9fd')

        except Exception as e:
            self.log_message(f"ERROR: Failed to start server: {e}", '#ff5555')
            self.running = False

    def _run_server(self):
        """Run the server (called in background thread)."""
        try:
            self.server.start()
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Server error: {e}", '#ff5555'))
        finally:
            self.running = False
            self.root.after(0, self._on_server_stopped)

    def stop_server(self):
        """Stop the chat server gracefully."""
        if not self.running or not self.server:
            return

        self.log_message("=== SHUTTING DOWN SERVER ===", '#ff5555')
        self.log_message("Archiving chat session...", '#8be9fd')
        self.log_message("Closing client connections...", '#8be9fd')

        try:
            self.running = False
            self.server.stop()

            self.log_message("Server shutdown complete", '#50fa7b')

        except Exception as e:
            self.log_message(f"ERROR during shutdown: {e}", '#ff5555')

        finally:
            self._on_server_stopped()

    def _on_server_stopped(self):
        """Update UI when server stops."""
        self.status_label.config(text="[ SERVER OFFLINE ]", fg='#ff5555')
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def clear_log(self):
        """Clear the terminal output."""
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)
        self.terminal.config(state=tk.DISABLED)
        self.log_message("Log cleared", '#6272a4')

    def on_closing(self):
        """Handle window close event."""
        if self.running:
            self.log_message("Closing window - shutting down server first...", '#ff5555')
            self.stop_server()

        # Wait a moment for shutdown to complete
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)

        self.root.destroy()

    def run(self):
        """Run the GUI application."""
        self.log_message("=== SHNet Server Console Started ===", '#50fa7b')
        self.log_message("Click START SERVER to begin accepting connections", '#8be9fd')
        self.root.mainloop()


def main():
    """Run the server GUI."""
    gui = ServerGUI()
    gui.run()


if __name__ == "__main__":
    main()
