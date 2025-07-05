#!/usr/bin/env python3
"""
Script to find the correct API entries for the stage time (14-17 Uhr).
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meteofrance_api.client import MeteoFranceClient


def find_etappe_times():
    """Find the correct API entries for the stage time (14-17 Uhr)."""
    
    print("🔍 FINDING ETAPPE TIMES (14-17 Uhr)")
    print("=" * 50)
    
    # Test coordinates (Asco)
    latitude = 42.4542
    longitude = 8.7389
    
    print(f"Testing coordinates: {latitude}, {longitude}")
    print()
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(latitude, longitude)
        
        print("✅ API call successful!")
        print(f"Number of forecast entries: {len(forecast.forecast)}")
        print()
        
        # Find entries for 14-17 Uhr (stage time)
        etappe_entries = []
        
        for i, entry in enumerate(forecast.forecast):
            dt_timestamp = entry.get('dt')
            if dt_timestamp:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                hour = entry_datetime.hour
                
                # Check if this is for the stage time (14-17 Uhr)
                if 14 <= hour <= 17:
                    etappe_entries.append({
                        'index': i,
                        'datetime': entry_datetime,
                        'entry': entry
                    })
        
        print(f"📅 Found {len(etappe_entries)} entries for stage time (14-17 Uhr):")
        print()
        
        for etappe_entry in etappe_entries:
            i = etappe_entry['index']
            dt = etappe_entry['datetime']
            entry = etappe_entry['entry']
            
            print(f"🕐 ENTRY {i+1} - {dt.strftime('%Y-%m-%d %H:%M')} (Hour {dt.hour}):")
            print("-" * 50)
            
            # Show weather condition
            weather = entry.get('weather', {})
            weather_desc = weather.get('desc', 'Unknown') if isinstance(weather, dict) else str(weather)
            print(f"🌤️ Weather: {weather_desc}")
            
            # Show temperature
            temp_data = entry.get('T', {})
            if isinstance(temp_data, dict):
                temp_value = temp_data.get('value', 'N/A')
                print(f"🌡️ Temperature: {temp_value}°C")
            
            # Show wind
            wind_data = entry.get('wind', {})
            if isinstance(wind_data, dict):
                wind_speed = wind_data.get('speed', 'N/A')
                wind_gust = wind_data.get('gust', 'N/A')
                print(f"💨 Wind: {wind_speed}km/h, Gusts: {wind_gust}km/h")
            
            # Show rain
            rain_data = entry.get('rain', {})
            if isinstance(rain_data, dict):
                rain_1h = rain_data.get('1h', 'N/A')
                print(f"🌧️ Rain (1h): {rain_1h}mm")
            
            # Show all fields for debugging
            print("📋 ALL FIELDS:")
            for key, value in entry.items():
                print(f"  {key}: {value}")
            
            print()
            print("=" * 50)
            print()
        
        # Save etappe entries to file
        output_file = "output/debug/etappe_times_data.json"
        Path("output/debug").mkdir(parents=True, exist_ok=True)
        
        etappe_data = []
        for etappe_entry in etappe_entries:
            etappe_data.append({
                'index': etappe_entry['index'],
                'datetime': etappe_entry['datetime'].isoformat(),
                'entry': etappe_entry['entry']
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(etappe_data, f, indent=2, default=str)
        
        print(f"💾 Etappe time data saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    find_etappe_times() 