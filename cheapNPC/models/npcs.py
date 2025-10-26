"""
NPC-related models for cheapNPC MVC architecture.
"""

from typing import List
from pydantic import BaseModel, Field
from enum import Enum
from .items import InventoryEntry, TransactionEntry


class ProfessionSkill(str, Enum):
    """Skill levels for NPCs."""
    poor = "poor"
    regular = "regular"
    fine = "fine"
    exceptional = "exceptional"


class SalesPersonProfession(str, Enum):
    """Professions for sales-oriented NPCs."""
    store_owner = "store owner"
    merchant = "merchant"


class CraftAndGatherProfessions(str, Enum):
    """Professions for crafting and gathering NPCs."""
    blacksmith = "blacksmith"
    carpenter = "carpenter"
    brewer = "brewer"
    baker = "baker"
    alchemist = "alchemist"
    weaver = "weaver"
    tanner = "tanner"
    potter = "potter"
    jeweler = "jeweler"
    leatherworker = "leatherworker"
    glassblower = "glassblower"
    stonecutter = "stonecutter"
    scribe = "scribe"
    cook = "cook"
    tailor = "tailor"
    cooper = "cooper"
    cobbler = "cobbler"
    apothecary = "apothecary"
    herbalist = "herbalist"
    miner = "miner"
    hunter = "hunter"
    trapper = "trapper"
    fisher = "fisher"
    gatherer = "gatherer"
    farmer = "farmer"
    woodcutter = "woodcutter"
    herder = "herder"
    butcher = "butcher"


class NPC(BaseModel):
    """Base NPC model."""
    name: str = Field(description="The name of the created NPC.")
    race: str = Field(description="The D&D race of the NPC.")
    profession_skill: ProfessionSkill = Field(description="How skilled the NPC is in their craft. Must be one of: 'poor', 'regular', 'fine', 'exceptional'.")
    inventory: List[InventoryEntry] = Field(description="The full, detailed inventory of the NPC.")
    silver_pieces: int = Field(description="The amount of silver pieces the NPC has to trade.")


class CrafterNPC(NPC):
    """NPC specialized in crafting and gathering."""
    profession: CraftAndGatherProfessions = Field(
        description="The NPC's specific craft, or gathering role. Must be one of: 'blacksmith', 'carpenter', 'brewer', 'baker', 'alchemist', 'weaver', 'tanner', 'potter', 'jeweler', 'leatherworker', 'glassblower', 'stonecutter', 'scribe', 'cook', 'tailor', 'cooper', 'cobbler', 'apothecary', 'herbalist', 'miner', 'hunter', 'trapper', 'fisher', 'gatherer', 'farmer', 'woodcutter', 'herder', or 'butcher'."
    )
    known_recipes: List[InventoryEntry] = Field(description="The full, detailed list of items the NPC is capable of producing/collecting")


class SalesPersonNPC(NPC):
    """NPC specialized in sales and trading."""
    profession: SalesPersonProfession = Field(description="The role of the salesperson. Must be either 'store owner' or 'merchant'.")
    customer_history: List[TransactionEntry] = Field(description="The NPC's transaction history with the current customer.")
