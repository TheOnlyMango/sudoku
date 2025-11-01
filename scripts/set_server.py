#!/usr/bin/env python3
"""Helper script to quickly update chat server address in config."""

import json
import sys
import os

CONFIG_FILE = 'chat_config.json'

def update_server_address(address):
    """Update server address in config file.

    Args:
        address: Server address (IP or hostname)
    """
    # Load or create config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        config = {
            "server": {"host": "0.0.0.0", "port": 7331},
            "client": {"server_address": "auto", "server_port": 7331},
            "tailscale": {"enabled": True, "hostname": "chat-server"}
        }

    # Update client server address
    if 'client' not in config:
        config['client'] = {}

    config['client']['server_address'] = address

    # Save config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Updated {CONFIG_FILE}")
    print(f"  Server address set to: {address}")
    print(f"\nYou can now run: python3 main.py")

def show_usage():
    """Show usage information."""
    print("Usage: python3 set_server.py <server-address>")
    print()
    print("Examples:")
    print("  python3 set_server.py kali-1")
    print("  python3 set_server.py main-win")
    print("  python3 set_server.py 100.67.191.120")
    print("  python3 set_server.py auto")
    print()
    print("Current Tailscale machines:")

    try:
        import subprocess
        result = subprocess.run(['tailscale', 'status'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print()
            for line in result.stdout.split('\n')[:10]:
                if line.strip():
                    print(f"  {line}")
    except:
        print("  (run 'tailscale status' to see available machines)")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        show_usage()
        sys.exit(1)

    address = sys.argv[1]
    update_server_address(address)
