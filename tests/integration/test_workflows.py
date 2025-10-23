"""
Integration tests for complete workflows.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock
from cheapNPC.infrastructure.ai.agents import (
    NPCAgent, NPCTradingAgent, PlannerAgent, TraderAgent,
    execute_npc_trading_from_plan
)
from cheapNPC.core.services import NPCService, TradingService, InventoryService


class TestNPCWorkflow:
    """Test complete NPC workflow from creation to trading."""
    
    @pytest.mark.asyncio
    async def test_npc_lifecycle(self, temp_db, sample_npcs):
        """Test complete NPC lifecycle."""
        npc_service = NPCService()
        
        # Create NPCs
        for npc_data in sample_npcs:
            # This would normally create NPCs in the database
            # For now, we'll mock the creation process
            pass
        
        # Test getting NPCs
        npcs = npc_service.get_all_npcs()
        assert isinstance(npcs, list)
    
    @pytest.mark.asyncio
    async def test_npc_agent_interaction(self, temp_db):
        """Test NPC agent interaction with services."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            # Mock NPC data
            mock_npc = Mock()
            mock_npc.name = "TestNPC"
            mock_npc.personality = "friendly"
            mock_npc.skills = ["woodworking"]
            mock_npc.inventory = []
            mock_npc.money = 1000
            
            mock_service.return_value.get_npc_by_name.return_value = mock_npc
            
            # Create NPC agent
            agent = NPCAgent("TestNPC")
            
            # Test agent functionality
            info = agent.get_npc_info()
            assert "TestNPC" in info
            
            priorities = agent.get_trading_priorities()
            assert isinstance(priorities, list)
            
            can_afford = agent.can_afford(500)
            assert can_afford is True


class TestTradingWorkflow:
    """Test complete trading workflow."""
    
    @pytest.mark.asyncio
    async def test_trading_negotiation_workflow(self, temp_db):
        """Test complete trading negotiation workflow."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            # Mock two NPCs with compatible inventories
            mock_npc1 = Mock()
            mock_npc1.name = "Crafter"
            mock_npc1.money = 1000
            mock_npc1.inventory = [Mock(name="Wooden Sword", quantity=1, quality="common", price=100)]
            
            mock_npc2 = Mock()
            mock_npc2.name = "Merchant"
            mock_npc2.money = 1000
            mock_npc2.inventory = [Mock(name="Health Potion", quantity=1, quality="common", price=50)]
            
            mock_service.return_value.get_npc_by_name.side_effect = [mock_npc1, mock_npc2]
            
            # Test negotiation
            result = await NPCTradingAgent.negotiate_trade("Crafter", "Merchant")
            
            assert result is not None
            assert hasattr(result, 'success')
    
    @pytest.mark.asyncio
    async def test_planner_to_execution_workflow(self, temp_db):
        """Test workflow from planning to execution."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            # Mock NPCs for planning
            mock_npc1 = Mock()
            mock_npc1.name = "NPC1"
            mock_npc1.inventory = [Mock(name="Item1", quantity=1, quality="common", price=100)]
            
            mock_npc2 = Mock()
            mock_npc2.name = "NPC2"
            mock_npc2.inventory = [Mock(name="Item2", quantity=1, quality="common", price=100)]
            
            mock_service.return_value.get_all_npcs_with_inventories.return_value = [mock_npc1, mock_npc2]
            
            # Create trading plan
            planner = PlannerAgent()
            plan = await planner.create_trading_plan()
            
            assert plan is not None
            assert isinstance(plan.pairings, list)
            
            # Execute trading from plan
            if plan.pairings:
                result = await execute_npc_trading_from_plan(plan)
                assert result is not None


class TestServiceIntegration:
    """Test integration between different services."""
    
    def test_npc_service_integration(self, temp_db, npc_service):
        """Test NPC service integration."""
        # Test basic operations
        npcs = npc_service.get_all_npcs()
        assert isinstance(npcs, list)
        
        summaries = npc_service.get_all_npc_summaries()
        assert isinstance(summaries, list)
    
    def test_trading_service_integration(self, temp_db, trading_service):
        """Test trading service integration."""
        # Test basic operations
        transactions = trading_service.get_all_transactions()
        assert isinstance(transactions, list)
    
    def test_inventory_service_integration(self, temp_db, inventory_service):
        """Test inventory service integration."""
        # Test basic operations
        inventory = inventory_service.get_npc_inventory("TestNPC")
        assert isinstance(inventory, list)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_system_workflow(self, temp_db):
        """Test complete system workflow from start to finish."""
        # This test would simulate a complete workflow:
        # 1. Create NPCs
        # 2. Generate trading plan
        # 3. Execute trades
        # 4. Verify results
        
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            # Mock the complete system state
            mock_npcs = [
                Mock(name="Crafter", inventory=[Mock(name="Sword", quantity=1, quality="common", price=100)]),
                Mock(name="Merchant", inventory=[Mock(name="Potion", quantity=1, quality="common", price=50)])
            ]
            
            mock_service.return_value.get_all_npcs_with_inventories.return_value = mock_npcs
            mock_service.return_value.get_npc_by_name.side_effect = [
                Mock(name="Crafter", money=1000, inventory=[Mock(name="Sword", quantity=1, quality="common", price=100)]),
                Mock(name="Merchant", money=1000, inventory=[Mock(name="Potion", quantity=1, quality="common", price=50)])
            ]
            
            # Step 1: Create trading plan
            planner = PlannerAgent()
            plan = await planner.create_trading_plan()
            
            assert plan is not None
            
            # Step 2: Execute trades (if any pairings exist)
            if plan.pairings:
                result = await execute_npc_trading_from_plan(plan)
                assert result is not None
            
            # Step 3: Verify system state
            # This would check that trades were executed correctly
            # and NPCs have updated inventories/money
