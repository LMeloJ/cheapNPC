"""
SQLite implementation of the Inventory repository.

This module contains the concrete implementation of inventory data access
operations using SQLite database.
"""

from typing import List, Dict, Any, Union, Tuple
from cheapNPC.models import CrafterNPC, SalesPersonNPC, InventoryEntry, ItemQuality
from .interfaces import InventoryRepository
from ..connection import get_database_connection


class SQLiteInventoryRepository(InventoryRepository):
    """SQLite implementation of inventory repository."""
    
    def __init__(self):
        self.db_conn = get_database_connection()
    
    def update_npc_inventory(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Update an NPC's inventory."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            try:
                # Find NPC ID
                cursor.execute("SELECT id FROM npcs WHERE name = ?", (npc.name,))
                npc_row = cursor.fetchone()
                if not npc_row:
                    return f"Update Failed: NPC '{npc.name}' not found in database."
                
                npc_id = npc_row['id']

                # Update silver and profession/profession_skill
                profession_value = npc.profession.value if hasattr(npc.profession, 'value') else str(npc.profession)
                profession_skill_value = npc.profession_skill.value if hasattr(npc.profession_skill, 'value') else str(npc.profession_skill)
                
                cursor.execute('''
                    UPDATE npcs SET silver_pieces = ?, profession = ?, profession_skill = ?
                    WHERE id = ?
                ''', (
                    npc.silver_pieces,
                    profession_value,
                    profession_skill_value,
                    npc_id
                ))

                # Remove all old inventory
                cursor.execute('DELETE FROM npc_inventory WHERE npc_id = ?', (npc_id,))

                # Insert new inventory
                for entry in npc.inventory:
                    if entry.quantity > 0:
                        item_id = self._get_or_create_item_id(conn, entry.name)
                        quality_val = getattr(entry, "quality", None)
                        if isinstance(quality_val, ItemQuality):
                            quality_val = quality_val.value
                        elif quality_val is not None:
                            quality_val = str(quality_val)
                        
                        cursor.execute('''
                            INSERT INTO npc_inventory (npc_id, item_id, quantity, price, quality)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            npc_id,
                            item_id,
                            entry.quantity,
                            entry.price,
                            quality_val
                        ))
                
                conn.commit()
                return f"Database updated for NPC '{npc.name}' with new inventory and silver: {npc.silver_pieces} SP."
                
            except Exception as e:
                conn.rollback()
                return f"Database Update Error for {npc.name}: {e}"
    
    def get_npc_inventory(self, npc_name: str) -> List[Dict[str, Any]]:
        """Get detailed inventory for a specific NPC."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    i.name as item_name,
                    ni.quantity,
                    ni.price,
                    ni.quality,
                    (ni.quantity * ni.price) as total_value
                FROM npcs n
                JOIN npc_inventory ni ON n.id = ni.npc_id
                JOIN items i ON ni.item_id = i.id
                WHERE n.name = ?
                ORDER BY total_value DESC
            '''
            
            cursor.execute(query, (npc_name,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_npc_initial_inventory(self, npc_name: str) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], float, float]:
        """Get the initial inventory state for an NPC by calculating from transactions."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            # Get current inventory and silver pieces
            current_query = '''
                SELECT 
                    n.silver_pieces,
                    i.name as item_name,
                    ni.quantity,
                    ni.price,
                    ni.quality
                FROM npcs n
                LEFT JOIN npc_inventory ni ON n.id = ni.npc_id
                LEFT JOIN items i ON ni.item_id = i.id
                WHERE n.name = ?
            '''
            cursor.execute(current_query, (npc_name,))
            current_rows = cursor.fetchall()
            
            # Get all transactions for this NPC
            transaction_query = '''
                SELECT 
                    i.name as item_name,
                    CASE 
                        WHEN t.buying_npc_id = (SELECT id FROM npcs WHERE name = ?) THEN t.quantity
                        ELSE -t.quantity
                    END as quantity_change,
                    CASE 
                        WHEN t.buying_npc_id = (SELECT id FROM npcs WHERE name = ?) THEN -(t.quantity * t.price)
                        ELSE (t.quantity * t.price)
                    END as silver_change,
                    t.price,
                    t.quality
                FROM npc_transactions t
                JOIN items i ON t.item_id = i.id
                WHERE t.buying_npc_id = (SELECT id FROM npcs WHERE name = ?) 
                   OR t.selling_npc_id = (SELECT id FROM npcs WHERE name = ?)
                ORDER BY t.transaction_time ASC
            '''
            cursor.execute(transaction_query, (npc_name, npc_name, npc_name, npc_name))
            transaction_rows = cursor.fetchall()
            
            # Get current silver pieces
            current_silver = current_rows[0]['silver_pieces'] if current_rows else 0
            
            # Calculate initial inventory by reversing transactions
            current_inventory = {}
            initial_inventory = {}
            
            # Process current inventory items
            for row in current_rows:
                if row['item_name']:  # Only process rows with items
                    item_name = row['item_name']
                    current_inventory[item_name] = {
                        'quantity': row['quantity'],
                        'price': row['price'],
                        'quality': row['quality']
                    }
            
            # Start with current inventory and subtract all changes to get initial state
            for item_name, item_data in current_inventory.items():
                initial_quantity = item_data['quantity']
                initial_inventory[item_name] = {
                    'quantity': initial_quantity,
                    'price': item_data['price'],
                    'quality': item_data['quality']
                }
            
            # Calculate initial silver pieces by reversing all silver changes
            initial_silver = current_silver
            for tx in transaction_rows:
                initial_silver -= tx['silver_change']
            
            # Subtract all transaction changes to get initial inventory state
            for tx in transaction_rows:
                item_name = tx['item_name']
                quantity_change = tx['quantity_change']
                
                if item_name in initial_inventory:
                    initial_inventory[item_name]['quantity'] -= quantity_change
                else:
                    # Item was completely sold, so initial was the negative of the change
                    initial_inventory[item_name] = {
                        'quantity': -quantity_change,
                        'price': tx['price'],
                        'quality': tx['quality']
                    }
            
            return initial_inventory, current_inventory, initial_silver, current_silver
    
    def exists(self, npc_id: int, item_id: int) -> bool:
        """Check if an inventory entry exists."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM npc_inventory WHERE npc_id = ? AND item_id = ?", (npc_id, item_id))
            return cursor.fetchone() is not None
    
    def _get_or_create_item_id(self, conn, item_name: str) -> int:
        """Get or create item ID by name."""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
        row = cursor.fetchone()
        if row:
            return row['id']
        cursor.execute("INSERT INTO items (name) VALUES (?)", (item_name,))
        return cursor.lastrowid
