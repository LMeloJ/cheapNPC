"""
Unit tests for core models and utilities.
"""

import pytest
from cheapNPC.core.models import (
    NPC, CrafterNPC, SalesPersonNPC, 
    ItemQuality, InventoryEntry, TradingPlan
)
from cheapNPC.core.models.utils import calculate_item_price


class TestNPCModels:
    """Test NPC model classes."""
    
    def test_npc_creation(self):
        """Test basic NPC creation."""
        npc = NPC(
            name="Test NPC",
            npc_type="crafter",
            personality="friendly",
            skills=["woodworking"]
        )
        
        assert npc.name == "Test NPC"
        assert npc.npc_type == "crafter"
        assert npc.personality == "friendly"
        assert "woodworking" in npc.skills
    
    def test_crafter_npc(self):
        """Test CrafterNPC specific functionality."""
        crafter = CrafterNPC(
            name="Test Crafter",
            personality="creative",
            skills=["woodworking", "metalworking"]
        )
        
        assert crafter.npc_type == "crafter"
        assert "woodworking" in crafter.skills
        assert "metalworking" in crafter.skills
    
    def test_salesperson_npc(self):
        """Test SalesPersonNPC specific functionality."""
        merchant = SalesPersonNPC(
            name="Test Merchant",
            personality="greedy",
            skills=["bargaining", "appraisal"]
        )
        
        assert merchant.npc_type == "salesperson"
        assert "bargaining" in merchant.skills
        assert "appraisal" in merchant.skills


class TestItemQuality:
    """Test ItemQuality enum."""
    
    def test_quality_values(self):
        """Test that quality values are correct."""
        assert ItemQuality.COMMON.value == "common"
        assert ItemQuality.RARE.value == "rare"
        assert ItemQuality.EPIC.value == "epic"
        assert ItemQuality.LEGENDARY.value == "legendary"
    
    def test_quality_comparison(self):
        """Test quality comparison functionality."""
        assert ItemQuality.COMMON < ItemQuality.RARE
        assert ItemQuality.RARE < ItemQuality.EPIC
        assert ItemQuality.EPIC < ItemQuality.LEGENDARY


class TestInventoryEntry:
    """Test InventoryEntry model."""
    
    def test_inventory_entry_creation(self):
        """Test inventory entry creation."""
        entry = InventoryEntry(
            name="Test Item",
            quantity=5,
            quality=ItemQuality.COMMON,
            price=100
        )
        
        assert entry.name == "Test Item"
        assert entry.quantity == 5
        assert entry.quality == ItemQuality.COMMON
        assert entry.price == 100
    
    def test_total_value(self):
        """Test total value calculation."""
        entry = InventoryEntry(
            name="Test Item",
            quantity=3,
            quality=ItemQuality.COMMON,
            price=50
        )
        
        assert entry.total_value == 150


class TestTradingPlan:
    """Test TradingPlan model."""
    
    def test_trading_plan_creation(self):
        """Test trading plan creation."""
        plan = TradingPlan(pairings=[])
        
        assert plan.pairings == []
        assert isinstance(plan.pairings, list)
    
    def test_trading_plan_with_pairings(self):
        """Test trading plan with pairings."""
        pairings = [
            {"buyer": "NPC1", "seller": "NPC2", "item": "Sword", "quantity": 1}
        ]
        plan = TradingPlan(pairings=pairings)
        
        assert len(plan.pairings) == 1
        assert plan.pairings[0]["buyer"] == "NPC1"


class TestUtils:
    """Test utility functions."""
    
    def test_calculate_item_price(self):
        """Test item price calculation."""
        base_price = 100
        
        # Test different quality multipliers
        common_price = calculate_item_price(base_price, ItemQuality.COMMON)
        rare_price = calculate_item_price(base_price, ItemQuality.RARE)
        epic_price = calculate_item_price(base_price, ItemQuality.EPIC)
        legendary_price = calculate_item_price(base_price, ItemQuality.LEGENDARY)
        
        assert common_price == base_price
        assert rare_price > common_price
        assert epic_price > rare_price
        assert legendary_price > epic_price
