"""
Unit tests for core services.
"""

import pytest
from unittest.mock import Mock, patch
from cheapNPC.core.services import NPCService, TradingService, InventoryService


class TestNPCService:
    """Test NPC service functionality."""
    
    def test_npc_service_initialization(self, npc_service):
        """Test NPC service can be initialized."""
        assert isinstance(npc_service, NPCService)
    
    def test_get_all_npcs_empty(self, npc_service):
        """Test getting all NPCs when database is empty."""
        npcs = npc_service.get_all_npcs()
        assert isinstance(npcs, list)
        assert len(npcs) == 0
    
    def test_get_all_npc_summaries_empty(self, npc_service):
        """Test getting NPC summaries when database is empty."""
        summaries = npc_service.get_all_npc_summaries()
        assert isinstance(summaries, list)
        assert len(summaries) == 0
    
    @patch('cheapNPC.core.services.npc_service.get_npc_repository')
    def test_get_npc_by_name_not_found(self, mock_repo, npc_service):
        """Test getting NPC by name when not found."""
        mock_repo.return_value.get_npc_by_name.return_value = None
        
        npc = npc_service.get_npc_by_name("NonExistentNPC")
        assert npc is None
    
    @patch('cheapNPC.core.services.npc_service.get_npc_repository')
    def test_get_npc_by_name_found(self, mock_repo, npc_service):
        """Test getting NPC by name when found."""
        mock_npc = Mock()
        mock_npc.name = "TestNPC"
        mock_repo.return_value.get_npc_by_name.return_value = mock_npc
        
        npc = npc_service.get_npc_by_name("TestNPC")
        assert npc is not None
        assert npc.name == "TestNPC"


class TestTradingService:
    """Test trading service functionality."""
    
    def test_trading_service_initialization(self, trading_service):
        """Test trading service can be initialized."""
        assert isinstance(trading_service, TradingService)
    
    @patch('cheapNPC.core.services.trading_service.get_transaction_repository')
    def test_get_all_transactions_empty(self, mock_repo, trading_service):
        """Test getting all transactions when database is empty."""
        mock_repo.return_value.get_all_transactions.return_value = []
        
        transactions = trading_service.get_all_transactions()
        assert isinstance(transactions, list)
        assert len(transactions) == 0
    
    @patch('cheapNPC.core.services.trading_service.get_transaction_repository')
    def test_create_transaction(self, mock_repo, trading_service):
        """Test creating a transaction."""
        mock_repo.return_value.create_transaction.return_value = True
        
        result = trading_service.create_transaction(
            buyer_name="Buyer",
            seller_name="Seller",
            item_name="Item",
            quantity=1,
            price=100
        )
        
        assert result is True
        mock_repo.return_value.create_transaction.assert_called_once()


class TestInventoryService:
    """Test inventory service functionality."""
    
    def test_inventory_service_initialization(self, inventory_service):
        """Test inventory service can be initialized."""
        assert isinstance(inventory_service, InventoryService)
    
    @patch('cheapNPC.core.services.inventory_service.get_inventory_repository')
    def test_get_npc_inventory_empty(self, mock_repo, inventory_service):
        """Test getting NPC inventory when empty."""
        mock_repo.return_value.get_npc_inventory.return_value = []
        
        inventory = inventory_service.get_npc_inventory("TestNPC")
        assert isinstance(inventory, list)
        assert len(inventory) == 0
    
    @patch('cheapNPC.core.services.inventory_service.get_inventory_repository')
    def test_add_item_to_inventory(self, mock_repo, inventory_service):
        """Test adding item to inventory."""
        mock_repo.return_value.add_item_to_inventory.return_value = True
        
        result = inventory_service.add_item_to_inventory(
            npc_name="TestNPC",
            item_name="TestItem",
            quantity=1,
            quality="common",
            price=100
        )
        
        assert result is True
        mock_repo.return_value.add_item_to_inventory.assert_called_once()
    
    @patch('cheapNPC.core.services.inventory_service.get_inventory_repository')
    def test_remove_item_from_inventory(self, mock_repo, inventory_service):
        """Test removing item from inventory."""
        mock_repo.return_value.remove_item_from_inventory.return_value = True
        
        result = inventory_service.remove_item_from_inventory(
            npc_name="TestNPC",
            item_name="TestItem",
            quantity=1
        )
        
        assert result is True
        mock_repo.return_value.remove_item_from_inventory.assert_called_once()
