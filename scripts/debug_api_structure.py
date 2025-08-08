#!/usr/bin/env python3
"""
Debug script to examine the actual MeteoFrance API structure.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteofrance_api.client import MeteoFranceClient

def debug_api_structure():
    """Debug the actual API structure."""
    
    # Test coordinates
    lat = 42.471359
    lon = 2.029742
    
    print("🔍 MeteoFrance API Struktur-Analyse")
    print("=" * 50)
    print(f"Koordinaten: {lat}, {lon}")
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        if not forecast.forecast or len(forecast.forecast) == 0:
            print("❌ Keine Forecast-Daten erhalten")
            return
        
        print(f"📊 Anzahl Forecast-Einträge: {len(forecast.forecast)}")
        print()
        
        # Examine first few entries in detail
        for i, entry in enumerate(forecast.forecast[:5]):
            print(f"🔍 Eintrag {i+1}:")
            print(f"  Raw entry type: {type(entry)}")
            print(f"  Keys: {list(entry.keys()) if isinstance(entry, dict) else 'Not a dict'}")
            
            if isinstance(entry, dict):
                # Check weather field
                weather = entry.get('weather')
                print(f"  Weather field: {weather}")
                print(f"  Weather type: {type(weather)}")
                
                if isinstance(weather, dict):
                    print(f"  Weather keys: {list(weather.keys())}")
                    print(f"  Weather desc: {weather.get('desc')}")
                    print(f"  Weather icon: {weather.get('icon')}")
                elif isinstance(weather, str):
                    print(f"  Weather as string: {weather}")
                
                # Check other relevant fields
                print(f"  Temperature: {entry.get('T')}")
                print(f"  Wind: {entry.get('wind')}")
                print(f"  Rain: {entry.get('rain')}")
                print(f"  Datetime: {entry.get('datetime')}")
                print(f"  DT timestamp: {entry.get('dt')}")
                print()
            else:
                print(f"  Entry is not a dict: {entry}")
                print()
        
        # Look for any entries with thunderstorm-related content
        print("⚡ Suche nach Gewitter-bezogenen Einträgen:")
        print("-" * 40)
        thunderstorm_found = False
        
        for i, entry in enumerate(forecast.forecast):
            if isinstance(entry, dict):
                weather = entry.get('weather', {})
                if isinstance(weather, dict):
                    desc = weather.get('desc', '').lower()
                    if any(keyword in desc for keyword in ['orage', 'thunderstorm', 'risque']):
                        dt_timestamp = entry.get('dt')
                        if dt_timestamp:
                            entry_datetime = datetime.fromtimestamp(dt_timestamp)
                            print(f"  {entry_datetime.strftime('%H:%M')} - {weather.get('desc')}")
                            thunderstorm_found = True
        
        if not thunderstorm_found:
            print("  Keine Gewitter-bezogenen Einträge gefunden")
        
        print()
        print("📋 Vollständige Struktur des ersten Eintrags:")
        print("-" * 40)
        if forecast.forecast and isinstance(forecast.forecast[0], dict):
            print(json.dumps(forecast.forecast[0], indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_structure() 