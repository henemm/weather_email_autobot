#!/usr/bin/env python3
"""
Test script to compare thunderstorm descriptions for two locations.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_meteofrance import get_french_weather_text

def test_location(name, lat, lon):
    """Test a specific location for thunderstorm descriptions."""
    
    print(f"🌤️  {name}")
    print("=" * 50)
    print(f"Koordinaten: {lat}, {lon}")
    print()
    
    try:
        weather_data = get_french_weather_text(lat, lon)
        
        # Check for thunderstorm-related descriptions
        thunderstorm_keywords = ['orage', 'orages', 'risque', 'thunderstorm']
        
        print("📅 HEUTE - Gewitterrelevante Beschreibungen:")
        print("-" * 45)
        found_thunderstorm = False
        for entry in weather_data['today']:
            desc_lower = entry['french_description'].lower()
            if any(keyword in desc_lower for keyword in thunderstorm_keywords):
                print(f"{entry['hour']:02d}:00 - {entry['french_description']}")
                print(f"    Temperatur: {entry['temperature']}°C")
                if entry['wind_gusts'] > 0:
                    print(f"    Windböen: {entry['wind_gusts']} km/h")
                print()
                found_thunderstorm = True
        
        if not found_thunderstorm:
            print("Keine Gewitterbeschreibungen gefunden")
            # Show first few entries for context
            print("Erste Einträge:")
            for entry in weather_data['today'][:3]:
                print(f"  {entry['hour']:02d}:00 - {entry['french_description']}")
        print()
        
        print("📅 MORGEN - Gewitterrelevante Beschreibungen:")
        print("-" * 45)
        found_thunderstorm = False
        for entry in weather_data['tomorrow']:
            desc_lower = entry['french_description'].lower()
            if any(keyword in desc_lower for keyword in thunderstorm_keywords):
                print(f"{entry['hour']:02d}:00 - {entry['french_description']}")
                print(f"    Temperatur: {entry['temperature']}°C")
                if entry['wind_gusts'] > 0:
                    print(f"    Windböen: {entry['wind_gusts']} km/h")
                print()
                found_thunderstorm = True
        
        if not found_thunderstorm:
            print("Keine Gewitterbeschreibungen gefunden")
            # Show first few entries for context
            print("Erste Einträge:")
            for entry in weather_data['tomorrow'][:3]:
                print(f"  {entry['hour']:02d}:00 - {entry['french_description']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def main():
    """Test both locations."""
    
    print("⚡ Gewitter-Test: FONT-ROMEU-ODEILLO-VIA vs SAILLAGOUSE")
    print("=" * 60)
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test locations
    locations = [
        {
            "name": "FONT-ROMEU-ODEILLO-VIA (66120)",
            "lat": 42.471359,
            "lon": 2.029742
        },
        {
            "name": "SAILLAGOUSE (66800) - Approximiert",
            "lat": 42.4544,  # Approximierte Koordinaten für SAILLAGOUSE
            "lon": 2.1694
        }
    ]
    
    results = []
    for location in locations:
        success = test_location(location["name"], location["lat"], location["lon"])
        results.append((location["name"], success))
        print("\n" + "="*60 + "\n")
    
    # Summary
    print("📊 ZUSAMMENFASSUNG:")
    print("-" * 30)
    for name, success in results:
        status = "✅ Erfolgreich" if success else "❌ Fehler"
        print(f"{name}: {status}")

if __name__ == "__main__":
    sys.exit(0 if main() else 1) 