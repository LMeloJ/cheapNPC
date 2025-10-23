"""
Agent Operations component for the CheapNPC dashboard.

This component handles all AI agent operations including:
- NPC generation using generator agents
- Trading plan creation using planner agent
- Trade execution using trader agent
"""

import gradio as gr
import asyncio
import threading
from typing import Any, Dict, List, Optional, Tuple

from cheapNPC.core.models.npcs import SalesPersonProfession, CraftAndGatherProfessions
from cheapNPC.infrastructure.ai.agents.generator_agent import (
    SalesPersonNPCGeneratorAgent, 
    CrafterNPCGeneratorAgent
)
from cheapNPC.infrastructure.ai.agents.planner_agent import PlannerAgent
from cheapNPC.infrastructure.ai.agents.trader_agent import TraderAgent

from cheapNPC.presentation.web.shared.base_component import BaseComponent


class AgentOperationsComponent(BaseComponent):
    """Component for handling AI agent operations."""
    
    def __init__(self):
        """Initialize the agent operations component."""
        super().__init__()
        
        # Lazy initialization of agents
        self._planner_agent = None
        
        # Execution status tracking
        self.execution_status = {
            "generator": {"running": False, "output": ""},
            "planner": {"running": False, "output": ""},
            "trader": {"running": False, "output": ""}
        }
    
    @property
    def planner_agent(self):
        """Lazy initialization of planner agent."""
        if self._planner_agent is None:
            self._planner_agent = PlannerAgent()
        return self._planner_agent
    
    def execute_generator_agent(self, npc_type: str, profession: str, quantity: int, progress_callback=None):
        """Execute the generator agent to create new NPCs."""
        self.execution_status["generator"]["running"] = True
        self.execution_status["generator"]["output"] = ""
        
        try:
            if progress_callback:
                progress_callback("🔄 Starting NPC generation...")
            
            # Get NPCs before generation to track what was created
            npcs_before = set(npc['name'] for npc in self.npc_service.get_all_npc_summaries())
            
            # Run async function in thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def generate_npcs():
                if npc_type == "SalesPersonNPC":
                    if quantity == 1:
                        result = await SalesPersonNPCGeneratorAgent.run_create_agent(profession)
                    else:
                        professions_list = [profession] * quantity if profession else []
                        result = await SalesPersonNPCGeneratorAgent.run_create_multiple_agents(professions_list)
                else:  # CrafterNPC
                    if quantity == 1:
                        result = await CrafterNPCGeneratorAgent.run_create_agent(profession)
                    else:
                        professions_list = [profession] * quantity if profession else []
                        result = await CrafterNPCGeneratorAgent.run_create_multiple_agents(professions_list)
                
                return result
            
            result = loop.run_until_complete(generate_npcs())
            loop.close()
            
            # Get NPCs after generation to find what was created
            npcs_after = set(npc['name'] for npc in self.npc_service.get_all_npc_summaries())
            created_npcs = list(npcs_after - npcs_before)
            
            output = f"✅ Successfully generated {quantity} {npc_type}(s)"
            if profession:
                output += f" with profession '{profession}'"
            
            if created_npcs:
                output += f"\n\n📝 Created NPCs:\n"
                for i, name in enumerate(created_npcs, 1):
                    output += f"   {i}. {name}\n"
            
            self.execution_status["generator"]["output"] = output
            self.execution_status["generator"]["running"] = False
            
            if progress_callback:
                progress_callback(output)
            
            return output
            
        except Exception as e:
            error_msg = f"❌ Error generating NPCs: {str(e)}"
            self.execution_status["generator"]["output"] = error_msg
            self.execution_status["generator"]["running"] = False
            
            if progress_callback:
                progress_callback(error_msg)
            
            return error_msg
    
    def execute_planner_agent(self, progress_callback=None):
        """Execute the planner agent to create trading plans."""
        self.execution_status["planner"]["running"] = True
        self.execution_status["planner"]["output"] = ""
        
        try:
            if progress_callback:
                progress_callback("🔄 Analyzing NPCs and creating trading plan...")
            
            # Run async function in thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def create_plan():
                plan = await self.planner_agent.create_trading_plan()
                return plan
            
            plan = loop.run_until_complete(create_plan())
            loop.close()
            
            # Format the trading plan for display
            output = f"📋 Trading Plan Created Successfully!\n\n"
            output += f"🤝 Number of Trading Pairs: {len(plan.pairings)}\n\n"
            output += "TRADING PAIRINGS:\n"
            output += "-" * 50 + "\n"
            
            for i, pair in enumerate(plan.pairings, 1):
                output += f"{i}. {pair.buyer_name} → {pair.seller_name}\n"
            
            output += f"\n✅ Plan ready for execution!"
            
            self.execution_status["planner"]["output"] = output
            self.execution_status["planner"]["running"] = False
            
            if progress_callback:
                progress_callback(output)
            
            return output, plan
            
        except Exception as e:
            error_msg = f"❌ Error creating trading plan: {str(e)}"
            self.execution_status["planner"]["output"] = error_msg
            self.execution_status["planner"]["running"] = False
            
            if progress_callback:
                progress_callback(error_msg)
            
            return error_msg, None
    
    def execute_trader_agent(self, plan, progress_callback=None):
        """Execute the trader agent to execute trading plans."""
        self.execution_status["trader"]["running"] = True
        self.execution_status["trader"]["output"] = ""
        
        try:
            if progress_callback:
                progress_callback("🔄 Executing trades...")
            
            # Run async function in thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def execute_trades():
                result = await TraderAgent.execute_trading_plan(plan)
                return result
            
            result = loop.run_until_complete(execute_trades())
            loop.close()
            
            output = f"💰 Trading Execution Completed!\n\n"
            output += f"{result}\n\n"
            output += f"✅ All trades processed successfully!"
            
            self.execution_status["trader"]["output"] = output
            self.execution_status["trader"]["running"] = False
            
            if progress_callback:
                progress_callback(output)
            
            return output
            
        except Exception as e:
            error_msg = f"❌ Error executing trades: {str(e)}"
            self.execution_status["trader"]["output"] = error_msg
            self.execution_status["trader"]["running"] = False
            
            if progress_callback:
                progress_callback(error_msg)
            
            return error_msg
    
    def create_interface(self) -> gr.Blocks:
        """Create the agent operations interface."""
        
        with gr.Blocks() as agent_interface:
            gr.Markdown("## AI Agent Operations")
            gr.Markdown("Use the AI agents to generate NPCs, create trading plans, and execute trades.")
            
            with gr.Row():
                # Generator Agent Section
                with gr.Column(scale=1):
                    with gr.Group(elem_classes="agent-section"):
                        gr.Markdown("### 🎭 NPC Generator Agent")
                        gr.Markdown("Create new NPCs with AI-generated characteristics and inventories.")
                        
                        npc_type_dropdown = gr.Dropdown(
                            choices=["SalesPersonNPC", "CrafterNPC"],
                            value="SalesPersonNPC",
                            label="NPC Type",
                            interactive=True
                        )
                        
                        profession_dropdown = gr.Dropdown(
                            choices=[],
                            label="Profession (optional)",
                            interactive=True,
                            allow_custom_value=True
                        )
                        gr.Markdown("*Select a profession or leave empty for random generation*")
                        
                        quantity_slider = gr.Slider(
                            minimum=1,
                            maximum=5,
                            value=1,
                            step=1,
                            label="Number of NPCs to create",
                            interactive=True
                        )
                        
                        generate_btn = gr.Button("🎭 Generate NPCs", variant="primary")
                        
                        generator_output = gr.Textbox(
                            label="Generator Output",
                            interactive=True,
                            elem_classes="output-box",
                            lines=12,
                            show_copy_button=True,
                            container=True
                        )
                
                # Planner Agent Section
                with gr.Column(scale=1):
                    with gr.Group(elem_classes="agent-section"):
                        gr.Markdown("### 📋 Trading Planner Agent")
                        gr.Markdown("Analyze NPCs and create optimal trading pairings.")
                        
                        plan_btn = gr.Button("📋 Create Trading Plan", variant="primary")
                        
                        planner_output = gr.Textbox(
                            label="Planner Output",
                            interactive=True,
                            elem_classes="output-box",
                            lines=12,
                            show_copy_button=True,
                            container=True
                        )
                
                # Trader Agent Section
                with gr.Column(scale=1):
                    with gr.Group(elem_classes="agent-section"):
                        gr.Markdown("### 💰 Trading Executor Agent")
                        gr.Markdown("Execute trading plans and update NPC inventories.")
                        
                        execute_btn = gr.Button("💰 Execute Trades", variant="primary", interactive=False)
                        
                        trader_output = gr.Textbox(
                            label="Trader Output",
                            interactive=True,
                            elem_classes="output-box",
                            lines=12,
                            show_copy_button=True,
                            container=True
                        )
            
            # Status indicators
            with gr.Row():
                generator_status = gr.Markdown("🟢 Generator: Ready")
                planner_status = gr.Markdown("🟢 Planner: Ready")
                trader_status = gr.Markdown("🟢 Trader: Ready")
            
            # Agent execution handlers
            def update_profession_choices(npc_type):
                """Update profession dropdown choices based on NPC type."""
                professions = self.get_available_professions(npc_type)
                return gr.Dropdown(choices=professions, value=None)
            
            def run_generator(npc_type, profession, quantity):
                def progress_callback(msg):
                    generator_output.value = msg
                    generator_status.value = f"🔄 Generator: Running..."
                
                result = self.execute_generator_agent(npc_type, profession, quantity, progress_callback)
                generator_status.value = "🟢 Generator: Ready"
                return result
            
            def run_planner():
                def progress_callback(msg):
                    planner_output.value = msg
                    planner_status.value = f"🔄 Planner: Running..."
                
                result, plan = self.execute_planner_agent(progress_callback)
                planner_status.value = "🟢 Planner: Ready"
                
                # Enable executor button if plan was created successfully
                if plan is not None:
                    return result, plan, gr.Button("💰 Execute Trades", variant="primary", interactive=True)
                else:
                    return result, plan, gr.Button("💰 Execute Trades", variant="primary", interactive=False)
            
            def run_trader(plan):
                if plan is None:
                    return "❌ No trading plan available. Please create a plan first."
                
                def progress_callback(msg):
                    trader_output.value = msg
                    trader_status.value = f"🔄 Trader: Running..."
                
                result = self.execute_trader_agent(plan, progress_callback)
                trader_status.value = "🟢 Trader: Ready"
                return result
            
            # Store the current plan
            current_plan = gr.State(None)
            
            # Event handlers
            npc_type_dropdown.change(
                update_profession_choices,
                inputs=npc_type_dropdown,
                outputs=profession_dropdown
            )
            
            generate_btn.click(
                run_generator,
                inputs=[npc_type_dropdown, profession_dropdown, quantity_slider],
                outputs=generator_output
            )
            
            plan_btn.click(
                run_planner,
                outputs=[planner_output, current_plan, execute_btn]
            )
            
            execute_btn.click(
                run_trader,
                inputs=current_plan,
                outputs=trader_output
            )
            
            # Initialize profession dropdown
            agent_interface.load(
                lambda: update_profession_choices("SalesPersonNPC"),
                outputs=profession_dropdown
            )
        
        return agent_interface
