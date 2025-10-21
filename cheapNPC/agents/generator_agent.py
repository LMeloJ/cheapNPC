import asyncio
from openai import AsyncOpenAI
import os
import sys
from pathlib import Path
from agents import Agent, OpenAIChatCompletionsModel, trace, Runner
from cheapNPC.db.village_db import save_merchant_to_db
from dotenv import load_dotenv
load_dotenv(override=True)
# --- Configuration and Client Setup ---

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# NOTE: Ensure GOOGLE_API_KEY is set in your environment
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)

DB_NAME = 'data/village.db'

# --- Agent Definition ---

INSTRUCTIONS = f"You are a helpful inventory and merchant generator. Your primary goal is to generate a detailed MerchantNPC object and then, using the provided tool, save it to the database. \
    Given a query, first formulate the complete MerchantNPC object with name, race, profession, inventory (list of items with quantity/price), and silver pieces. \
    Then, immediately call the 'save_merchant_to_db' tool with the complete MerchantNPC object as the argument. The output of the tool is the final answer."

generator_agent = Agent(
    name="Generator Agent",
    instructions=INSTRUCTIONS,
    model=gemini_model,
    # output_type is None because the primary output is the tool call itself
    output_type=None, 
    tools=[save_merchant_to_db] 
)

async def run_create_agent():
    message = "Generate a new random NPC for me."

    with trace("Search"):
        result = await Runner.run(generator_agent, message)

if __name__ == '__main__':
    asyncio.run(run_create_agent())