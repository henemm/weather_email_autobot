"""
Utility to format the risk block for SMS/Email (Zonen & Massifs).

Format example: Z:HIGH204,208 MAX209 M:3,5,9
- Z:HIGH... for zones with level 2
- Z:MAX... for zones with level 3
- M:... for restricted massifs
- No brackets, no extra spaces, only if relevant
"""
from typing import List

def format_risk_block(
    high_zones: List[int],
    max_zones: List[int],
    restricted_massifs: List[int]
) -> str:
    """
    Format the risk block for SMS/Email according to the compact spec.

    Args:
        high_zones: List of zone IDs with level 2 (HIGH)
        max_zones: List of zone IDs with level 3 (MAX)
        restricted_massifs: List of massif IDs with current restriction
    Returns:
        Compact string, e.g. 'Z:HIGH204,208 MAX209 M:3,5,9' or '' if nothing relevant
    """
    parts = []
    if high_zones:
        ids = ','.join(str(z) for z in sorted(high_zones))
        parts.append(f"Z:HIGH{ids}")
    if max_zones:
        ids = ','.join(str(z) for z in sorted(max_zones))
        parts.append(f"MAX{ids}")
    if restricted_massifs:
        ids = ','.join(str(m) for m in sorted(restricted_massifs))
        parts.append(f"M:{ids}")
    return ' '.join(parts) 