"""
Unit tests for AI agents.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from cheapNPC.infrastructure.ai.agents import (
    NPCAgent, NPCTradingAgent, PlannerAgent, TraderAgent
)


class TestNPCAgent:
    """Test NPC agent functionality."""
    
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    def test_npc_agent_initialization(self, mock_service):
        """Test NPC agent initialization."""
        mock_npc = Mock()
        mock_npc.name = "TestNPC"
        mock_npc.personality = "friendly"
        mock_npc.skills = ["woodworking"]
        mock_npc.inventory = []
        mock_npc.money = 1000
        
        mock_service.return_value.get_npc_by_name.return_value = mock_npc
        
        agent = NPCAgent("TestNPC")
        
        assert agent.npc_name == "TestNPC"
        assert agent.npc_data.name == "TestNPC"
    
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    def test_get_npc_info(self, mock_service):
        """Test getting NPC information."""
        mock_npc = Mock()
        mock_npc.name = "TestNPC"
        mock_npc.personality = "friendly"
        mock_npc.skills = ["woodworking"]
        mock_npc.inventory = []
        mock_npc.money = 1000
        
        mock_service.return_value.get_npc_by_name.return_value = mock_npc
        
        agent = NPCAgent("TestNPC")
        info = agent.get_npc_info()
        
        assert "TestNPC" in info
        assert "friendly" in info
    
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    def test_can_afford(self, mock_service):
        """Test affordability check."""
        mock_npc = Mock()
        mock_npc.money = 500
        
        mock_service.return_value.get_npc_by_name.return_value = mock_npc
        
        agent = NPCAgent("TestNPC")
        
        assert agent.can_afford(400) is True
        assert agent.can_afford(600) is False
    
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    def test_has_item(self, mock_service):
        """Test item ownership check."""
        mock_item = Mock()
        mock_item.name = "TestItem"
        
        mock_npc = Mock()
        mock_npc.inventory = [mock_item]
        
        mock_service.return_value.get_npc_by_name.return_value = mock_npc
        
        agent = NPCAgent("TestNPC")
        
        assert agent.has_item("TestItem") is True
        assert agent.has_item("NonExistentItem") is False


class TestNPCTradingAgent:
    """Test NPC trading agent functionality."""
    
    @pytest.mark.asyncio
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    async def test_negotiate_trade_success(self, mock_service):
        """Test successful trade negotiation."""
        # Mock NPCs with compatible inventories
        mock_npc1 = Mock()
        mock_npc1.name = "NPC1"
        mock_npc1.money = 1000
        mock_npc1.inventory = [Mock(name="Item1", quantity=1, quality="common", price=100)]
        
        mock_npc2 = Mock()
        mock_npc2.name = "NPC2"
        mock_npc2.money = 1000
        mock_npc2.inventory = [Mock(name="Item2", quantity=1, quality="common", price=100)]
        
        mock_service.return_value.get_npc_by_name.side_effect = [mock_npc1, mock_npc2]
        
        result = await NPCTradingAgent.negotiate_trade("NPC1", "NPC2")
        
        assert result is not None
        assert hasattr(result, 'success')
    
    @pytest.mark.asyncio
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    async def test_negotiate_trade_no_npcs(self, mock_service):
        """Test trade negotiation when NPCs don't exist."""
        mock_service.return_value.get_npc_by_name.return_value = None
        
        result = await NPCTradingAgent.negotiate_trade("NonExistentNPC1", "NonExistentNPC2")
        
        assert result.success is False
        assert "not found" in result.reasoning.lower()


class TestPlannerAgent:
    """Test planner agent functionality."""
    
    @pytest.mark.asyncio
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    async def test_create_trading_plan_empty(self, mock_service):
        """Test creating trading plan with no NPCs."""
        mock_service.return_value.get_all_npcs_with_inventories.return_value = []
        
        planner = PlannerAgent()
        plan = await planner.create_trading_plan()
        
        assert plan is not None
        assert len(plan.pairings) == 0
    
    @pytest.mark.asyncio
    @patch('cheapNPC.infrastructure.ai.agents.npc_service.NPCService')
    async def test_create_trading_plan_with_npcs(self, mock_service):
        """Test creating trading plan with NPCs."""
        # Mock NPCs with inventories
        mock_npc1 = Mock()
        mock_npc1.name = "NPC1"
        mock_npc1.inventory = [Mock(name="Item1", quantity=1, quality="common", price=100)]
        
        mock_npc2 = Mock()
        mock_npc2.name = "NPC2"
        mock_npc2.inventory = [Mock(name="Item2", quantity=1, quality="common", price=100)]
        
        mock_service.return_value.get_all_npcs_with_inventories.return_value = [mock_npc1, mock_npc2]
        
        planner = PlannerAgent()
        plan = await planner.create_trading_plan()
        
        assert plan is not None
        assert isinstance(plan.pairings, list)


class TestTraderAgent:
    """Test trader agent functionality."""
    
    def test_trader_agent_initialization(self):
        """Test trader agent initialization."""
        agent = TraderAgent()
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_execute_trade(self):
        """Test trade execution."""
        agent = TraderAgent()
        
        # Mock trade data
        trade_data = {
            "buyer": "BuyerNPC",
            "seller": "SellerNPC",
            "item": "TestItem",
            "quantity": 1,
            "price": 100
        }
        
        result = await agent.execute_trade(trade_data)
        
        # Should return some result (success or failure)
        assert result is not None
