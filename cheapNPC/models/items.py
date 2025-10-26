"""
Item-related models for cheapNPC MVC architecture.
"""

from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class ItemQuality(str, Enum):
    """Quality levels for items."""
    poor = "poor"
    regular = "regular"
    fine = "fine"
    exceptional = "exceptional"


class RecipeDifficulty(str, Enum):
    """Difficulty levels for recipes."""
    easy = "easy"
    medium = "medium"
    hard = "hard"
    very_hard = "very_hard"


class ItemBase(BaseModel):
    """Base model for items."""
    name: str = Field(description="The name of the unique item.")
    description: str = Field(description="A description of the item, including what it is used for.")
    created_by: str = Field(description="Which professions are capable of creating or collecting the item.")
    creation_time: float = Field(description="Average time it takes (in hours) for the item to be collected or created by an average skilled NPC.")


class RecipeItem(ItemBase):
    """Item used in recipes."""
    quantity: int = Field(description="The base quantity required for that item for the recipe to be finished.")


class Recipe(BaseModel):
    """Recipe for creating items."""
    item: ItemBase = Field(description="The item that is produced by the recipe.")
    ingredients: List[RecipeItem] = Field(description="The list of items required to produce the item.")
    time_to_produce: int = Field(description="The time in seconds to produce the item.")
    quantity_produced: int = Field(description="The quantity of the item that is produced by the recipe.")
    difficulty: RecipeDifficulty = Field(description="The difficulty of the recipe. Must be one of: 'easy', 'medium', 'hard', 'very_hard'.")


class InventoryEntry(ItemBase):
    """Represents an item in an NPC's inventory."""
    quantity: int = Field(description="The amount of that item this NPC has.")
    price: float = Field(description="The price in silver pieces this NPC sells it for.")
    quality: ItemQuality = Field(description="The quality of the item. Must be one of: 'poor', 'regular', 'fine', 'exceptional'.")


class TransactionEntry(InventoryEntry):
    """Represents a transaction between NPCs."""
    buying_npc: str = Field(description="The name of the NPC who bought the item.")
    selling_npc: str = Field(description="The name of the NPC who sold the item.")
