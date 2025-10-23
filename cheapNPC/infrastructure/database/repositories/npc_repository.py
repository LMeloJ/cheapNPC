"""
SQLite implementation of the NPC repository.

This module contains the concrete implementation of NPC data access
operations using SQLite database.
"""

from typing import List, Optional, Union
from cheapNPC.core.models import NPC, CrafterNPC, SalesPersonNPC, InventoryEntry, ItemQuality, ProfessionSkill
from .interfaces import NPCRepository
from ..connection import get_database_connection


class SQLiteNPCRepository(NPCRepository):
    """SQLite implementation of NPC repository."""
    
    def __init__(self):
        self.db_conn = get_database_connection()
    
    def save(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Save an NPC to the database."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            try:
                # Handle profession as enum value
                profession_value = npc.profession.value if hasattr(npc.profession, 'value') else str(npc.profession)
                profession_skill_value = npc.profession_skill.value if hasattr(npc.profession_skill, 'value') else str(npc.profession_skill)
                
                cursor.execute('''
                    INSERT INTO npcs (name, race, profession, profession_skill, silver_pieces)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    npc.name,
                    npc.race,
                    profession_value,
                    profession_skill_value,
                    npc.silver_pieces
                ))
                npc_id = cursor.lastrowid

                # Save inventory
                for entry in npc.inventory:
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

                # Save customer history if present
                customer_history = getattr(npc, "customer_history", None)
                if customer_history:
                    for tx in customer_history:
                        buying_npc_id = self._get_npc_id_by_name(conn, tx.buying_npc)
                        selling_npc_id = self._get_npc_id_by_name(conn, tx.selling_npc)
                        if buying_npc_id is None or selling_npc_id is None:
                            continue
                        
                        item_id = self._get_or_create_item_id(conn, tx.name)
                        quality_tx = getattr(tx, "quality", None)
                        if isinstance(quality_tx, ItemQuality):
                            quality_tx = quality_tx.value
                        elif quality_tx is not None:
                            quality_tx = str(quality_tx)
                        
                        cursor.execute('''
                            INSERT INTO npc_transactions 
                                (buying_npc_id, selling_npc_id, item_id, quantity, price, quality)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            buying_npc_id,
                            selling_npc_id,
                            item_id,
                            tx.quantity,
                            tx.price,
                            quality_tx
                        ))

                conn.commit()
                return f"NPC '{npc.name}' ({profession_value}) saved to database successfully."
                
            except Exception as e:
                conn.rollback()
                return f"An unexpected database error occurred: {e}. Transaction rolled back."
    
    def get_by_name(self, name: str) -> Optional[Union[CrafterNPC, SalesPersonNPC]]:
        """Get an NPC by name."""
        return self.get_with_inventory(name)
    
    def get_all(self) -> List[Union[CrafterNPC, SalesPersonNPC]]:
        """Get all NPCs."""
        return self.get_all_with_inventories()
    
    def update(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Update an existing NPC."""
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
    
    def delete(self, name: str) -> bool:
        """Delete an NPC by name."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM npcs WHERE name = ?", (name,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception:
                conn.rollback()
                return False
    
    def exists(self, name: str) -> bool:
        """Check if an NPC exists by name."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM npcs WHERE name = ?", (name,))
            return cursor.fetchone() is not None
    
    def get_with_inventory(self, name: str) -> Optional[Union[CrafterNPC, SalesPersonNPC]]:
        """Get an NPC with their complete inventory."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT 
                    n.name, n.race, n.profession, n.profession_skill, n.silver_pieces,
                    n.id as npc_id,
                    i.name as item_name,
                    ni.quantity, ni.price, ni.quality
                FROM npcs n
                LEFT JOIN npc_inventory ni ON n.id = ni.npc_id
                LEFT JOIN items i ON ni.item_id = i.id
                WHERE n.name = ?
            '''
            cursor.execute(query, (name,))
            rows = cursor.fetchall()

            if not rows:
                return None

            first_row = rows[0]
            inventory: List[InventoryEntry] = []

            for row in rows:
                if row['item_name']:
                    quality_val = row['quality']
                    item_quality = None
                    if quality_val:
                        try:
                            item_quality = ItemQuality(quality_val)
                        except Exception:
                            item_quality = None
                    
                    inventory.append(InventoryEntry(
                        name=row['item_name'],
                        quantity=row['quantity'],
                        price=row['price'],
                        description="",
                        created_by="",
                        creation_time=0.0,
                        quality=item_quality if item_quality else ItemQuality.regular
                    ))

            profession_skill_val = first_row['profession_skill']
            profession_val = first_row['profession']
            
            # Determine NPC type based on profession
            from cheapNPC.core.models import CraftAndGatherProfessions, SalesPersonProfession
            
            try:
                # Try to create as CrafterNPC first
                craft_profession = CraftAndGatherProfessions(profession_val)
                return CrafterNPC(
                    name=first_row['name'],
                    race=first_row['race'],
                    profession=craft_profession,
                    profession_skill=ProfessionSkill(profession_skill_val) if profession_skill_val else ProfessionSkill.regular,
                    inventory=inventory,
                    silver_pieces=first_row['silver_pieces'],
                    known_recipes=[]
                )
            except ValueError:
                try:
                    # Try to create as SalesPersonNPC
                    sales_profession = SalesPersonProfession(profession_val)
                    return SalesPersonNPC(
                        name=first_row['name'],
                        race=first_row['race'],
                        profession=sales_profession,
                        profession_skill=ProfessionSkill(profession_skill_val) if profession_skill_val else ProfessionSkill.regular,
                        inventory=inventory,
                        silver_pieces=first_row['silver_pieces'],
                        customer_history=[]
                    )
                except ValueError:
                    # Fallback to CrafterNPC with blacksmith profession
                    return CrafterNPC(
                        name=first_row['name'],
                        race=first_row['race'],
                        profession=CraftAndGatherProfessions.blacksmith,
                        profession_skill=ProfessionSkill(profession_skill_val) if profession_skill_val else ProfessionSkill.regular,
                        inventory=inventory,
                        silver_pieces=first_row['silver_pieces'],
                        known_recipes=[]
                    )
    
    def get_all_with_inventories(self) -> List[Union[CrafterNPC, SalesPersonNPC]]:
        """Get all NPCs with their complete inventories."""
        with self.db_conn.get_connection_context() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT 
                    n.name, n.race, n.profession, n.profession_skill, n.silver_pieces,
                    n.id as npc_id,
                    i.name as item_name,
                    ni.quantity, ni.price, ni.quality
                FROM npcs n
                LEFT JOIN npc_inventory ni ON n.id = ni.npc_id
                LEFT JOIN items i ON ni.item_id = i.id
                ORDER BY n.name, i.name
            '''
            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                return []

            # Group rows by NPC
            npcs_data = {}
            for row in rows:
                npc_name = row['name']
                if npc_name not in npcs_data:
                    npcs_data[npc_name] = {
                        'info': row,
                        'inventory': []
                    }
                
                # Add inventory item if it exists
                if row['item_name']:
                    quality_val = row['quality']
                    item_quality = None
                    if quality_val:
                        try:
                            item_quality = ItemQuality(quality_val)
                        except Exception:
                            item_quality = None
                    
                    npcs_data[npc_name]['inventory'].append(InventoryEntry(
                        name=row['item_name'],
                        quantity=row['quantity'],
                        price=row['price'],
                        description="",
                        created_by="",
                        creation_time=0.0,
                        quality=item_quality if item_quality else ItemQuality.regular
                    ))

            # Convert to NPC objects
            npcs = []
            from cheapNPC.core.models import CraftAndGatherProfessions, SalesPersonProfession
            
            for npc_name, data in npcs_data.items():
                info = data['info']
                inventory = data['inventory']
                
                profession_skill_val = info['profession_skill']
                profession_val = info['profession']
                
                try:
                    # Try to create as CrafterNPC first
                    craft_profession = CraftAndGatherProfessions(profession_val)
                    npc = CrafterNPC(
                        name=info['name'],
                        race=info['race'],
                        profession=craft_profession,
                        profession_skill=ProfessionSkill(profession_skill_val) if profession_skill_val else ProfessionSkill.regular,
                        inventory=inventory,
                        silver_pieces=info['silver_pieces'],
                        known_recipes=[]
                    )
                except ValueError:
                    try:
                        # Try to create as SalesPersonNPC
                        sales_profession = SalesPersonProfession(profession_val)
                        npc = SalesPersonNPC(
                            name=info['name'],
                            race=info['race'],
                            profession=sales_profession,
                            profession_skill=ProfessionSkill(profession_skill_val) if profession_skill_val else ProfessionSkill.regular,
                            inventory=inventory,
                            silver_pieces=info['silver_pieces'],
                            customer_history=[]
                        )
                    except ValueError:
                        # Fallback to CrafterNPC with blacksmith profession
                        npc = CrafterNPC(
                            name=info['name'],
                            race=info['race'],
                            profession=CraftAndGatherProfessions.blacksmith,
                            profession_skill=ProfessionSkill(profession_skill_val) if profession_skill_val else ProfessionSkill.regular,
                            inventory=inventory,
                            silver_pieces=info['silver_pieces'],
                            known_recipes=[]
                        )
                
                npcs.append(npc)
            
            return npcs
    
    def _get_or_create_item_id(self, conn, item_name: str) -> int:
        """Get or create item ID by name."""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
        row = cursor.fetchone()
        if row:
            return row['id']
        cursor.execute("INSERT INTO items (name) VALUES (?)", (item_name,))
        return cursor.lastrowid
    
    def _get_npc_id_by_name(self, conn, npc_name: str) -> Optional[int]:
        """Get NPC ID by name."""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM npcs WHERE name = ?", (npc_name,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        return None
