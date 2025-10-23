"""
Trade History component for the CheapNPC dashboard.

This component displays detailed transaction history for NPCs
with pagination support.
"""

import gradio as gr
from typing import Any, Dict, List

from cheapNPC.presentation.web.shared.base_component import BaseComponent


class TradeHistoryComponent(BaseComponent):
    """Component for displaying trade history."""
    
    def get_npc_trade_count(self, npc_name: str) -> int:
        """Get total number of transactions for an NPC."""
        return self.trading_service.get_npc_transaction_count(npc_name)
    
    def get_npc_trade_history_paginated(self, npc_name: str, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """Get paginated trade history for a specific NPC."""
        return self.trading_service.get_npc_transaction_history_paginated(npc_name, limit, offset)
    
    def format_trade_history_table(self, transactions: List[Dict[str, Any]], selected_npc: str = "") -> List[List[str]]:
        """Format transaction data for display in a table."""
        return self.inventory_service.format_trade_history_table(transactions, selected_npc)
    
    def create_interface(self) -> gr.Blocks:
        """Create the trade history interface."""
        
        with gr.Blocks() as trade_history_interface:
            gr.Markdown("## Individual NPC Trade History")
            gr.Markdown("View detailed transaction history for each NPC with pagination.")
            
            with gr.Row():
                trade_npc_dropdown = gr.Dropdown(
                    choices=[],
                    label="Select NPC",
                    interactive=True,
                    allow_custom_value=True
                )
                refresh_npc_list_btn = gr.Button("🔄 Load NPCs", variant="secondary")
                refresh_trade_btn = gr.Button("🔄 Refresh Trade Data", variant="secondary")
            
            with gr.Row():
                trade_history_table = gr.Dataframe(
                    headers=["Date", "Role", "Other NPC", "Item", "Qty", "Price", "Total", "Quality"],
                    label="Recent Trades",
                    interactive=False,
                    wrap=True,
                    datatype=["str", "str", "str", "str", "str", "str", "str", "str"]
                )
            
            with gr.Row():
                load_more_btn = gr.Button("📄 Load More Trades", variant="secondary", visible=False)
                trade_count_info = gr.Markdown("")
            
            # State to track current offset
            current_offset = gr.State(0)
            current_npc = gr.State("")
            
            def update_trade_npc_list():
                try:
                    npcs = self.get_all_npcs()
                    choices = [("All NPCs", None)] + [(f"{npc['name']} ({npc['profession']})", npc['name']) for npc in npcs]
                    return gr.Dropdown(choices=choices)
                except Exception as e:
                    print(f"Error updating trade NPC list: {e}")
                    return gr.Dropdown(choices=[])
            
            def load_trade_history(npc_name, offset=0):
                try:
                    if not npc_name:
                        return [], "", 0, False, ""
                    
                    transactions = self.get_npc_trade_history_paginated(npc_name, limit=5, offset=offset)
                    total_count = self.get_npc_trade_count(npc_name)
                    
                    # Add selected_npc to each transaction for role determination
                    for tx in transactions:
                        tx['selected_npc'] = npc_name
                    
                    table_data = self.format_trade_history_table(transactions, npc_name)
                    
                    # Show load more button if there are more transactions
                    show_load_more = (offset + 5) < total_count
                    
                    count_info = f"Showing {min(offset + len(transactions), total_count)} of {total_count} total trades"
                    
                    return table_data, count_info, offset, show_load_more, npc_name
                except Exception as e:
                    print(f"Error loading trade history: {e}")
                    return [], f"Error loading trade history: {e}", offset, False, ""
            
            def load_more_trades(npc_name, current_offset):
                try:
                    if not npc_name:
                        return [], "", current_offset, False
                    
                    new_offset = current_offset + 5
                    transactions = self.get_npc_trade_history_paginated(npc_name, limit=5, offset=new_offset)
                    total_count = self.get_npc_trade_count(npc_name)
                    
                    # Add selected_npc to each transaction for role determination
                    for tx in transactions:
                        tx['selected_npc'] = npc_name
                    
                    table_data = self.format_trade_history_table(transactions, npc_name)
                    
                    # Show load more button if there are more transactions
                    show_load_more = (new_offset + 5) < total_count
                    
                    count_info = f"Showing {min(new_offset + len(transactions), total_count)} of {total_count} total trades"
                    
                    return table_data, count_info, new_offset, show_load_more
                except Exception as e:
                    print(f"Error loading more trades: {e}")
                    return [], f"Error loading more trades: {e}", current_offset, False
            
            # Event handlers
            refresh_npc_list_btn.click(update_trade_npc_list, outputs=trade_npc_dropdown)
            refresh_trade_btn.click(
                lambda npc: load_trade_history(npc, 0),
                inputs=trade_npc_dropdown,
                outputs=[trade_history_table, trade_count_info, current_offset, load_more_btn, current_npc]
            )
            
            trade_npc_dropdown.change(
                lambda npc: load_trade_history(npc, 0),
                inputs=trade_npc_dropdown,
                outputs=[trade_history_table, trade_count_info, current_offset, load_more_btn, current_npc]
            )
            
            load_more_btn.click(
                load_more_trades,
                inputs=[current_npc, current_offset],
                outputs=[trade_history_table, trade_count_info, current_offset, load_more_btn]
            )
            
            # Auto-load NPC list when the interface loads
            trade_history_interface.load(update_trade_npc_list, outputs=trade_npc_dropdown)
            
            # Add auto-loading when tab is accessed
            def auto_load_trade_data():
                """Auto-load trade data when tab is accessed."""
                try:
                    # Load NPC list
                    npcs = self.get_all_npcs()
                    choices = [("All NPCs", None)] + [(f"{npc['name']} ({npc['profession']})", npc['name']) for npc in npcs]
                    return gr.Dropdown(choices=choices)
                except Exception as e:
                    print(f"Error auto-loading trade data: {e}")
                    return gr.Dropdown(choices=[])
        
        return trade_history_interface, auto_load_trade_data
