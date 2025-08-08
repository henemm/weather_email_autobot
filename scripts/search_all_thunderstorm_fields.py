#!/usr/bin/env python3
"""
Search all possible fields for thunderstorm-related content.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteofrance_api.client import MeteoFranceClient

def search_all_thunderstorm_fields():
    """Search all possible fields for thunderstorm content."""
    
    # Test coordinates
    lat = 42.471359
    lon = 2.029742
    
    print("🔍 Suche nach allen Gewitter-bezogenen Feldern")
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
        
        # Search through all entries for any thunderstorm-related content
        thunderstorm_entries = []
        
        for i, entry in enumerate(forecast.forecast):
            if not isinstance(entry, dict):
                continue
                
            # Convert entry to string and search for keywords
            entry_str = json.dumps(entry, default=str).lower()
            if any(keyword in entry_str for keyword in ['orage', 'thunderstorm', 'risque', 'orageux']):
                dt_timestamp = entry.get('dt')
                if dt_timestamp:
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    thunderstorm_entries.append((entry_datetime, entry))
        
        print(f"📊 Gefundene Gewitter-bezogene Einträge: {len(thunderstorm_entries)}")
        print()
        
        # Show detailed analysis of thunderstorm entries
        for i, (dt, entry) in enumerate(thunderstorm_entries[:10]):  # Show first 10
            print(f"⚡ Eintrag {i+1} - {dt.strftime('%Y-%m-%d %H:%M')}:")
            
            # Check weather field
            weather = entry.get('weather', {})
            if isinstance(weather, dict):
                print(f"  Weather desc: {weather.get('desc')}")
                print(f"  Weather icon: {weather.get('icon')}")
            
            # Check all other fields for thunderstorm content
            for key, value in entry.items():
                if key == 'weather':
                    continue  # Already checked
                    
                value_str = str(value).lower()
                if any(keyword in value_str for keyword in ['orage', 'thunderstorm', 'risque']):
                    print(f"  {key}: {value}")
            
            print()
        
        # Also check if there are other API methods that might have different data
        print("🔍 Prüfung anderer API-Methoden:")
        print("-" * 30)
        
        # Try to get alerts for the same location
        try:
            alerts = client.get_alert(lat, lon)
            print(f"Alerts verfügbar: {alerts is not None}")
            if alerts:
                print(f"Alert-Daten: {alerts}")
        except Exception as e:
            print(f"Alerts nicht verfügbar: {e}")
        
        # Try to get current weather
        try:
            current = client.get_current_weather(lat, lon)
            print(f"Current weather verfügbar: {current is not None}")
            if current:
                print(f"Current weather: {current}")
        except Exception as e:
            print(f"Current weather nicht verfügbar: {e}")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_all_thunderstorm_fields() 