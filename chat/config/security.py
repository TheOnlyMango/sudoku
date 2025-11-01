"""Security configuration and utilities for chat system."""

import hashlib
import secrets
import time
from typing import Dict, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import threading

# File upload security settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {
    # Documents
    'application/pdf': ['.pdf'],
    'text/plain': ['.txt', '.log', '.md'],
    'text/markdown': ['.md'],

    # Images
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp'],

    # Archives
    'application/zip': ['.zip'],
    'application/x-tar': ['.tar'],
    'application/gzip': ['.gz', '.tgz'],

    # Code/Config
    'application/json': ['.json'],
    'text/x-python': ['.py'],
    'text/x-sh': ['.sh'],
    'application/x-yaml': ['.yaml', '.yml'],
}

# Rate limiting settings
MESSAGE_RATE_LIMIT = 10  # messages per window
MESSAGE_RATE_WINDOW = 60  # seconds
FILE_RATE_LIMIT = 3  # uploads per window
FILE_RATE_WINDOW = 300  # seconds (5 minutes)

# Buffer limits
MAX_BUFFER_SIZE = 10 * 1024 * 1024  # 10 MB max buffer
MAX_MESSAGE_LENGTH = 4096  # 4 KB per message


class TokenManager:
    """Manages authentication tokens for users."""

    def __init__(self):
        self.tokens: Dict[str, Tuple[str, datetime]] = {}  # token -> (username, expiry)
        self.user_tokens: Dict[str, str] = {}  # username -> token
        self.lock = threading.Lock()
        self.token_lifetime = timedelta(hours=24)

    def generate_token(self, username: str) -> str:
        """Generate a secure token for a user."""
        with self.lock:
            # Invalidate old token if exists
            if username in self.user_tokens:
                old_token = self.user_tokens[username]
                if old_token in self.tokens:
                    del self.tokens[old_token]

            # Generate new token
            token = secrets.token_urlsafe(32)
            expiry = datetime.now() + self.token_lifetime

            self.tokens[token] = (username, expiry)
            self.user_tokens[username] = token

            return token

    def verify_token(self, token: str) -> Tuple[bool, str]:
        """Verify a token and return (is_valid, username)."""
        with self.lock:
            if token not in self.tokens:
                return False, ""

            username, expiry = self.tokens[token]

            # Check if expired
            if datetime.now() > expiry:
                del self.tokens[token]
                if username in self.user_tokens and self.user_tokens[username] == token:
                    del self.user_tokens[username]
                return False, ""

            return True, username

    def invalidate_token(self, token: str):
        """Invalidate a token."""
        with self.lock:
            if token in self.tokens:
                username, _ = self.tokens[token]
                del self.tokens[token]
                if username in self.user_tokens and self.user_tokens[username] == token:
                    del self.user_tokens[username]

    def cleanup_expired(self):
        """Remove expired tokens."""
        with self.lock:
            now = datetime.now()
            expired_tokens = [
                token for token, (_, expiry) in self.tokens.items()
                if now > expiry
            ]

            for token in expired_tokens:
                username, _ = self.tokens[token]
                del self.tokens[token]
                if username in self.user_tokens and self.user_tokens[username] == token:
                    del self.user_tokens[username]


class RateLimiter:
    """Rate limiting for messages and file uploads."""

    def __init__(self):
        self.message_counts: Dict[str, list] = defaultdict(list)
        self.file_counts: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def check_message_rate(self, username: str) -> Tuple[bool, str]:
        """Check if user is within message rate limit."""
        with self.lock:
            now = time.time()
            cutoff = now - MESSAGE_RATE_WINDOW

            # Clean old entries
            self.message_counts[username] = [
                t for t in self.message_counts[username] if t > cutoff
            ]

            # Check limit
            if len(self.message_counts[username]) >= MESSAGE_RATE_LIMIT:
                return False, f"Rate limit exceeded. Max {MESSAGE_RATE_LIMIT} messages per {MESSAGE_RATE_WINDOW}s"

            # Add this message
            self.message_counts[username].append(now)
            return True, ""

    def check_file_rate(self, username: str) -> Tuple[bool, str]:
        """Check if user is within file upload rate limit."""
        with self.lock:
            now = time.time()
            cutoff = now - FILE_RATE_WINDOW

            # Clean old entries
            self.file_counts[username] = [
                t for t in self.file_counts[username] if t > cutoff
            ]

            # Check limit
            if len(self.file_counts[username]) >= FILE_RATE_LIMIT:
                return False, f"Upload rate limit exceeded. Max {FILE_RATE_LIMIT} uploads per {FILE_RATE_WINDOW}s"

            # Add this upload
            self.file_counts[username].append(now)
            return True, ""


def validate_file_upload(filename: str, file_data: bytes) -> Tuple[bool, str]:
    """Validate file upload against security policies.

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    if len(file_data) > MAX_FILE_SIZE:
        return False, f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.1f} MB"

    # Check file extension
    import os
    ext = os.path.splitext(filename)[1].lower()

    # Validate extension against allowed MIME types
    allowed = False
    for mime_type, extensions in ALLOWED_MIME_TYPES.items():
        if ext in extensions:
            allowed = True
            break

    if not allowed:
        return False, f"File type not allowed: {ext}"

    # Basic content validation (check magic bytes for common types)
    if ext in ['.jpg', '.jpeg']:
        if not file_data.startswith(b'\xff\xd8\xff'):
            return False, "Invalid JPEG file"
    elif ext == '.png':
        if not file_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return False, "Invalid PNG file"
    elif ext == '.pdf':
        if not file_data.startswith(b'%PDF-'):
            return False, "Invalid PDF file"
    elif ext == '.zip':
        if not file_data.startswith(b'PK\x03\x04') and not file_data.startswith(b'PK\x05\x06'):
            return False, "Invalid ZIP file"

    return True, ""


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and other attacks."""
    import os
    import re

    # Remove any path components
    filename = os.path.basename(filename)

    # Remove potentially dangerous characters
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    filename = name + ext

    return filename
