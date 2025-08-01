#!/usr/bin/env python3

import json
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def main():
    # Load config
    with open("config.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)
    
    # Initialize refactor
    refactor = MorningEveningRefactor(config)
    
    # Fetch weather data
    target_date = date(2025, 8, 2)
    weather_data = refactor.fetch_weather_data("Test", target_date)
    
    print("🔍 DEBUG: Gust Keys Analysis")
    print("=" * 50)
    
    # Check hourly_data structure
    hourly_data = weather_data.get('hourly_data', [])
    print(f"Found {len(hourly_data)} geo points")
    
    # Check each geo point
    for i, geo_data in enumerate(hourly_data):
        print(f"\n📍 G{i+1}:")
        
        if 'data' not in geo_data:
            print("  ❌ No 'data' key found")
            continue
        
        hour_data_list = geo_data['data']
        print(f"  Found {len(hour_data_list)} hourly entries")
        
        # Check first few entries for gust-related keys
        for j, hour_data in enumerate(hour_data_list[:3]):  # Check first 3 entries
            print(f"  Hour {j}:")
            
            # List all keys in hour_data
            all_keys = list(hour_data.keys())
            print(f"    All keys: {all_keys}")
            
            # Look for gust-related keys
            gust_keys = [key for key in all_keys if 'gust' in key.lower() or 'wind' in key.lower()]
            if gust_keys:
                print(f"    Gust-related keys: {gust_keys}")
                
                # Check values for gust-related keys
                for key in gust_keys:
                    value = hour_data.get(key)
                    print(f"    {key}: {value}")
            
            # Check if there's a 'wind' object
            if 'wind' in hour_data:
                wind_obj = hour_data['wind']
                print(f"    wind object: {wind_obj}")
                if isinstance(wind_obj, dict):
                    wind_keys = list(wind_obj.keys())
                    print(f"    wind keys: {wind_keys}")
                    
                    # Check for gust in wind object
                    gust_in_wind = [key for key in wind_keys if 'gust' in key.lower()]
                    if gust_in_wind:
                        print(f"    gust in wind: {gust_in_wind}")
                        for key in gust_in_wind:
                            value = wind_obj.get(key)
                            print(f"    wind.{key}: {value}")

if __name__ == "__main__":
    main() 