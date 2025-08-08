#!/usr/bin/env python3
"""
Debug script to understand the actual data structure.
A senior developer would analyze the data first before making changes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml
import json

def debug_data_structure():
    """Analyze the actual data structure to understand what we're working with."""
    
    print("🔍 SENIOR DEVELOPER: DATENSTRUKTUR ANALYSE")
    print("=" * 60)
    
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize refactor
    refactor = MorningEveningRefactor(config)
    
    # Test date
    test_date = "2025-08-03"
    stage_name = "Test"
    
    print(f"📅 Test Date: {test_date}")
    print(f"📍 Stage: {stage_name}")
    print()
    
    # Fetch weather data
    print("📊 FETCHING WEATHER DATA:")
    print("-" * 30)
    try:
        weather_data = refactor.fetch_weather_data(stage_name, test_date)
        
        print("✅ Weather data fetched successfully")
        print(f"📋 Keys: {list(weather_data.keys())}")
        print()
        
        # Analyze daily_forecast structure
        print("📋 DAILY_FORECAST STRUCTURE:")
        print("-" * 30)
        daily_forecast = weather_data.get('daily_forecast', {})
        print(f"Type: {type(daily_forecast)}")
        print(f"Keys: {list(daily_forecast.keys())}")
        
        if isinstance(daily_forecast, dict):
            print("\n📊 Daily forecast dict content:")
            for key, value in daily_forecast.items():
                print(f"Key: {key}")
                print(f"Type: {type(value)}")
                if isinstance(value, list):
                    print(f"Length: {len(value)}")
                    if len(value) > 0:
                        print(f"First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'N/A'}")
                elif isinstance(value, dict):
                    print(f"Keys: {list(value.keys())}")
                print()
        
        print()
        
        # Analyze hourly_data structure
        print("📋 HOURLY_DATA STRUCTURE:")
        print("-" * 30)
        hourly_data = weather_data.get('hourly_data', [])
        print(f"Type: {type(hourly_data)}")
        print(f"Length: {len(hourly_data)}")
        
        if isinstance(hourly_data, list) and len(hourly_data) > 0:
            print("\n📊 First hourly_data entry:")
            first_entry = hourly_data[0]
            print(f"Keys: {list(first_entry.keys())}")
            
            if 'data' in first_entry:
                hour_data = first_entry['data']
                print(f"Hour data type: {type(hour_data)}")
                print(f"Hour data length: {len(hour_data)}")
                
                if len(hour_data) > 0:
                    print("\n📊 First hour entry:")
                    first_hour = hour_data[0]
                    print(f"Keys: {list(first_hour.keys())}")
                    print(f"Sample data: {json.dumps(first_hour, indent=2, default=str)}")
        
        print()
        
        # Test the original working approach
        print("🧪 TESTING ORIGINAL WORKING APPROACH:")
        print("-" * 40)
        
        # Try to extract night data manually
        if isinstance(daily_forecast, dict) and 'daily' in daily_forecast:
            daily_data = daily_forecast['daily']
            print(f"Daily data type: {type(daily_data)}")
            print(f"Daily data length: {len(daily_data)}")
            
            if len(daily_data) > 0:
                print("\n📊 First daily entry:")
                first_daily = daily_data[0]
                print(f"Keys: {list(first_daily.keys())}")
                print(f"Sample data: {json.dumps(first_daily, indent=2, default=str)}")
                
                # Find today's data
                target_date_str = test_date
                found_today = False
                for i, day_data in enumerate(daily_data):
                    entry_dt = day_data.get('dt')
                    if entry_dt:
                        from datetime import datetime
                        entry_date = datetime.fromtimestamp(entry_dt).date()
                        entry_date_str = entry_date.strftime('%Y-%m-%d')
                        
                        print(f"Entry {i}: {entry_date_str} - T: {day_data.get('T', {})}")
                        
                        if entry_date_str == target_date_str:
                            found_today = True
                            temp_min = day_data.get('T', {}).get('min')
                            temp_max = day_data.get('T', {}).get('max')
                            temp_value = day_data.get('T', {}).get('value')
                            print(f"✅ Found today's data:")
                            print(f"   temp_min: {temp_min}")
                            print(f"   temp_max: {temp_max}")
                            print(f"   temp_value: {temp_value}")
                            break
                
                if not found_today:
                    print("❌ No matching date found in daily data")
                
                # Check next few entries for temp_min values
                print("\n📊 Checking next 5 entries for temp_min:")
                for i in range(min(5, len(daily_data))):
                    day_data = daily_data[i]
                    entry_dt = day_data.get('dt')
                    if entry_dt:
                        from datetime import datetime
                        entry_date = datetime.fromtimestamp(entry_dt).date()
                        entry_date_str = entry_date.strftime('%Y-%m-%d')
                        temp_min = day_data.get('T', {}).get('min')
                        temp_max = day_data.get('T', {}).get('max')
                        print(f"Entry {i}: {entry_date_str} - min: {temp_min}, max: {temp_max}")
            else:
                print("❌ No daily data available")
        else:
            print("❌ No daily data in daily_forecast")
        
    except Exception as e:
        print(f"❌ Data analysis failed: {e}")
    
    print()
    print("🎯 ANALYSIS COMPLETED!")

if __name__ == "__main__":
    debug_data_structure() 