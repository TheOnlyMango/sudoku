"""Database connection pool for thread-safe database access."""

import sqlite3
import threading
from contextlib import contextmanager
from queue import Queue, Empty
from typing import Generator


class DatabasePool:
    """Connection pool for SQLite database."""

    def __init__(self, db_path: str, pool_size: int = 5):
        """Initialize database connection pool.

        Args:
            db_path: Path to SQLite database file
            pool_size: Number of connections to maintain in pool
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool: Queue = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._closed = False

        # Create initial connections
        for _ in range(pool_size):
            conn = self._create_connection()
            self.pool.put(conn)

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    @contextmanager
    def get_connection(self, timeout: float = 5.0) -> Generator[sqlite3.Connection, None, None]:
        """Get a connection from the pool.

        Args:
            timeout: Maximum time to wait for a connection

        Yields:
            Database connection

        Raises:
            Empty: If no connection available within timeout
        """
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        conn = None
        try:
            # Get connection from pool
            conn = self.pool.get(timeout=timeout)
            yield conn
            conn.commit()  # Auto-commit on successful context exit
        except Exception as e:
            if conn:
                conn.rollback()  # Auto-rollback on error
            raise
        finally:
            if conn and not self._closed:
                # Return connection to pool
                self.pool.put(conn)

    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            if self._closed:
                return

            self._closed = True

            # Close all connections
            while not self.pool.empty():
                try:
                    conn = self.pool.get_nowait()
                    conn.close()
                except Empty:
                    break

    def __del__(self):
        """Cleanup on deletion."""
        self.close_all()


# Singleton pools for each database
_pools = {}
_pools_lock = threading.Lock()


def get_pool(db_path: str, pool_size: int = 5) -> DatabasePool:
    """Get or create a connection pool for a database.

    Args:
        db_path: Path to database file
        pool_size: Size of connection pool

    Returns:
        DatabasePool instance
    """
    with _pools_lock:
        if db_path not in _pools:
            _pools[db_path] = DatabasePool(db_path, pool_size)
        return _pools[db_path]


def close_all_pools():
    """Close all database pools."""
    with _pools_lock:
        for pool in _pools.values():
            pool.close_all()
        _pools.clear()
