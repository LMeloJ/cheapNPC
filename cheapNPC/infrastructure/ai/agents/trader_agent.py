"""
Refactored Trader Agent using the service layer.

This module contains AI agents for executing trading plans using the clean architecture.
"""

import asyncio
from openai import AsyncOpenAI
import os
from agents import Agent, OpenAIChatCompletionsModel, trace, Runner, function_tool
from cheapNPC.core.models import (
    CrafterNPC, SalesPersonNPC, InventoryEntry, ItemQuality,
    TradeItem, TradingPair, TradingPlan, TradeResult, TradingExecutionResult
)
from cheapNPC.core.services import NPCService, TradingService
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any


load_dotenv(override=True)

# --- Configuration and Client Setup ---

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)


# Service layer integration
npc_service = NPCService()
trading_service = TradingService()


@function_tool
def get_npcs_for_trading() -> List[Any]:
    """Get all NPCs with their inventories for trading analysis using the service layer."""
    return npc_service.get_all_npcs_with_inventories()


@function_tool
def update_npc_inventory(data: CrafterNPC | SalesPersonNPC) -> str:
    """Update an NPC's inventory using the service layer."""
    return npc_service.update_npc(data)


@function_tool
def record_npc_transaction(
    buying_npc: str,
    selling_npc: str,
    item_name: str,
    quantity: int,
    price: float,
    quality: str = None,
    transaction_time: float = None
) -> str:
    """Record a transaction between NPCs using the service layer."""
    return trading_service.record_transaction(
        buying_npc, selling_npc, item_name, quantity, price, quality, transaction_time
    )


class TraderAgent:
    """
    An agent that receives a trading plan and executes all trades using the service layer,
    updating the database with the results.
    """
    
    INSTRUCTIONS = (
        "You are a trading execution agent for a D&D village simulation. "
        "You will receive a trading plan with multiple trading pairs and must execute all trades "
        "by updating NPC inventories and recording transactions using the provided tools.\n\n"
        
        "CRITICAL: You MUST use the provided tools to execute trades. For each trading pair:\n"
        "1. **Verify Trade Feasibility**: Check if the seller has enough items and the buyer has enough silver\n"
        "2. **Execute the Trade**: Use 'update_npc_inventory' to update BOTH NPCs' inventories and silver pieces\n"
        "3. **Record Transaction**: Use 'record_npc_transaction' to log each successful transaction\n"
        "4. **Handle Failures**: If a trade fails, provide a clear reason\n\n"
        
        "IMPORTANT TOOL USAGE:\n"
        "- Use 'update_npc_inventory' with the COMPLETE NPC object (including all inventory items)\n"
        "- For each trade, you need to call 'update_npc_inventory' TWICE (once for buyer, once for seller)\n"
        "- Use 'record_npc_transaction' for each successful trade\n"
        "- If any trade fails, continue with the others\n\n"
        
        "After executing all trades, provide a DETAILED summary including:\n"
        "- Which trades were successful (list each one)\n"
        "- Which trades failed and why\n"
        "- Total value traded\n"
        "- Confirmation that tools were called\n"
        "- Any important notes about the execution"
    )

    trader_agent = Agent(
        name="Trading Execution Agent",
        instructions=INSTRUCTIONS,
        model=gemini_model,
        output_type=None,
        tools=[update_npc_inventory, record_npc_transaction]
    )

    @staticmethod
    def format_trading_plan_for_ai(plan: TradingPlan) -> str:
        """
        Formats the trading plan into a readable string for the AI agent.
        """
        formatted_data = "=== TRADING PLAN TO EXECUTE ===\n\n"
        formatted_data += f"Plan Summary: {plan.plan_summary}\n"
        formatted_data += f"Total Expected Value: {plan.total_expected_value:.2f} SP\n"
        formatted_data += f"Number of Trading Pairs: {len(plan.trading_pairs)}\n\n"
        
        formatted_data += "TRADING PAIRS TO EXECUTE:\n"
        formatted_data += "-" * 50 + "\n"
        
        for i, pair in enumerate(plan.trading_pairs, 1):
            formatted_data += f"\n{i}. {pair.buyer_name} → {pair.seller_name}\n"
            formatted_data += f"   Reasoning: {pair.reasoning}\n"
            formatted_data += f"   Items to Trade:\n"
            
            total_cost = 0
            for item in pair.items_to_trade:
                item_cost = item.quantity * item.price
                total_cost += item_cost
                formatted_data += f"      • {item.name}: {item.quantity} @ {item.price} SP = {item_cost:.2f} SP\n"
            
            formatted_data += f"   Total Cost: {total_cost:.2f} SP\n"
        
        return formatted_data

    @staticmethod
    def format_npc_data_for_ai(npcs: List[Any]) -> str:
        """
        Formats NPC data into a readable string for the AI agent.
        """
        formatted_data = "=== CURRENT NPCs AND INVENTORIES ===\n\n"
        
        for npc in npcs:
            formatted_data += f"**{npc.name}** ({npc.race})\n"
            formatted_data += f"- Profession: {npc.profession}\n"
            formatted_data += f"- Silver Pieces: {npc.silver_pieces} SP\n"
            formatted_data += f"- Inventory ({len(npc.inventory)} items):\n"
            
            if npc.inventory:
                for item in npc.inventory:
                    formatted_data += f"  • {item.name}: {item.quantity} @ {item.price} SP ({item.quality})\n"
            else:
                formatted_data += "  • No items in inventory\n"
            
            formatted_data += "\n"
        
        return formatted_data

    @staticmethod
    async def execute_trading_plan(plan: TradingPlan) -> str:
        """
        Main method that executes a trading plan by making a single API call
        to process all trades and update the database using the service layer.
        """
        print("🔄 Executing trading plan using service layer...")
        
        # Step 1: Get NPCs using service layer
        print("📊 Retrieving NPCs using service layer...")
        npcs = npc_service.get_all_npcs_with_inventories()
        print(f"✅ Retrieved {len(npcs)} NPCs from service layer")
        
        # Step 2: Format trading plan and NPC data for AI
        plan_data = TraderAgent.format_trading_plan_for_ai(plan)
        npc_data = TraderAgent.format_npc_data_for_ai(npcs)
        print("📊 Formatted trading plan and NPC data for AI execution")
        
        # Step 3: Execute all trades via single API call
        print("🤖 Calling AI to execute all trades...")
        
        message = (
            f"{plan_data}\n\n"
            f"{npc_data}\n\n"
            "Execute all the trading pairs listed above using the current NPC data provided. For each trade:\n"
            "1. Verify that each trade is feasible (seller has items, buyer has silver)\n"
            "2. Use 'update_npc_inventory' to update both NPCs' inventories and silver pieces\n"
            "3. Use 'record_npc_transaction' to log each successful transaction\n"
            "4. If any trade fails, note the reason and continue with others\n\n"
            "Process all trades in a single response, updating the database as you go."
        )
        
        with trace("Execute Trading Plan"):
            result = await Runner.run(TraderAgent.trader_agent, message)
        
        print("✅ Trading execution completed")
        return result.final_output

    @staticmethod
    def display_execution_results(result: str):
        """
        Displays the trading execution results in a readable format.
        """
        print("\n" + "="*60)
        print("💰 TRADING EXECUTION RESULTS")
        print("="*60)
        print(f"\n{result}")
        print("\n" + "="*60)


# Example usage function
async def execute_plan_from_planner():
    """
    Example function that shows how to use the trader_agent with a plan from planner_agent.
    """
    from cheapNPC.infrastructure.ai.agents.planner_agent import PlannerAgent
    
    print("🚀 Starting Trading Execution Pipeline...")
    
    try:
        # Step 1: Create trading plan using planner_agent
        print("\n📋 Step 1: Creating trading plan...")
        planner = PlannerAgent()
        plan = await planner.create_trading_plan()
        PlannerAgent.display_trading_plan(plan)
        
        # Step 2: Execute trading plan using trader_agent
        print("\n💰 Step 2: Executing trading plan...")
        result = await TraderAgent.execute_trading_plan(plan)
        TraderAgent.display_execution_results(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


# Main execution
if __name__ == '__main__':
    asyncio.run(execute_plan_from_planner())
