"""
Pytest configuration and shared fixtures for the cheapNPC test suite.
"""

import pytest
import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cheapNPC.infrastructure.database.connection import get_database_connection
from cheapNPC.infrastructure.database.migrations import setup_database
from cheapNPC.core.services import NPCService, TradingService, InventoryService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_village.db")
    
    # Set environment variable to use temp database
    original_db_path = os.environ.get('DATABASE_PATH')
    os.environ['DATABASE_PATH'] = temp_db_path
    
    # Setup the database
    setup_database()
    
    yield temp_db_path
    
    # Cleanup
    if original_db_path:
        os.environ['DATABASE_PATH'] = original_db_path
    else:
        os.environ.pop('DATABASE_PATH', None)
    
    shutil.rmtree(temp_dir)


@pytest.fixture
def npc_service(temp_db):
    """Provide an NPC service instance with test database."""
    return NPCService()


@pytest.fixture
def trading_service(temp_db):
    """Provide a trading service instance with test database."""
    return TradingService()


@pytest.fixture
def inventory_service(temp_db):
    """Provide an inventory service instance with test database."""
    return InventoryService()


@pytest.fixture
def sample_npcs():
    """Provide sample NPC data for testing."""
    return [
        {
            "name": "Test Crafter",
            "npc_type": "crafter",
            "personality": "friendly",
            "skills": ["woodworking", "metalworking"],
            "inventory": [
                {"name": "Wooden Sword", "quantity": 2, "quality": "common", "price": 50},
                {"name": "Iron Shield", "quantity": 1, "quality": "rare", "price": 200}
            ]
        },
        {
            "name": "Test Merchant",
            "npc_type": "salesperson",
            "personality": "greedy",
            "skills": ["bargaining", "appraisal"],
            "inventory": [
                {"name": "Health Potion", "quantity": 5, "quality": "common", "price": 25},
                {"name": "Magic Scroll", "quantity": 1, "quality": "epic", "price": 500}
            ]
        }
    ]


@pytest.fixture
def sample_items():
    """Provide sample item data for testing."""
    return [
        {"name": "Wooden Sword", "item_type": "weapon", "base_price": 50},
        {"name": "Iron Shield", "item_type": "armor", "base_price": 200},
        {"name": "Health Potion", "item_type": "consumable", "base_price": 25},
        {"name": "Magic Scroll", "item_type": "magic", "base_price": 500}
    ]
