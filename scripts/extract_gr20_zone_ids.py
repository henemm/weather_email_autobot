#!/usr/bin/env python3
"""
Extract GR20 Zone IDs from Fire Risk Website

This script extracts zone IDs from the official fire risk website
and saves them to a file for use in the GR20 weather system.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fire.gr20_zone_massif_ids import GR20ZoneMassifExtractor
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to extract zone IDs and save results."""
    logger.info("Starting GR20 zone ID extraction...")
    
    # Create extractor
    extractor = GR20ZoneMassifExtractor()
    
    # Use existing zone mappings (no need to extract from website)
    logger.info("Using existing zone mappings...")
    
    # Format and display output
    output = extractor.format_output()
    print("\n" + "="*60)
    print("GR20 ZONE AND MASSIF ID EXTRACTION RESULTS")
    print("="*60)
    print(output)
    print("="*60)
    
    # Save to file
    output_file = Path("data/gr20_zone_massif_ids.txt")
    output_file.parent.mkdir(exist_ok=True)
    
    extractor.save_mappings_to_file(str(output_file))
    
    logger.info(f"Results saved to {output_file}")
    
    # Display summary
    restricted_massifs = extractor.get_restricted_massif_ids()
    high_risk_zones = extractor.get_high_risk_zone_ids()
    gr20_relevant_zones = extractor.get_gr20_relevant_zone_ids()
    
    print(f"\nSummary:")
    print(f"- Restricted massifs found: {len(restricted_massifs)}")
    print(f"- High risk zones found: {len(high_risk_zones)}")
    print(f"- GR20 relevant zones found: {len(gr20_relevant_zones)}")
    print(f"- Zone mappings available: {len(extractor.zone_mapping)}")
    
    if restricted_massifs:
        print(f"- Restricted massif IDs: {', '.join(map(str, restricted_massifs))}")
    
    if gr20_relevant_zones:
        print(f"- GR20 relevant zone IDs: {', '.join(map(str, gr20_relevant_zones))}")
        print(f"- GR20 relevant zone names: {', '.join([extractor.zone_mapping[zid] for zid in gr20_relevant_zones])}")
    
    if extractor.zone_mapping:
        print(f"- All zone mappings: {', '.join([f'{k}→{v}' for k, v in extractor.zone_mapping.items()])}")


if __name__ == "__main__":
    main() 