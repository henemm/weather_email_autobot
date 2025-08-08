#!/usr/bin/env python3
"""
Debug-Script um die Wind-Werte für morgen zu prüfen.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
import yaml

def get_stage_coordinates_direct(stage_name: str) -> list:
    """Get stage coordinates directly from etappen.json."""
    try:
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
        
        for etappe in etappen_data:
            if etappe.get("name") == stage_name:
                coordinates = []
                for point in etappe.get("punkte", []):
                    lat = point.get("lat")
                    lon = point.get("lon")
                    if lat is not None and lon is not None:
                        coordinates.append((lat, lon))
                return coordinates
        
        return []
    except Exception as e:
        print(f"Error reading coordinates: {e}")
        return []

def debug_wind_tomorrow():
    """Debug Wind-Werte für morgen."""
    
    # Test parameters
    stage_name = "FONT-ROMEU-ODEILLO-VIA"
    tomorrow_date = date(2025, 8, 9)  # Tomorrow
    
    print("🔍 DEBUGGING WIND VALUES FOR TOMORROW")
    print("=" * 50)
    print(f"Stage: {stage_name}")
    print(f"Tomorrow: {tomorrow_date}")
    print()
    
    # Get coordinates directly
    coordinates = get_stage_coordinates_direct(stage_name)
    print(f"📍 Found {len(coordinates)} coordinates: {coordinates}")
    print()
    
    try:
        # Fetch weather data using direct MeteoFrance API
        from meteofrance_api import MeteoFranceClient
        
        client = MeteoFranceClient()
        
        for i, (lat, lon) in enumerate(coordinates):
            print(f"📍 Coordinate {i+1}: {lat}, {lon}")
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'forecast') and forecast.forecast:
                print(f"  ✅ Got {len(forecast.forecast)} entries")
                
                # Find entries for tomorrow
                tomorrow_entries = []
                for entry in forecast.forecast:
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        entry_date = entry_time.date()
                        
                        if entry_date == tomorrow_date:
                            # Only 4:00 - 19:00 Uhr
                            hour = entry_time.hour
                            if 4 <= hour <= 19:
                                wind_data = entry.get('wind', {})
                                wind_speed_ms = wind_data.get('speed', 0)
                                wind_gust_ms = wind_data.get('gust', 0)
                                wind_speed_kmh = wind_speed_ms * 3.6
                                wind_gust_kmh = wind_gust_ms * 3.6
                                
                                tomorrow_entries.append({
                                    'time': entry_time,
                                    'hour': hour,
                                    'wind_speed_ms': wind_speed_ms,
                                    'wind_gust_ms': wind_gust_ms,
                                    'wind_speed_kmh': wind_speed_kmh,
                                    'wind_gust_kmh': wind_gust_kmh
                                })
                
                print(f"  📊 Found {len(tomorrow_entries)} entries for tomorrow (4:00-19:00)")
                
                if tomorrow_entries:
                    print("  📋 Wind values for tomorrow:")
                    for entry in tomorrow_entries:
                        print(f"    {entry['hour']:02d}:00 - Wind: {entry['wind_speed_kmh']:.1f} km/h, Gust: {entry['wind_gust_kmh']:.1f} km/h")
                    
                    # Find max values
                    max_wind = max(entry['wind_speed_kmh'] for entry in tomorrow_entries)
                    max_gust = max(entry['wind_gust_kmh'] for entry in tomorrow_entries)
                    
                    print(f"  🏆 Max wind: {max_wind:.1f} km/h, Max gust: {max_gust:.1f} km/h")
                    
                    # Check thresholds
                    wind_threshold = 20.0
                    gust_threshold = 5.0
                    
                    if max_wind >= wind_threshold:
                        print(f"  ✅ Wind threshold ({wind_threshold} km/h) reached!")
                    else:
                        print(f"  ❌ Wind threshold ({wind_threshold} km/h) not reached")
                    
                    if max_gust >= gust_threshold:
                        print(f"  ✅ Gust threshold ({gust_threshold} km/h) reached!")
                    else:
                        print(f"  ❌ Gust threshold ({gust_threshold} km/h) not reached")
                else:
                    print("  ❌ No entries found for tomorrow")
                
                print()
            else:
                print(f"  ❌ No forecast data")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_wind_tomorrow()
