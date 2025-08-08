#!/usr/bin/env python3
"""
Debug script to find the correct API method for rain probability data.
I previously said the API provides this information, so I must find the right method.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌧️ DEBUG: Finding Correct API Method for Rain Probability")
    print("=" * 60)
    print("I previously said the API provides rain probability data")
    print()
    
    try:
        client = MeteoFranceClient()
        lat, lon = 47.6386, 6.8631
        
        print(f"📍 Coordinates: {lat}, {lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Test get_rain method more thoroughly
        print("🔍 Testing get_rain method thoroughly:")
        print("-" * 40)
        
        try:
            rain_data = client.get_rain(lat, lon)
            print(f"✅ Rain data type: {type(rain_data)}")
            
            if hasattr(rain_data, 'raw_data'):
                print(f"📊 Raw data available")
                raw_data = rain_data.raw_data
                print(f"🔍 Raw data: {raw_data}")
                
                # Check if raw_data contains probability information
                if isinstance(raw_data, dict):
                    for key, value in raw_data.items():
                        print(f"   Key: {key}, Value: {value}")
                        
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'prob' in subkey.lower() or 'rain' in subkey.lower():
                                    print(f"   Found {key}.{subkey}: {subvalue}")
            
            if hasattr(rain_data, 'forecast') and rain_data.forecast:
                print(f"📅 Forecast entries: {len(rain_data.forecast)}")
                
                # Check first entry
                first_entry = rain_data.forecast[0]
                print(f"🔍 First entry: {first_entry}")
                print(f"🔍 First entry keys: {list(first_entry.keys())}")
                
                # Check for rain_3h or probability fields
                rain_3h = first_entry.get('rain_3h', 'N/A')
                rain_prob = first_entry.get('rain_probability', 'N/A')
                probability = first_entry.get('probability', 'N/A')
                
                print(f"💧 rain_3h: {rain_3h}")
                print(f"💧 rain_probability: {rain_prob}")
                print(f"💧 probability: {probability}")
                
                # Check all entries for tomorrow
                tomorrow = date.today() + timedelta(days=1)
                tomorrow_entries = []
                
                for entry in rain_data.forecast:
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        entry_date = entry_time.date()
                        if entry_date == tomorrow:
                            tomorrow_entries.append(entry)
                
                print(f"📅 Tomorrow entries: {len(tomorrow_entries)}")
                
                if tomorrow_entries:
                    print("\n🌧️ Rain data for tomorrow:")
                    print("Time | Rain | Rain_3h | Probability | All Fields")
                    print("-" * 70)
                    
                    for entry in tomorrow_entries[:5]:  # First 5 entries
                        time = datetime.fromtimestamp(entry['dt'])
                        time_str = time.strftime('%H:%M')
                        
                        rain = entry.get('rain', 'N/A')
                        rain_3h = entry.get('rain_3h', 'N/A')
                        probability = entry.get('probability', 'N/A')
                        
                        print(f"{time_str} | {rain} | {rain_3h} | {probability} | {entry}")
                
        except Exception as e:
            print(f"❌ Error with get_rain: {e}")
        
        # Test get_forecast method more thoroughly
        print("\n🔍 Testing get_forecast method thoroughly:")
        print("-" * 40)
        
        try:
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'raw_data'):
                print(f"📊 Raw data available")
                raw_data = forecast.raw_data
                
                # Check if raw_data contains probability information
                if isinstance(raw_data, dict):
                    for key, value in raw_data.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'prob' in subkey.lower() or 'rain' in subkey.lower():
                                    print(f"Found {key}.{subkey}: {subvalue}")
            
            if hasattr(forecast, 'forecast') and forecast.forecast:
                # Check first entry for any probability fields
                first_entry = forecast.forecast[0]
                
                # Look for any fields that might contain probability
                for key, value in first_entry.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if 'prob' in subkey.lower():
                                print(f"Found probability field: {key}.{subkey}: {subvalue}")
                
        except Exception as e:
            print(f"❌ Error with get_forecast: {e}")
        
        print("\n🎯 CONCLUSION:")
        print("If I previously said the API provides rain probability data:")
        print("1. I must have found it in a different method")
        print("2. I must have found it in a different field name")
        print("3. I must have found it in raw_data")
        print("4. I must have been wrong about the field name")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 