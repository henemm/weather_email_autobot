#!/usr/bin/env python3
"""
Test script specifically for Refuge Manganu and Refuge d'Usciolu zone assignments.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wetter.fire_risk_massif import FireRiskZone
from shapely.geometry import Point

def test_specific_refuges():
    """Test zone assignments for specific refuges."""
    print("🏔️ Testing Specific Refuge Zone Assignments")
    print("=" * 60)
    
    # Coordinates from etappen.json
    refuges = {
        "Refuge Manganu": (42.22026, 8.980731),  # End point of Manganu stage
        "Refuge d'Usciolu": (41.934961, 9.205803),  # End point of Usciolu stage
    }
    
    fire_risk = FireRiskZone()
    zone_mapper = fire_risk.zone_mapper
    
    for refuge_name, (lat, lon) in refuges.items():
        print(f"\n🎯 {refuge_name} ({lat}, {lon})")
        print("-" * 40)
        
        # Step 1: Find which polygon contains the point
        point = Point(lon, lat)
        
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
            print(f"❌ No polygon found containing ({lat}, {lon})")
            continue
            
        print(f"✅ Found in polygon {found_zone['index']}: '{found_zone['raw_name']}'")
        
        # Step 2: Map unofficial name to official name
        raw_name = found_zone['raw_name']
        official_name = zone_mapper.ZONE_NAME_MAPPING.get(raw_name, raw_name)
        if raw_name != official_name:
            print(f"🔄 Mapped '{raw_name}' → '{official_name}'")
        else:
            print(f"✅ Official name: '{official_name}'")
        
        # Step 3: Get zm_key for official name
        zm_key = fire_risk.ZONE_NAME_TO_ZM_KEY.get(official_name)
        if zm_key:
            print(f"🔗 zm_key: '{zm_key}'")
        else:
            print(f"❌ No zm_key found for '{official_name}'")
            continue
        
        # Step 4: Get fire risk level from API
        api_data = fire_risk.fetch_fire_risk_data()
        if api_data and 'zm' in api_data:
            level = api_data['zm'].get(zm_key)
            if level is not None:
                print(f"🔥 API level: {level}")
                
                # Step 5: Format warning
                warning = fire_risk.format_fire_warnings(lat, lon)
                print(f"⚠️  Warning: '{warning}'")
            else:
                print(f"❌ No level found in API for zm_key '{zm_key}'")
        else:
            print(f"❌ No API data available")
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print("This test shows the exact zone assignment process for these specific refuges.")
    print("The coordinates come directly from etappen.json and are mapped to zones")
    print("using the GeoJSON polygon data and the verified zm_key mapping.")

if __name__ == "__main__":
    test_specific_refuges() 