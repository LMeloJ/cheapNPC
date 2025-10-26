"""
SQLite implementation of the Item repository.

This module contains the concrete implementation of item data access
operations using SQLite database.
"""

from typing import List, Optional
from cheapNPC.models import ItemBase
from .interfaces import ItemRepository
from ..connection import get_database_connection


class SQLiteItemRepository(ItemRepository):
    """SQLite implementation of item repository."""
    
    def __init__(self):
        self.db_conn = get_database_connection()
    
    def get_or_create(self, name: str) -> int:
        """Get item ID by name, creating if it doesn't exist."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM items WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return row['id']
            cursor.execute("INSERT INTO items (name) VALUES (?)", (name,))
            return cursor.lastrowid
    
    def get_by_name(self, name: str) -> Optional[ItemBase]:
        """Get an item by name."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return ItemBase(
                    name=row['name'],
                    description="",  # Not stored in current schema
                    created_by="",   # Not stored in current schema
                    creation_time=0.0  # Not stored in current schema
                )
            return None
    
    def get_all(self) -> List[ItemBase]:
        """Get all items."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items ORDER BY name")
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                items.append(ItemBase(
                    name=row['name'],
                    description="",  # Not stored in current schema
                    created_by="",   # Not stored in current schema
                    creation_time=0.0  # Not stored in current schema
                ))
            return items
    
    def exists(self, name: str) -> bool:
        """Check if an item exists by name."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM items WHERE name = ?", (name,))
            return cursor.fetchone() is not None
