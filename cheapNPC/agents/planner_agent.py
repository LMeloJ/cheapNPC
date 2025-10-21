import sqlite3
import os
import asyncio
from typing import List, Optional
from dotenv import load_dotenv

# Assuming 'agents' and 'AsyncOpenAI' are available in your environment.
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
from pydantic import BaseModel, Field

from cheapNPC.db.village_db import get_npc_with_inventory, update_npc_inventory
load_dotenv(override=True)

# --- Configuration and Client Setup ---

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# NOTE: Ensure GOOGLE_API_KEY is set in your environment
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)

DB_NAME = 'data/village.db'

# --- Trade-Specific Pydantic Model (Agent Output) ---

class TradeSummary(BaseModel):
    """Summarizes the outcome of the simulated trade."""
    npc_buyer: str = Field(description="The name of the NPC who made purchases.")
    npc_seller: str = Field(description="The name of the NPC who sold items.")
    items_exchanged_description: str = Field(description="A narrative description of the items that were successfully bought and sold, and the total silver exchanged.")
    transaction_status: str = Field(description="The final status of the trade, e.g., 'Success: Database updated' or 'Failure: Insufficient funds.'")


# --- Agent Definition ---

TRADE_INSTRUCTIONS = f"""
You are the Trade Simulation Agent. Your task is to facilitate a fair trade between two NPCs whose names are provided in the query.

Follow these steps precisely:
1. **Retrieve Data:** Use the 'get_npc_with_inventory' tool twice to fetch the full data for both NPCs.
2. **Analyze and Simulate Trade:** - Determine which NPC would benefit most from buying an item the other NPC is selling.
    - Both NPCs can buy and sell items. The transaction must be based on the listed prices, items, and the silver available to both NPCs.
    - A transaction should only happen if the buyer has enough silver (Buyer.silver_pieces >= Item.price * quantity).
    - The NPC decides to buy an item if he plans on using it during this week.
    - Calculate the final inventory and silver for both NPCs after the successful trade(s).
3. **Update Database:** Use the 'update_npc_inventory' tool for *both* NPCs with their new, post-trade data.
4. **Final Output:** Formulate the final response as a detailed TradeSummary object describing the interaction and the outcome. If no trade was possible (e.g., one NPC was missing), explain why in the summary.
"""

trade_agent = Agent(
    name="TradeSimulationAgent",
    instructions=TRADE_INSTRUCTIONS,
    model=gemini_model,
    output_type=None, 
    tools=[get_npc_with_inventory, update_npc_inventory]
)

# --- Example Usage (Requires NPCs to be in fantasy_commerce.db) ---

async def run_trade_example():
    """
    Demonstrates running the trade agent. 
    NOTE: You must run 'run_agent.py' from the previous step at least once 
    to populate the 'fantasy_commerce.db' file before this script will work correctly.
    """
    print("--- Trade Simulation Agent Initialized ---")
    
    # Query assumes 'Talin Stonehand' and 'Faelar' exist from previous examples
    query = "Simulate a trade between Grizelda Goodbarrel and Grimgor Ironhide. \
        They will inspect each other's items and according to their gold and item prices purchase or sell items to each other."
    print(f"User Query: {query}")
    
    print("\n--- Agent Working... (Check tool calls in console) ---")
    
    try:
        trade_result = await Runner.run(trade_agent, query)
        
    except Exception as e:
        print(f"\nAn error occurred during agent execution: {e}")
        print("Please ensure the required 'agents' library is installed and GOOGLE_API_KEY is set.")


if __name__ == '__main__':
    asyncio.run(run_trade_example())