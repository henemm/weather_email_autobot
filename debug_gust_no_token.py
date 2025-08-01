#!/usr/bin/env python3
"""
Debug script to test meteofrance-api without API token.
The user says the Python API doesn't need an API token.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌪️ DEBUG: MeteoFrance API without Token")
    print("=" * 50)
    print("Testing meteofrance-api without API token")
    print()
    
    try:
        client = MeteoFranceClient()
        belfort_lat, belfort_lon = 47.6386, 6.8631
        
        print(f"📍 Belfort coordinates: {belfort_lat}, {belfort_lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Test get_forecast without any token
        print("🔍 Testing get_forecast without token:")
        print("-" * 40)
        
        forecast = client.get_forecast(belfort_lat, belfort_lon)
        
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print(f"✅ Got forecast data: {len(forecast.forecast)} entries")
            
            # Check tomorrow's data
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_entries = []
            
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    if entry_date == tomorrow:
                        tomorrow_entries.append(entry)
            
            print(f"📅 Tomorrow entries: {len(tomorrow_entries)}")
            
            if tomorrow_entries:
                print("\n🌪️ Wind data for tomorrow:")
                print("Time | Wind Speed | Gust | Direction")
                print("-" * 40)
                
                gust_found = False
                for entry in tomorrow_entries:
                    time = datetime.fromtimestamp(entry['dt'])
                    wind_data = entry.get('wind', {})
                    wind_speed = wind_data.get('speed', 0)
                    gust = wind_data.get('gust', 0)
                    direction = wind_data.get('direction', 0)
                    
                    print(f"{time.strftime('%H:%M')} | {wind_speed} km/h | {gust} km/h | {direction}°")
                    
                    if gust > 0:
                        gust_found = True
                
                print("-" * 40)
                if gust_found:
                    print("✅ Found non-zero gust values!")
                else:
                    print("❌ All gust values are 0")
                
                # Check if there are other wind-related fields
                print("\n🔍 Checking for other wind-related fields:")
                first_entry = tomorrow_entries[0]
                print(f"All keys: {list(first_entry.keys())}")
                
                if 'wind' in first_entry:
                    wind_data = first_entry['wind']
                    print(f"Wind keys: {list(wind_data.keys())}")
                    
                    # Check for any non-zero values
                    for key, value in wind_data.items():
                        if value != 0:
                            print(f"Non-zero wind.{key}: {value}")
                
                # Check if gust data might be in a different field
                print("\n🔍 Checking for gust data in other fields:")
                for key, value in first_entry.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if 'gust' in subkey.lower():
                                print(f"Found {key}.{subkey}: {subvalue}")
                
                # Check if gust data might be calculated
                print("\n🔍 Checking if gust can be calculated:")
                wind_data = first_entry.get('wind', {})
                wind_speed = wind_data.get('speed', 0)
                
                if wind_speed > 0:
                    print(f"Wind speed: {wind_speed} km/h")
                    print("Possible gust calculations:")
                    print(f"  Wind speed * 1.5 = {wind_speed * 1.5}")
                    print(f"  Wind speed * 2.0 = {wind_speed * 2.0}")
                    print(f"  Wind speed * 2.5 = {wind_speed * 2.5}")
                    print(f"  Wind speed * 3.0 = {wind_speed * 3.0}")
            else:
                print("❌ No tomorrow entries found")
        else:
            print("❌ No forecast data available")
        
        print("\n🎯 CONCLUSION:")
        print("The meteofrance-api library works without API token.")
        print("If all gust values are 0:")
        print("1. The API might not provide gust data for this location")
        print("2. Gust data might be in a different field")
        print("3. Gust data might need to be calculated")
        print("4. The user might be referring to a different data source")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 