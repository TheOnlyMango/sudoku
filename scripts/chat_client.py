#!/usr/bin/env python3
"""Launch the chat client GUI."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from chat.client.chat_client import ChatClient

def main():
    """Start the chat client."""
    root = tk.Tk()
    client = ChatClient(root)

    # Start the GUI main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down chat client...")
        if hasattr(client, 'disconnect'):
            client.disconnect()

if __name__ == "__main__":
    main()
