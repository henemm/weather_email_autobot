#!/usr/bin/env python3
"""
Debug script to check what rain probability data is actually available from MeteoFrance API.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌧️ DEBUG: Rain Probability Data from MeteoFrance API")
    print("=" * 60)
    
    try:
        client = MeteoFranceClient()
        lat, lon = 47.6386, 6.8631
        
        print(f"📍 Coordinates: {lat}, {lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Get forecast
        forecast = client.get_forecast(lat, lon)
        
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print(f"📅 Total forecast entries: {len(forecast.forecast)}")
            
            # Focus on tomorrow
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_entries = []
            
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    if entry_date == tomorrow:
                        tomorrow_entries.append(entry)
            
            print(f"📅 Tomorrow entries: {len(tomorrow_entries)}")
            print()
            
            if tomorrow_entries:
                print("🌧️ Rain data for tomorrow (first 10 entries):")
                print("Time | Rain (1h) | Rain (probability) | All Rain Fields")
                print("-" * 80)
                
                for i, entry in enumerate(tomorrow_entries[:10]):
                    time = datetime.fromtimestamp(entry['dt'])
                    time_str = time.strftime('%H:%M')
                    
                    rain_data = entry.get('rain', {})
                    rain_1h = rain_data.get('1h', 'N/A')
                    rain_prob = rain_data.get('probability', 'N/A')
                    
                    print(f"{time_str} | {rain_1h} | {rain_prob} | {rain_data}")
                
                print("-" * 80)
                
                # Check all available fields in first entry
                first_entry = tomorrow_entries[0]
                print(f"\n🔍 All available fields in first entry:")
                print(f"Keys: {list(first_entry.keys())}")
                
                if 'rain' in first_entry:
                    rain_data = first_entry['rain']
                    print(f"Rain data: {rain_data}")
                    print(f"Rain keys: {list(rain_data.keys())}")
                    
                    # Check for any non-zero values
                    for key, value in rain_data.items():
                        if value != 0 and value != 'N/A':
                            print(f"Non-zero rain.{key}: {value}")
                
                # Check if rain probability is in a different field
                print(f"\n🔍 Checking for rain probability in other fields:")
                for key, value in first_entry.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if 'prob' in subkey.lower() or 'rain' in subkey.lower():
                                print(f"Found {key}.{subkey}: {subvalue}")
                
                # Check if rain probability is calculated differently
                print(f"\n🔍 Checking if rain probability is calculated:")
                if 'rain' in first_entry:
                    rain_data = first_entry['rain']
                    rain_1h = rain_data.get('1h', 0)
                    
                    if rain_1h > 0:
                        print(f"Rain 1h: {rain_1h} mm")
                        print("Possible probability calculations:")
                        print(f"  If rain > 0: 100%")
                        print(f"  If rain = 0: 0%")
                    else:
                        print(f"Rain 1h: {rain_1h} mm (no rain)")
                        print("Probability should be 0%")
        
        print("\n🎯 CONCLUSION:")
        print("If rain probability is always 0 in raw data but 40% in processed data:")
        print("1. The API might not provide rain probability")
        print("2. Rain probability might be calculated from rain amount")
        print("3. Rain probability might be in a different field")
        print("4. The processed data might be wrong")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 