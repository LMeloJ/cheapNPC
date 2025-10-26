"""
Inventory service controller for cheapNPC MVC architecture.

This controller handles business logic for inventory operations,
including inventory management and analysis.
"""

from typing import List, Dict, Any, Tuple
from cheapNPC.models import CrafterNPC, SalesPersonNPC
from cheapNPC.infrastructure.database.repositories import get_inventory_repository, get_npc_repository


class InventoryService:
    """Controller for inventory business logic."""
    
    def __init__(self):
        self.inventory_repository = get_inventory_repository()
        self.npc_repository = get_npc_repository()
    
    def update_npc_inventory(self, npc: CrafterNPC | SalesPersonNPC) -> str:
        """Update an NPC's inventory."""
        return self.inventory_repository.update_npc_inventory(npc)
    
    def get_npc_inventory(self, npc_name: str) -> List[Dict[str, Any]]:
        """Get detailed inventory for a specific NPC."""
        return self.inventory_repository.get_npc_inventory(npc_name)
    
    def get_npc_initial_inventory(self, npc_name: str) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], float, float]:
        """Get the initial inventory state for an NPC."""
        return self.inventory_repository.get_npc_initial_inventory(npc_name)
    
    def create_inventory_comparison_table(self, npc_name: str) -> List[List[str]]:
        """Create a comparison table showing initial vs current inventory with changes."""
        initial_inv, current_inv, initial_silver, current_silver = self.get_npc_initial_inventory(npc_name)
        
        # Get all unique items
        all_items = set(initial_inv.keys()) | set(current_inv.keys())
        
        comparison_data = []
        
        # Add silver pieces row first
        silver_change = current_silver - initial_silver
        if silver_change > 0:
            silver_change_str = f"🟢 +{silver_change:.2f}"
        elif silver_change < 0:
            silver_change_str = f"🔴 {silver_change:.2f}"
        else:
            silver_change_str = "⚪ 0.00"
        
        comparison_data.append([
            "💰 Silver Pieces",
            f"{initial_silver:.2f}",
            f"{current_silver:.2f}",
            silver_change_str,
            "1.00",  # Silver pieces are always 1 SP per piece
            "Currency"
        ])
        
        # Add separator row
        comparison_data.append([
            "─" * 20,
            "─" * 10,
            "─" * 10,
            "─" * 10,
            "─" * 10,
            "─" * 10
        ])
        
        # Add inventory items
        for item_name in sorted(all_items):
            initial_qty = initial_inv.get(item_name, {}).get('quantity', 0)
            current_qty = current_inv.get(item_name, {}).get('quantity', 0)
            change = current_qty - initial_qty
            
            # Get price and quality from current inventory (or initial if not in current)
            price = current_inv.get(item_name, {}).get('price', initial_inv.get(item_name, {}).get('price', 0))
            quality = current_inv.get(item_name, {}).get('quality', initial_inv.get(item_name, {}).get('quality', 'Regular'))
            
            # Format change with simple text indicators
            if change > 0:
                change_str = f"🟢 +{change}"
            elif change < 0:
                change_str = f"🔴 {change}"
            else:
                change_str = "⚪ 0"
            
            comparison_data.append([
                item_name,
                str(initial_qty),
                str(current_qty),
                change_str,
                f"{price:.2f}",
                quality or 'Regular'
            ])
        
        return comparison_data
    
    def get_npc_overview_table(self) -> List[List[str]]:
        """Create a table showing NPC overview data."""
        npcs = self.npc_repository.get_all_with_inventories()
        table_data = []
        
        for npc in npcs:
            inventory_count = len(npc.inventory)
            inventory_value = sum(item.quantity * item.price for item in npc.inventory)
            
            # Get trade count
            from cheapNPC.infrastructure.database.repositories import get_transaction_repository
            transaction_repo = get_transaction_repository()
            trade_count = transaction_repo.get_npc_transaction_count(npc.name)
            
            # Format profession to show only the profession name
            profession_str = str(npc.profession)
            if "." in profession_str:
                profession_str = profession_str.split(".")[-1]
            
            table_data.append([
                npc.name,
                f"{npc.silver_pieces:.2f}",
                str(trade_count),
                profession_str,
                npc.race,
                str(inventory_count),
                f"{inventory_value:.2f}"
            ])
        
        return table_data
    
    def format_trade_history_table(self, transactions: List[Dict[str, Any]], selected_npc: str = "") -> List[List[str]]:
        """Format transaction data for display in a table."""
        table_data = []
        
        for tx in transactions:
            # Determine if this NPC was the buyer or seller
            npc_role = "Buyer" if tx['buyer_name'] == selected_npc else "Seller"
            other_npc = tx['seller_name'] if npc_role == "Buyer" else tx['buyer_name']
            
            # Format transaction details
            total_value = tx['quantity'] * tx['price']
            
            table_data.append([
                tx['transaction_datetime'][:16],  # Format datetime
                npc_role,
                other_npc,
                tx['item_name'],
                str(tx['quantity']),
                f"{tx['price']:.2f}",
                f"{total_value:.2f}",
                tx['quality'] or 'Regular'
            ])
        
        return table_data
