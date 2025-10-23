"""
Village Overview component for the CheapNPC dashboard.

This component displays an overview of all NPCs in the village,
showing their basic information, trade counts, and inventory data.
"""

import gradio as gr
from typing import Any, Dict, List

from cheapNPC.presentation.web.shared.base_component import BaseComponent


class VillageOverviewComponent(BaseComponent):
    """Component for displaying village NPC overview."""
    
    def create_npc_overview_table(self) -> List[List[str]]:
        """Create a table showing NPC overview data with formatted professions."""
        table_data = self.inventory_service.get_npc_overview_table()
        
        # Profession formatting is now handled in the service layer
        return table_data
    
    def create_interface(self) -> gr.Blocks:
        """Create the village overview interface."""
        
        with gr.Blocks() as overview_interface:
            gr.Markdown("## Village NPCs Overview")
            gr.Markdown("Click on any NPC row to view their inventory changes. The NPC will be selected automatically - then click the 'Inventory Changes' tab above to view their data.")
            
            refresh_overview_btn = gr.Button("🔄 Refresh Overview", variant="secondary")
            
            with gr.Row():
                npc_overview_table = gr.Dataframe(
                    headers=["Name", "Silver Pieces", "Trades", "Profession", "Race", "Items", "Inventory Value"],
                    label="NPC Overview",
                    interactive=False,  # Disable editing
                    wrap=True,
                    datatype=["str", "str", "str", "str", "str", "str", "str"],
                    elem_id="npc_overview_table"
                )
            
            def update_overview():
                table_data = self.create_npc_overview_table()
                return table_data
            
            refresh_overview_btn.click(update_overview, outputs=npc_overview_table)
            
            # Auto-load data when the interface loads
            overview_interface.load(update_overview, outputs=npc_overview_table)
            
            # Store reference to overview table for click handling
            overview_table_ref = npc_overview_table
            
            # Add auto-loading when tab is accessed
            def auto_load_overview():
                """Auto-load overview data when tab is accessed."""
                try:
                    table_data = self.create_npc_overview_table()
                    return table_data
                except Exception as e:
                    print(f"Error auto-loading overview: {e}")
                    return []
        
        return overview_interface, overview_table_ref, auto_load_overview
