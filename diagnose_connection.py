#!/usr/bin/env python3
"""Diagnose chat connection issues."""

import socket
import subprocess
import sys
import os

print("=" * 60)
print("  CHAT CONNECTION DIAGNOSTICS")
print("=" * 60)
print()

# 1. Check config
print("[1] Checking configuration...")
try:
    from chat_config_reader import get_config
    config = get_config()
    server_addr, server_port = config.get_client_config()
    print(f"  ✓ Client will try to connect to: {server_addr}:{server_port}")
except Exception as e:
    print(f"  ✗ Error reading config: {e}")
    server_addr = "unknown"
    server_port = 7331

print()

# 2. Check Tailscale
print("[2] Checking Tailscale status...")
try:
    result = subprocess.run(['tailscale', 'status'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("  ✓ Tailscale is running")
        print()
        print("  Available machines:")
        for line in result.stdout.split('\n')[:8]:
            if line.strip():
                print(f"    {line}")
    else:
        print("  ✗ Tailscale command failed")
except FileNotFoundError:
    print("  ✗ Tailscale not found in PATH")
except Exception as e:
    print(f"  ✗ Error checking Tailscale: {e}")

print()

# 3. Test hostname resolution
print("[3] Testing hostname resolution...")
hostnames_to_test = [
    server_addr,
    'kali-1',
    'main-win',
    'localhost',
]

for hostname in set(hostnames_to_test):
    if hostname in ['auto', 'unknown']:
        continue
    try:
        ip = socket.gethostbyname(hostname)
        print(f"  ✓ {hostname:20s} -> {ip}")
    except socket.gaierror:
        print(f"  ✗ {hostname:20s} -> Cannot resolve")
    except Exception as e:
        print(f"  ✗ {hostname:20s} -> Error: {e}")

print()

# 4. Test connection to server
print(f"[4] Testing connection to {server_addr}:{server_port}...")
try:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(3)
    test_socket.connect((server_addr, server_port))
    print(f"  ✓ SUCCESS! Server is reachable")
    test_socket.close()
except socket.timeout:
    print(f"  ✗ TIMEOUT - Server not responding")
    print(f"    Possible issues:")
    print(f"      - Server not running on {server_addr}")
    print(f"      - Firewall blocking port {server_port}")
    print(f"      - Wrong server address in config")
except ConnectionRefusedError:
    print(f"  ✗ CONNECTION REFUSED - Server not listening")
    print(f"    Possible issues:")
    print(f"      - Server not running on {server_addr}")
    print(f"      - Server listening on different port")
except socket.gaierror:
    print(f"  ✗ HOSTNAME ERROR - Cannot resolve {server_addr}")
    print(f"    Possible issues:")
    print(f"      - Invalid hostname in config")
    print(f"      - Tailscale MagicDNS not working")
except Exception as e:
    print(f"  ✗ ERROR: {e}")

print()

# 5. Recommendations
print("[5] Recommendations:")
print()

if server_addr == "100.115.233.16":
    print("  ⚠ You're trying to connect to 100.115.233.16 (main-win)")
    print("    If your server is running on a different machine:")
    print()
    print("    1. Find your server's Tailscale IP:")
    print("       tailscale status")
    print()
    print("    2. Update chat_config.json on THIS machine:")
    print('       {"client": {"server_address": "SERVER_IP", "server_port": 7331}}')
    print()
    print("    Or use the helper script:")
    print("       python3 set_server.py <server-ip-or-hostname>")
elif server_addr == "auto":
    print("  ⚠ Server address is set to 'auto' but resolution failed")
    print("    Try using explicit IP or hostname:")
    print("       python3 set_server.py kali-1")
    print("       python3 set_server.py 100.67.191.120")
else:
    print(f"  Current server: {server_addr}:{server_port}")
    print()
    print("  If connection still fails:")
    print("    1. Verify server is running:")
    print("       lsof -i :7331")
    print()
    print("    2. Check firewall on server machine")
    print()
    print("    3. Try pinging the server:")
    print(f"       ping {server_addr}")

print()
print("=" * 60)
