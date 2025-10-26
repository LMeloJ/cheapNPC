"""
Landing page component for CheapNPC web interface.

This component provides a landing page that checks if the database is set up
and offers a button to initialize the world if needed.
"""

import gradio as gr
import os
import asyncio
import threading
from typing import Optional

from cheapNPC.infrastructure.database.migrations import check_database_health
from cheapNPC.services.world_service import create_world_sync
from cheapNPC.views.shared.css_styles import LANDING_PAGE_CSS, COMMON_UTILITY_CSS


class LandingPageComponent:
    """Component for the landing page with database setup functionality."""
    
    def __init__(self):
        """Initialize the landing page component."""
        self.is_setting_up = False
    
    def check_database_status(self) -> tuple[str, bool, bool]:
        """
        Check if the database is properly set up.
        
        Returns:
            tuple: (status_message, is_setup, show_button)
        """
        try:
            # Check if database file exists
            from cheapNPC.config import get_config
            config = get_config()
            db_path = config.database.path
            if not os.path.exists(db_path):
                return (
                    "❌ Database not found. The village database needs to be created.",
                    False,
                    True
                )
            
            # Check if database is properly initialized
            if not check_database_health():
                return (
                    "⚠️ Database exists but is not properly set up. Tables may be missing or corrupted.",
                    False,
                    True
                )
            
            # Check if there are any NPCs in the database
            try:
                from cheapNPC.services.npc_service import NPCService
                npc_service = NPCService()
                npc_count = len(npc_service.get_all_npc_summaries())
                
                if npc_count == 0:
                    return (
                        "✅ Database is set up but empty. No NPCs have been created yet.",
                        False,
                        True
                    )
                
                return (
                    f"✅ Database is properly set up with {npc_count} NPCs. Ready to go!",
                    True,
                    False
                )
            except Exception as npc_error:
                # If there's an error accessing NPCs, the database might not be fully set up
                # This is expected when tables don't exist yet
                return (
                    "⚠️ Database exists but tables may not be properly initialized.",
                    False,
                    True
                )
            
        except Exception as e:
            return (
                f"❌ Error checking database status: {str(e)}",
                False,
                True
            )
    
    def run_create_world(self, progress_callback=None) -> str:
        """
        Create the world using the world service function.
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            str: Result message
        """
        if self.is_setting_up:
            return "⚠️ World creation is already in progress. Please wait..."
        
        self.is_setting_up = True
        
        try:
            if progress_callback:
                progress_callback("🔄 Starting world creation process...")
            
            # Run the world creation function directly
            result = create_world_sync(progress_callback)
            
            if progress_callback:
                progress_callback(result)
            
            return result
                
        except Exception as e:
            error_msg = f"❌ Exception during world creation: {str(e)}"
            if progress_callback:
                progress_callback(error_msg)
            return error_msg
        finally:
            self.is_setting_up = False
    
    def create_interface(self) -> tuple[gr.Blocks, callable]:
        """
        Create the landing page interface.
        
        Returns:
            tuple: (interface, check_status_function)
        """
        with gr.Blocks(
            title="CheapNPC - Welcome",
            theme=gr.themes.Soft(),
            css=LANDING_PAGE_CSS + COMMON_UTILITY_CSS
        ) as interface:
            
            gr.Markdown("""
            # 🤖 Welcome to CheapNPC
            
            **CheapNPC** is an AI-powered NPC simulation system that creates intelligent characters 
            for your virtual world. NPCs can trade, craft, and interact with each other using 
            advanced AI agents.
            """)
            
            with gr.Group(elem_classes="status-box"):
                gr.Markdown("### 📊 Database Status Check")
                
                status_display = gr.Markdown("Checking database status...")
                
                check_status_btn = gr.Button("🔄 Check Status", variant="secondary")
                
                setup_world_btn = gr.Button(
                    "🌍 Create World", 
                    variant="primary",
                    elem_classes="setup-button",
                    visible=True
                )
                
                # Status indicator for world creation
                setup_status = gr.Markdown(
                    """
                    # 🔄 Creating World...
                    
                    **Please wait while we set up your NPC world. This may take a few moments.**
                    
                    *Setting up database, creating NPCs, and preparing the world...*
                    """,
                    visible=False,
                    elem_classes="status-running"
                )
                
                # Output box for results
                setup_output = gr.Textbox(
                    label="Setup Results",
                    interactive=False,
                    elem_classes="output-box",
                    lines=15,
                    show_copy_button=True,
                    visible=False,
                    placeholder="World creation results will appear here..."
                )
            
            gr.Markdown("""
            ### 🚀 What happens when you create the world?
            
            1. **Database Setup**: Creates all necessary database tables
            2. **NPC Generation**: Creates 6 crafters/gatherers with different professions
            3. **Merchant Creation**: Creates 2 salespeople (merchant and store owner)
            4. **Inventory Setup**: Each NPC gets an AI-generated inventory and characteristics
            
            Once the world is created, you'll be able to access the full dashboard with all features!
            """)
            
            # Success message and navigation
            with gr.Group(visible=False, elem_id="success_section") as success_section:
                gr.Markdown("""
                ### ✅ World Created Successfully!
                
                Your NPC world has been created and is ready to use. Click the button below to refresh and access the dashboard.
                """)
                
                # Add a refresh button that will trigger the view switch
                refresh_dashboard_btn = gr.Button(
                    "🔄 Refresh & Go to Dashboard", 
                    variant="primary",
                    size="lg",
                    elem_classes="setup-button"
                )
                
                instructions_display = gr.Markdown(visible=False)
                
                def show_dashboard_instructions():
                    """Show instructions for accessing the dashboard."""
                    return """
                    ## 🎉 Ready to Go!
                    
                    Your NPC world has been created successfully! 
                    
                    **Click the button below to refresh and access the dashboard.**
                    
                    The dashboard includes:
                    - 🤖 AI Agent Operations (Generate NPCs, Plan Trades, Execute Trades)
                    - 📊 Village Overview (View all NPCs and their status)
                    - 💰 Trade History (Track all transactions)
                    - 📈 Inventory Changes (Compare initial vs current inventories)
                    
                    **Dashboard URL:** http://localhost:7861
                    """
                
                # Manual refresh button
                refresh_dashboard_btn.click(
                    fn=show_dashboard_instructions,
                    inputs=None,
                    outputs=instructions_display,
                    js="""
                    () => {
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    }
                    """
                )
            
            # State to track if we should show the dashboard
            show_dashboard = gr.State(False)
            
            # Hidden trigger for auto-refresh after world creation
            refresh_trigger = gr.Textbox(visible=False, elem_id="refresh_trigger")
            
            def check_status():
                """Check database status and update UI accordingly."""
                status_msg, is_setup, show_button = self.check_database_status()
                
                return (
                    status_msg,
                    gr.Button(visible=True),  # Always show the button
                    gr.Textbox(visible=False),
                    is_setup
                )
            
            def show_creating_status():
                """Show status message that world is being created."""
                return (
                    gr.Textbox(visible=False),
                    gr.Markdown(visible=True),
                    gr.Button(visible=False)
                )
            
            def run_setup():
                """Run the world setup process."""
                # Run the world creation process
                result = self.run_create_world(lambda msg: None)  # Simplified callback
                
                # Check status again after setup
                db_status_msg, is_setup, show_button = self.check_database_status()
                
                # Show success section if setup was successful
                show_success = "✅" in result and "successfully" in result.lower()
                
                # Update status message based on result
                if show_success:
                    status_msg = "✅ World creation completed successfully!"
                    db_status_msg = "✅ Database is properly set up and ready to use!"
                else:
                    status_msg = "❌ World creation failed. Check the results below."
                
                # Create a list of return values
                return_vals = [
                    result,
                    gr.Textbox(visible=True),
                    status_msg,
                    gr.Markdown(visible=False),  # Hide status indicator
                    db_status_msg,
                    gr.Button(visible=not show_success),  # Hide button only if setup was successful
                    is_setup,
                    gr.Group(visible=show_success, elem_id="success_section"),
                    "refresh" if show_success else ""  # Trigger auto-refresh
                ]
                
                return tuple(return_vals)
            
            # Event handlers
            check_status_btn.click(
                check_status,
                outputs=[status_display, setup_world_btn, setup_output, show_dashboard]
            )
            
            setup_world_btn.click(
                show_creating_status,
                outputs=[setup_output, setup_status, setup_world_btn]
            ).then(
                run_setup,
                outputs=[setup_output, setup_output, status_display, setup_status, status_display, setup_world_btn, show_dashboard, success_section, refresh_trigger],
                js="""
                (trigger) => {
                    // Auto-refresh after successful world creation
                    if (trigger === 'refresh') {
                        setTimeout(() => {
                            window.location.reload();
                        }, 3000);
                    }
                    return '';
                }
                """
            )
            
        
        return interface, check_status
