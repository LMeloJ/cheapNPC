"""
Trader Agent controller for cheapNPC MVC architecture.

This controller contains AI agents for executing trading plans using the MVC pattern.
"""

import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, trace, Runner, function_tool
from cheapNPC.models import (
    CrafterNPC, SalesPersonNPC, InventoryEntry, ItemQuality,
    TradeItem, TradingPair, TradingPlan, TradeResult, TradingExecutionResult
)
from cheapNPC.services.npc_service import NPCService
from cheapNPC.services.trading_service import TradingService
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any


load_dotenv(override=True)

# --- Configuration and Client Setup ---
from cheapNPC.config import get_config

config = get_config()

ai_client = AsyncOpenAI(base_url=config.ai.base_url, api_key=config.ai.api_key)
ai_model = OpenAIChatCompletionsModel(model=config.ai.model_name, openai_client=ai_client)


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
        
        "After executing all trades, provide a CONCISE summary with:\n"
        "- Simple list of successful trades (format: 'Buyer → Seller: Item (Qty x Price)')\n"
        "- List of failed trades with brief reason\n"
        "- Total value traded\n"
        "- Keep the summary brief and easy to read"
    )

    trader_agent = Agent(
        name="Trading Execution Agent",
        instructions=INSTRUCTIONS,
        model=ai_model,
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
            "Execute all the trading pairs listed above using the current NPC data provided.\n\n"
            "Instructions:\n"
            "1. Verify each trade is feasible (seller has items, buyer has silver)\n"
            "2. Use 'update_npc_inventory' to update both NPCs (buyer and seller)\n"
            "3. Use 'record_npc_transaction' to log each successful transaction\n"
            "4. If any trade fails, note the reason and continue with others\n\n"
            "Provide a brief summary at the end in this format:\n"
            "**Successful Trades:**\n"
            "- Buyer → Seller: Item (Qty × Price)\n"
            "**Failed Trades:**\n"
            "- Buyer → Seller: Reason\n"
            "**Total Value:** XX.XX SP"
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



