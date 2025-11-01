"""Operations Wiki Database - PirateBox-style knowledge base"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
from chat.database.db_pool import get_pool


class OperationsDB:
    """Database handler for operations wiki/forum system."""

    def __init__(self, db_path='operations.db'):
        self.db_path = db_path
        self.db_pool = get_pool(db_path, pool_size=5)
        self.init_db()

    def init_db(self):
        """Initialize database with required tables."""
        with self.db_pool.get_connection() as conn:
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

            # Intelligence Information Reports (IIR) table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS intelligence_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id INTEGER NOT NULL,
                    report_number TEXT UNIQUE NOT NULL,
                    submitter TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    dtg_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dtg_info_date TEXT NOT NULL,
                    dtg_cutoff TEXT NOT NULL,
                    target TEXT NOT NULL,
                    title TEXT NOT NULL,
                    information TEXT NOT NULL,
                    filename TEXT,
                    file_path TEXT,
                    FOREIGN KEY (operation_id) REFERENCES operations (id)
                )
            ''')

            conn.commit()

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
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()

                password_hash = self.hash_password(password)
                cursor.execute('''
                    INSERT INTO operations (name, creator, password_hash, description)
                    VALUES (?, ?, ?, ?)
                ''', (name, creator, password_hash, description))

                conn.commit()
                return True, f"Operation '{name}' created successfully"
        except sqlite3.IntegrityError:
            return False, f"Operation '{name}' already exists"
        except Exception as e:
            return False, f"Error creating operation: {str(e)}"

    def verify_operation_password(self, operation_name: str, password: str) -> bool:
        """Verify password for an operation."""
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT password_hash FROM operations WHERE name = ?
            ''', (operation_name,))

            result = cursor.fetchone()

            if not result:
                return False

            password_hash = self.hash_password(password)
            return password_hash == result[0]

    def get_all_operations(self) -> List[Dict]:
        """Get list of all operations."""
        with self.db_pool.get_connection() as conn:
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

            return operations

    def add_post(self, operation_name: str, username: str, comment: str,
                 filename: str = None, file_path: str = None) -> Tuple[bool, str]:
        """Add a post to an operation."""
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()

                # Get operation ID
                cursor.execute('SELECT id FROM operations WHERE name = ?', (operation_name,))
                result = cursor.fetchone()

                if not result:
                    return False, "Operation not found"

                operation_id = result[0]

                cursor.execute('''
                    INSERT INTO posts (operation_id, username, comment, filename, file_path)
                    VALUES (?, ?, ?, ?, ?)
                ''', (operation_id, username, comment, filename, file_path))

                conn.commit()
                return True, "Post added successfully"
        except Exception as e:
            return False, f"Error adding post: {str(e)}"

    def get_operation_posts(self, operation_name: str) -> List[Dict]:
        """Get all posts for an operation."""
        with self.db_pool.get_connection() as conn:
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

            return posts

    def get_operation_info(self, operation_name: str) -> Optional[Dict]:
        """Get operation information."""
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, name, creator, created_at, description
                FROM operations
                WHERE name = ?
            ''', (operation_name,))

            result = cursor.fetchone()

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
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT file_path, filename FROM posts WHERE id = ?
            ''', (post_id,))

            result = cursor.fetchone()

            if not result or not result[0]:
                from server_logging import ops_logger
                ops_logger.warning(f"No file_path found for post_id: {post_id}")
                return None

            file_path = result[0]
            filename = result[1]

            try:
                import base64
                import os

                # Check if file exists
                if not os.path.exists(file_path):
                    from server_logging import ops_logger
                    ops_logger.error(f"File does not exist: {file_path}")
                    return None

                with open(file_path, 'rb') as f:
                    file_data = f.read()

                return base64.b64encode(file_data).decode('utf-8')
            except Exception as e:
                from server_logging import ops_logger
                ops_logger.error(f"Error reading file {file_path}: {e}")
                return None

    def generate_ir_number(self) -> str:
        """Generate next IR number in format IR25-0001.

        Returns:
            Next available IR number for current year
        """
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()

            # Get current year (last 2 digits)
            current_year = datetime.now().strftime('%y')

            # Find highest number for current year
            cursor.execute('''
                SELECT report_number FROM intelligence_reports
                WHERE report_number LIKE ?
                ORDER BY report_number DESC
                LIMIT 1
            ''', (f'IR{current_year}-%',))

            result = cursor.fetchone()

            if result:
                # Extract number and increment
                last_number = int(result[0].split('-')[1])
                next_number = last_number + 1
            else:
                # First report of the year
                next_number = 1

            # Format as IR25-0001
            return f'IR{current_year}-{next_number:04d}'

    def submit_iir(self, operation_name: str, submitter: str, priority: str,
                   dtg_info_date: str, dtg_cutoff: str, target: str, title: str,
                   information: str, filename: str = None, file_data_b64: str = None) -> Tuple[bool, str]:
        """Submit an Intelligence Information Report (IIR).

        Args:
            operation_name: Name of operation
            submitter: Username submitting report
            priority: Priority level (routine, urgent, priority, flash)
            dtg_info_date: DTG of information date
            dtg_cutoff: DTG of information cutoff
            target: Target of intelligence
            title: Report title
            information: Information text block
            filename: Optional filename for attachment
            file_data_b64: Optional base64-encoded file data

        Returns:
            Tuple of (success, message/report_number)
        """
        try:
            with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()

                # Get operation ID
                cursor.execute('SELECT id FROM operations WHERE name = ?', (operation_name,))
                result = cursor.fetchone()

                if not result:
                    return False, "Operation not found"

                operation_id = result[0]

                # Generate IR number
                report_number = self.generate_ir_number()

                # Handle file if provided
                file_path = None
                if filename and file_data_b64:
                    file_dir = os.path.join('operation_files', operation_name, 'iirs')
                    os.makedirs(file_dir, exist_ok=True)
                    file_path = os.path.join(file_dir, filename)

                    import base64
                    file_data = base64.b64decode(file_data_b64)
                    with open(file_path, 'wb') as f:
                        f.write(file_data)

                # Insert IIR
                cursor.execute('''
                    INSERT INTO intelligence_reports
                    (operation_id, report_number, submitter, priority, dtg_info_date,
                     dtg_cutoff, target, title, information, filename, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (operation_id, report_number, submitter, priority, dtg_info_date,
                      dtg_cutoff, target, title, information, filename, file_path))

                conn.commit()
                return True, report_number

        except Exception as e:
            from server_logging import ops_logger
            ops_logger.error(f"Error submitting IIR: {e}")
            return False, str(e)

    def get_iirs(self, operation_name: str) -> List[Dict]:
        """Get all IIRs for an operation.

        Returns:
            List of IIR dictionaries
        """
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row

            cursor.execute('''
                SELECT ir.* FROM intelligence_reports ir
                JOIN operations op ON ir.operation_id = op.id
                WHERE op.name = ?
                ORDER BY ir.dtg_submitted DESC
            ''', (operation_name,))

            iirs = []
            for row in cursor.fetchall():
                iirs.append({
                    'id': row['id'],
                    'report_number': row['report_number'],
                    'submitter': row['submitter'],
                    'priority': row['priority'],
                    'dtg_submitted': row['dtg_submitted'],
                    'dtg_info_date': row['dtg_info_date'],
                    'dtg_cutoff': row['dtg_cutoff'],
                    'target': row['target'],
                    'title': row['title'],
                    'information': row['information'],
                    'filename': row['filename']
                })

            return iirs

    def get_iir_file_data(self, iir_id: int) -> Optional[str]:
        """Get base64-encoded file data for an IIR.

        Returns:
            Base64-encoded file data or None
        """
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT file_path FROM intelligence_reports WHERE id = ?', (iir_id,))
            result = cursor.fetchone()

            if not result or not result[0]:
                return None

            file_path = result[0]

            try:
                if not os.path.exists(file_path):
                    return None

                with open(file_path, 'rb') as f:
                    file_data = f.read()

                import base64
                return base64.b64encode(file_data).decode('utf-8')
            except Exception as e:
                from server_logging import ops_logger
                ops_logger.error(f"Error reading IIR file {file_path}: {e}")
                return None
