#!/usr/bin/env uv run python3
"""
Direct launcher for the CheapNPC Dashboard.

This script launches the dashboard directly, bypassing the landing page.
Use this after the world has been created.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the dashboard directly."""
    print("🚀 Starting CheapNPC Dashboard...")
    print("=" * 50)
    
    # Import and run the dashboard
    try:
        from cheapNPC.presentation.web.dashboard import main as dashboard_main
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
