#!/usr/bin/env python3
"""
Debug script to check thunderstorm data for Belfort and Metz.
Both show thunderstorms for tomorrow on Météo-France website.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌩️ DEBUG: Thunderstorm Data for Belfort and Metz")
    print("=" * 60)
    
    # Test coordinates
    belfort_lat, belfort_lon = 47.6386, 6.8631  # Belfort
    metz_lat, metz_lon = 49.1193, 6.1757  # Metz
    
    print(f"📍 Belfort: {belfort_lat}, {belfort_lon}")
    print(f"📍 Metz: {metz_lat}, {metz_lon}")
    print()
    
    try:
        client = MeteoFranceClient()
        
        # Test both locations
        locations = [
            ("Belfort", belfort_lat, belfort_lon),
            ("Metz", metz_lat, metz_lon)
        ]
        
        for location_name, lat, lon in locations:
            print(f"🔍 Testing {location_name}...")
            print("-" * 40)
            
            # Get forecast
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'forecast') and forecast.forecast:
                print(f"📅 Total forecast entries: {len(forecast.forecast)}")
                
                # Focus on tomorrow (2025-08-02)
                tomorrow = date.today() + timedelta(days=1)
                print(f"📅 Analyzing data for: {tomorrow}")
                print()
                
                print("📊 Hourly data for tomorrow:")
                print("Time | Weather Condition | Description")
                print("-" * 50)
                
                thunderstorm_found = False
                
                for entry in forecast.forecast:
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        entry_date = entry_time.date()
                        
                        if entry_date == tomorrow:
                            time_str = entry_time.strftime('%H:%M')
                            weather_data = entry.get('weather', {})
                            condition = weather_data.get('desc', 'Unknown')
                            
                            print(f"{time_str} | {condition}")
                            
                            # Check for thunderstorm conditions
                            thunderstorm_keywords = ['orage', 'orageuse', 'orageux', 'thunderstorm']
                            if any(keyword in condition.lower() for keyword in thunderstorm_keywords):
                                thunderstorm_found = True
                                print(f"   ⚡ THUNDERSTORM DETECTED: {condition}")
                
                print("-" * 50)
                if thunderstorm_found:
                    print(f"✅ Thunderstorms found for {location_name}!")
                else:
                    print(f"❌ No thunderstorms found for {location_name}")
                
                # Check raw data structure
                print(f"\n🔍 Raw data structure for {location_name}:")
                if forecast.forecast:
                    first_entry = forecast.forecast[0]
                    print(f"First entry keys: {list(first_entry.keys())}")
                    
                    if 'weather' in first_entry:
                        weather_data = first_entry['weather']
                        print(f"Weather data: {weather_data}")
                
                print("\n" + "=" * 60)
        
        print("🎯 SUMMARY:")
        print("If no thunderstorms found in API but website shows them:")
        print("1. API might use different field names")
        print("2. API might use different data source")
        print("3. Website might use different forecast model")
        print("4. I need to check other API methods")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 