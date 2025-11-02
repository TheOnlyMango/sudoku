"""Encryption layer for socket communication using Fernet (AES-128)."""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import socket
import os
from typing import Optional


# Shared secret for symmetric encryption
# Read from environment variable or use default (CHANGE THIS IN PRODUCTION!)
SHARED_SECRET = os.environ.get('CHAT_ENCRYPTION_SECRET', 'CHANGE_THIS_SECRET_KEY_IN_PRODUCTION').encode()


def derive_key(password: bytes, salt: bytes = b'sudoku_salt_v1') -> bytes:
    """Derive encryption key from password using PBKDF2.

    Args:
        password: Password bytes
        salt: Salt for key derivation

    Returns:
        32-byte encryption key
    """
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


class EncryptedSocket:
    """Wrapper for socket with encryption."""

    def __init__(self, sock: socket.socket, key: Optional[bytes] = None):
        """Initialize encrypted socket.

        Args:
            sock: Underlying socket
            key: Encryption key (if None, uses shared secret)
        """
        self.sock = sock
        if key is None:
            key = derive_key(SHARED_SECRET)
        self.cipher = Fernet(key)

    def send(self, data: bytes) -> int:
        """Send encrypted data.

        Args:
            data: Data to send

        Returns:
            Number of bytes sent
        """
        # Encrypt the data
        encrypted = self.cipher.encrypt(data)

        # Send length prefix (4 bytes) + encrypted data
        length = len(encrypted)
        length_bytes = length.to_bytes(4, byteorder='big')

        self.sock.sendall(length_bytes + encrypted)
        return len(data)

    def recv(self, bufsize: int = 4096, timeout: Optional[float] = None) -> bytes:
        """Receive and decrypt data.

        Args:
            bufsize: Not used (for compatibility)
            timeout: Optional timeout in seconds

        Returns:
            Decrypted data

        Raises:
            socket.timeout: If timeout occurs
            ValueError: If decryption fails
        """
        if timeout:
            self.sock.settimeout(timeout)

        try:
            # Read length prefix (4 bytes)
            length_bytes = self._recv_exactly(4)
            if not length_bytes:
                return b''

            length = int.from_bytes(length_bytes, byteorder='big')

            # Read encrypted data
            encrypted = self._recv_exactly(length)
            if not encrypted:
                return b''

            # Decrypt
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted

        finally:
            if timeout:
                self.sock.settimeout(None)

    def _recv_exactly(self, n: int) -> bytes:
        """Receive exactly n bytes.

        Args:
            n: Number of bytes to receive

        Returns:
            Exactly n bytes or empty bytes if connection closed
        """
        data = b''
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                return b''
            data += chunk
        return data

    def close(self):
        """Close the socket."""
        self.sock.close()

    def settimeout(self, timeout: Optional[float]):
        """Set socket timeout."""
        self.sock.settimeout(timeout)

    def fileno(self):
        """Get socket file descriptor."""
        return self.sock.fileno()

    def getpeername(self):
        """Get peer address."""
        return self.sock.getpeername()

    def getsockname(self):
        """Get socket address."""
        return self.sock.getsockname()


def wrap_socket(sock: socket.socket, key: Optional[bytes] = None) -> EncryptedSocket:
    """Wrap a socket with encryption.

    Args:
        sock: Socket to wrap
        key: Optional encryption key

    Returns:
        EncryptedSocket instance
    """
    return EncryptedSocket(sock, key)
