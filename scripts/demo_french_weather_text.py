#!/usr/bin/env python3
"""
Demo script to show French weather text descriptions from MeteoFrance API.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_meteofrance import get_french_weather_text

def main():
    """Demo the French weather text function."""
    
    # Test coordinates (provided by user)
    lat = 42.471359
    lon = 2.029742
    
    print("🌤️  MeteoFrance API - Französische Wetterberichte")
    print("=" * 60)
    print(f"Koordinaten: {lat}, {lon}")
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Get French weather text
        weather_data = get_french_weather_text(lat, lon)
        
        # Display today's weather
        print("📅 HEUTE:")
        print("-" * 30)
        if weather_data['today']:
            for entry in weather_data['today']:
                print(f"{entry['hour']:02d}:00 - {entry['french_description']}")
                print(f"    Temperatur: {entry['temperature']}°C")
                if entry['precipitation'] > 0:
                    print(f"    Niederschlag: {entry['precipitation']} mm/h")
                if entry['wind_gusts'] > 0:
                    print(f"    Windböen: {entry['wind_gusts']} km/h")
                print()
        else:
            print("Keine Daten für heute verfügbar")
        
        # Display tomorrow's weather
        print("📅 MORGEN:")
        print("-" * 30)
        if weather_data['tomorrow']:
            for entry in weather_data['tomorrow']:
                print(f"{entry['hour']:02d}:00 - {entry['french_description']}")
                print(f"    Temperatur: {entry['temperature']}°C")
                if entry['precipitation'] > 0:
                    print(f"    Niederschlag: {entry['precipitation']} mm/h")
                if entry['wind_gusts'] > 0:
                    print(f"    Windböen: {entry['wind_gusts']} km/h")
                print()
        else:
            print("Keine Daten für morgen verfügbar")
        
        # Show raw data for debugging
        print("🔍 ROHDATEN (erste 3 Einträge pro Tag):")
        print("-" * 50)
        print("HEUTE:")
        for i, entry in enumerate(weather_data['today'][:3]):
            print(f"  {i+1}. {entry}")
        print()
        print("MORGEN:")
        for i, entry in enumerate(weather_data['tomorrow'][:3]):
            print(f"  {i+1}. {entry}")
            
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Wetterdaten: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 