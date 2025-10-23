"""
Main application file for the CheapNPC web dashboard.

This module orchestrates all the dashboard components and creates the main interface.
It also handles the landing page for database setup.
"""

import gradio as gr
import os

from cheapNPC.presentation.web.components.agent_operations import AgentOperationsComponent
from cheapNPC.presentation.web.components.village_overview import VillageOverviewComponent
from cheapNPC.presentation.web.components.trade_history import TradeHistoryComponent
from cheapNPC.presentation.web.components.inventory_changes import InventoryChangesComponent
from cheapNPC.presentation.web.components.landing_page import LandingPageComponent
from cheapNPC.infrastructure.database.migrations import check_database_health


class CheapNPCDashboard:
    """Main dashboard application that orchestrates all components."""
    
    def __init__(self):
        """Initialize the dashboard with all components."""
        self.agent_operations = AgentOperationsComponent()
        self.village_overview = VillageOverviewComponent()
        self.trade_history = TradeHistoryComponent()
        self.inventory_changes = InventoryChangesComponent()
        self.landing_page = LandingPageComponent()
    
    def create_dashboard(self) -> gr.Blocks:
        """Create the main dashboard interface."""
        
        with gr.Blocks(
            title="CheapNPC Agent Dashboard", 
            theme=gr.themes.Soft()
        ) as demo:
            
            gr.Markdown("# 🤖 CheapNPC Agent Dashboard")
            gr.Markdown("Create NPCs, plan trades, and execute transactions using AI agents.")
            
            with gr.Row():
                gr.Markdown("### Dashboard Controls")
                stop_btn = gr.Button("🛑 Stop Server", variant="stop", size="sm")
            
            def stop_server():
                import os
                os._exit(0)
            
            stop_btn.click(stop_server)
            
            with gr.Tabs() as tabs:
                # Agent Operations Tab
                with gr.Tab("🤖 Agent Operations") as agent_tab:
                    agent_interface = self.agent_operations.create_interface()
                
                # Overview Tab
                with gr.Tab("📊 Village Overview") as overview_tab:
                    overview_interface, overview_table_ref, auto_load_overview = self.village_overview.create_interface()
                
                # Trade History Tab
                with gr.Tab("💰 Trade History") as trade_tab:
                    trade_history_interface, auto_load_trade_data = self.trade_history.create_interface()
                
                # Inventory Changes Tab
                with gr.Tab("📈 Inventory Changes") as inventory_tab:
                    inventory_interface, auto_load_inventory_data = self.inventory_changes.create_interface(overview_table_ref)
            
            # Add auto-loading when dashboard becomes visible
            # This will be handled by the unified interface when switching from landing to dashboard
        
        return demo
    
    def create_unified_interface(self) -> gr.Blocks:
        """Create a unified interface that can switch between landing page and dashboard."""
        
        with gr.Blocks(
            title="CheapNPC",
            theme=gr.themes.Soft(),
            css="""
            .landing-container { 
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .dashboard-container {
                width: 100%;
                margin: 0;
                padding: 0;
            }
            .agent-section { 
                border: 2px solid #e1e5e9; 
                border-radius: 10px; 
                padding: 20px; 
                margin: 10px 0;
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            }
            .status-running { 
                background-color: #e3f2fd !important;
                border: 3px solid #2196f3 !important;
                border-radius: 15px !important;
                padding: 25px !important;
                margin: 20px 0 !important;
                text-align: center !important;
                color: #1565c0 !important;
                font-weight: bold !important;
                font-size: 18px !important;
                box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3) !important;
            }
            .status-success { 
                color: #28a745; 
                font-weight: bold; 
            }
            .status-error { 
                color: #dc3545; 
                font-weight: bold; 
            }
            .output-box {
                background-color: #f8f9fa !important;
                border: 1px solid #dee2e6 !important;
                border-radius: 5px !important;
                padding: 15px !important;
                font-family: 'Courier New', monospace !important;
                white-space: pre-wrap !important;
                max-height: 400px !important;
                overflow-y: auto !important;
                scrollbar-width: thin !important;
                scrollbar-color: #6c757d #f8f9fa !important;
                resize: vertical !important;
            }
            .output-box textarea {
                max-height: 400px !important;
                overflow-y: auto !important;
                resize: vertical !important;
            }
            .output-box::-webkit-scrollbar {
                width: 8px !important;
            }
            .output-box::-webkit-scrollbar-track {
                background: #f8f9fa !important;
                border-radius: 4px !important;
            }
            .output-box::-webkit-scrollbar-thumb {
                background: #6c757d !important;
                border-radius: 4px !important;
            }
            .output-box::-webkit-scrollbar-thumb:hover {
                background: #495057 !important;
            }
            """
        ) as interface:
            
            # State to track current view
            current_view = gr.State("checking")
            
            # Container for the current view
            with gr.Column():
                # Landing page interface
                with gr.Group(visible=True, elem_id="landing_view") as landing_view:
                    landing_interface, check_status_func = self.landing_page.create_interface()
                
                # Dashboard interface - use the full dashboard
                with gr.Group(visible=False, elem_id="dashboard_view") as dashboard_view:
                    dashboard_interface = self.create_dashboard()
            
            def check_and_show_view():
                """Check database status and show appropriate view."""
                try:
                    db_path = "data/village.db"
                    if os.path.exists(db_path) and check_database_health():
                        # Only check NPCs if database is healthy (tables exist)
                        try:
                            from cheapNPC.core.services import NPCService
                            npc_service = NPCService()
                            npc_count = len(npc_service.get_all_npc_summaries())
                            
                            if npc_count > 0:
                                # Load dashboard data when switching to dashboard view
                                load_dashboard_data()
                                return (
                                    gr.Group(visible=False, elem_id="landing_view"),
                                    gr.Group(visible=True, elem_id="dashboard_view"),
                                    "dashboard"
                                )
                        except Exception as e:
                            # If there's an error accessing NPCs, show landing page
                            # This could happen if tables exist but are empty or corrupted
                            print(f"Error accessing NPCs: {e}")
                            pass
                    
                    # Show landing page if database doesn't exist, isn't healthy, or has no NPCs
                    return (
                        gr.Group(visible=True, elem_id="landing_view"),
                        gr.Group(visible=False, elem_id="dashboard_view"),
                        "landing"
                    )
                except Exception as e:
                    # Any other error - show landing page
                    print(f"Error in check_and_show_view: {e}")
                    return (
                        gr.Group(visible=True, elem_id="landing_view"),
                        gr.Group(visible=False, elem_id="dashboard_view"),
                        "landing"
                    )
            
            def load_dashboard_data():
                """Load data for dashboard components only when dashboard is shown."""
                try:
                    # This will be called when dashboard becomes visible
                    # The components will load their data on first access
                    pass
                except Exception as e:
                    print(f"Error loading dashboard data: {e}")
            
            # Auto-check status when interface loads
            interface.load(
                check_and_show_view,
                outputs=[landing_view, dashboard_view, current_view]
            )
                
        return interface

    def create_landing_page(self) -> gr.Blocks:
        """Create the landing page interface."""
        return self.landing_page.create_interface()[0]

    def main(self):
        """Main function to launch the application."""
        print("🚀 Starting CheapNPC Application...")
        
        # Always use the unified interface that can handle both views
        demo = self.create_unified_interface()
        
        print("🌐 Launching web interface...")
        print("📊 Port: 7861")
        print("🤖 Agent Integration: Generator, Planner, Trader")
        
        # Launch with public access (set share=False for local only)
        demo.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7861,  # Changed port to avoid conflicts
            share=False,  # Set to True to create a public link
            show_error=True
        )


def main():
    """Main function to launch the dashboard."""
    dashboard = CheapNPCDashboard()
    dashboard.main()


if __name__ == "__main__":
    main()
