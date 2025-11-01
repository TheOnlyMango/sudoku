#!/usr/bin/env python3
"""Launch the chat server GUI."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.server.server_gui import ServerGUI


def main():
    """Start the chat server GUI."""
    gui = ServerGUI()
    gui.run()


if __name__ == "__main__":
    main()
