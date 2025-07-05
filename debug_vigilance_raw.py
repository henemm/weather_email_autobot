#!/usr/bin/env python3
"""
Debug script to output raw vigilance API response for Conca.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from meteofrance_api.client import MeteoFranceClient
import json

def debug_vigilance_raw():
    """Debug raw vigilance API response for Conca."""
    lat, lon = 41.79418, 9.259567  # Conca coordinates
    
    try:
        client = MeteoFranceClient()
        department = "2A"  # Corse-du-Sud
        warnings = client.get_warning_current_phenomenons(department)
        
        print("=== RAW VIGILANCE API RESPONSE ===")
        print(f"Department: {department}")
        print(f"Coordinates: {lat}, {lon}")
        print()
        
        # Print all attributes
        print("All attributes of warnings object:")
        for attr in dir(warnings):
            if not attr.startswith('_'):
                value = getattr(warnings, attr)
                print(f"  {attr}: {value}")
        print()
        
        # Print phenomenons_max_colors in detail
        max_colors = getattr(warnings, 'phenomenons_max_colors', None)
        print("phenomenons_max_colors:")
        print(f"  Type: {type(max_colors)}")
        print(f"  Value: {max_colors}")
        print()
        
        if isinstance(max_colors, list):
            print("List entries:")
            for i, entry in enumerate(max_colors):
                print(f"  Entry {i}: {entry} (type: {type(entry)})")
                if isinstance(entry, dict):
                    for key, value in entry.items():
                        print(f"    {key}: {value} (type: {type(value)})")
        print()
        
        # Test the mapping logic
        print("=== TESTING MAPPING LOGIC ===")
        from src.wetter.fetch_meteofrance import PHENOMENON_ID_MAP, LEVEL_ID_MAP
        
        print("PHENOMENON_ID_MAP:", PHENOMENON_ID_MAP)
        print("LEVEL_ID_MAP:", LEVEL_ID_MAP)
        print()
        
        for i, entry in enumerate(max_colors):
            if isinstance(entry, dict):
                phenomenon_id = entry.get('phenomenon_id')
                level_id = entry.get('phenomenon_max_color_id')
                
                print(f"Entry {i}:")
                print(f"  phenomenon_id: {phenomenon_id} (type: {type(phenomenon_id)})")
                print(f"  level_id: {level_id} (type: {type(level_id)})")
                
                # Test mapping
                phenomenon = PHENOMENON_ID_MAP.get(str(phenomenon_id), 'unknown')
                level = LEVEL_ID_MAP.get(level_id, 'unknown')
                
                print(f"  Mapped phenomenon: {phenomenon}")
                print(f"  Mapped level: {level}")
                print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vigilance_raw() 