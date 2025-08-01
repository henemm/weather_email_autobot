#!/usr/bin/env python3
"""
Debug script to identify API access errors causing 0 gust values.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🔍 DEBUG: CHECKING daily_forecast - THE MISSING PIECE!")
    print("=" * 60)
    
    # Test coordinates: Nantes (44000)
    nantes_lat, nantes_lon = 47.2184, -1.5536  # Nantes coordinates
    
    print(f"📍 Testing Nantes coordinates: {nantes_lat}, {nantes_lon}")
    print("🎯 Found daily_forecast - this might contain the 40 km/h gust!")
    print()
    
    try:
        client = MeteoFranceClient()
        
        # Get forecast for Nantes
        forecast = client.get_forecast(nantes_lat, nantes_lon)
        
        # Method 1: Check daily_forecast structure
        print("🔍 METHOD 1: Check daily_forecast Structure")
        print("-" * 40)
        
        if hasattr(forecast, 'daily_forecast'):
            daily_data = forecast.daily_forecast
            print(f"📅 Daily forecast type: {type(daily_data)}")
            print(f"📅 Daily forecast length: {len(daily_data)}")
            
            if daily_data:
                print(f"📅 First daily entry: {daily_data[0]}")
                print(f"📅 First daily entry keys: {list(daily_data[0].keys())}")
        
        print("\n" + "=" * 60)
        
        # Method 2: Check ALL daily entries for 2025-08-05
        print("🔍 METHOD 2: Check ALL Daily Entries for 2025-08-05")
        print("-" * 40)
        
        target_date = date(2025, 8, 5)
        
        if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
            print(f"📅 ALL daily entries for {target_date}:")
            
            for i, entry in enumerate(forecast.daily_forecast):
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    print(f"\n📅 Daily Entry {i} - {entry_date}:")
                    print(f"   COMPLETE ENTRY: {json.dumps(entry, indent=2)}")
                    
                    # Check EVERY field for wind-related data
                    for key, value in entry.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'wind' in subkey.lower() or 'gust' in subkey.lower():
                                    print(f"   {key}.{subkey}: {subvalue}")
                        elif 'wind' in key.lower() or 'gust' in key.lower():
                            print(f"   {key}: {value}")
                    
                    # Check if this is our target date
                    if entry_date == target_date:
                        print(f"   🎯 TARGET DATE FOUND!")
        
        print("\n" + "=" * 60)
        
        # Method 3: Check if daily_forecast has wind data
        print("🔍 METHOD 3: Check if daily_forecast has Wind Data")
        print("-" * 40)
        
        if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
            print("📅 Checking all daily entries for wind data:")
            
            for i, entry in enumerate(forecast.daily_forecast):
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    print(f"\n📅 {entry_date}:")
                    
                    # Look for ANY wind-related fields
                    wind_found = False
                    for key, value in entry.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'wind' in subkey.lower() or 'gust' in subkey.lower():
                                    print(f"   {key}.{subkey}: {subvalue}")
                                    wind_found = True
                        elif 'wind' in key.lower() or 'gust' in key.lower():
                            print(f"   {key}: {value}")
                            wind_found = True
                    
                    if not wind_found:
                        print(f"   ❌ No wind data found")
        
        print("\n" + "=" * 60)
        
        # Method 4: Compare hourly vs daily for 2025-08-05
        print("🔍 METHOD 4: Compare Hourly vs Daily for 2025-08-05")
        print("-" * 40)
        
        target_date = date(2025, 8, 5)
        
        print("📅 HOURLY forecast for 2025-08-05:")
        if hasattr(forecast, 'forecast') and forecast.forecast:
            max_hourly_gust = 0
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    if entry_time.date() == target_date:
                        wind_data = entry.get('wind', {})
                        gust = wind_data.get('gust', 0)
                        if gust > max_hourly_gust:
                            max_hourly_gust = gust
            print(f"   Max hourly gust: {max_hourly_gust} km/h")
        
        print("📅 DAILY forecast for 2025-08-05:")
        if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
            for entry in forecast.daily_forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    if entry_time.date() == target_date:
                        print(f"   Daily entry: {entry}")
                        # Check for wind data in daily entry
                        for key, value in entry.items():
                            if isinstance(value, dict):
                                for subkey, subvalue in value.items():
                                    if 'wind' in subkey.lower() or 'gust' in subkey.lower():
                                        print(f"     {key}.{subkey}: {subvalue}")
        
        print("\n" + "=" * 60)
        print("🔍 SUMMARY:")
        print("Checking if daily_forecast contains the 40 km/h gust data!")
        print()
        print("If daily_forecast has wind data:")
        print("- I need to use daily_forecast for wind/gust")
        print("- The hourly forecast is incomplete")
        print()
        print("If daily_forecast has no wind data:")
        print("- I need to look elsewhere")
        print("- The API might not provide detailed wind data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 