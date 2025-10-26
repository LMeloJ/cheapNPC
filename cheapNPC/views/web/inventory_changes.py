"""
Inventory Changes view for cheapNPC MVC architecture.

This view displays inventory comparison between initial and current states,
showing how NPC inventories have changed over time.
"""

import gradio as gr
from typing import Any, Dict, List

from cheapNPC.views.shared.base_view import BaseView


class InventoryChangesView(BaseView):
    """View for displaying inventory changes."""
    
    def create_inventory_comparison_table(self, npc_name: str) -> List[List[str]]:
        """Create a comparison table showing initial vs current inventory with changes."""
        return self.inventory_service.create_inventory_comparison_table(npc_name)
    
    def create_interface(self, overview_table_ref=None) -> gr.Blocks:
        """Create the inventory changes interface."""
        
        with gr.Blocks() as inventory_interface:
            gr.Markdown("## Compare Initial vs Current Inventory")
            gr.Markdown("Shows how each NPC's inventory and silver pieces have changed over time. **🟢 Green** indicates items/silver gained, **🔴 Red** indicates items/silver lost, **⚪ White** indicates no change.")
            
            with gr.Row():
                inventory_npc_dropdown = gr.Dropdown(
                    choices=[],
                    label="Select NPC",
                    interactive=True
                )
                refresh_npc_list_btn = gr.Button("🔄 Load NPCs", variant="secondary")
                refresh_inventory_btn = gr.Button("🔄 Refresh Inventory Data", variant="secondary")
            
            with gr.Row():
                inventory_comparison_table = gr.Dataframe(
                    headers=["Item", "Initial Qty", "Current Qty", "Change", "Price (SP)", "Quality"],
                    label="Inventory Comparison: Initial vs Current",
                    interactive=False,
                    wrap=True,
                    datatype=["str", "str", "str", "str", "str", "str"]
                )
            
            def update_inventory_comparison(npc_name):
                try:
                    if not npc_name:
                        return []
                    
                    comparison_data = self.create_inventory_comparison_table(npc_name)
                    return comparison_data
                except Exception as e:
                    print(f"Error updating inventory comparison: {e}")
                    return []
            
            def update_npc_list():
                try:
                    npcs = self.get_all_npcs()
                    choices = [(f"{npc['name']} ({npc['profession']})", npc['name']) for npc in npcs]
                    return gr.Dropdown(choices=choices)
                except Exception as e:
                    print(f"Error updating NPC list: {e}")
                    return gr.Dropdown(choices=[])
            
            refresh_npc_list_btn.click(update_npc_list, outputs=inventory_npc_dropdown)
            refresh_inventory_btn.click(update_inventory_comparison, inputs=inventory_npc_dropdown,
                                      outputs=inventory_comparison_table)
            inventory_npc_dropdown.change(update_inventory_comparison, inputs=inventory_npc_dropdown,
                                        outputs=inventory_comparison_table)
            
            # Load initial NPC list only when dashboard is active
            # inventory_interface.load(update_npc_list, outputs=inventory_npc_dropdown)
            
            # Add click handler for overview table to switch to inventory changes
            if overview_table_ref is not None:
                def on_npc_click(evt: gr.SelectData):
                    """Handle NPC row click to switch to inventory changes tab."""
                    try:
                        if evt and hasattr(evt, 'index') and evt.index is not None and len(evt.index) > 0 and evt.index[0] is not None:
                            # Get the table data to find the NPC name in the clicked row
                            table_data = self.inventory_service.get_npc_overview_table()
                            if evt.index[0] < len(table_data):
                                npc_name = table_data[evt.index[0]][0]  # First column is the name
                                return gr.Dropdown(value=npc_name)
                    except Exception as e:
                        print(f"Error in on_npc_click: {e}")
                    return gr.Dropdown()
                
                # Connect the click handler
                overview_table_ref.select(on_npc_click, outputs=inventory_npc_dropdown)
                
                # Add JavaScript to switch tabs when dropdown changes
                inventory_npc_dropdown.change(
                    fn=None,
                    inputs=inventory_npc_dropdown,
                    outputs=None,
                    js="() => { setTimeout(() => { document.querySelector('[data-testid=\"tab-3\"]').click(); }, 100); }"
                )
        
            # Auto-load NPC list when the interface loads
            inventory_interface.load(update_npc_list, outputs=inventory_npc_dropdown)
            
            # Add auto-loading when tab is accessed
            def auto_load_inventory_data():
                """Auto-load inventory data when tab is accessed."""
                try:
                    # Load NPC list
                    npcs = self.get_all_npcs()
                    choices = [(f"{npc['name']} ({npc['profession']})", npc['name']) for npc in npcs]
                    return gr.Dropdown(choices=choices)
                except Exception as e:
                    print(f"Error auto-loading inventory data: {e}")
                    return gr.Dropdown(choices=[])
        
        return inventory_interface, auto_load_inventory_data
