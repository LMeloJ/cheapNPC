"""
Web views package for cheapNPC MVC architecture.

Contains web dashboard components and interfaces.
"""

from .village_overview import VillageOverviewView
from .agent_operations import AgentOperationsView
from .trade_history import TradeHistoryView
from .inventory_changes import InventoryChangesView

__all__ = [
    'VillageOverviewView',
    'AgentOperationsView',
    'TradeHistoryView',
    'InventoryChangesView'
]
