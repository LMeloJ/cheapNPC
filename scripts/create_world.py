"""
Script to create the NPC world.

This script uses the WorldService to create the complete NPC world.
"""

from cheapNPC.core.services.world_service import create_world_sync


def main():
    """Create the NPC world using the world service."""
    print("🌍 Creating NPC World...")
    print("=" * 50)
    
    def progress_callback(msg):
        """Print progress updates."""
        print(msg)
    
    result = create_world_sync(progress_callback)
    print("\n" + "=" * 50)
    print(result)


if __name__ == '__main__':
    main()

