"""
NPC service controller for cheapNPC MVC architecture.

This controller handles business logic for NPC operations,
acting as a bridge between the view layer and data access layer.
"""

from typing import List, Optional, Union
from cheapNPC.models import NPC, CrafterNPC, SalesPersonNPC, InventoryEntry
from cheapNPC.infrastructure.database.repositories import get_npc_repository


class NPCService:
    """Controller for NPC business logic."""
    
    def __init__(self):
        self.npc_repository = get_npc_repository()
    
    def create_npc(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Create a new NPC."""
        if self.npc_repository.exists(npc.name):
            return f"NPC '{npc.name}' already exists."
        
        return self.npc_repository.save(npc)
    
    def get_npc(self, name: str) -> Optional[Union[CrafterNPC, SalesPersonNPC]]:
        """Get an NPC by name."""
        return self.npc_repository.get_by_name(name)
    
    def get_all_npcs(self) -> List[Union[CrafterNPC, SalesPersonNPC]]:
        """Get all NPCs."""
        return self.npc_repository.get_all()
    
    def update_npc(self, npc: Union[CrafterNPC, SalesPersonNPC]) -> str:
        """Update an existing NPC."""
        if not self.npc_repository.exists(npc.name):
            return f"NPC '{npc.name}' not found."
        
        return self.npc_repository.update(npc)
    
    def delete_npc(self, name: str) -> bool:
        """Delete an NPC."""
        if not self.npc_repository.exists(name):
            return False
        
        return self.npc_repository.delete(name)
    
    def npc_exists(self, name: str) -> bool:
        """Check if an NPC exists."""
        return self.npc_repository.exists(name)
    
    def get_npc_with_inventory(self, name: str) -> Optional[Union[CrafterNPC, SalesPersonNPC]]:
        """Get an NPC with their complete inventory."""
        return self.npc_repository.get_with_inventory(name)
    
    def get_all_npcs_with_inventories(self) -> List[Union[CrafterNPC, SalesPersonNPC]]:
        """Get all NPCs with their complete inventories."""
        return self.npc_repository.get_all_with_inventories()
    
    def get_npc_summary(self, name: str) -> Optional[dict]:
        """Get a summary of an NPC's basic information."""
        npc = self.get_npc_with_inventory(name)
        if not npc:
            return None
        
        inventory_count = len(npc.inventory)
        inventory_value = sum(item.quantity * item.price for item in npc.inventory)
        
        # Format profession to show only the profession name
        profession_str = str(npc.profession)
        if "." in profession_str:
            profession_str = profession_str.split(".")[-1]
        
        return {
            'name': npc.name,
            'race': npc.race,
            'profession': profession_str,
            'profession_skill': npc.profession_skill,
            'silver_pieces': npc.silver_pieces,
            'inventory_count': inventory_count,
            'inventory_value': inventory_value
        }
    
    def get_all_npc_summaries(self) -> List[dict]:
        """Get summaries for all NPCs."""
        npcs = self.get_all_npcs_with_inventories()
        summaries = []
        
        for npc in npcs:
            summary = self.get_npc_summary(npc.name)
            if summary:
                summaries.append(summary)
        
        return summaries
