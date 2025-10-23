"""
Refactored NPC Agent using the service layer.

This module contains AI agents for NPC trading negotiations using the clean architecture.
"""

import asyncio
from openai import AsyncOpenAI
import os
from agents import Agent, OpenAIChatCompletionsModel, trace, Runner
from cheapNPC.core.models import (
    CrafterNPC, SalesPersonNPC, ProfessionSkill, InventoryEntry, ItemQuality,
    TradeOffer, TradeResponse, NegotiationResult, TradingPlan, NPCPairing
)
from cheapNPC.core.services import NPCService, TradingService
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


load_dotenv(override=True)

# --- Configuration and Client Setup ---

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)


class NPCAgent:
    """
    An agent that represents a single NPC and can make trading decisions
    based on their profession, skill level, and current inventory.
    """
    
    def __init__(self, npc_name: str):
        self.npc_name = npc_name
        self.npc_data = None
        self.npc_service = NPCService()
        self._load_npc_data()
    
    def _load_npc_data(self):
        """Load NPC data using the service layer."""
        self.npc_data = self.npc_service.get_npc_with_inventory(self.npc_name)
        if not self.npc_data:
            raise ValueError(f"NPC '{self.npc_name}' not found in database")
    
    def get_npc_info(self) -> str:
        """Get formatted information about this NPC."""
        if not self.npc_data:
            return f"NPC '{self.npc_name}' not found"
        
        info = f"**{self.npc_data.name}** ({self.npc_data.race})\n"
        info += f"- Profession: {self.npc_data.profession}\n"
        info += f"- Skill Level: {self.npc_data.profession_skill}\n"
        info += f"- Silver Pieces: {self.npc_data.silver_pieces} SP\n"
        info += f"- Inventory ({len(self.npc_data.inventory)} items):\n"
        
        if self.npc_data.inventory:
            for item in self.npc_data.inventory:
                info += f"  • {item.name}: {item.quantity} @ {item.price} SP ({item.quality})\n"
        else:
            info += "  • No items in inventory\n"
        
        return info
    
    def get_trading_priorities(self) -> List[str]:
        """Get trading priorities based on profession and skill level."""
        priorities = []
        
        # Base priorities on profession
        if hasattr(self.npc_data.profession, 'value'):
            profession = self.npc_data.profession.value
        else:
            profession = str(self.npc_data.profession)
        
        # Crafting professions want raw materials
        if profession in ['blacksmith', 'carpenter', 'tailor', 'leatherworker']:
            priorities.extend(['iron ore', 'wood', 'cloth', 'leather', 'raw materials'])
        
        # Gathering professions want tools and finished goods
        elif profession in ['miner', 'woodcutter', 'farmer', 'herder']:
            priorities.extend(['tools', 'weapons', 'clothing', 'food', 'finished goods'])
        
        # Sales professions want variety and profitable items
        elif profession in ['merchant', 'trader']:
            priorities.extend(['rare items', 'high-quality goods', 'profitable items'])
        
        return priorities
    
    def can_afford(self, price: float) -> bool:
        """Check if NPC can afford a given price."""
        return self.npc_data.silver_pieces >= price
    
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Check if NPC has enough of a specific item."""
        for item in self.npc_data.inventory:
            if item.name.lower() == item_name.lower():
                return item.quantity >= quantity
        return False
    
    def get_item_price(self, item_name: str) -> Optional[float]:
        """Get the price of an item this NPC sells."""
        for item in self.npc_data.inventory:
            if item.name.lower() == item_name.lower():
                return item.price
        return None
    
    def get_item_quantity(self, item_name: str) -> int:
        """Get the quantity of an item this NPC has."""
        for item in self.npc_data.inventory:
            if item.name.lower() == item_name.lower():
                return item.quantity
        return 0


class NPCTradingAgent:
    """
    An agent that handles trading negotiations between two NPCs using the service layer.
    """
    
    def __init__(self):
        self.npc_service = NPCService()
        self.trading_service = TradingService()
    
    INSTRUCTIONS = (
        "You are a trading negotiation agent for a D&D village simulation. "
        "You will receive information about two NPCs and must facilitate a trading negotiation "
        "between them. Your goal is to help them reach a mutually beneficial trade agreement.\n\n"
        
        "Consider the following factors:\n"
        "1. **Profession Compatibility**: What items would each NPC naturally want based on their profession?\n"
        "2. **Economic Viability**: Can both NPCs afford the proposed trade?\n"
        "3. **Inventory Needs**: What does each NPC need vs. what they have excess of?\n"
        "4. **Skill Level**: Higher skilled NPCs may be more selective about quality\n"
        "5. **Previous Transactions**: Consider their trading history if available\n\n"
        
        "The negotiation should be realistic and consider each NPC's personality, profession, "
        "and economic situation. Help them reach a fair agreement or determine if no trade is possible."
    )
    
    trading_agent = Agent(
        name="NPC Trading Negotiation Agent",
        instructions=INSTRUCTIONS,
        model=gemini_model,
        output_type=NegotiationResult,
        tools=[]
    )
    
    def format_npc_pair_for_negotiation(self, npc1: NPCAgent, npc2: NPCAgent, trading_history: List[Any] = None) -> str:
        """Format information about two NPCs for trading negotiation."""
        formatted_data = "=== NPC TRADING NEGOTIATION ===\n\n"
        
        formatted_data += "NPC 1 (Potential Buyer):\n"
        formatted_data += npc1.get_npc_info() + "\n"
        formatted_data += f"Trading Priorities: {', '.join(npc1.get_trading_priorities())}\n\n"
        
        formatted_data += "NPC 2 (Potential Seller):\n"
        formatted_data += npc2.get_npc_info() + "\n"
        formatted_data += f"Trading Priorities: {', '.join(npc2.get_trading_priorities())}\n\n"
        
        if trading_history:
            formatted_data += "Previous Trading History:\n"
            for tx in trading_history[:5]:  # Show last 5 transactions
                formatted_data += f"  • {tx.buying_npc} bought {tx.quantity} {tx.name} from {tx.selling_npc} for {tx.price} SP\n"
            formatted_data += "\n"
        
        return formatted_data
    
    async def negotiate_trade(self, npc1_name: str, npc2_name: str) -> NegotiationResult:
        """
        Facilitate a trading negotiation between two NPCs using the service layer.
        Returns the result of their negotiation.
        """
        print(f"🤝 Starting trade negotiation between {npc1_name} and {npc2_name}...")
        
        # Load NPC data using service layer
        npc1 = NPCAgent(npc1_name)
        npc2 = NPCAgent(npc2_name)
        
        # Get trading history between these NPCs using service layer
        trading_history = self.trading_service.get_transaction_history_between(npc1_name, npc2_name)
        
        # Format data for AI negotiation
        npc_data = self.format_npc_pair_for_negotiation(npc1, npc2, trading_history)
        
        # Create negotiation prompt
        message = (
            f"{npc_data}\n\n"
            "Facilitate a trading negotiation between these two NPCs. Consider their professions, "
            "inventories, silver pieces, and trading priorities. Help them reach a mutually beneficial "
            "trade agreement or determine if no trade is possible.\n\n"
            "Provide a realistic negotiation result including:\n"
            "- Whether they successfully agreed on a trade\n"
            "- What item, quantity, and price they agreed on\n"
            "- A log of the negotiation process\n"
            "- Reasoning for the outcome"
        )
        
        with trace("NPC Trade Negotiation"):
            result = await Runner.run(NPCTradingAgent.trading_agent, message)
        
        print(f"✅ Negotiation completed between {npc1_name} and {npc2_name}")
        return result.final_output
    
    async def execute_negotiated_trade(self, negotiation_result: NegotiationResult) -> str:
        """
        Execute a successfully negotiated trade using the service layer.
        """
        return self.trading_service.execute_negotiated_trade(negotiation_result)


async def execute_npc_trading_from_plan(trading_plan: TradingPlan) -> str:
    """
    Execute trading negotiations for all NPC pairs in a trading plan using the service layer.
    This is the main function that processes a trading plan and makes NPCs negotiate trades.
    """
    print("🚀 Starting NPC Trading Execution from Plan...")
    
    trading_agent = NPCTradingAgent()
    results = []
    successful_trades = 0
    failed_trades = 0
    
    for pairing in trading_plan.pairings:
        print(f"\n--- Processing Pair: {pairing.buyer_name} ↔ {pairing.seller_name} ---")
        
        try:
            # Negotiate trade between the two NPCs
            negotiation_result = await trading_agent.negotiate_trade(
                pairing.buyer_name, 
                pairing.seller_name
            )
            
            if negotiation_result.success:
                # Execute the successful trade
                execution_result = await trading_agent.execute_negotiated_trade(negotiation_result)
                results.append(f"✅ {pairing.buyer_name} ↔ {pairing.seller_name}: {execution_result}")
                successful_trades += 1
            else:
                results.append(f"❌ {pairing.buyer_name} ↔ {pairing.seller_name}: No trade agreed - {negotiation_result.reasoning}")
                failed_trades += 1
                
        except Exception as e:
            results.append(f"❌ {pairing.buyer_name} ↔ {pairing.seller_name}: Error - {e}")
            failed_trades += 1
    
    # Summary
    summary = f"""
🏪 NPC TRADING EXECUTION SUMMARY
===============================
Total Pairs Processed: {len(trading_plan.pairings)}
Successful Trades: {successful_trades}
Failed Trades: {failed_trades}

DETAILED RESULTS:
{chr(10).join(results)}
"""
    
    print(summary)
    return summary


# Example usage function
async def demo_npc_trading():
    """
    Demo function showing how to use the NPC trading system with the service layer.
    """
    from cheapNPC.infrastructure.ai.agents.planner_agent import PlannerAgent
    
    print("🚀 Starting NPC Trading Demo...")
    
    try:
        # Step 1: Create trading plan using planner_agent
        print("\n📋 Step 1: Creating trading plan...")
        planner = PlannerAgent()
        plan = await planner.create_trading_plan()
        PlannerAgent.display_trading_plan(plan)
        
        # Step 2: Execute NPC trading negotiations
        print("\n🤝 Step 2: Executing NPC trading negotiations...")
        result = await execute_npc_trading_from_plan(plan)
        
        print("\n" + "="*60)
        print("💰 FINAL TRADING RESULTS")
        print("="*60)
        print(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


# Main execution
if __name__ == '__main__':
    asyncio.run(demo_npc_trading())
