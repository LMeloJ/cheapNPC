"""
Planner Agent controller for cheapNPC MVC architecture.

This controller contains AI agents for planning trading operations using the MVC pattern.
"""

import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, trace, Runner
from cheapNPC.models import NPCPairing, TradingPlan
from cheapNPC.services.npc_service import NPCService
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any


load_dotenv(override=True)

# --- Configuration and Client Setup ---
from cheapNPC.config import get_config

config = get_config()

ai_client = AsyncOpenAI(base_url=config.ai.base_url, api_key=config.ai.api_key)
ai_model = OpenAIChatCompletionsModel(model=config.ai.model_name, openai_client=ai_client)


class PlannerAgent:
    """
    An agent that retrieves all NPCs using the service layer and uses AI to decide on trading pairings.
    """
    
    def __init__(self):
        self._npc_service = None
    
    @property
    def npc_service(self):
        """Lazy initialization of NPC service."""
        if self._npc_service is None:
            self._npc_service = NPCService()
        return self._npc_service
    
    INSTRUCTIONS = (
        "You are a trading planner for a D&D village simulation. "
        "You will receive information about all NPCs in the village, including their inventories, "
        "professions, and silver pieces. Your job is to create simple trading pairings.\n\n"
        
        "Consider the following factors when creating trading pairs:\n"
        "1. **Complementary Professions**: Pair NPCs whose professions naturally complement each other\n"
        "2. **Supply and Demand**: Look for NPCs who have excess items that others need\n"
        "3. **Economic Viability**: Ensure both parties have sufficient silver pieces\n\n"
        
        "Create 3-5 simple trading pairings. For each pairing, only specify:\n"
        "- Which NPC is the buyer\n"
        "- Which NPC is the seller\n\n"
        
        "Return only a list of NPC pairings - no detailed reasoning or item specifications needed."
    )

    planner_agent = Agent(
        name="Trading Planner Agent",
        instructions=INSTRUCTIONS,
        model=ai_model,
        output_type=TradingPlan,
        tools=[]
    )

    def format_npc_data_for_ai(self, npcs: List[Any]) -> str:
        """
        Formats NPC data into a readable string for the AI agent.
        """
        formatted_data = "=== VILLAGE NPCs AND INVENTORIES ===\n\n"
        
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

    async def create_trading_plan(self) -> TradingPlan:
        """
        Main method that retrieves all NPCs using the service layer and creates a trading plan via API call.
        """
        print("🔄 Retrieving all NPCs using service layer...")
        
        # Step 1: Retrieve all NPCs using service layer
        npcs = self.npc_service.get_all_npcs_with_inventories()
        print(f"✅ Retrieved {len(npcs)} NPCs from service layer")
        
        if len(npcs) < 2:
            print("⚠️  Not enough NPCs for trading (need at least 2)")
            return TradingPlan(
                pairings=[]
            )
        
        # Step 2: Format NPC data for AI
        npc_data = self.format_npc_data_for_ai(npcs)
        print("📊 Formatted NPC data for AI analysis")
        
        # Step 3: Create trading plan via API call
        print("🤖 Calling AI to create trading plan...")
        
        message = (
            f"{npc_data}\n\n"
            "Based on the NPCs and their inventories above, create simple trading pairings. "
            "Focus on pairing NPCs whose professions complement each other and who have "
            "complementary inventory needs. Create 3-5 simple pairings with just buyer and seller names."
        )
        
        with trace("Create Trading Plan"):
            result = await Runner.run(PlannerAgent.planner_agent, message)
        
        print("✅ Trading plan created successfully")
        return result.final_output

    @staticmethod
    def display_trading_plan(plan: TradingPlan):
        """
        Displays the trading plan in a simple format.
        """
        print("\n" + "="*50)
        print("🏪 VILLAGE TRADING PAIRINGS")
        print("="*50)
        
        print(f"🤝 Number of Trading Pairs: {len(plan.pairings)}")
        
        print("\n" + "-"*50)
        print("TRADING PAIRINGS:")
        print("-"*50)
        
        for i, pair in enumerate(plan.pairings, 1):
            print(f"{i}. {pair.buyer_name} → {pair.seller_name}")
        
        print("\n" + "="*50)


