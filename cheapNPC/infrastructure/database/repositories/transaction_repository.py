"""
SQLite implementation of the Transaction repository.

This module contains the concrete implementation of transaction data access
operations using SQLite database.
"""

from typing import List, Optional, Dict, Any
from cheapNPC.core.models import TransactionEntry, ItemQuality
from .interfaces import TransactionRepository
from ..connection import get_database_connection


class SQLiteTransactionRepository(TransactionRepository):
    """SQLite implementation of transaction repository."""
    
    def __init__(self):
        self.db_conn = get_database_connection()
    
    def record_transaction(
        self,
        buying_npc: str,
        selling_npc: str,
        item_name: str,
        quantity: int,
        price: float,
        quality: Optional[str] = None,
        transaction_time: Optional[float] = None
    ) -> str:
        """Record a transaction between NPCs."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()

            try:
                buying_npc_id = self._get_npc_id_by_name(conn, buying_npc)
                selling_npc_id = self._get_npc_id_by_name(conn, selling_npc)
                if buying_npc_id is None or selling_npc_id is None:
                    return f"Could not find buying or selling NPC by provided name."

                item_id = self._get_or_create_item_id(conn, item_name)

                if isinstance(quality, ItemQuality):
                    quality_val = quality.value
                elif quality is not None:
                    quality_val = str(quality)
                else:
                    quality_val = None

                if transaction_time is not None:
                    cursor.execute('''
                        INSERT INTO npc_transactions (buying_npc_id, selling_npc_id, item_id, quantity, price, quality, transaction_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        buying_npc_id,
                        selling_npc_id,
                        item_id,
                        quantity,
                        price,
                        quality_val,
                        transaction_time
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO npc_transactions (buying_npc_id, selling_npc_id, item_id, quantity, price, quality)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        buying_npc_id,
                        selling_npc_id,
                        item_id,
                        quantity,
                        price,
                        quality_val
                    ))

                conn.commit()
                return "Transaction recorded successfully."
            except Exception as e:
                conn.rollback()
                return f"Failed to record transaction: {e}"
    
    def get_transaction_history_between(
        self, 
        npc1: str, 
        npc2: str
    ) -> List[TransactionEntry]:
        """Get transaction history between two NPCs."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            transactions: List[TransactionEntry] = []

            try:
                npc1_id = self._get_npc_id_by_name(conn, npc1)
                npc2_id = self._get_npc_id_by_name(conn, npc2)

                if npc1_id is None or npc2_id is None:
                    return []

                query = '''
                    SELECT 
                        t.*, 
                        i.name as item_name, 
                        n_buy.name as buying_npc_name, 
                        n_sell.name as selling_npc_name 
                    FROM npc_transactions t
                    JOIN items i ON t.item_id = i.id
                    JOIN npcs n_buy ON t.buying_npc_id = n_buy.id
                    JOIN npcs n_sell ON t.selling_npc_id = n_sell.id
                    WHERE 
                        (t.buying_npc_id = ? AND t.selling_npc_id = ?)
                        OR (t.buying_npc_id = ? AND t.selling_npc_id = ?)
                    ORDER BY t.transaction_time DESC, t.id DESC
                '''
                cursor.execute(query, (npc1_id, npc2_id, npc2_id, npc1_id))
                rows = cursor.fetchall()

                for row in rows:
                    # Build TransactionEntry
                    quality_val = row['quality']
                    try:
                        quality_obj = ItemQuality(quality_val) if quality_val else None
                    except Exception:
                        quality_obj = None

                    transactions.append(TransactionEntry(
                        name=row['item_name'],
                        quantity=row['quantity'],
                        price=row['price'],
                        description="",  # Not stored in transaction table
                        created_by="",   # Not stored in transaction table
                        creation_time=row['transaction_time'],
                        quality=quality_obj if quality_obj else ItemQuality.regular,
                        buying_npc=row['buying_npc_name'],
                        selling_npc=row['selling_npc_name']
                    ))
                return transactions

            finally:
                pass  # Connection is closed by context manager
    
    def get_npc_transaction_count(self, npc_name: str) -> int:
        """Get total number of transactions for an NPC."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT COUNT(*) as total
                FROM npc_transactions t
                JOIN npcs n_buy ON t.buying_npc_id = n_buy.id
                JOIN npcs n_sell ON t.selling_npc_id = n_sell.id
                WHERE n_buy.name = ? OR n_sell.name = ?
            '''
            
            cursor.execute(query, (npc_name, npc_name))
            result = cursor.fetchone()
            return result['total'] if result else 0
    
    def get_npc_transaction_history_paginated(
        self, 
        npc_name: str, 
        limit: int = 5, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get paginated transaction history for an NPC."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    t.*,
                    i.name as item_name,
                    n_buy.name as buyer_name,
                    n_sell.name as seller_name,
                    datetime(t.transaction_time, 'unixepoch') as transaction_datetime
                FROM npc_transactions t
                JOIN items i ON t.item_id = i.id
                JOIN npcs n_buy ON t.buying_npc_id = n_buy.id
                JOIN npcs n_sell ON t.selling_npc_id = n_sell.id
                WHERE n_buy.name = ? OR n_sell.name = ?
                ORDER BY t.transaction_time DESC, t.id DESC
                LIMIT ? OFFSET ?
            '''
            
            cursor.execute(query, (npc_name, npc_name, limit, offset))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def exists(self, transaction_id: int) -> bool:
        """Check if a transaction exists by ID."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM npc_transactions WHERE id = ?", (transaction_id,))
            return cursor.fetchone() is not None
    
    def _get_npc_id_by_name(self, conn, npc_name: str) -> Optional[int]:
        """Get NPC ID by name."""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM npcs WHERE name = ?", (npc_name,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        return None
    
    def _get_or_create_item_id(self, conn, item_name: str) -> int:
        """Get or create item ID by name."""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
        row = cursor.fetchone()
        if row:
            return row['id']
        cursor.execute("INSERT INTO items (name) VALUES (?)", (item_name,))
        return cursor.lastrowid
