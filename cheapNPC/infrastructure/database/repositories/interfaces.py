"""
Repository interfaces for cheapNPC.

This module defines the abstract interfaces for data access,
following the Repository pattern for clean separation of concerns.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict, Any
from cheapNPC.models import (
    NPC, CrafterNPC, SalesPersonNPC, InventoryEntry, 
    TransactionEntry, ItemBase, ItemQuality
)


class BaseRepository(ABC):
    """Base repository interface."""
    
    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """Check if an entity exists by identifier."""
        pass


class NPCRepository(BaseRepository):
    """Repository interface for NPC operations."""
    
    @abstractmethod
    def save(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Save an NPC to the database."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Union[CrafterNPC, SalesPersonNPC]]:
        """Get an NPC by name."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Union[CrafterNPC, SalesPersonNPC]]:
        """Get all NPCs."""
        pass
    
    @abstractmethod
    def update(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Update an existing NPC."""
        pass
    
    @abstractmethod
    def delete(self, name: str) -> bool:
        """Delete an NPC by name."""
        pass
    
    @abstractmethod
    def exists(self, name: str) -> bool:
        """Check if an NPC exists by name."""
        pass
    
    @abstractmethod
    def get_with_inventory(self, name: str) -> Optional[Union[CrafterNPC, SalesPersonNPC]]:
        """Get an NPC with their complete inventory."""
        pass
    
    @abstractmethod
    def get_all_with_inventories(self) -> List[Union[CrafterNPC, SalesPersonNPC]]:
        """Get all NPCs with their complete inventories."""
        pass


class ItemRepository(BaseRepository):
    """Repository interface for item operations."""
    
    @abstractmethod
    def get_or_create(self, name: str) -> int:
        """Get item ID by name, creating if it doesn't exist."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[ItemBase]:
        """Get an item by name."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[ItemBase]:
        """Get all items."""
        pass
    
    @abstractmethod
    def exists(self, name: str) -> bool:
        """Check if an item exists by name."""
        pass


class TransactionRepository(BaseRepository):
    """Repository interface for transaction operations."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_transaction_history_between(
        self, 
        npc1: str, 
        npc2: str
    ) -> List[TransactionEntry]:
        """Get transaction history between two NPCs."""
        pass
    
    @abstractmethod
    def get_npc_transaction_count(self, npc_name: str) -> int:
        """Get total number of transactions for an NPC."""
        pass
    
    @abstractmethod
    def get_npc_transaction_history_paginated(
        self, 
        npc_name: str, 
        limit: int = 5, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get paginated transaction history for an NPC."""
        pass
    
    @abstractmethod
    def exists(self, transaction_id: int) -> bool:
        """Check if a transaction exists by ID."""
        pass


class InventoryRepository(BaseRepository):
    """Repository interface for inventory operations."""
    
    @abstractmethod
    def update_npc_inventory(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Update an NPC's inventory."""
        pass
    
    @abstractmethod
    def get_npc_inventory(self, npc_name: str) -> List[Dict[str, Any]]:
        """Get detailed inventory for a specific NPC."""
        pass
    
    @abstractmethod
    def get_npc_initial_inventory(self, npc_name: str) -> tuple:
        """Get the initial inventory state for an NPC."""
        pass
    
    @abstractmethod
    def exists(self, npc_id: int, item_id: int) -> bool:
        """Check if an inventory entry exists."""
        pass
