#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml
import json

def debug_wind_api():
    """Debug the raw API data structure for wind"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    
    print(f"🔍 Debugging Wind API Data for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Fetch weather data directly
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    print("📊 Weather Data Structure:")
    print(f"Keys: {list(weather_data.keys())}")
    
    hourly_data = weather_data.get('hourly_data', [])
    print(f"Hourly data count: {len(hourly_data)}")
    
    if hourly_data:
        print("\n🔍 First hourly data point:")
        first_point = hourly_data[0]
        print(f"Keys: {list(first_point.keys())}")
        
        if 'data' in first_point:
            print(f"Data count: {len(first_point['data'])}")
            
            if first_point['data']:
                print("\n📊 First hour data:")
                first_hour = first_point['data'][0]
                print(f"Keys: {list(first_hour.keys())}")
                print(f"Raw data: {json.dumps(first_hour, indent=2, default=str)}")
                
                # Test wind extractor
                wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
                wind_value = wind_extractor(first_hour)
                print(f"\n💨 Wind extractor result: {wind_value}")
                
                # Test alternative extractors
                print(f"h.get('wind'): {first_hour.get('wind')}")
                print(f"h.get('wind_speed'): {first_hour.get('wind_speed')}")
                wind_speed = first_hour.get('wind', {}).get('speed')
                print(f"h.get('wind', {{}}).get('speed'): {wind_speed}")
                wind_gust = first_hour.get('wind', {}).get('gust')
                print(f"h.get('wind', {{}}).get('gust'): {wind_gust}")
                
                # Check all keys that might contain wind data
                wind_keys = [k for k in first_hour.keys() if 'wind' in k.lower()]
                print(f"\n🔍 All keys containing 'wind': {wind_keys}")
                
                for key in wind_keys:
                    print(f"  {key}: {first_hour[key]}")

if __name__ == "__main__":
    debug_wind_api() 