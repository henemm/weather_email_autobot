#!/usr/bin/env python3
"""
Live test script for fire risk massif support.

This script tests the fire risk warnings for different locations
to demonstrate the functionality of the fire_risk_massif module.
"""

import sys
import os
from datetime import date, datetime
from typing import List, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wetter.fire_risk_massif import (
    FireRiskMassif,
    get_fire_alerts_for_coordinates,
    format_fire_alert_for_report
)


def test_location(name: str, lat: float, lon: float, target_date: date) -> None:
    """
    Test fire risk alerts for a specific location.
    
    Args:
        name: Location name for display
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        target_date: Date to test
    """
    print(f"\n{'='*60}")
    print(f"Testing location: {name}")
    print(f"Coordinates: {lat:.6f}, {lon:.6f}")
    print(f"Date: {target_date}")
    print(f"{'='*60}")
    
    try:
        # Get fire alerts for coordinates
        alerts = get_fire_alerts_for_coordinates(lat, lon, target_date)
        
        if not alerts:
            print("❌ No fire alerts found")
            print("   Possible reasons:")
            print("   - Coordinates outside Corsica massifs")
            print("   - No data available for this date")
            print("   - API not accessible")
            return
        
        # Display each alert
        for i, alert in enumerate(alerts, 1):
            print(f"\nAlert #{i}:")
            print(f"  Massif ID: {alert.massif_id}")
            print(f"  Level: {alert.level}/5 ({alert.description})")
            print(f"  Is Warning: {'✅ Yes' if alert.is_warning() else '❌ No'}")
            print(f"  Level String: {alert.get_level_string()}")
            
            # Format for report
            formatted = format_fire_alert_for_report(alert)
            if formatted:
                print(f"  Report Format: '{formatted}'")
            else:
                print(f"  Report Format: (no warning - below threshold)")
                
    except Exception as e:
        print(f"❌ Error testing location {name}: {e}")


def test_massif_direct(massif_id: int, target_date: date) -> None:
    """
    Test fire risk alerts directly by massif ID.
    
    Args:
        massif_id: The massif ID to test
        target_date: Date to test
    """
    print(f"\n{'='*60}")
    print(f"Testing Massif ID: {massif_id}")
    print(f"Date: {target_date}")
    print(f"{'='*60}")
    
    try:
        fire_risk = FireRiskMassif()
        
        # Get massif info
        massif = fire_risk.get_massif_by_id(massif_id)
        if massif:
            print(f"Massif Name: {massif.name}")
            print(f"Geographic Bounds:")
            print(f"  Latitude: {massif.min_lat:.2f} to {massif.max_lat:.2f}")
            print(f"  Longitude: {massif.min_lon:.2f} to {massif.max_lon:.2f}")
        else:
            print(f"❌ Massif ID {massif_id} not found in mapping")
            return
        
        # Get fire alert
        alert = fire_risk.get_fire_alert_for_massif(massif_id, target_date)
        
        if alert is None:
            print("❌ No fire alert data found")
            print("   Possible reasons:")
            print("   - No data available for this date")
            print("   - API not accessible")
            return
        
        print(f"\nFire Alert Data:")
        print(f"  Level: {alert.level}/5 ({alert.description})")
        print(f"  Is Warning: {'✅ Yes' if alert.is_warning() else '❌ No'}")
        print(f"  Level String: {alert.get_level_string()}")
        
        # Format for report
        formatted = format_fire_alert_for_report(alert)
        if formatted:
            print(f"  Report Format: '{formatted}'")
        else:
            print(f"  Report Format: (no warning - below threshold)")
            
    except Exception as e:
        print(f"❌ Error testing massif {massif_id}: {e}")


def main():
    """Main test function."""
    print("🔥 Fire Risk Massif Live Test")
    print("=" * 60)
    print(f"Test Date: {date.today()}")
    print(f"Current Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test locations in Corsica
    corsica_locations = [
        ("Conca (Corse-du-Sud)", 41.79418, 9.259567),
        ("Corte (Haute-Corse)", 42.3069, 9.1497),
        ("Ajaccio (Corse-du-Sud)", 41.9192, 8.7386),
        ("Bastia (Haute-Corse)", 42.7028, 9.4491),
        ("Calvi (Haute-Corse)", 42.5667, 8.7575),
        ("Porto-Vecchio (Corse-du-Sud)", 41.5911, 9.2794),
    ]
    
    # Test locations outside Corsica (should return no alerts)
    other_locations = [
        ("Paris (France)", 48.8566, 2.3522),
        ("Nice (France)", 43.7102, 7.2620),
        ("Marseille (France)", 43.2965, 5.3698),
    ]
    
    print("\n📍 Testing Corsica Locations:")
    for name, lat, lon in corsica_locations:
        test_location(name, lat, lon, date.today())
    
    print("\n📍 Testing Non-Corsica Locations (should return no alerts):")
    for name, lat, lon in other_locations:
        test_location(name, lat, lon, date.today())
    
    print("\n🏔️ Testing Direct Massif IDs:")
    # Test the two Corsica massifs directly
    for massif_id in [1, 2]:
        test_massif_direct(massif_id, date.today())
    
    print(f"\n{'='*60}")
    print("✅ Live test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main() 