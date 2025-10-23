"""
Database migrations and setup for cheapNPC.

This module handles database schema creation, migrations,
and initial setup.
"""

from .connection import get_database_connection


def setup_database():
    """
    Creates the necessary tables: npcs, items, the junction table npc_inventory,
    AND the npc_transactions table for transaction history.
    """
    db_conn = get_database_connection()
    
    with db_conn.get_connection_context() as conn:
        cursor = conn.cursor()

        # NPC Table, storing name, race, profession, and silver_pieces
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS npcs (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                race TEXT NOT NULL,
                profession TEXT NOT NULL,
                profession_skill TEXT,
                silver_pieces INTEGER
            );
        ''')

        # Items Table, storing a unique item name
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        ''')

        # Junction Table: npc_inventory, linking npcs <-> items and holding additional relationship attributes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS npc_inventory (
                npc_id INTEGER,
                item_id INTEGER,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                quality TEXT,
                PRIMARY KEY (npc_id, item_id),
                FOREIGN KEY (npc_id) REFERENCES npcs(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT
            );
        ''')

        # Transaction History Table: npc_transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS npc_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buying_npc_id INTEGER NOT NULL,
                selling_npc_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                quality TEXT,
                transaction_time REAL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (buying_npc_id) REFERENCES npcs(id) ON DELETE CASCADE,
                FOREIGN KEY (selling_npc_id) REFERENCES npcs(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT
            );
        ''')

        conn.commit()
        print(f"Database and all tables set up successfully.")


def reset_database():
    """Reset the database by dropping all tables."""
    db_conn = get_database_connection()
    
    with db_conn.get_connection_context() as conn:
        cursor = conn.cursor()
        
        # Drop tables in reverse dependency order
        cursor.execute("DROP TABLE IF EXISTS npc_transactions")
        cursor.execute("DROP TABLE IF EXISTS npc_inventory")
        cursor.execute("DROP TABLE IF EXISTS items")
        cursor.execute("DROP TABLE IF EXISTS npcs")
        
        conn.commit()
        print("Database reset successfully.")


def check_database_health() -> bool:
    """Check if the database is properly set up."""
    db_conn = get_database_connection()
    
    try:
        with db_conn.get_connection_context() as conn:
            cursor = conn.cursor()
            
            # Check if all required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = {'npcs', 'items', 'npc_inventory', 'npc_transactions'}
            existing_tables = set(tables)
            
            if not required_tables.issubset(existing_tables):
                missing_tables = required_tables - existing_tables
                print(f"Missing tables: {missing_tables}")
                return False
            
            # All required tables exist
            return True
            
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False


# Example usage -- just create tables on direct invocation
if __name__ == '__main__':
    setup_database()
