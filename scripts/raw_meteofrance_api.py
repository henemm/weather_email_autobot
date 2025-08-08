#!/usr/bin/env python3
"""
Raw MeteoFrance API output without any wrappers.
"""

import json
from datetime import datetime
from meteofrance_api.client import MeteoFranceClient

def get_raw_api_output():
    """Get raw output directly from MeteoFrance API."""
    
    # Test coordinates
    lat = 42.471359
    lon = 2.029742
    
    print("🔍 RAW MeteoFrance API Output")
    print("=" * 50)
    print(f"Koordinaten: {lat}, {lon}")
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        print(f"📊 Anzahl Forecast-Einträge: {len(forecast.forecast)}")
        print()
        
        # Show first 10 entries in raw format
        print("📋 Erste 10 Einträge (RAW):")
        print("-" * 40)
        
        for i, entry in enumerate(forecast.forecast[:10]):
            dt_timestamp = entry.get('dt')
            if dt_timestamp:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                print(f"\n🔍 Eintrag {i+1} - {entry_datetime.strftime('%Y-%m-%d %H:%M')}:")
                print(json.dumps(entry, indent=2, default=str))
            else:
                print(f"\n🔍 Eintrag {i+1} - Kein Timestamp:")
                print(json.dumps(entry, indent=2, default=str))
        
        # Look specifically for thunderstorm entries
        print("\n⚡ GEWITTER-EINTRÄGE (RAW):")
        print("-" * 40)
        
        thunderstorm_count = 0
        for i, entry in enumerate(forecast.forecast):
            weather = entry.get('weather', {})
            if isinstance(weather, dict):
                desc = weather.get('desc', '').lower()
                if any(keyword in desc for keyword in ['orage', 'thunderstorm', 'risque']):
                    dt_timestamp = entry.get('dt')
                    if dt_timestamp:
                        entry_datetime = datetime.fromtimestamp(dt_timestamp)
                        print(f"\n⚡ Gewitter-Eintrag {thunderstorm_count + 1} - {entry_datetime.strftime('%Y-%m-%d %H:%M')}:")
                        print(json.dumps(entry, indent=2, default=str))
                        thunderstorm_count += 1
        
        if thunderstorm_count == 0:
            print("Keine Gewitter-Einträge gefunden")
        
        # Show precipitation data specifically
        print("\n🌧️  NIEDERSCHLAGS-DATEN (RAW):")
        print("-" * 40)
        
        for i, entry in enumerate(forecast.forecast[:10]):
            dt_timestamp = entry.get('dt')
            if dt_timestamp:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                rain_data = entry.get('rain', {})
                snow_data = entry.get('snow', {})
                
                print(f"\n🌧️  Eintrag {i+1} - {entry_datetime.strftime('%Y-%m-%d %H:%M')}:")
                print(f"  Rain: {rain_data}")
                print(f"  Snow: {snow_data}")
                print(f"  Weather: {entry.get('weather')}")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_raw_api_output() 