"""
Comprehensive test suite that consolidates functionality from the original test files.

This test suite replaces the individual test files in the root directory with
a proper organized test structure.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from cheapNPC.infrastructure.ai.agents import (
    NPCAgent, NPCTradingAgent, PlannerAgent, TraderAgent,
    execute_npc_trading_from_plan
)
from cheapNPC.core.services import NPCService, TradingService, InventoryService


class TestOriginalFunctionality:
    """Test functionality from the original test files."""
    
    @pytest.mark.asyncio
    async def test_npc_agent_individual_functionality(self, temp_db):
        """Test individual NPC agent functionality from test_npc_agent.py."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            # Mock NPC data
            mock_npc = Mock()
            mock_npc.name = "Test NPC"
            mock_npc.personality = "friendly"
            mock_npc.skills = ["woodworking"]
            mock_npc.inventory = [Mock(name="Test Item", quantity=1, quality="common", price=100)]
            mock_npc.money = 1000
            
            mock_service.return_value.get_npc_by_name.return_value = mock_npc
            
            # Create NPC agent
            npc_agent = NPCAgent("Test NPC")
            
            # Test basic functionality
            info = npc_agent.get_npc_info()
            assert "Test NPC" in info
            
            priorities = npc_agent.get_trading_priorities()
            assert isinstance(priorities, list)
            
            # Test affordability
            assert npc_agent.can_afford(100) is True
            assert npc_agent.can_afford(1000) is False
            
            # Test item operations
            assert npc_agent.has_item("Test Item") is True
            assert npc_agent.get_item_quantity("Test Item") == 1
            assert npc_agent.get_item_price("Test Item") == 100
    
    @pytest.mark.asyncio
    async def test_npc_trading_negotiation(self, temp_db):
        """Test NPC trading negotiation from test_npc_agent.py."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            # Mock two NPCs
            mock_npc1 = Mock()
            mock_npc1.name = "NPC1"
            mock_npc1.money = 1000
            mock_npc1.inventory = [Mock(name="Item1", quantity=1, quality="common", price=100)]
            
            mock_npc2 = Mock()
            mock_npc2.name = "NPC2"
            mock_npc2.money = 1000
            mock_npc2.inventory = [Mock(name="Item2", quantity=1, quality="common", price=100)]
            
            mock_service.return_value.get_npc_by_name.side_effect = [mock_npc1, mock_npc2]
            
            # Test negotiation
            result = await NPCTradingAgent.negotiate_trade("NPC1", "NPC2")
            
            assert result is not None
            assert hasattr(result, 'success')
    
    @pytest.mark.asyncio
    async def test_complete_trading_system(self, temp_db):
        """Test complete trading system from test_npc_agent.py."""
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
            plan = await PlannerAgent.create_trading_plan()
            
            assert plan is not None
            assert isinstance(plan.pairings, list)
            
            # Execute trading if pairings exist
            if plan.pairings:
                result = await execute_npc_trading_from_plan(plan)
                assert result is not None
    
    def test_refactored_agent_imports(self):
        """Test refactored agent imports from test_refactored_agents.py."""
        try:
            # Test AI agents
            from cheapNPC.infrastructure.ai.agents import (
                NPCAgent, NPCTradingAgent, PlannerAgent, TraderAgent
            )
            assert True  # If we get here, imports worked
            
            # Test services
            from cheapNPC.core.services import NPCService, TradingService, InventoryService
            assert True  # If we get here, imports worked
            
            # Test presentation layer
            from cheapNPC.presentation.cli.print_npc import print_npc_details
            from cheapNPC.presentation.web.dashboard import NPCVisualizer
            assert True  # If we get here, imports worked
            
        except ImportError as e:
            pytest.fail(f"Import error: {e}")
    
    def test_service_integration(self, temp_db):
        """Test service integration from test_refactored_agents.py."""
        npc_service = NPCService()
        
        # Test getting all NPCs
        npcs = npc_service.get_all_npcs()
        assert isinstance(npcs, list)
        
        # Test getting summaries
        summaries = npc_service.get_all_npc_summaries()
        assert isinstance(summaries, list)
    
    @pytest.mark.asyncio
    async def test_planner_agent_functionality(self, temp_db):
        """Test planner agent from test_refactored_agents.py."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            mock_service.return_value.get_all_npcs_with_inventories.return_value = []
            
            planner = PlannerAgent()
            plan = await planner.create_trading_plan()
            
            assert plan is not None
            assert isinstance(plan.pairings, list)
    
    def test_npc_agent_functionality(self, temp_db):
        """Test NPC agent from test_refactored_agents.py."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            mock_npc = Mock()
            mock_npc.name = "TestNPC"
            mock_npc.personality = "friendly"
            mock_npc.skills = ["woodworking"]
            mock_npc.inventory = []
            mock_npc.money = 1000
            
            mock_service.return_value.get_npc_by_name.return_value = mock_npc
            
            npc_agent = NPCAgent("TestNPC")
            
            # Test basic functionality
            info = npc_agent.get_npc_info()
            priorities = npc_agent.get_trading_priorities()
            
            assert "TestNPC" in info
            assert isinstance(priorities, list)
    
    def test_cli_tool_functionality(self, temp_db):
        """Test CLI tool from test_refactored_agents.py."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            mock_npc = Mock()
            mock_npc.name = "TestNPC"
            mock_service.return_value.get_npc_by_name.return_value = mock_npc
            
            from cheapNPC.presentation.cli.print_npc import print_npc_details
            
            # This should not raise an exception
            print_npc_details("TestNPC")
    
    def test_refactored_structure_imports(self):
        """Test refactored structure imports from test_refactored_structure.py."""
        try:
            # Test core models
            from cheapNPC.core.models import (
                NPC, CrafterNPC, SalesPersonNPC, 
                ItemQuality, InventoryEntry, TradingPlan
            )
            assert True
            
            # Test infrastructure
            from cheapNPC.infrastructure.database.connection import get_database_connection
            from cheapNPC.infrastructure.database.migrations import setup_database
            from cheapNPC.infrastructure.database.repositories import get_npc_repository
            assert True
            
            # Test services
            from cheapNPC.core.services import NPCService, TradingService, InventoryService
            assert True
            
            # Test presentation
            from cheapNPC.presentation.web.dashboard import NPCVisualizer
            assert True
            
        except ImportError as e:
            pytest.fail(f"Import error: {e}")
    
    def test_database_setup(self, temp_db):
        """Test database setup from test_refactored_structure.py."""
        from cheapNPC.infrastructure.database.migrations import setup_database, check_database_health
        
        # Setup database
        setup_database()
        
        # Check health
        assert check_database_health() is True
    
    def test_service_functionality(self, temp_db):
        """Test service functionality from test_refactored_structure.py."""
        npc_service = NPCService()
        
        # Test getting all NPCs (should work even if empty)
        npcs = npc_service.get_all_npcs()
        assert isinstance(npcs, list)


class TestComprehensiveWorkflow:
    """Test comprehensive workflow combining all original test functionality."""
    
    @pytest.mark.asyncio
    async def test_full_system_workflow(self, temp_db):
        """Test the complete system workflow."""
        with patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService') as mock_service:
            # Mock NPCs with inventories
            mock_npcs = [
                Mock(name="Crafter", inventory=[Mock(name="Sword", quantity=1, quality="common", price=100)]),
                Mock(name="Merchant", inventory=[Mock(name="Potion", quantity=1, quality="common", price=50)])
            ]
            
            mock_service.return_value.get_all_npcs_with_inventories.return_value = mock_npcs
            mock_service.return_value.get_npc_by_name.side_effect = [
                Mock(name="Crafter", money=1000, inventory=[Mock(name="Sword", quantity=1, quality="common", price=100)]),
                Mock(name="Merchant", money=1000, inventory=[Mock(name="Potion", quantity=1, quality="common", price=50)])
            ]
            
            # Step 1: Test individual NPC agents
            crafter_agent = NPCAgent("Crafter")
            merchant_agent = NPCAgent("Merchant")
            
            assert crafter_agent.npc_name == "Crafter"
            assert merchant_agent.npc_name == "Merchant"
            
            # Step 2: Test trading negotiation
            result = await NPCTradingAgent.negotiate_trade("Crafter", "Merchant")
            assert result is not None
            
            # Step 3: Test planning
            planner = PlannerAgent()
            plan = await planner.create_trading_plan()
            assert plan is not None
            
            # Step 4: Test execution
            if plan.pairings:
                execution_result = await execute_npc_trading_from_plan(plan)
                assert execution_result is not None
            
            # Step 5: Test services
            npc_service = NPCService()
            npcs = npc_service.get_all_npcs()
            assert isinstance(npcs, list)
