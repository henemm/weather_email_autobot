#!/usr/bin/env python3
"""
Debug script to show exactly how coordinate-to-zone mapping works.
Shows the complete process from coordinates to fire risk warnings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wetter.fire_risk_massif import FireRiskZone
from src.wetter.zone_polygon_mapper import ZonePolygonMapper
import json

def debug_zone_mapping():
    """Show the complete zone mapping process step by step."""
    print("🗺️ DEBUG: Zone Mapping Process")
    print("=" * 80)
    
    # Test coordinates from GR20 stages
    test_coords = [
        (42.4653, 8.9070, "Ortu"),
        (42.4262, 8.9003, "Carozzu"), 
        (41.7330, 9.3377, "Conca"),
    ]
    
    fire_risk = FireRiskZone()
    zone_mapper = fire_risk.zone_mapper
    
    print("📋 STEP 1: Available zones in GeoJSON file:")
    print("-" * 50)
    for i, row in zone_mapper.gdf.iterrows():
        zone_name = row['name']
        print(f"  Zone {i}: {zone_name}")
    print()
    
    print("🔄 STEP 2: Zone name mapping (unofficial → official):")
    print("-" * 50)
    for unofficial, official in zone_mapper.ZONE_NAME_MAPPING.items():
        print(f"  '{unofficial}' → '{official}'")
    print()
    
    print("🔗 STEP 3: Official zone names to zm_key mapping:")
    print("-" * 50)
    for zone_name, zm_key in fire_risk.ZONE_NAME_TO_ZM_KEY.items():
        print(f"  '{zone_name}' → zm_key '{zm_key}'")
    print()
    
    print("📍 STEP 4: Coordinate testing for each stage:")
    print("-" * 50)
    
    for lat, lon, stage_name in test_coords:
        print(f"\n🎯 Testing: {stage_name} ({lat}, {lon})")
        print(f"  └─ Step 4a: Check which polygon contains these coordinates...")
        
        # Step 4a: Find which polygon contains the point
        from shapely.geometry import Point
        point = Point(lon, lat)  # Create Point
        
        found_zone = None
        for i, row in zone_mapper.gdf.iterrows():
            if row.geometry.contains(point):
                found_zone = {
                    'index': i,
                    'raw_name': row['name'],
                    'geometry': row.geometry
                }
                break
        
        if not found_zone:
            print(f"    ❌ No polygon found containing ({lat}, {lon})")
            continue
            
        print(f"    ✅ Found in polygon {found_zone['index']}: '{found_zone['raw_name']}'")
        
        # Step 4b: Map unofficial name to official name
        raw_name = found_zone['raw_name']
        official_name = zone_mapper.ZONE_NAME_MAPPING.get(raw_name, raw_name)
        print(f"  └─ Step 4b: Map '{raw_name}' → '{official_name}'")
        
        # Step 4c: Get zm_key for official name
        zm_key = fire_risk.ZONE_NAME_TO_ZM_KEY.get(official_name)
        if zm_key:
            print(f"  └─ Step 4c: Map '{official_name}' → zm_key '{zm_key}'")
        else:
            print(f"    ❌ No zm_key found for '{official_name}'")
            continue
        
        # Step 4d: Get fire risk level from API
        print(f"  └─ Step 4d: Get fire risk level from API for zm_key '{zm_key}'...")
        api_data = fire_risk.fetch_fire_risk_data()
        if api_data and 'zm' in api_data:
            level = api_data['zm'].get(zm_key)
            if level is not None:
                print(f"    ✅ API level for zm_key '{zm_key}': {level}")
                
                # Step 4e: Format warning
                warning = fire_risk.format_fire_warnings(lat, lon)
                print(f"  └─ Step 4e: Formatted warning: '{warning}'")
            else:
                print(f"    ❌ No level found in API for zm_key '{zm_key}'")
        else:
            print(f"    ❌ No API data available")
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY: Complete mapping process")
    print("=" * 80)
    print("1. Coordinates → GeoJSON polygon lookup")
    print("2. Raw zone name → Official zone name mapping") 
    print("3. Official zone name → zm_key mapping")
    print("4. zm_key → API fire risk level")
    print("5. Level → Formatted warning text")

if __name__ == "__main__":
    debug_zone_mapping() 