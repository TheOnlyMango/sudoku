#!/usr/bin/env python3
"""Launch the chat client with authentication."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from chat.client.auth_ui import AuthUI
from chat.client.chat_client import ChatClient
from chat.client.operations_client import OperationsClient

class ChatApplication:
    """Main chat application with authentication and view management."""

    def __init__(self):
        """Initialize the chat application."""
        self.root = tk.Tk()
        self.root.title("SHNet Secure Chat")
        self.root.geometry("700x850")
        self.root.configure(bg='#282a36')

        # Components
        self.auth_ui = None
        self.chat_client = None
        self.operations_client = None
        self.current_view = None

        # Container for switching views
        self.main_container = tk.Frame(self.root, bg='#282a36')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Start with authentication
        self.show_auth()

    def show_auth(self):
        """Show authentication screen."""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Create auth UI
        self.auth_ui = AuthUI(
            self.main_container,
            on_success=self.on_auth_success
        )
        self.auth_ui.show_auth_screen()
        self.current_view = 'auth'

    def on_auth_success(self, username, password, is_anon):
        """Handle successful authentication."""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Create chat client
        self.chat_client = ChatClient(
            self.main_container,
            exit_callback=self.on_exit_chat,
            operations_callback=self.show_operations
        )
        self.chat_client.create_ui()

        # Connect to server
        self.chat_client.connect(username, password, is_anon)
        self.current_view = 'chat'

    def show_operations(self):
        """Show operations view."""
        if not self.chat_client or not self.chat_client.message_router:
            return

        # Hide chat
        if self.chat_client:
            for widget in self.main_container.winfo_children():
                widget.pack_forget()

        # Create or show operations client
        if not self.operations_client:
            self.operations_client = OperationsClient(
                self.main_container,
                self.chat_client.message_router,
                self.chat_client.username,
                back_callback=self.show_chat
            )
            self.operations_client.create_ui()
        else:
            # Re-show operations
            for widget in self.main_container.winfo_children():
                if hasattr(widget, 'master') and widget.master == self.main_container:
                    widget.pack(fill=tk.BOTH, expand=True)

        self.current_view = 'operations'

    def show_chat(self):
        """Return to chat view."""
        # Hide operations
        if self.operations_client:
            for widget in self.main_container.winfo_children():
                widget.pack_forget()

        # Show chat
        if self.chat_client:
            self.chat_client.is_hidden = False
            for widget in self.main_container.winfo_children():
                if hasattr(widget, 'master') and widget.master == self.main_container:
                    widget.pack(fill=tk.BOTH, expand=True)

        self.current_view = 'chat'

    def on_exit_chat(self):
        """Handle exit from chat."""
        # Disconnect
        if self.chat_client:
            self.chat_client.disconnect()

        # Clear operations if exists
        self.operations_client = None
        self.chat_client = None

        # Return to auth
        self.show_auth()

    def run(self):
        """Run the application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down...")
            if self.chat_client:
                self.chat_client.disconnect()

def main():
    """Entry point."""
    app = ChatApplication()
    app.run()

if __name__ == "__main__":
    main()
