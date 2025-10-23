"""
Refactored CLI tool for printing NPC details using the service layer.
"""

import sys
from cheapNPC.core.services import NPCService


def print_npc_details(npc_name: str):
    """Print NPC details using the service layer."""
    npc_service = NPCService()
    
    npc = npc_service.get_npc_with_inventory(npc_name)
    
    if not npc:
        print(f"Error: NPC '{npc_name}' not found in the database.")
        print("Please ensure you have run the NPC creation scripts first.")
        return
    
    print("\n" + "="*50)
    print(f" MERCHANT PROFILE: {npc.name.upper()}")
    print("="*50)
    print(f"  Name:       {npc.name}")
    print(f"  Race:       {npc.race}")
    print(f"  Profession: {npc.profession}")
    print(f"  Skill:      {npc.profession_skill}")
    print(f"  Silver:     {npc.silver_pieces} SP")
    
    print("-" * 50)
    print(" INVENTORY:")
    if not npc.inventory:
        print("  <EMPTY INVENTORY>")
        return

    # Determine maximum width for neat alignment
    max_name_len = max(len(item.name) for item in npc.inventory) if npc.inventory else 0
    max_quality_len = max(len(str(item.quality)) for item in npc.inventory) if npc.inventory else 0
    max_quality_len = max(max_quality_len, len('QUALITY'))

    # Print header with quality column
    print(f"  {'ITEM NAME':<{max_name_len+2}} | {'QTY':>4} | {'PRICE (SP)':>10} | {'QUALITY':<{max_quality_len}}")
    print(f"  {'-'*(max_name_len+2)}-+-{'-'*4}-+-{'-'*10}-+-{'-'*max_quality_len}")

    for item in sorted(npc.inventory, key=lambda x: x.name):
        quality_str = str(item.quality) if item.quality else '-'
        print(f"  {item.name:<{max_name_len+2}} | {item.quantity:>4} | {item.price:>10.2f} | {quality_str:<{max_quality_len}}")
    
    print("="*50)


def main():
    """Main function for CLI tool."""
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <NPC Name>")
        print("Example: python print_npc.py 'Talin Stonehand'")
        sys.exit(1)

    # Get NPC name from command-line arguments
    npc_name_to_find = sys.argv[1]
    
    print(f"Searching for NPC '{npc_name_to_find}' using service layer...")
    print_npc_details(npc_name_to_find)


if __name__ == '__main__':
    main()
