"""
World creation service for CheapNPC.

This module provides functionality to create and initialize the NPC world,
including database setup and NPC generation.
"""

import asyncio
import os
from typing import Optional

from cheapNPC.infrastructure.database.migrations import setup_database, reset_database
from cheapNPC.infrastructure.ai.agents.generator_agent import (
    CrafterNPCGeneratorAgent,
    SalesPersonNPCGeneratorAgent,
)


class WorldService:
    """Service for world creation and management."""
    
    def __init__(self):
        """Initialize the world service."""
        pass
    
    async def create_world(self, progress_callback: Optional[callable] = None) -> str:
        """
        Create the complete NPC world with database setup and NPC generation.
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            str: Result message with creation details
        """
        try:
            if progress_callback:
                progress_callback("🔄 Starting world creation process...")
            
            # Create DB if needed
            # Get the project root directory (3 levels up from this file)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            db_path = os.path.join(project_root, "data", "village.db")
            db_dir = os.path.dirname(db_path)
            if not os.path.exists(db_dir):
                if progress_callback:
                    progress_callback("📁 Creating data directory...")
                os.makedirs(db_dir, exist_ok=True)
            
            if progress_callback:
                progress_callback("🗄️ Setting up database...")
            
            # Completely reset the database to start fresh
            if progress_callback:
                progress_callback("🔄 Resetting database to start fresh...")
            print(f"Resetting database at {db_path}...")
            reset_database()
            print("Database reset complete.")
            
            # Use setup_database() to initialize tables (idempotent)
            if progress_callback:
                progress_callback("🏗️ Creating database tables...")
            print(f"Setting up fresh DB schema at {db_path}...")
            setup_database()
            print("Fresh DB schema created.")
            
            if progress_callback:
                progress_callback("🎭 Generating crafters and gatherers...")
            
            # 2 crafters/gatherers with specific professions (reduced for faster setup)
            if progress_callback:
                progress_callback("🔨 Creating blacksmith NPC...")
            print("Generating 2 Crafters/Gatherers...")
            crafter_professions = [
                "blacksmith", "carpenter"
            ]
            crafter_results = await CrafterNPCGeneratorAgent.run_create_multiple_agents(crafter_professions)
            if progress_callback:
                progress_callback("✅ Crafters created successfully!")
            print("Crafters created.")
            
            if progress_callback:
                progress_callback("🏪 Creating merchant NPC...")
            
            # 2 salespeople (merchant and store owner)
            print("Generating 2 SalesPeople...")
            salesperson_professions = ["merchant", "store owner"]
            salesperson_results = await SalesPersonNPCGeneratorAgent.run_create_multiple_agents(salesperson_professions)
            if progress_callback:
                progress_callback("✅ Merchants created successfully!")
            print("SalesPeople created.")
            
            if progress_callback:
                progress_callback("✅ World creation completed successfully!")
            
            result_msg = "✅ World created successfully!\n\n"
            result_msg += "📊 Database: Set up with all required tables\n"
            result_msg += f"🎭 Crafters: {len(crafter_results) if hasattr(crafter_results, '__len__') else 'Multiple'} NPCs created\n"
            result_msg += f"💰 Merchants: {len(salesperson_results) if hasattr(salesperson_results, '__len__') else 'Multiple'} NPCs created\n"
            result_msg += f"📦 Total NPCs: 8 (6 crafters + 2 merchants)\n\n"
            
            # Add details about created NPCs
            if crafter_results:
                result_msg += "🔨 Crafters created:\n"
                if hasattr(crafter_results, '__iter__') and not isinstance(crafter_results, str):
                    for i, npc in enumerate(crafter_results, 1):
                        result_msg += f"   {i}. {npc}\n"
                else:
                    result_msg += f"   Multiple crafters with professions: blacksmith, carpenter, brewer, baker, alchemist, weaver\n"
                result_msg += "\n"
            
            if salesperson_results:
                result_msg += "🏪 Merchants created:\n"
                if hasattr(salesperson_results, '__iter__') and not isinstance(salesperson_results, str):
                    for i, npc in enumerate(salesperson_results, 1):
                        result_msg += f"   {i}. {npc}\n"
                else:
                    result_msg += f"   Multiple merchants with professions: merchant, store owner\n"
            
            print("Done!")
            return result_msg
            
        except Exception as e:
            error_msg = f"❌ Error creating world: {str(e)}"
            print(error_msg)
            if progress_callback:
                progress_callback(error_msg)
            return error_msg


def create_world_sync(progress_callback: Optional[callable] = None) -> str:
    """
    Synchronous wrapper for the world creation function.
    
    Args:
        progress_callback: Optional callback function for progress updates
        
    Returns:
        str: Result message with creation details
    """
    try:
        world_service = WorldService()
        return asyncio.run(world_service.create_world(progress_callback))
    except Exception as e:
        error_msg = f"❌ Error in world creation: {str(e)}"
        if progress_callback:
            progress_callback(error_msg)
        return error_msg
