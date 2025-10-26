"""
Trading service controller for cheapNPC MVC architecture.

This controller handles business logic for trading operations,
including transaction recording and history management.
"""

from typing import List, Optional, Dict, Any
from cheapNPC.models import TransactionEntry, NegotiationResult, ItemQuality
from cheapNPC.infrastructure.database.repositories import get_transaction_repository, get_npc_repository


class TradingService:
    """Controller for trading business logic."""
    
    def __init__(self):
        self.transaction_repository = get_transaction_repository()
        self.npc_repository = get_npc_repository()
    
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
        # Validate NPCs exist
        if not self.npc_repository.exists(buying_npc):
            return f"Buying NPC '{buying_npc}' not found."
        
        if not self.npc_repository.exists(selling_npc):
            return f"Selling NPC '{selling_npc}' not found."
        
        return self.transaction_repository.record_transaction(
            buying_npc, selling_npc, item_name, quantity, price, quality, transaction_time
        )
    
    def get_transaction_history_between(self, npc1: str, npc2: str) -> List[TransactionEntry]:
        """Get transaction history between two NPCs."""
        return self.transaction_repository.get_transaction_history_between(npc1, npc2)
    
    def get_npc_transaction_count(self, npc_name: str) -> int:
        """Get total number of transactions for an NPC."""
        return self.transaction_repository.get_npc_transaction_count(npc_name)
    
    def get_npc_transaction_history_paginated(
        self, 
        npc_name: str, 
        limit: int = 5, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get paginated transaction history for an NPC."""
        return self.transaction_repository.get_npc_transaction_history_paginated(
            npc_name, limit, offset
        )
    
    def execute_negotiated_trade(self, negotiation_result: NegotiationResult) -> str:
        """Execute a successfully negotiated trade."""
        if not negotiation_result.success or not negotiation_result.final_item:
            return f"No trade to execute: {negotiation_result.reasoning}"
        
        # Load current NPC data
        buyer = self.npc_repository.get_with_inventory(negotiation_result.buyer_name)
        seller = self.npc_repository.get_with_inventory(negotiation_result.seller_name)
        
        if not buyer or not seller:
            return "Error: Could not load NPC data for trade execution"
        
        # Calculate total cost
        total_cost = negotiation_result.final_quantity * negotiation_result.final_price
        
        # Verify trade feasibility
        if buyer.silver_pieces < total_cost:
            return f"Trade failed: {buyer.name} cannot afford {total_cost} SP (has {buyer.silver_pieces} SP)"
        
        # Check if seller has the item
        seller_has_item = False
        for item in seller.inventory:
            if item.name.lower() == negotiation_result.final_item.lower():
                if item.quantity >= negotiation_result.final_quantity:
                    seller_has_item = True
                    break
        
        if not seller_has_item:
            return f"Trade failed: {seller.name} does not have enough {negotiation_result.final_item}"
        
        # Execute the trade
        try:
            # Update buyer: add item, subtract silver
            buyer.silver_pieces -= total_cost
            
            # Add item to buyer's inventory
            item_found = False
            for item in buyer.inventory:
                if item.name.lower() == negotiation_result.final_item.lower():
                    item.quantity += negotiation_result.final_quantity
                    item_found = True
                    break
            
            if not item_found:
                # Create new inventory entry for buyer
                buyer.inventory.append(InventoryEntry(
                    name=negotiation_result.final_item,
                    quantity=negotiation_result.final_quantity,
                    price=negotiation_result.final_price,
                    description="",
                    created_by="",
                    creation_time=0.0,
                    quality=ItemQuality(negotiation_result.final_quality) if negotiation_result.final_quality else ItemQuality.regular
                ))
            
            # Update seller: remove item, add silver
            seller.silver_pieces += total_cost
            
            # Remove item from seller's inventory
            for item in seller.inventory:
                if item.name.lower() == negotiation_result.final_item.lower():
                    item.quantity -= negotiation_result.final_quantity
                    if item.quantity <= 0:
                        seller.inventory.remove(item)
                    break
            
            # Update database
            self.npc_repository.update(buyer)
            self.npc_repository.update(seller)
            
            # Record transaction
            self.record_transaction(
                buying_npc=negotiation_result.buyer_name,
                selling_npc=negotiation_result.seller_name,
                item_name=negotiation_result.final_item,
                quantity=negotiation_result.final_quantity,
                price=negotiation_result.final_price,
                quality=negotiation_result.final_quality
            )
            
            return f"✅ Trade executed successfully: {negotiation_result.buyer_name} bought {negotiation_result.final_quantity} {negotiation_result.final_item} from {negotiation_result.seller_name} for {total_cost} SP"
            
        except Exception as e:
            return f"❌ Trade execution failed: {e}"
