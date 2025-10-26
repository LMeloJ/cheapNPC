"""
World service controller for cheapNPC MVC architecture.

This controller handles world creation and initialization.
"""

import asyncio
import time
from cheapNPC.infrastructure.database.migrations import setup_database
from cheapNPC.agents.generator_agent import (
    SalesPersonNPCGeneratorAgent, 
    CrafterNPCGeneratorAgent
)


def create_world_sync(progress_callback=None):
    """
    Create the NPC world synchronously.
    
    This function:
    1. Sets up the database schema
    2. Creates initial crafters/gatherers
    3. Creates initial merchants
    
    Args:
        progress_callback: Optional callback function for progress updates
        
    Returns:
        str: Result message
    """
    try:
        # Step 1: Setup database
        if progress_callback:
            progress_callback("🔄 Setting up database...")
        
        setup_database()
        
        if progress_callback:
            progress_callback("✅ Database setup complete!")
        
        # Small delay to ensure database tables are fully committed and flushed to disk
        # This prevents race conditions where NPC creation starts before tables are visible
        time.sleep(1.0)
        
        # Step 2: Create crafters/gatherers
        crafters = [
            "blacksmith", "carpenter", "brewer", 
            "miner", "gatherer", "alchemist"
        ]
        
        if progress_callback:
            progress_callback(f"🔄 Creating {len(crafters)} crafters/gatherers...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def create_crafters():
            results = []
            for i, profession in enumerate(crafters, 1):
                if progress_callback:
                    progress_callback(f"  Creating {i}/{len(crafters)}: {profession}...")
                try:
                    result = await CrafterNPCGeneratorAgent.run_create_agent(profession)
                    results.append(result)
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"  ⚠️ Error creating {profession}: {str(e)}")
            return results
        
        loop.run_until_complete(create_crafters())
        loop.close()
        
        if progress_callback:
            progress_callback("✅ Crafters/gatherers created!")
        
        # Step 3: Create merchants
        merchants = ["merchant", "store owner"]
        
        if progress_callback:
            progress_callback(f"🔄 Creating {len(merchants)} merchants...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def create_merchants():
            results = []
            for i, profession in enumerate(merchants, 1):
                if progress_callback:
                    progress_callback(f"  Creating {i}/{len(merchants)}: {profession}...")
                try:
                    result = await SalesPersonNPCGeneratorAgent.run_create_agent(profession)
                    results.append(result)
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"  ⚠️ Error creating {profession}: {str(e)}")
            return results
        
        loop.run_until_complete(create_merchants())
        loop.close()
        
        if progress_callback:
            progress_callback("✅ Merchants created!")
        
        # Final success message
        return (
            "🌍 World created successfully!\n\n"
            f"✅ Database initialized\n"
            f"✅ {len(crafters)} crafters/gatherers created\n"
            f"✅ {len(merchants)} merchants created\n\n"
            "You can now access the dashboard and start trading!"
        )
        
    except Exception as e:
        error_msg = f"❌ Error creating world: {str(e)}"
        if progress_callback:
            progress_callback(error_msg)
        return error_msg
