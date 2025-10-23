"""
Refactored Generator Agent using the service layer.

This module contains AI agents for generating NPCs using the clean architecture.
"""

import asyncio
from openai import AsyncOpenAI
import os
from agents import Agent, OpenAIChatCompletionsModel, trace, Runner, function_tool
from cheapNPC.core.models import SalesPersonNPC, CrafterNPC, get_item_quality_by_skill
from cheapNPC.core.services import NPCService
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List


load_dotenv(override=True)

# --- Configuration and Client Setup ---

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)


# Service layer integration
npc_service = NPCService()


def save_npc_to_db(npc_data: SalesPersonNPC | CrafterNPC) -> str:
    """
    Saves a CrafterNPC or SalesPersonNPC to the database using the service layer.
    """
    print(f"\n[TOOL CALLED] Attempting to save NPC: {npc_data.name}")
    return npc_service.create_npc(npc_data)

# Create the function tool with proper name
save_npc_tool = function_tool(save_npc_to_db)

@function_tool
def get_item_quality_by_skill_tool(profession_skill: str) -> str:
    """
    Return an ItemQuality based on profession_skill using the service layer.
    """
    return get_item_quality_by_skill(profession_skill)



class SalesPersonNPCGeneratorAgent:
    """AI agent for generating SalesPerson NPCs."""
    
    SALESPERSON_NPC_SCHEMA = (
        "SalesPerson(\n"
        "  name: str (The name of the created NPC),\n"
        "  race: str (D&D race),\n"
        "  profession: str (merchant type, e.g., local or traveling),\n"
        "  profession_skill: str (must be one of: 'poor', 'regular', 'fine', 'exceptional'),\n"
        "  inventory: List[InventoryEntry] (with 'name', 'quantity', 'price', 'quality' [one of: 'poor', 'regular', 'fine', 'exceptional']),\n"
        "  silver_pieces: int (amount of silver pieces the NPC has),\n"
        "  customer_history: List[TransactionEntry] (transaction history with the current customer. Include at least one past transaction; each entry must have 'name', 'quantity', 'price', 'quality', 'buying_npc', 'selling_npc')\n"
        ")"
    )

    INSTRUCTIONS = (
        "You are a helpful generator for merchant NPCs in a D&D village simulation. "
        "The NPC name should start with the same letter as its profession. Come up with exciting and novel names."
        "Generate a valid and detailed SalesPersonNPC object using this schema:\n\n"
        f"{SALESPERSON_NPC_SCHEMA}\n\n"
        "The customer_history starts empty, so do not create anything. "
        "The inventory must contain at least 10 unique items, with varying quantities."
        "After constructing a valid SalesPersonNPC object, immediately call the 'save_npc_to_db' tool with the full object as argument. "
        "The tool output is the final answer. Do not skip any fields. Refer to the schema; all inventory items should have at least name, quantity, price, and quality. The NPC must have a valid profession_skill."
    )

    generator_agent = Agent(
        name="SalesPersonNPC Generator Agent",
        instructions=INSTRUCTIONS,
        model=gemini_model,
        output_type=None,
        tools=[save_npc_tool]
    )

    @staticmethod
    async def run_create_agent(profession: str = None):
        """Create a single SalesPerson NPC."""
        message = (
            "Generate a valid random SalesPersonNPC for me following the schema, "
            "Do not include transactions in the customer_history. "
            "Double check the inventory list is not empty, each item has name/quantity/price/quality, "
            "profession_skill is present and valid, and customer_history has valid TransactionEntry items."
        )
        if profession:
            message += f" Set the profession to '{profession}'."
        
        with trace("Create SalesPersonNPC"):
            result = await Runner.run(SalesPersonNPCGeneratorAgent.generator_agent, message)
        return result

    @staticmethod
    async def run_create_multiple_agents(professions: List[str]):
        """Create multiple SalesPerson NPCs in a single trace."""
        if not professions:
            return []
        
        professions_str = ", ".join(professions)
        message = (
            f"Generate {len(professions)} valid random SalesPersonNPCs for me following the schema. "
            f"The professions should be: {professions_str}. "
            "Each NPC should have a unique name that starts with the same letter as their profession. "
            "Do not include transactions in the customer_history. "
            "Double check the inventory list is not empty, each item has name/quantity/price/quality, "
            "profession_skill is present and valid. "
            "The inventory must contain at least 10 unique items with varying quantities for each NPC. "
            "After constructing all SalesPersonNPC objects, immediately call the 'save_npc_to_db' tool for each one."
        )
        
        with trace("Create Multiple SalesPersonNPCs"):
            result = await Runner.run(SalesPersonNPCGeneratorAgent.generator_agent, message)
        return result


class CrafterNPCGeneratorAgent:
    """AI agent for generating Crafter NPCs."""
    
    CRAFTER_NPC_SCHEMA = (
        "CrafterNPC(\n"
        "  name: str (The name of the created NPC),\n"
        "  race: str (D&D race),\n"
        "  profession: str (the NPC's craft/profession),\n"
        "  profession_skill: str (must be one of: 'poor', 'regular', 'fine', 'exceptional'),\n"
        "  inventory: List[InventoryEntry] (with 'name', 'quantity', 'price', 'quality' [one of: 'poor', 'regular', 'fine', 'exceptional']),\n"
        "  known_recipes: List[ItemBase] (the list of items the NPC can produce or collect),\n"
        "  silver_pieces: int (amount of silver pieces the NPC has)\n"
        ")"
    )

    INSTRUCTIONS = (
        "You are a helpful generator for crafter NPCs in a D&D village simulation. "
        "The NPC name should start with the same letter as its profession. Come up with exciting and novel names."
        "Generate a valid and detailed CrafterNPC object using this schema:\n\n"
        f"{CRAFTER_NPC_SCHEMA}\n\n"
        "Always include a non-empty known_recipes list. "
        "The inventory must contain at least 10 unique items, with varying quantities."
        "After constructing a valid CrafterNPC object, immediately call the 'save_npc_to_db' tool with the full object as argument. "
        "The tool output is the final answer. Do not skip any fields. Refer to the schema; all inventory items should have at least name, quantity, price, and quality. The NPC must have a valid profession_skill."
    )

    generator_agent = Agent(
        name="CrafterNPC Generator Agent",
        instructions=INSTRUCTIONS,
        model=gemini_model,
        output_type=None,
        tools=[save_npc_tool, get_item_quality_by_skill_tool]
    )

    @staticmethod
    async def run_create_agent(profession: str = None):
        """Create a single Crafter NPC."""
        message = (
            "Generate a valid random CrafterNPC for me following the schema. "
            "Double check that the inventory list is not empty, each item has name/quantity/price/quality, "
            "profession_skill is present and valid, and known_recipes is a non-empty list of items in recent schema."
        )
        if profession:
            message += f" Set the profession to '{profession}'."
        
        with trace("Create CrafterNPC"):
            result = await Runner.run(CrafterNPCGeneratorAgent.generator_agent, message)
        return result

    @staticmethod
    async def run_create_multiple_agents(professions: List[str]):
        """Create multiple Crafter NPCs in a single trace."""
        if not professions:
            return []
        
        professions_str = ", ".join(professions)
        message = (
            f"Generate {len(professions)} valid random CrafterNPCs for me following the schema. "
            f"The professions should be: {professions_str}. "
            "Each NPC should have a unique name that starts with the same letter as their profession. "
            "Double check that each inventory list is not empty, each item has name/quantity/price/quality, "
            "profession_skill is present and valid, and known_recipes is a non-empty list of items. "
            "The inventory must contain at least 10 unique items with varying quantities for each NPC. "
            "After constructing all CrafterNPC objects, immediately call the 'save_npc_to_db' tool for each one."
        )
        
        with trace("Create Multiple CrafterNPCs"):
            result = await Runner.run(CrafterNPCGeneratorAgent.generator_agent, message)
        return result


# Main entry: now routes each type to its dedicated agent
if __name__ == '__main__':
    import sys

    async def main():
        npc_type = "SalesPersonNPC"
        profession = None
        
        if len(sys.argv) > 1:
            npc_type = sys.argv[1].lower()
        if len(sys.argv) > 2:
            profession = sys.argv[2]
        
        if not npc_type:
            npc_type = "SalesPersonNPC"

        if npc_type == "SalesPersonNPC":
            await SalesPersonNPCGeneratorAgent.run_create_agent(profession)
        elif npc_type == "crafternpc":
            await CrafterNPCGeneratorAgent.run_create_agent(profession)
        else:
            print("Unknown NPC type. Use 'SalesPersonNPC' or 'crafternpc'")

    asyncio.run(main())
