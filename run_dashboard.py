#!/usr/bin/env uv run python3
"""
Launcher script for the CheapNPC Agent Dashboard.

This script starts the web interface with agent functionality.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the CheapNPC Agent Dashboard."""
    print("🚀 Starting CheapNPC Agent Dashboard...")
    print("=" * 60)
    
    # Check database status
    try:
        from cheapNPC.config import get_config
        config = get_config()
        db_path = config.database.path
        if not os.path.exists(db_path):
            print(f"⚠️  Warning: Database '{db_path}' not found!")
            print("   The dashboard will still start, but some features may not work.")
            print("   Click 'Create World' on the landing page to initialize.")
            print()
    except Exception as e:
        print(f"⚠️  Warning: Could not load configuration: {e}")
        print()
    
    # Start the dashboard
    try:
        from cheapNPC.app import main as dashboard_main
        dashboard_main()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you're running this from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
