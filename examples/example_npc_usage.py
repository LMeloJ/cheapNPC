#!/usr/bin/env python3
"""
Example usage of the NPC Agent trading system.
This demonstrates how to use NPCs to negotiate and execute trades.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cheapNPC.infrastructure.ai.agents import NPCAgent, NPCTradingAgent, execute_npc_trading_from_plan, PlannerAgent

async def example_individual_npc_usage():
    """Example of using individual NPC agents"""
    print("👤 Individual NPC Agent Example")
    print("=" * 40)
    
    # Create an NPC agent for a specific NPC
    npc_name = "Alaric Alembic"  # Replace with an actual NPC name from your database
    try:
        npc_agent = NPCAgent(npc_name)
        
        # Get NPC information
        print("NPC Information:")
        print(npc_agent.get_npc_info())
        
        # Get trading priorities based on profession
        priorities = npc_agent.get_trading_priorities()
        print(f"\nTrading Priorities: {', '.join(priorities)}")
        
        # Check economic status
        print(f"\nSilver Pieces: {npc_agent.npc_data.silver_pieces} SP")
        print(f"Can afford 50 SP: {npc_agent.can_afford(50)}")
        
        # Check inventory
        if npc_agent.npc_data.inventory:
            for item in npc_agent.npc_data.inventory:
                print(f"Has {item.quantity} {item.name} @ {item.price} SP each")
        
    except ValueError as e:
        print(f"❌ {e}")
        print("Make sure the NPC exists in the database.")

async def example_direct_trading():
    """Example of direct trading between two NPCs"""
    print("\n🤝 Direct Trading Example")
    print("=" * 40)
    
    npc1_name = "Alaric Alembic"  # Replace with actual NPC names
    npc2_name = "Beatrice Biscuit"
    
    try:
        # Create trading agent instance
        trading_agent = NPCTradingAgent()
        
        # Negotiate a trade between two NPCs
        negotiation_result = await trading_agent.negotiate_trade(npc1_name, npc2_name)
        
        print(f"Negotiation between {npc1_name} and {npc2_name}:")
        print(f"Success: {negotiation_result.success}")
        
        if negotiation_result.success:
            print(f"Agreed Trade:")
            print(f"  Item: {negotiation_result.final_item}")
            print(f"  Quantity: {negotiation_result.final_quantity}")
            print(f"  Price: {negotiation_result.final_price} SP per unit")
            print(f"  Quality: {negotiation_result.final_quality}")
            
            # Execute the trade
            execution_result = await trading_agent.execute_negotiated_trade(negotiation_result)
            print(f"\nExecution Result: {execution_result}")
        else:
            print(f"No trade agreed: {negotiation_result.reasoning}")
            
    except ValueError as e:
        print(f"❌ {e}")
        print("Make sure both NPCs exist in the database.")

async def example_plan_based_trading():
    """Example of using trading plans to execute multiple trades"""
    print("\n📋 Plan-Based Trading Example")
    print("=" * 40)
    
    try:
        # Step 1: Create a trading plan
        print("Creating trading plan...")
        planner = PlannerAgent()
        plan = await planner.create_trading_plan()
        
        if not plan.pairings:
            print("No trading pairs created. Need more NPCs or different inventory distribution.")
            return
        
        print(f"Created plan with {len(plan.pairings)} trading pairs:")
        for i, pair in enumerate(plan.pairings, 1):
            print(f"  {i}. {pair.buyer_name} ↔ {pair.seller_name}")
        
        # Step 2: Execute all trades in the plan
        print("\nExecuting trades...")
        result = await execute_npc_trading_from_plan(plan)
        
        print("\nTrading Results:")
        print(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main example function"""
    print("🎮 NPC Agent Trading System Examples")
    print("=" * 50)
    
    # Run examples
    await example_individual_npc_usage()
    await example_direct_trading()
    await example_plan_based_trading()
    
    print("\n✨ Examples completed!")
    print("\nTo use this system in your own code:")
    print("1. Create NPC agents: npc_agent = NPCAgent('NPC_Name')")
    print("2. Negotiate trades: result = await NPCTradingAgent.negotiate_trade('NPC1', 'NPC2')")
    print("3. Execute trades: await NPCTradingAgent.execute_negotiated_trade(result)")
    print("4. Use trading plans: await execute_npc_trading_from_plan(plan)")

if __name__ == '__main__':
    asyncio.run(main())
