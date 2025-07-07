#!/usr/bin/env python3
"""
Test script to debug fire risk warnings (zone-based only).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wetter.fire_risk_massif import FireRiskZone
from src.report.weather_report_generator import generate_weather_report


def test_fire_risk_implementation():
    """Test fire risk implementation and integration (zone-based only)."""
    print("Testing fire risk implementation (zone-based only)...")
    
    test_coords = [
        (42.3069, 9.1497, "Corte"),
        (41.9181, 8.9247, "Vizzavona"),
        (41.5912, 9.2806, "Conca"),
        (41.7358, 9.2042, "Col de Bavella")
    ]
    
    fire_risk = FireRiskZone()
    print("\n📍 Testing Fire Risk for Different Locations (Zone-based):")
    for lat, lon, name in test_coords:
        zone_alert = fire_risk.get_zone_fire_alert_for_location(lat, lon)
        print(f"{name}: {zone_alert}")


def test_fire_risk_api():
    """Test direct API access to fire risk data."""
    print("\n🌐 Testing Fire Risk API Access:")
    print("-" * 60)
    
    fire_risk = FireRiskZone()
    
    try:
        # Fetch today's data
        data = fire_risk.fetch_fire_risk_data()
        
        if data:
            print("✅ Successfully fetched fire risk data")
            print(f"📊 Data keys: {list(data.keys())}")
            
            if 'zm' in data:
                zm_data = data['zm']
                print(f"🏔️ Zone data type: {type(zm_data)}")
                
                if isinstance(zm_data, dict):
                    print(f"🏔️ Number of zones: {len(zm_data)}")
                    print(f"🏔️ Zone IDs: {list(zm_data.keys())}")
                    
                    # Show first few zones
                    for i, (zone_id, zone_level) in enumerate(zm_data.items()):
                        if i >= 3:  # Show only first 3
                            break
                        print(f"   Zone {zone_id}: Level {zone_level}")
                else:
                    print(f"🏔️ Zone data: {zm_data}")
            else:
                print("⚠️ No 'zm' key in data")
        else:
            print("❌ No data returned from API")
            
    except Exception as e:
        print(f"❌ Error accessing fire risk API: {e}")
        import traceback
        traceback.print_exc()


def test_zone_mapping():
    """Test zone mapping for different locations."""
    print("\n🗺️ Testing Zone Mapping:")
    print("-" * 60)
    
    fire_risk = FireRiskZone()
    
    test_locations = [
        (42.3069, 9.1497, "Corte"),
        (41.9181, 8.9247, "Vizzavona"),
        (41.5912, 9.2806, "Conca"),
        (41.7358, 9.2042, "Col de Bavella"),
        (42.5667, 8.7575, "Calvi"),
        (41.9192, 8.7386, "Ajaccio")
    ]
    
    for lat, lon, name in test_locations:
        zone_alert = fire_risk.get_zone_fire_alert_for_location(lat, lon)
        if zone_alert:
            print(f"{name}: Zone {zone_alert.get('zm_key')} ({zone_alert.get('zone_name')}) -> Level {zone_alert.get('level')}")
        else:
            print(f"{name}: No zone found")


def test_warning_formatting():
    """Test warning formatting according to email_format.mdc."""
    print("\n📝 Testing Warning Formatting:")
    print("-" * 60)
    
    fire_risk = FireRiskZone()
    
    test_locations = [
        (42.3069, 9.1497, "Corte"),
        (41.9181, 8.9247, "Vizzavona"),
        (41.5912, 9.2806, "Conca"),
        (41.7358, 9.2042, "Col de Bavella")
    ]
    
    for lat, lon, name in test_locations:
        warning = fire_risk.format_fire_warnings(lat, lon)
        print(f"{name}: '{warning}'")


if __name__ == "__main__":
    print("🔥 Fire Risk Debug Test (Zone-based only)")
    print("=" * 60)
    
    test_fire_risk_implementation()
    test_fire_risk_api()
    test_zone_mapping()
    test_warning_formatting()
    
    print("\n" + "=" * 60)
    print("🏁 Fire risk debug test completed.")
    print("=" * 60) 