"""
Database connection management for cheapNPC.

This module provides centralized database connection handling,
configuration, and connection pooling.
"""

import sqlite3
import os
from typing import Optional
from contextlib import contextmanager


class DatabaseConfig:
    """Database configuration settings."""
    
    def __init__(self, db_path: str = "data/village.db"):
        self.db_path = db_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
    
    @property
    def connection_string(self) -> str:
        """Get the database connection string."""
        return self.db_path


class DatabaseConnection:
    """Manages database connections."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection with proper configuration."""
        conn = sqlite3.connect(self.config.connection_string)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    
    @contextmanager
    def get_connection_context(self):
        """Get a database connection with automatic cleanup."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    def test_connection(self) -> bool:
        """Test if the database connection works."""
        try:
            with self.get_connection_context() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_database_connection() -> DatabaseConnection:
    """Get the global database connection instance."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def configure_database(db_path: str):
    """Configure the global database connection."""
    global _db_connection
    _db_connection = DatabaseConnection(DatabaseConfig(db_path))
