#!/usr/bin/env uv run python3
"""
Launcher script for the CheapNPC Agent Dashboard.

This script provides an easy way to start the enhanced web interface
with all agent functionality integrated.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the Enhanced NPC Agent Dashboard."""
    print("🚀 Starting CheapNPC Agent Dashboard...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("data/village.db"):
        print("⚠️  Warning: Database 'data/village.db' not found!")
        print("   The dashboard will still start, but some features may not work.")
        print("   Consider running NPC generation scripts first.")
        print()
    
    # Import and run the dashboard
    try:
        from cheapNPC.presentation.web.app import main as dashboard_main
        dashboard_main()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you're running this from the project root directory.")
        print("   Try: python -m cheapNPC.presentation.web.app")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
