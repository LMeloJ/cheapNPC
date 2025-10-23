"""
Test fixtures and utilities for consistent test data.
"""

import pytest
from cheapNPC.core.models import NPC, CrafterNPC, SalesPersonNPC, ItemQuality, InventoryEntry


@pytest.fixture
def sample_crafter_npc():
    """Provide a sample crafter NPC for testing."""
    return CrafterNPC(
        name="Test Crafter",
        personality="creative",
        skills=["woodworking", "metalworking", "leatherworking"]
    )


@pytest.fixture
def sample_merchant_npc():
    """Provide a sample merchant NPC for testing."""
    return SalesPersonNPC(
        name="Test Merchant",
        personality="greedy",
        skills=["bargaining", "appraisal", "persuasion"]
    )


@pytest.fixture
def sample_inventory_items():
    """Provide sample inventory items for testing."""
    return [
        InventoryEntry(
            name="Wooden Sword",
            quantity=2,
            quality=ItemQuality.COMMON,
            price=50
        ),
        InventoryEntry(
            name="Iron Shield",
            quantity=1,
            quality=ItemQuality.RARE,
            price=200
        ),
        InventoryEntry(
            name="Health Potion",
            quantity=5,
            quality=ItemQuality.COMMON,
            price=25
        ),
        InventoryEntry(
            name="Magic Scroll",
            quantity=1,
            quality=ItemQuality.EPIC,
            price=500
        )
    ]


@pytest.fixture
def sample_trading_scenarios():
    """Provide sample trading scenarios for testing."""
    return [
        {
            "buyer": "Test Crafter",
            "seller": "Test Merchant",
            "item": "Health Potion",
            "quantity": 2,
            "expected_price_range": (40, 60)
        },
        {
            "buyer": "Test Merchant",
            "seller": "Test Crafter",
            "item": "Wooden Sword",
            "quantity": 1,
            "expected_price_range": (40, 60)
        }
    ]


@pytest.fixture
def mock_npc_data():
    """Provide mock NPC data for testing."""
    return {
        "crafter": {
            "name": "Master Smith",
            "npc_type": "crafter",
            "personality": "perfectionist",
            "skills": ["metalworking", "weapon_crafting"],
            "money": 1500,
            "inventory": [
                {"name": "Steel Sword", "quantity": 1, "quality": "rare", "price": 300},
                {"name": "Iron Ingot", "quantity": 5, "quality": "common", "price": 50}
            ]
        },
        "merchant": {
            "name": "Trade Master",
            "npc_type": "salesperson",
            "personality": "charismatic",
            "skills": ["bargaining", "appraisal", "persuasion"],
            "money": 2000,
            "inventory": [
                {"name": "Health Potion", "quantity": 10, "quality": "common", "price": 25},
                {"name": "Mana Potion", "quantity": 5, "quality": "rare", "price": 100}
            ]
        }
    }


@pytest.fixture
def sample_item_catalog():
    """Provide a sample item catalog for testing."""
    return {
        "weapons": [
            {"name": "Wooden Sword", "base_price": 50, "item_type": "weapon"},
            {"name": "Iron Sword", "base_price": 150, "item_type": "weapon"},
            {"name": "Steel Sword", "base_price": 300, "item_type": "weapon"}
        ],
        "armor": [
            {"name": "Leather Armor", "base_price": 100, "item_type": "armor"},
            {"name": "Chain Mail", "base_price": 250, "item_type": "armor"},
            {"name": "Plate Armor", "base_price": 500, "item_type": "armor"}
        ],
        "consumables": [
            {"name": "Health Potion", "base_price": 25, "item_type": "consumable"},
            {"name": "Mana Potion", "base_price": 50, "item_type": "consumable"},
            {"name": "Stamina Potion", "base_price": 30, "item_type": "consumable"}
        ],
        "materials": [
            {"name": "Iron Ingot", "base_price": 50, "item_type": "material"},
            {"name": "Steel Ingot", "base_price": 100, "item_type": "material"},
            {"name": "Magic Crystal", "base_price": 200, "item_type": "material"}
        ]
    }


@pytest.fixture
def sample_trading_pairs():
    """Provide sample trading pairs for testing."""
    return [
        {
            "buyer": "Master Smith",
            "seller": "Trade Master",
            "item": "Health Potion",
            "quantity": 3,
            "quality": "common"
        },
        {
            "buyer": "Trade Master",
            "seller": "Master Smith",
            "item": "Iron Ingot",
            "quantity": 2,
            "quality": "common"
        }
    ]


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_npc(name, npc_type="crafter", personality="neutral", skills=None, money=1000):
        """Create an NPC for testing."""
        if skills is None:
            skills = ["basic_skill"]
        
        if npc_type == "crafter":
            return CrafterNPC(name=name, personality=personality, skills=skills)
        elif npc_type == "salesperson":
            return SalesPersonNPC(name=name, personality=personality, skills=skills)
        else:
            return NPC(name=name, npc_type=npc_type, personality=personality, skills=skills)
    
    @staticmethod
    def create_inventory_entry(name, quantity=1, quality=ItemQuality.COMMON, price=100):
        """Create an inventory entry for testing."""
        return InventoryEntry(
            name=name,
            quantity=quantity,
            quality=quality,
            price=price
        )
    
    @staticmethod
    def create_trading_scenario(buyer, seller, item, quantity=1, price=100):
        """Create a trading scenario for testing."""
        return {
            "buyer": buyer,
            "seller": seller,
            "item": item,
            "quantity": quantity,
            "price": price
        }
