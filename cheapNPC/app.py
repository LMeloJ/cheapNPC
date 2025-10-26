"""Main application module for CheapNPC web dashboard."""

import os
import gradio as gr

from cheapNPC.views.web.agent_operations import AgentOperationsView
from cheapNPC.views.web.village_overview import VillageOverviewView
from cheapNPC.views.web.trade_history import TradeHistoryView
from cheapNPC.views.web.inventory_changes import InventoryChangesView
from cheapNPC.views.web.landing_page import LandingPageComponent
from cheapNPC.infrastructure.database.migrations import check_database_health
from cheapNPC.views.shared.css_styles import DASHBOARD_CSS, COMMON_UTILITY_CSS, UNIFIED_INTERFACE_CSS


class CheapNPCDashboard:
    """Main dashboard application orchestrating all views."""
    
    def __init__(self):
        self.agent_operations = AgentOperationsView()
        self.village_overview = VillageOverviewView()
        self.trade_history = TradeHistoryView()
        self.inventory_changes = InventoryChangesView()
        self.landing_page = LandingPageComponent()
    
    def create_dashboard(self) -> gr.Blocks:
        """Create the main dashboard interface."""
        
        with gr.Blocks(
            title="CheapNPC Agent Dashboard", 
            theme=gr.themes.Soft(),
            css=DASHBOARD_CSS + COMMON_UTILITY_CSS
        ) as demo:
            
            gr.Markdown("# 🤖 CheapNPC Agent Dashboard")
            gr.Markdown("Create NPCs, plan trades, and execute transactions using AI agents.")
            
            with gr.Row():
                gr.Markdown("### Dashboard Controls")
                stop_btn = gr.Button("🛑 Stop Server", variant="stop", size="sm")
            
            def stop_server():
                os._exit(0)
            
            stop_btn.click(stop_server)
            
            with gr.Tabs():
                with gr.Tab("🤖 Agent Operations"):
                    self.agent_operations.create_interface()
                
                with gr.Tab("📊 Village Overview"):
                    _, overview_table_ref, _ = self.village_overview.create_interface()
                
                with gr.Tab("💰 Trade History"):
                    self.trade_history.create_interface()
                
                with gr.Tab("📈 Inventory Changes"):
                    self.inventory_changes.create_interface(overview_table_ref)
        
        return demo
    
    def create_unified_interface(self) -> gr.Blocks:
        """Create interface switching between landing page and dashboard."""
        
        with gr.Blocks(
            title="CheapNPC",
            theme=gr.themes.Soft(),
            css=UNIFIED_INTERFACE_CSS + COMMON_UTILITY_CSS
        ) as interface:
            
            with gr.Column():
                with gr.Group(visible=True, elem_id="landing_view") as landing_view:
                    self.landing_page.create_interface()
                
                with gr.Group(visible=False, elem_id="dashboard_view") as dashboard_view:
                    self.create_dashboard()
            
            def check_and_show_view():
                try:
                    from cheapNPC.config import get_config
                    config = get_config()
                    db_path = config.database.path
                    if os.path.exists(db_path) and check_database_health():
                        try:
                            from cheapNPC.services.npc_service import NPCService
                            npc_service = NPCService()
                            npc_count = len(npc_service.get_all_npc_summaries())
                            
                            if npc_count > 0:
                                return (
                                    gr.Group(visible=False, elem_id="landing_view"),
                                    gr.Group(visible=True, elem_id="dashboard_view")
                                )
                        except Exception as e:
                            print(f"Error accessing NPCs: {e}")
                            pass
                    
                    return (
                        gr.Group(visible=True, elem_id="landing_view"),
                        gr.Group(visible=False, elem_id="dashboard_view")
                    )
                except Exception as e:
                    print(f"Error in check_and_show_view: {e}")
                    return (
                        gr.Group(visible=True, elem_id="landing_view"),
                        gr.Group(visible=False, elem_id="dashboard_view")
                    )
            
            interface.load(check_and_show_view, outputs=[landing_view, dashboard_view])
                
        return interface
    
    def main(self):
        """Launch the application."""
        from cheapNPC.config import get_config
        config = get_config()
        
        demo = self.create_unified_interface()
        
        print("🚀 Starting CheapNPC Application...")
        print("🌐 Launching web interface...")
        print(f"📊 Port: {config.server.port}")
        print("🤖 Agent Integration: Generator, Planner, Trader")
        
        demo.launch(
            server_name=config.server.host,
            server_port=config.server.port,
            share=config.server.share,
            show_error=config.server.show_error
        )


def main():
    """Main function to launch the dashboard."""
    dashboard = CheapNPCDashboard()
    dashboard.main()


if __name__ == "__main__":
    main()
