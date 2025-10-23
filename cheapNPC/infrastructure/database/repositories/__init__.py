"""
Data access repositories for cheapNPC.

This module provides access to all repository implementations and interfaces.
"""

from .interfaces import (
    BaseRepository, NPCRepository, ItemRepository, 
    TransactionRepository, InventoryRepository
)
from .npc_repository import SQLiteNPCRepository
from .item_repository import SQLiteItemRepository
from .transaction_repository import SQLiteTransactionRepository
from .inventory_repository import SQLiteInventoryRepository
from .factory import (
    RepositoryFactory, get_repository_factory,
    get_npc_repository, get_item_repository, 
    get_transaction_repository, get_inventory_repository
)

__all__ = [
    # Interfaces
    'BaseRepository', 'NPCRepository', 'ItemRepository', 
    'TransactionRepository', 'InventoryRepository',
    
    # Implementations
    'SQLiteNPCRepository', 'SQLiteItemRepository', 
    'SQLiteTransactionRepository', 'SQLiteInventoryRepository',
    
    # Factory
    'RepositoryFactory', 'get_repository_factory',
    'get_npc_repository', 'get_item_repository', 
    'get_transaction_repository', 'get_inventory_repository',
]