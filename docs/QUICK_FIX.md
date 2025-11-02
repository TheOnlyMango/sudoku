# Quick Fix: Connection Failed Error

## Problem
Client shows "Connection Failed - Could not connect to chat server"

## Root Cause
The client on main-win is trying to connect to the wrong IP address (probably 100.115.233.16 which is main-win itself, but the server is running on laptop).

---

## Solution (Choose One):

### Option 1: Use Helper Script (Easiest) ⭐

**On main-win:**

1. Pull latest code:
   ```bash
   git pull
   ```

2. Find your server's IP (on laptop where server is running):
   ```bash
   tailscale status
   # Look for laptop's IP (e.g., kali-1 at 100.67.191.120)
   ```

3. Run helper script on main-win:
   ```bash
   python3 set_server.py 100.67.191.120
   # Or use hostname:
   python3 set_server.py kali-1
   ```

4. Try connecting again!

---

### Option 2: Manual Config Edit

**On main-win:**

Create or edit `chat_config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 7331
  },
  "client": {
    "server_address": "100.67.191.120",
    "server_port": 7331
  },
  "tailscale": {
    "enabled": true,
    "hostname": "chat-server"
  }
}
```

Replace `100.67.191.120` with your laptop's actual Tailscale IP.

---

### Option 3: Diagnose First

**On main-win:**

```bash
python3 diagnose_connection.py
```

This will:
- Show what IP the client is trying to connect to
- Test if the server is reachable
- Give specific recommendations

---

## Step-by-Step Troubleshooting:

### 1. Verify Server is Running

**On laptop (where server should be):**
```bash
lsof -i :7331
# Should show python3 listening on port 7331
```

If nothing shows, start the server:
```bash
python3 chat_server_improved.py
```

### 2. Get Server's Tailscale IP

**On laptop:**
```bash
tailscale status | grep "^100"
# Note the IP for your laptop (e.g., 100.67.191.120)
```

### 3. Update Client Config

**On main-win:**
```bash
# Quick way:
python3 set_server.py 100.67.191.120

# Or manual way:
# Edit chat_config.json and set client.server_address to laptop's IP
```

### 4. Test Connection

**On main-win:**
```bash
python3 diagnose_connection.py
```

Should show: "✓ SUCCESS! Server is reachable"

### 5. Try Sudoku Game

**On main-win:**
```bash
python3 main.py
# Play on Expert difficulty
# Click ERR button
# Should connect!
```

---

## Common Issues:

### Issue: "Tailscale not found"
- Make sure Tailscale is installed and running on both machines
- Run `tailscale status` to verify

### Issue: "Connection refused"
- Server not running on laptop
- Run `python3 chat_server_improved.py` on laptop

### Issue: "Timeout"
- Firewall blocking port 7331
- Wrong IP address in config

### Issue: "Cannot resolve hostname"
- Use IP address instead of hostname:
  ```bash
  python3 set_server.py 100.67.191.120
  ```

---

## Why This Happened:

The auto-discovery looks for a Tailscale machine named "chat-server", but none of your machines have that hostname. The system then falls back to the hardcoded default (100.115.233.16 = main-win).

**Solutions:**
1. Use explicit IP/hostname in config (recommended for now)
2. OR rename one machine to "chat-server" in Tailscale settings

---

## Quick Reference:

**Find server IP (on server machine):**
```bash
tailscale status | head -1
```

**Update client (on client machine):**
```bash
python3 set_server.py <server-ip>
```

**Diagnose (on client machine):**
```bash
python3 diagnose_connection.py
```

**Test server is running (on server machine):**
```bash
lsof -i :7331
```

---

## Example Session:

**Laptop (server):**
```bash
$ tailscale status | head -1
100.67.191.120  kali-1  ...

$ python3 chat_server_improved.py
[2025-10-30 14:30:00] INFO: SERVER STARTED: Listening on 100.67.191.120:7331
```

**Main-win (client):**
```bash
$ python3 set_server.py 100.67.191.120
✓ Updated chat_config.json
  Server address set to: 100.67.191.120

$ python3 diagnose_connection.py
...
[4] Testing connection to 100.67.191.120:7331...
  ✓ SUCCESS! Server is reachable

$ python3 main.py
# Works!
```

---

Need help? Run `python3 diagnose_connection.py` and share the output!
