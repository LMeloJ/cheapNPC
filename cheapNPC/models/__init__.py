"""
Models package for cheapNPC MVC architecture.

Contains all data models and business entities:
- NPCs (Non-Player Characters)
- Items and inventory
- Trading and transactions
- World state
"""

# Import all models for easy access
from .npcs import (
    NPC, CrafterNPC, SalesPersonNPC,
    ProfessionSkill, SalesPersonProfession, CraftAndGatherProfessions
)
from .items import (
    ItemBase, RecipeItem, Recipe, InventoryEntry, TransactionEntry,
    ItemQuality, RecipeDifficulty
)
from .trading import (
    TradeItem, TradeOffer, TradeResponse, NPCPairing, TradingPair,
    TradingPlan, NegotiationResult, TradeResult, TradingExecutionResult
)
from .utils import get_item_quality_by_skill

__all__ = [
    # NPC Models
    'NPC', 'CrafterNPC', 'SalesPersonNPC',
    'ProfessionSkill', 'SalesPersonProfession', 'CraftAndGatherProfessions',
    
    # Item Models
    'ItemBase', 'RecipeItem', 'Recipe', 'InventoryEntry', 'TransactionEntry',
    'ItemQuality', 'RecipeDifficulty',
    
    # Trading Models
    'TradeItem', 'TradeOffer', 'TradeResponse', 'NPCPairing', 'TradingPair',
    'TradingPlan', 'NegotiationResult', 'TradeResult', 'TradingExecutionResult',
    
    # Utilities
    'get_item_quality_by_skill'
]