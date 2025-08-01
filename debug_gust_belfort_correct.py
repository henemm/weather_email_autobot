#!/usr/bin/env python3
"""
Debug script to find the correct API method and field names for Belfort gust data.
User expects 55 km/h gusts, so I must be using wrong API method or field names.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌪️ DEBUG: Correct Gust Data for Belfort (Expected: 55 km/h)")
    print("=" * 60)
    
    try:
        client = MeteoFranceClient()
        belfort_lat, belfort_lon = 47.6386, 6.8631
        
        print(f"📍 Belfort coordinates: {belfort_lat}, {belfort_lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Test ALL possible API methods
        print("🔍 Testing ALL possible API methods:")
        print("-" * 50)
        
        # 1. get_forecast
        print("1. get_forecast:")
        forecast = client.get_forecast(belfort_lat, belfort_lon)
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print(f"   ✅ Has forecast data: {len(forecast.forecast)} entries")
            
            # Check tomorrow's data
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_entries = []
            
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    if entry_date == tomorrow:
                        tomorrow_entries.append(entry)
            
            print(f"   📅 Tomorrow entries: {len(tomorrow_entries)}")
            
            if tomorrow_entries:
                first_tomorrow = tomorrow_entries[0]
                print(f"   🔍 First tomorrow entry structure:")
                print(f"      Keys: {list(first_tomorrow.keys())}")
                
                if 'wind' in first_tomorrow:
                    wind_data = first_tomorrow['wind']
                    print(f"      Wind data: {wind_data}")
                    print(f"      Wind keys: {list(wind_data.keys())}")
                    
                    # Check for any non-zero gust values
                    gust_values = []
                    for entry in tomorrow_entries:
                        wind = entry.get('wind', {})
                        gust = wind.get('gust', 0)
                        if gust > 0:
                            time = datetime.fromtimestamp(entry['dt'])
                            gust_values.append(f"{time.strftime('%H:%M')}: {gust} km/h")
                    
                    if gust_values:
                        print(f"      ✅ Found non-zero gusts: {gust_values}")
                    else:
                        print(f"      ❌ All gusts are 0")
        
        # 2. Check if there are other API methods
        print("\n2. Available API methods:")
        methods = [method for method in dir(client) if not method.startswith('_')]
        print(f"   Available methods: {methods}")
        
        # 3. Try get_rain method (might have wind data)
        print("\n3. Testing get_rain method:")
        try:
            rain_data = client.get_rain(belfort_lat, belfort_lon)
            print(f"   Rain data type: {type(rain_data)}")
            if hasattr(rain_data, '__dict__'):
                print(f"   Rain data attributes: {list(rain_data.__dict__.keys())}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 4. Try get_warning_full method
        print("\n4. Testing get_warning_full method:")
        try:
            warnings = client.get_warning_full(belfort_lat, belfort_lon)
            print(f"   Warnings data type: {type(warnings)}")
            if hasattr(warnings, '__dict__'):
                print(f"   Warnings attributes: {list(warnings.__dict__.keys())}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 5. Check if gust data is in a different field
        print("\n5. Checking for gust data in different fields:")
        if hasattr(forecast, 'forecast') and forecast.forecast:
            first_entry = forecast.forecast[0]
            
            # Check all fields for any wind-related data
            for key, value in first_entry.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if 'gust' in subkey.lower() or 'wind' in subkey.lower():
                            print(f"   Found {key}.{subkey}: {subvalue}")
                
                # Check if the field itself contains wind data
                if 'gust' in key.lower() or 'wind' in key.lower():
                    print(f"   Found {key}: {value}")
        
        # 6. Check if gust data is calculated from other parameters
        print("\n6. Checking if gust can be calculated:")
        if hasattr(forecast, 'forecast') and forecast.forecast:
            first_entry = forecast.forecast[0]
            
            # Check wind speed and direction
            wind_data = first_entry.get('wind', {})
            wind_speed = wind_data.get('speed', 0)
            wind_direction = wind_data.get('direction', 0)
            
            print(f"   Wind speed: {wind_speed} km/h")
            print(f"   Wind direction: {wind_direction}°")
            
            # Maybe gust is wind_speed * some factor?
            if wind_speed > 0:
                print(f"   Possible gust calculations:")
                print(f"      Wind speed * 1.5 = {wind_speed * 1.5}")
                print(f"      Wind speed * 2.0 = {wind_speed * 2.0}")
                print(f"      Wind speed * 2.5 = {wind_speed * 2.5}")
        
        print("\n🎯 CONCLUSION:")
        print("Since user expects 55 km/h gusts for Belfort:")
        print("1. I must be using the wrong API method")
        print("2. I must be using the wrong field name")
        print("3. Gust data might be in a different API endpoint")
        print("4. Gust data might need to be calculated differently")
        print("5. The meteofrance-api library might be incomplete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 