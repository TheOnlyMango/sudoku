# Network Configuration Guide

## Overview

The chat system now supports **flexible networking** - you can run the server on ANY machine in your Tailscale network and clients will automatically find it!

## How It Works

The system uses a **hybrid configuration approach** with multiple fallback layers:

```
1. Config file (chat_config.json)
   ↓ if not found or "auto"
2. Tailscale hostname resolution
   ↓ if resolution fails
3. Hardcoded fallback (100.115.233.16:7331)
```

This ensures the system "just works" in most scenarios while still being configurable.

---

## Quick Start

### Option 1: Zero Configuration (Recommended)

**On the server machine:**
1. Set your Tailscale hostname to `chat-server`
2. Run: `python3 chat_server.py`

**On client machines:**
1. Just run the Sudoku game
2. Client automatically finds server via Tailscale hostname

**That's it!** No config files needed.

---

### Option 2: Custom Configuration

**Create `chat_config.json`:**
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 7331
  },
  "client": {
    "server_address": "auto",
    "server_port": 7331
  },
  "tailscale": {
    "enabled": true,
    "hostname": "chat-server"
  }
}
```

Place this file in the same directory as the scripts.

---

## Configuration Options

### Server Configuration

**`server.host`** - Address to bind to
- `"0.0.0.0"` - Listen on ALL network interfaces (recommended)
- `"100.115.233.16"` - Listen only on specific IP
- Default: `"0.0.0.0"`

**`server.port`** - Port to bind to
- Range: 1024-65535
- Default: `7331`

**Example:**
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 7331
  }
}
```

---

### Client Configuration

**`client.server_address`** - Server to connect to
- `"auto"` - Automatically discover via Tailscale hostname
- `"100.115.233.16"` - Connect to specific IP address
- `"chat-server"` - Connect to Tailscale hostname
- `"main-win"` - Connect to Tailscale machine name
- Default: `"auto"`

**`client.server_port`** - Server port
- Must match server port
- Default: `7331`

**Example:**
```json
{
  "client": {
    "server_address": "auto",
    "server_port": 7331
  }
}
```

---

### Tailscale Configuration

**`tailscale.enabled`** - Enable Tailscale hostname resolution
- `true` - Try to resolve Tailscale hostnames
- `false` - Skip hostname resolution (use IP only)
- Default: `true`

**`tailscale.hostname`** - Tailscale hostname to resolve
- Short hostname (without `.tail-scale.ts.net`)
- Default: `"chat-server"`

**Example:**
```json
{
  "tailscale": {
    "enabled": true,
    "hostname": "chat-server"
  }
}
```

---

## Common Scenarios

### Scenario 1: Server on main-win, Clients on other machines

**Server (main-win):**
```bash
# No config needed if hostname is "main-win"
python3 chat_server.py
```

**Client config (optional):**
```json
{
  "client": {
    "server_address": "main-win",
    "server_port": 7331
  }
}
```

Or just use `"auto"` and it will find it.

---

### Scenario 2: Server on kali machine, Clients on other machines

**Server (kali):**
```bash
# Set Tailscale hostname to "chat-server" or use config
python3 chat_server.py
```

**Client config:**
```json
{
  "client": {
    "server_address": "kali",
    "server_port": 7331
  }
}
```

Or use `"auto"` if server hostname is `chat-server`.

---

### Scenario 3: Testing on same machine

**Server:**
```bash
python3 chat_server.py
```

**Client config:**
```json
{
  "client": {
    "server_address": "localhost",
    "server_port": 7331
  }
}
```

Or use the machine's Tailscale hostname.

---

### Scenario 4: Custom port

**Both server and client config:**
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8888
  },
  "client": {
    "server_address": "auto",
    "server_port": 8888
  }
}
```

---

## Tailscale Hostname Resolution

The client tries to resolve hostnames in this order:

1. **`hostname`** - Simple hostname (e.g., `chat-server`)
2. **`hostname.tail-scale.ts.net`** - Full Tailscale domain
3. **`hostname.local`** - mDNS fallback

### Setting Your Tailscale Hostname

**Via Tailscale Admin Console:**
1. Go to https://login.tailscale.com/admin/machines
2. Find your machine
3. Click "..." → "Edit machine"
4. Set hostname to `chat-server`

**Via CLI:**
```bash
sudo tailscale set --hostname chat-server
```

---

## Troubleshooting

### Issue: Client can't connect

**Check 1: Is server running?**
```bash
# On server machine
lsof -i :7331
```

**Check 2: Can you ping the server?**
```bash
# From client machine
ping <server-tailscale-ip>
```

**Check 3: Check config**
```bash
# Print config
python3 -c "from chat_config_reader import get_config; c = get_config(); print('Server:', c.get_client_config())"
```

**Check 4: Test hostname resolution**
```bash
# Try to resolve hostname
nslookup chat-server
# or
ping chat-server
```

---

### Issue: Server binds to wrong IP

**Solution:** Set `server.host` explicitly in config:
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 7331
  }
}
```

Or pass as argument:
```python
server = ChatServer(host='0.0.0.0', port=7331)
```

---

### Issue: "auto" doesn't work

**Solution 1:** Verify Tailscale hostname
```bash
tailscale status
```

**Solution 2:** Use explicit IP
```json
{
  "client": {
    "server_address": "100.115.233.16",
    "server_port": 7331
  }
}
```

**Solution 3:** Check Tailscale MagicDNS is enabled
```bash
tailscale status --json | grep MagicDNS
```

---

## File Locations

### Config File Priority

The system looks for `chat_config.json` in:
1. Current working directory
2. Script directory (where chat_server.py is located)

### Example Config File Location

```
/home/mango/Desktop/claude/sudoku/
├── chat_config.json          ← Config file
├── chat_config.json.example  ← Example template
├── chat_server.py
├── chat_server_improved.py
└── sudoku/
    └── chat_client.py
```

---

## Migration from Old Setup

### Old System (Hardcoded)
- Server always on main-win (100.115.233.16)
- Clients always connect to main-win
- No flexibility

### New System (Flexible)
- Server can run anywhere
- Clients find server automatically
- Backwards compatible with old IPs

### No Changes Needed!

The new system is **100% backwards compatible**. If you don't create a config file:
- Server defaults to `0.0.0.0:7331` (listens on all interfaces)
- Client defaults to `100.115.233.16:7331` (main-win)
- Everything works as before!

---

## Advanced: Programmatic Configuration

You can override config in code:

**Server:**
```python
from chat_server import ChatServer

# Explicit configuration
server = ChatServer(host='0.0.0.0', port=7331)
server.start()
```

**Client:**
```python
from sudoku.chat_client import ChatClient

# Explicit configuration
client = ChatClient(root, server_host='100.115.233.16', server_port=7331)
```

---

## Best Practices

1. **Use `0.0.0.0` for server** - Allows connections from any interface
2. **Use `"auto"` for client** - Enables automatic discovery
3. **Set consistent Tailscale hostname** - Makes discovery reliable
4. **Keep default port (7331)** - Avoid conflicts
5. **Commit `chat_config.json.example`** - Don't commit actual config with IPs

---

## Security Notes

- Server binds to `0.0.0.0` but still requires Tailscale connection
- Only Tailscale network members can connect
- Firewall rules still apply
- Consider using improved server for additional security (tokens, rate limiting)

---

## Summary

**Zero Config Setup:**
```bash
# On any machine in Tailscale network
python3 chat_server.py

# Clients automatically connect via "auto" discovery
```

**Custom Setup:**
```bash
# 1. Create chat_config.json
# 2. Set server and client addresses
# 3. Run server and clients
```

**It just works!** 🚀
