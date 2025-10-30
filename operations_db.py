"""Operations Wiki Database - PirateBox-style knowledge base"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re


class OperationsDB:
    """Database handler for operations wiki/forum system."""

    def __init__(self, db_path='operations.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Operations/threads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                creator TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')

        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                comment TEXT NOT NULL,
                filename TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operation_id) REFERENCES operations (id)
            )
        ''')

        conn.commit()
        conn.close()

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password meets requirements.

        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 special character

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least 1 uppercase letter"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least 1 special character"

        return True, ""

    def hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_operation(self, name: str, creator: str, password: str, description: str = "") -> Tuple[bool, str]:
        """Create a new operation/thread.

        Returns:
            Tuple of (success, message/error)
        """
        # Validate password
        valid, error = self.validate_password(password)
        if not valid:
            return False, error

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO operations (name, creator, password_hash, description)
                VALUES (?, ?, ?, ?)
            ''', (name, creator, password_hash, description))

            conn.commit()
            conn.close()
            return True, f"Operation '{name}' created successfully"
        except sqlite3.IntegrityError:
            return False, f"Operation '{name}' already exists"
        except Exception as e:
            return False, f"Error creating operation: {str(e)}"

    def verify_operation_password(self, operation_name: str, password: str) -> bool:
        """Verify password for an operation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT password_hash FROM operations WHERE name = ?
        ''', (operation_name,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return False

        password_hash = self.hash_password(password)
        return password_hash == result[0]

    def get_all_operations(self) -> List[Dict]:
        """Get list of all operations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, creator, created_at, description
            FROM operations
            ORDER BY created_at DESC
        ''')

        operations = []
        for row in cursor.fetchall():
            operations.append({
                'id': row[0],
                'name': row[1],
                'creator': row[2],
                'created_at': row[3],
                'description': row[4]
            })

        conn.close()
        return operations

    def add_post(self, operation_name: str, username: str, comment: str,
                 filename: str = None, file_path: str = None) -> Tuple[bool, str]:
        """Add a post to an operation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get operation ID
            cursor.execute('SELECT id FROM operations WHERE name = ?', (operation_name,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False, "Operation not found"

            operation_id = result[0]

            cursor.execute('''
                INSERT INTO posts (operation_id, username, comment, filename, file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (operation_id, username, comment, filename, file_path))

            conn.commit()
            conn.close()
            return True, "Post added successfully"
        except Exception as e:
            return False, f"Error adding post: {str(e)}"

    def get_operation_posts(self, operation_name: str) -> List[Dict]:
        """Get all posts for an operation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.id, p.username, p.comment, p.filename, p.file_path, p.created_at
            FROM posts p
            JOIN operations o ON p.operation_id = o.id
            WHERE o.name = ?
            ORDER BY p.created_at ASC
        ''', (operation_name,))

        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row[0],
                'username': row[1],
                'comment': row[2],
                'filename': row[3],
                'file_path': row[4],
                'created_at': row[5]
            })

        conn.close()
        return posts

    def get_operation_info(self, operation_name: str) -> Optional[Dict]:
        """Get operation information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, creator, created_at, description
            FROM operations
            WHERE name = ?
        ''', (operation_name,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        return {
            'id': result[0],
            'name': result[1],
            'creator': result[2],
            'created_at': result[3],
            'description': result[4]
        }

    def get_file_data(self, post_id: int) -> Optional[str]:
        """Get base64-encoded file data for a post."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT file_path, filename FROM posts WHERE id = ?
        ''', (post_id,))

        result = cursor.fetchone()
        conn.close()

        if not result or not result[0]:
            print(f"No file_path found for post_id: {post_id}")
            return None

        file_path = result[0]
        filename = result[1]
        print(f"Attempting to read file: {file_path} (filename: {filename})")

        try:
            import base64
            import os

            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return None

            with open(file_path, 'rb') as f:
                file_data = f.read()
            print(f"Successfully read {len(file_data)} bytes from {file_path}")
            return base64.b64encode(file_data).decode('utf-8')
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
