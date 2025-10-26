"""
Views package for cheapNPC MVC architecture.

Contains all UI components and presentation logic:
- Web dashboard components
- CLI tools and interfaces
- Shared UI components
"""

# Import web views
from .web.village_overview import VillageOverviewView
from .web.agent_operations import AgentOperationsView
from .web.trade_history import TradeHistoryView
from .web.inventory_changes import InventoryChangesView

# Import CLI views
from .cli.print_npc import print_npc_details

# Import shared components
from .shared.base_view import BaseView

__all__ = [
    # Web Views
    'VillageOverviewView',
    'AgentOperationsView',
    'TradeHistoryView',
    'InventoryChangesView',
    
    # CLI Views
    'print_npc_details',
    
    # Shared Components
    'BaseView'
]