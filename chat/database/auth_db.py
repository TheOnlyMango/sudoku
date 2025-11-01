"""Authentication and Messaging Database"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import uuid


class AuthDB:
    """Database handler for user authentication and direct messages."""

    def __init__(self, db_path='auth.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        """Initialize database with required tables."""
        cursor = self.conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_anon BOOLEAN DEFAULT 0
            )
        ''')

        # Direct messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS direct_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                message TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0
            )
        ''')

        # Chat history (current session)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT NOT NULL
            )
        ''')

        # Chat archive (closed sessions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP,
                session_id TEXT NOT NULL,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str, is_anon: bool = False) -> Tuple[bool, str]:
        """Register a new user.

        Returns:
            Tuple of (success, message)
        """
        try:
            cursor = self.conn.cursor()
            password_hash = self.hash_password(password) if not is_anon else ""

            cursor.execute(
                'INSERT INTO users (username, password_hash, is_anon) VALUES (?, ?, ?)',
                (username, password_hash, is_anon)
            )
            self.conn.commit()
            return True, "Registration successful"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user with username and password."""
        cursor = self.conn.cursor()
        password_hash = self.hash_password(password)

        cursor.execute(
            'SELECT id FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )

        return cursor.fetchone() is not None

    def user_exists(self, username: str) -> bool:
        """Check if username exists."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        return cursor.fetchone() is not None

    def is_anon_user(self, username: str) -> bool:
        """Check if user is anonymous."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT is_anon FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        return result['is_anon'] if result else False

    def send_dm(self, sender: str, recipient: str, message: str) -> Tuple[bool, str]:
        """Send a direct message."""
        if not self.user_exists(recipient):
            return False, "Recipient not found"

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO direct_messages (sender, recipient, message) VALUES (?, ?, ?)',
                (sender, recipient, message)
            )
            self.conn.commit()
            return True, "Message sent"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_inbox(self, username: str) -> List[Dict]:
        """Get inbox summary for user (conversations with unread count)."""
        cursor = self.conn.cursor()

        # Get all unique conversation partners
        cursor.execute('''
            SELECT DISTINCT
                CASE
                    WHEN sender = ? THEN recipient
                    ELSE sender
                END as other_user
            FROM direct_messages
            WHERE sender = ? OR recipient = ?
        ''', (username, username, username))

        conversations = []
        for row in cursor.fetchall():
            other_user = row['other_user']

            # Get unread count for this conversation
            cursor.execute('''
                SELECT COUNT(*) as unread_count
                FROM direct_messages
                WHERE recipient = ? AND sender = ? AND is_read = 0
            ''', (username, other_user))
            unread_count = cursor.fetchone()['unread_count']

            # Get last message and timestamp
            cursor.execute('''
                SELECT message, sent_at
                FROM direct_messages
                WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)
                ORDER BY sent_at DESC LIMIT 1
            ''', (username, other_user, other_user, username))
            last_msg = cursor.fetchone()

            if last_msg:
                conversations.append({
                    'user': other_user,
                    'unread': unread_count,
                    'preview': last_msg['message'][:50] + '...' if len(last_msg['message']) > 50 else last_msg['message'],
                    'timestamp': last_msg['sent_at']
                })

        # Sort by timestamp descending
        conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        return conversations

    def get_conversation(self, user1: str, user2: str) -> List[Dict]:
        """Get all messages between two users."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT sender, recipient, message, sent_at, is_read
            FROM direct_messages
            WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)
            ORDER BY sent_at ASC
        ''', (user1, user2, user2, user1))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'sender': row['sender'],
                'recipient': row['recipient'],
                'message': row['message'],
                'timestamp': row['sent_at'],
                'is_read': bool(row['is_read'])
            })

        return messages

    def mark_conversation_read(self, recipient: str, sender: str):
        """Mark all messages from sender to recipient as read."""
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE direct_messages SET is_read = 1 WHERE recipient = ? AND sender = ?',
            (recipient, sender)
        )
        self.conn.commit()

    def add_chat_message(self, username: str, message: str, session_id: str):
        """Add message to current chat history."""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO chat_history (username, message, session_id) VALUES (?, ?, ?)',
            (username, message, session_id)
        )
        self.conn.commit()

    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get all chat history for current session."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT username, message, timestamp
            FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))

        history = []
        for row in cursor.fetchall():
            history.append({
                'username': row['username'],
                'message': row['message'],
                'timestamp': row['timestamp']
            })

        return history

    def archive_session(self, session_id: str):
        """Archive current session and clear history."""
        cursor = self.conn.cursor()

        # Copy to archive
        cursor.execute('''
            INSERT INTO chat_archive (username, message, timestamp, session_id)
            SELECT username, message, timestamp, session_id
            FROM chat_history
            WHERE session_id = ?
        ''', (session_id,))

        # Clear current history
        cursor.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))

        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()
