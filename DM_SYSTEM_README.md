# Direct Messaging & Authentication System

## Overview

Complete DM/Authentication system with 90s hacker aesthetic for the SHNet Secure Terminal chat application.

## Features Implemented

### Authentication System
- **User Registration**: Create account with username and password
- **Login**: Authenticate with existing credentials
- **Anonymous Mode**: Generate random Russian spy name for anonymous access
- **Password Hashing**: Secure SHA256 password storage

### Direct Messaging
- **Send DMs**: Send private messages to any registered user
- **Inbox**: View all conversations with unread counts
- **Bold Unread Messages**: Unread conversations highlighted in pink
- **Message History**: Full conversation history stored on server
- **Mark Read**: Conversations automatically marked as read when viewed

### Persistent Chat
- **Session History**: New users joining see all messages from current session
- **Chat Archive**: All messages archived to database on server shutdown
- **Session Tracking**: UUID-based session management

### Anonymous Users
- **Russian Spy Names**: 100 authentic Russian male names
- **RED Username Display**: Anonymous users shown in RED in group chat
- **No DM Access**: INBOX button hidden for anonymous users
- **Random Generation**: Automatic unique name selection

### Server Management
- **GUI Console**: Terminal-style server interface
- **Real-time Logs**: All server events displayed in console
- **Graceful Shutdown**: Proper chat archiving on shutdown
- **Start/Stop Controls**: Easy server management

## File Structure

```
sudoku/
├── auth_db.py                  # Authentication & messaging database
├── russian_spy_names.py        # Russian spy name generator
├── auth_ui.py                  # Authentication UI (Login/Register/Anon)
├── inbox_ui.py                 # Complete inbox interface
├── chat_server_improved.py     # Updated server with auth & DM support
├── chat_server_gui.py          # Server management GUI
└── sudoku/
    ├── chat_client.py          # Updated client with auth integration
    └── gui.py                  # Updated to use AuthUI
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP,
    is_anon BOOLEAN DEFAULT 0
);
```

### Direct Messages Table
```sql
CREATE TABLE direct_messages (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP,
    is_read BOOLEAN DEFAULT 0
);
```

### Chat History Table (Current Session)
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP,
    session_id TEXT
);
```

### Chat Archive Table (Closed Sessions)
```sql
CREATE TABLE chat_archive (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP,
    session_id TEXT,
    archived_at TIMESTAMP
);
```

## Protocol Commands

### Authentication
- `AUTH_REQUIRED:` - Server requests authentication
- `AUTH:username:password` - Standard login
- `AUTH_ANON:username` - Anonymous login
- `AUTH_FAILED:reason` - Authentication failure
- `WELCOME:username:token:is_anon` - Authentication success

### Direct Messages
- `DM:recipient:message` - Send direct message
- `DM_INBOX:` - Request inbox list
- `DM_CONVERSATION:username` - Request conversation with user
- `DM_MARK_READ:username` - Mark conversation as read
- `DM_SENT:recipient` - DM sent confirmation

### Group Chat
- `MSG:message` - Send group message
- `USERLIST:user1:0,user2:1` - User list with anon flags (0=normal, 1=anon)
- `JOIN:username:is_anon` - User joined notification
- `HISTORY:username:timestamp:message` - Historical message

## Usage Instructions

### 1. Start the Server

Run the server GUI for easy management:
```bash
python3 chat_server_gui.py
```

Or run the server directly:
```bash
python3 chat_server_improved.py
```

The server will:
- Generate a unique session ID
- Listen for connections on configured port (default: 7331)
- Archive chat history on shutdown

### 2. Launch the Game Client

```bash
python3 main.py
```

From the Sudoku game, click the **SECRET CHAT** button.

### 3. Authentication

You'll see three options:

**LOGIN**
- Enter existing username and password
- Click LOGIN button
- Access to all features including DMs

**REGISTER**
- Create new account
- Username must be 3+ characters
- Password must be 6+ characters
- Confirm password must match
- After registration, return to login

**ANONYMOUS MODE**
- Instant access with random Russian spy name
- Username displayed in RED
- No DM/Inbox access (button hidden)
- Cannot be contacted via DM

### 4. Using Group Chat

- Type messages in input box at bottom
- Press ENTER or click SEND
- See all users in left panel
- Anonymous users shown in RED
- New joiners see all session history

### 5. Using Direct Messages (Registered Users Only)

**Viewing Inbox:**
- Click **INBOX** button (top right)
- See all conversations
- **[!] Bold Pink** = Unread messages
- **Regular Muted Blue** = Read messages

**Reading Messages:**
- Click on a conversation in left panel
- Full message thread loads
- Messages automatically marked as read
- Sent messages shown with ">>>"
- Received messages shown with "[username]"

**Sending DMs:**
- Click **[ NEW MESSAGE ]** button
- Enter recipient username
- Type your message
- Click **[ SEND ]**

**Replying:**
- Select conversation from list
- Type reply in "REPLY >>>" box
- Press ENTER or click **[ SEND ]**

### 6. Operations Database

- Click **OPERATIONS** button to access ops database
- Chat connection stays alive in background
- Return to chat anytime

### 7. Shutting Down

**Server:**
- Click **SHUTDOWN SERVER** in server GUI
- Chat history automatically archived
- All connections closed gracefully

**Client:**
- Click **ABORT** button to disconnect
- Or close window

## Color Scheme (90s Hacker Aesthetic)

- **Background**: Dark purple/gray (#282a36)
- **Panel**: Very dark blue (#0a0e14)
- **Text**: Light gray (#f8f8f2)
- **Usernames**: Cyan (#8be9fd)
- **Anonymous Users**: RED (#ff5555)
- **System Messages**: Orange (#ffb86c)
- **DMs**: Pink (#ff79c6)
- **Prompts**: Muted blue (#6272a4)
- **Unread**: Hot pink (#ff79c6)
- **Read**: Muted blue (#6272a4)

## Features Summary

✅ Force user registration when entering chat
✅ Anonymous mode with Russian spy names
✅ Anonymous users displayed in RED
✅ INBOX button hidden for anonymous users
✅ Persistent group chat during session
✅ New users see chat history
✅ Chat archived on server shutdown
✅ Server GUI with graceful shutdown
✅ Full DM system (send, receive, inbox, read/unread)
✅ Inbox with bold unread messages (mutt-style)
✅ Complete 90s hacker aesthetic

## Security Notes

- Passwords hashed with SHA256 before storage
- Token-based session management
- Rate limiting on messages and file uploads
- Database connection pooling
- Proper input validation
- No DM access for anonymous users

## Troubleshooting

**Cannot connect to server:**
- Ensure server is running (check server GUI)
- Verify server host/port in chat_config.toml
- Check firewall settings

**Authentication failed:**
- Verify username and password
- Check that user is registered
- For anon mode, try again (may be name collision)

**Inbox not loading:**
- Click REFRESH button
- Check server connection
- Verify you're not in anonymous mode

**Anonymous user can't see INBOX:**
- This is by design
- Anonymous users cannot send/receive DMs
- Register an account to access DMs

## Development Notes

All features are fully integrated into the existing chat system with no backward compatibility - this is the only version. The system maintains the 90s hacker aesthetic throughout with Courier fonts, ASCII art headers, terminal-style prompts, and Dracula color scheme.
