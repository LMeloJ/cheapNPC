"""
Repository factory for cheapNPC.

This module provides a centralized way to access all repository implementations.
"""

from .npc_repository import SQLiteNPCRepository
from .item_repository import SQLiteItemRepository
from .transaction_repository import SQLiteTransactionRepository
from .inventory_repository import SQLiteInventoryRepository


class RepositoryFactory:
    """Factory for creating repository instances."""
    
    def __init__(self):
        self._npc_repo = None
        self._item_repo = None
        self._transaction_repo = None
        self._inventory_repo = None
    
    @property
    def npc_repository(self) -> SQLiteNPCRepository:
        """Get NPC repository instance."""
        if self._npc_repo is None:
            self._npc_repo = SQLiteNPCRepository()
        return self._npc_repo
    
    @property
    def item_repository(self) -> SQLiteItemRepository:
        """Get item repository instance."""
        if self._item_repo is None:
            self._item_repo = SQLiteItemRepository()
        return self._item_repo
    
    @property
    def transaction_repository(self) -> SQLiteTransactionRepository:
        """Get transaction repository instance."""
        if self._transaction_repo is None:
            self._transaction_repo = SQLiteTransactionRepository()
        return self._transaction_repo
    
    @property
    def inventory_repository(self) -> SQLiteInventoryRepository:
        """Get inventory repository instance."""
        if self._inventory_repo is None:
            self._inventory_repo = SQLiteInventoryRepository()
        return self._inventory_repo


# Global repository factory instance
_repository_factory: RepositoryFactory = None


def get_repository_factory() -> RepositoryFactory:
    """Get the global repository factory instance."""
    global _repository_factory
    if _repository_factory is None:
        _repository_factory = RepositoryFactory()
    return _repository_factory


# Convenience functions for direct repository access
def get_npc_repository() -> SQLiteNPCRepository:
    """Get NPC repository instance."""
    return get_repository_factory().npc_repository


def get_item_repository() -> SQLiteItemRepository:
    """Get item repository instance."""
    return get_repository_factory().item_repository


def get_transaction_repository() -> SQLiteTransactionRepository:
    """Get transaction repository instance."""
    return get_repository_factory().transaction_repository


def get_inventory_repository() -> SQLiteInventoryRepository:
    """Get inventory repository instance."""
    return get_repository_factory().inventory_repository
