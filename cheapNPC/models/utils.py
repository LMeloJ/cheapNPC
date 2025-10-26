"""
Utility functions for NPC-related operations in MVC architecture.
"""

from typing import Optional
from .items import ItemQuality


def get_item_quality_by_skill(profession_skill: str) -> str:
    """
    Return an ItemQuality based on profession_skill.
    
    Statistical distribution for item quality by skill rank:
    - 'poor':        70% poor,  25% regular,  5% fine,      0% exceptional
    - 'regular':     20% poor,  60% regular, 15% fine,      5% exceptional
    - 'fine':         5% poor,  25% regular, 50% fine,     20% exceptional
    - 'exceptional':  0% poor,  10% regular, 40% fine,     50% exceptional
    """
    import random

    probabilities = {
        "poor":        [(ItemQuality.poor, 0.70), (ItemQuality.regular, 0.25), (ItemQuality.fine, 0.05), (ItemQuality.exceptional, 0.0)],
        "regular":     [(ItemQuality.poor, 0.20), (ItemQuality.regular, 0.60), (ItemQuality.fine, 0.15), (ItemQuality.exceptional, 0.05)],
        "fine":        [(ItemQuality.poor, 0.05), (ItemQuality.regular, 0.25), (ItemQuality.fine, 0.50), (ItemQuality.exceptional, 0.20)],
        "exceptional": [(ItemQuality.poor, 0.0),  (ItemQuality.regular, 0.10), (ItemQuality.fine, 0.40), (ItemQuality.exceptional, 0.50)],
    }

    # Fetch probability distribution for this skill level
    dist = probabilities.get(profession_skill, probabilities["regular"])
    qualities, weights = zip(*dist)
    selected_quality = random.choices(qualities, weights=weights, k=1)[0]
    return selected_quality.value
