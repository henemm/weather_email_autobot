#!/usr/bin/env python3
"""
Analyze precipitation amounts for thunderstorm locations.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_meteofrance import get_french_weather_text

def analyze_precipitation():
    """Analyze precipitation for both locations."""
    
    # Test locations
    locations = [
        {
            "name": "FONT-ROMEU-ODEILLO-VIA (66120)",
            "lat": 42.471359,
            "lon": 2.029742
        },
        {
            "name": "SAILLAGOUSE (66800) - Approximiert",
            "lat": 42.4544,
            "lon": 2.1694
        }
    ]
    
    print("🌧️  Niederschlagsanalyse für Gewitter-Orte")
    print("=" * 60)
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for location in locations:
        print(f"📍 {location['name']}")
        print(f"Koordinaten: {location['lat']}, {location['lon']}")
        print("-" * 50)
        
        try:
            weather_data = get_french_weather_text(location['lat'], location['lon'])
            
            # Analyze today's precipitation
            print("📅 HEUTE - Niederschlag:")
            today_with_rain = []
            for entry in weather_data['today']:
                if entry['precipitation'] > 0:
                    today_with_rain.append(entry)
            
            if today_with_rain:
                for entry in today_with_rain:
                    print(f"  {entry['hour']:02d}:00 - {entry['precipitation']} mm/h")
                    print(f"    Wetter: {entry['french_description']}")
                    print(f"    Temperatur: {entry['temperature']}°C")
                    if entry['wind_gusts'] > 0:
                        print(f"    Windböen: {entry['wind_gusts']} km/h")
                    print()
            else:
                print("  Kein Niederschlag vorhergesagt")
                # Show first few entries for context
                print("  Erste Einträge:")
                for entry in weather_data['today'][:3]:
                    print(f"    {entry['hour']:02d}:00 - {entry['french_description']} (0 mm/h)")
                print()
            
            # Analyze tomorrow's precipitation
            print("📅 MORGEN - Niederschlag:")
            tomorrow_with_rain = []
            for entry in weather_data['tomorrow']:
                if entry['precipitation'] > 0:
                    tomorrow_with_rain.append(entry)
            
            if tomorrow_with_rain:
                for entry in tomorrow_with_rain:
                    print(f"  {entry['hour']:02d}:00 - {entry['precipitation']} mm/h")
                    print(f"    Wetter: {entry['french_description']}")
                    print(f"    Temperatur: {entry['temperature']}°C")
                    if entry['wind_gusts'] > 0:
                        print(f"    Windböen: {entry['wind_gusts']} km/h")
                    print()
            else:
                print("  Kein Niederschlag vorhergesagt")
                # Show first few entries for context
                print("  Erste Einträge:")
                for entry in weather_data['tomorrow'][:3]:
                    print(f"    {entry['hour']:02d}:00 - {entry['french_description']} (0 mm/h)")
                print()
            
            # Summary statistics
            print("📊 ZUSAMMENFASSUNG:")
            print("-" * 20)
            
            # Today stats
            today_total = sum(entry['precipitation'] for entry in weather_data['today'])
            today_max = max(entry['precipitation'] for entry in weather_data['today'])
            today_entries_with_rain = len([e for e in weather_data['today'] if e['precipitation'] > 0])
            
            print(f"  HEUTE:")
            print(f"    Gesamtmenge: {today_total} mm")
            print(f"    Max. pro Stunde: {today_max} mm/h")
            print(f"    Stunden mit Regen: {today_entries_with_rain}")
            
            # Tomorrow stats
            tomorrow_total = sum(entry['precipitation'] for entry in weather_data['tomorrow'])
            tomorrow_max = max(entry['precipitation'] for entry in weather_data['tomorrow'])
            tomorrow_entries_with_rain = len([e for e in weather_data['tomorrow'] if e['precipitation'] > 0])
            
            print(f"  MORGEN:")
            print(f"    Gesamtmenge: {tomorrow_total} mm")
            print(f"    Max. pro Stunde: {tomorrow_max} mm/h")
            print(f"    Stunden mit Regen: {tomorrow_entries_with_rain}")
            
        except Exception as e:
            print(f"❌ Fehler: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    analyze_precipitation() 