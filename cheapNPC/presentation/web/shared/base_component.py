"""
Base component class for web interface components.
"""

import gradio as gr
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from cheapNPC.core.services import NPCService, InventoryService, TradingService


class BaseComponent(ABC):
    """Base class for all web interface components."""
    
    def __init__(self):
        """Initialize the component with lazy service loading."""
        self._npc_service = None
        self._inventory_service = None
        self._trading_service = None
    
    @property
    def npc_service(self):
        """Lazy initialization of NPC service."""
        if self._npc_service is None:
            self._npc_service = NPCService()
        return self._npc_service
    
    @property
    def inventory_service(self):
        """Lazy initialization of inventory service."""
        if self._inventory_service is None:
            self._inventory_service = InventoryService()
        return self._inventory_service
    
    @property
    def trading_service(self):
        """Lazy initialization of trading service."""
        if self._trading_service is None:
            self._trading_service = TradingService()
        return self._trading_service
    
    @abstractmethod
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface for this component."""
        pass
    
    def get_all_npcs(self) -> List[Dict[str, Any]]:
        """Get all NPCs with their basic information including trade count."""
        summaries = self.npc_service.get_all_npc_summaries()
        
        # Add trade count to each summary
        for summary in summaries:
            trade_count = self.trading_service.get_npc_transaction_count(summary['name'])
            summary['trade_count'] = trade_count
        
        return summaries
    
    def format_profession_display(self, profession_str: str) -> str:
        """Format profession string to show only the profession name."""
        if "." in profession_str:
            # Extract just the profession name from enum format
            return profession_str.split(".")[-1]
        return profession_str
    
    def get_available_professions(self, npc_type: str) -> List[str]:
        """Get available professions for the selected NPC type."""
        from cheapNPC.core.models.npcs import SalesPersonProfession, CraftAndGatherProfessions
        
        if npc_type == "SalesPersonNPC":
            return [prof.value for prof in SalesPersonProfession]
        else:  # CrafterNPC
            return [prof.value for prof in CraftAndGatherProfessions]
