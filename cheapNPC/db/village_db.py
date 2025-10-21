import sqlite3
from typing import List
from pydantic import BaseModel, Field
from agents import function_tool

# --- Pydantic Models for Data Structure and Retrieval ---

# 1. Base Item Model (What defines a unique item, independent of any NPC)
class ItemBase(BaseModel):
    name: str = Field(description="The name of the unique item.")

# 2. Inventory Entry Model (What an NPC holds - includes relationship attributes)
class InventoryEntry(ItemBase):
    quantity: int = Field(description="The amount of that item this NPC has.")
    price: float = Field(description="The price in silver pieces this NPC sells it for.")

# 3. Main NPC Model (Used for retrieval, includes the list of InventoryEntry)
class MerchantNPC(BaseModel):
    name: str = Field(description="The name of the created NPC.")
    race: str = Field(description="The D&D race of the NPC.")
    profession: str = Field(description="The NPC's profession.")
    inventory: List[InventoryEntry] = Field(description="The full, detailed inventory of the merchant.")
    silver_pieces: int = Field(description="The amount of silver pieces the NPC has to trade.")

# --- SQLite Database Helper ---

DB_NAME = 'data/village.db'

def get_db_connection():
    """Returns a connection object to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    # Set row factory to sqlite3.Row for easier column access by name
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Creates the three necessary tables: npcs, items, and the junction table npc_inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. NPCs Table (Primary entity 1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS npcs (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            race TEXT NOT NULL,
            profession TEXT NOT NULL,
            silver_pieces INTEGER
        )
    ''')

    # 2. Items Table (Primary entity 2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # 3. Junction Table (n:n Relationship)
    # This table links NPCs and Items and holds the relationship attributes (quantity/price).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS npc_inventory (
            npc_id INTEGER,
            item_id INTEGER,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            PRIMARY KEY (npc_id, item_id),
            FOREIGN KEY (npc_id) REFERENCES npcs(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' and all tables set up successfully.")

def get_or_create_item_id(conn, item_name: str) -> int:
    """Checks if an item exists, inserts it if not, and returns its ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
    row = cursor.fetchone()
    if row:
        return row['id']
    else:
        cursor.execute("INSERT INTO items (name) VALUES (?)", (item_name,))
        return cursor.lastrowid

# --- The Agent Tool Function ---
@function_tool
def save_merchant_to_db(npc_data: MerchantNPC) -> str:
    """
    Saves a complete MerchantNPC object and its detailed inventory to the SQLite database
    using a normalized three-table structure (npcs, items, npc_inventory).
    This function is automatically called by the generative model.
    """
    print(f"\n[TOOL CALLED] Attempting to save NPC: {npc_data.name}")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print(npc_data)
        # 1. Insert NPC data and get the NPC ID
        cursor.execute('''
            INSERT INTO npcs (name, race, profession, silver_pieces)
            VALUES (?, ?, ?, ?)
        ''', (npc_data.name, npc_data.race, npc_data.profession, npc_data.silver_pieces))
        
        npc_id = cursor.lastrowid
        
        # 2. Populate Junction Table (npc_inventory)
        for entry in npc_data.inventory:
            # Ensure the unique item exists in the 'items' table and get its ID
            item_id = get_or_create_item_id(conn, entry.name)

            # Insert the relationship details into the junction table
            cursor.execute('''
                INSERT INTO npc_inventory (npc_id, item_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (npc_id, item_id, entry.quantity, entry.price))

        conn.commit()
        return f"NPC '{npc_data.name}' ({npc_data.profession}) saved to database successfully."

    except sqlite3.IntegrityError as e:
        conn.rollback()
        return f"Error: NPC with name '{npc_data.name}' already exists. Transaction rolled back. {e}"
    except Exception as e:
        conn.rollback()
        return f"An unexpected database error occurred: {e}. Transaction rolled back."
    finally:
        conn.close()


@function_tool
def get_npc_with_inventory(name: str) -> MerchantNPC:
    """
    TOOL: Retrieves a MerchantNPC object and their full inventory from the database.
    
    Args:
        name: The name of the NPC to retrieve.
        
    Returns:
        The MerchantNPC object or a dictionary indicating failure.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT 
            n.name, n.race, n.profession, n.silver_pieces, n.id AS npc_id,
            i.name AS item_name,
            ni.quantity, ni.price
        FROM npcs n
        LEFT JOIN npc_inventory ni ON n.id = ni.npc_id
        LEFT JOIN items i ON ni.item_id = i.id
        WHERE n.name = ?
    '''
    
    cursor.execute(query, (name,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        # Must return an object that can be handled by the LLM as a structured response
        return MerchantNPC(name=name, race="Unknown", profession="None", inventory=[], silver_pieces=0) 

    first_row = rows[0]
    inventory_list: List[InventoryEntry] = []
    
    for row in rows:
        if row['item_name']:
            inventory_list.append(InventoryEntry(
                name=row['item_name'],
                quantity=row['quantity'],
                price=row['price']
            ))

    return MerchantNPC(
        name=first_row['name'],
        race=first_row['race'],
        profession=first_row['profession'],
        silver_pieces=first_row['silver_pieces'],
        inventory=inventory_list
    )


@function_tool
def update_npc_inventory(data: MerchantNPC) -> str:
    """
    TOOL: Updates an NPC's silver count and entirely replaces their inventory 
    in the database based on the final state of the MerchantNPC object.
    
    Args:
        data: The MerchantNPC object containing the final, post-trade inventory and silver.
        
    Returns:
        A status message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Get NPC ID and update silver count
        cursor.execute("SELECT id FROM npcs WHERE name = ?", (data.name,))
        npc_row = cursor.fetchone()
        if not npc_row:
            return f"Update Failed: NPC '{data.name}' not found in database."
        
        npc_id = npc_row['id']
        
        # Update silver pieces
        cursor.execute('''
            UPDATE npcs SET silver_pieces = ?
            WHERE id = ?
        ''', (data.silver_pieces, npc_id))
        
        # 2. Delete existing inventory entries for this NPC
        cursor.execute('DELETE FROM npc_inventory WHERE npc_id = ?', (npc_id,))
        
        # 3. Insert new inventory entries
        for entry in data.inventory:
            item_id = get_or_create_item_id(conn, entry.name) # Ensure item exists
            
            # Skip items with zero quantity after the trade
            if entry.quantity > 0:
                cursor.execute('''
                    INSERT INTO npc_inventory (npc_id, item_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (npc_id, item_id, entry.quantity, entry.price))

        conn.commit()
        return f"Database updated for NPC '{data.name}' with new inventory and silver: {data.silver_pieces} SP."

    except Exception as e:
        conn.rollback()
        return f"Database Update Error for {data.name}: {e}"
    finally:
        conn.close()


# --- Example Usage ---

if __name__ == '__main__':
    # 1. Set up the database and tables
    setup_database()