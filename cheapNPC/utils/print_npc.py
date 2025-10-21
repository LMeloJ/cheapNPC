import sqlite3
import sys
from typing import List
from pydantic import BaseModel, Field

# --- Database Configuration (Must match other files) ---
DB_NAME = 'data/village.db'

# --- Pydantic Models (Reused for consistent data structure) ---

class ItemBase(BaseModel):
    name: str = Field(description="The name of the unique item.")

class InventoryEntry(ItemBase):
    quantity: int = Field(description="The amount of that item this NPC has.")
    price: float = Field(description="The price in silver pieces this NPC sells it for.")

class MerchantNPC(BaseModel):
    name: str = Field(description="The name of the created NPC.")
    race: str = Field(description="The D&D race of the NPC following the 5e edition.")
    profession: str = Field(description="The NPC's profession.")
    inventory: List[InventoryEntry] = Field(description="The full, detailed inventory of the merchant.")
    silver_pieces: int = Field(description="The amount of silver pieces the NPC has to trade.")

# --- Database Functions ---

def get_db_connection():
    """Returns a connection object to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    # Set row factory to sqlite3.Row to allow accessing columns by name
    conn.row_factory = sqlite3.Row 
    return conn

def get_npc_data(name: str) -> MerchantNPC | None:
    """Retrieves a MerchantNPC object and their full inventory from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT 
            n.name, n.race, n.profession, n.silver_pieces,
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

    if not rows or rows[0]['name'] is None:
        return None

    first_row = rows[0]
    inventory_list: List[InventoryEntry] = []
    
    for row in rows:
        # Check if the NPC has any items (i.e., item_name is not NULL)
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

def print_npc_details(npc: MerchantNPC):
    """Prints the MerchantNPC data in a clean, readable format."""
    
    print("\n" + "="*50)
    print(f" MERCHANT PROFILE: {npc.name.upper()}")
    print("="*50)
    print(f"  Name:       {npc.name}")
    print(f"  Race:       {npc.race}")
    print(f"  Profession: {npc.profession}")
    print(f"  Silver:     {npc.silver_pieces} SP")
    
    print("-" * 50)
    print(" INVENTORY:")
    if not npc.inventory:
        print("  <EMPTY INVENTORY>")
        return

    # Determine maximum width for neat alignment
    max_name_len = max(len(item.name) for item in npc.inventory) if npc.inventory else 0
    
    print(f"  {'ITEM NAME':<{max_name_len+2}} | {'QTY':>4} | {'PRICE (SP)':>10}")
    print(f"  {'-'*(max_name_len+2)}-+-{'-'*4}-+-{'-'*10}")
    
    for item in sorted(npc.inventory, key=lambda x: x.name):
        print(f"  {item.name:<{max_name_len+2}} | {item.quantity:>4} | {item.price:>10.2f}")
    
    print("="*50)


# --- Main Execution ---

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <NPC Name>")
        print("Example: python print_npc.py 'Talin Stonehand'")
        # Exit if no argument is provided
        sys.exit(1)

    # Get NPC name from command-line arguments
    npc_name_to_find = sys.argv[1]
    
    print(f"Searching for NPC '{npc_name_to_find}' in {DB_NAME}...")
    
    npc_data = get_npc_data(npc_name_to_find)
    
    if npc_data:
        print_npc_details(npc_data)
    else:
        print(f"Error: NPC '{npc_name_to_find}' not found in the database.")
        print("Please ensure you have run 'run_agent.py' to populate the database.")
