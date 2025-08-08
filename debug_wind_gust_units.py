#!/usr/bin/env python3
"""
Debug script to check wind and gust units from API data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def main():
    print("🔍 WIND/GUST EINHEITEN ANALYSE")
    print("=" * 50)
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize refactor
    refactor = MorningEveningRefactor(config)
    
    # Test stage and date
    stage_name = "Test"
    target_date = date(2025, 8, 3)
    
    print(f"📅 Test Date: {target_date}")
    print(f"📍 Stage: {stage_name}")
    print()
    
    # Fetch weather data
    print("🌤️ Fetching weather data...")
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("❌ No weather data available")
        return
    
    print("✅ Weather data fetched successfully")
    print()
    
    # Analyze hourly data for wind and gust
    print("🌬️ ANALYZING WIND/GUST DATA:")
    print("-" * 30)
    
    hourly_data = weather_data.get('hourly_data', [])
    
    for geo_index, geo_data in enumerate(hourly_data):
        if not geo_data or 'data' not in geo_data:
            continue
            
        print(f"\n📍 GEO Point {geo_index + 1}:")
        
        # Get first few hours with wind data
        wind_samples = []
        gust_samples = []
        
        for hour_data in geo_data['data']:
            if not hour_data or 'dt' not in hour_data:
                continue
                
            hour_time = datetime.fromtimestamp(hour_data['dt'])
            hour_date = hour_time.date()
            
            # Only process data for the target date
            if hour_date != target_date:
                continue
            
            # Apply time filter: only 4:00 - 19:00 Uhr
            hour = hour_time.hour
            if hour < 4 or hour > 19:
                continue
            
            # Extract wind data
            wind_speed = None
            wind_gust = None
            
            if 'wind' in hour_data:
                wind_data = hour_data['wind']
                wind_speed = wind_data.get('speed')
                wind_gust = wind_data.get('gust')
            
            if wind_speed is not None:
                wind_samples.append({
                    'time': hour_time.strftime('%H:%M'),
                    'wind_speed': wind_speed,
                    'raw_data': hour_data.get('wind', {})
                })
            
            if wind_gust is not None:
                gust_samples.append({
                    'time': hour_time.strftime('%H:%M'),
                    'wind_gust': wind_gust,
                    'raw_data': hour_data.get('wind', {})
                })
            
            # Show first 5 samples
            if len(wind_samples) >= 5 and len(gust_samples) >= 5:
                break
        
        print(f"  Wind Speed Samples:")
        for sample in wind_samples[:5]:
            print(f"    {sample['time']}: {sample['wind_speed']} (raw: {sample['raw_data']})")
        
        print(f"  Wind Gust Samples:")
        for sample in gust_samples[:5]:
            print(f"    {sample['time']}: {sample['wind_gust']} (raw: {sample['raw_data']})")
    
    # Also check the raw weather data structure
    print("\n🔍 RAW WEATHER DATA STRUCTURE:")
    print("-" * 30)
    
    if hourly_data:
        first_geo = hourly_data[0]
        if first_geo and 'data' in first_geo:
            first_hour = first_geo['data'][0] if first_geo['data'] else None
            if first_hour:
                print("First hour data structure:")
                print(f"  Keys: {list(first_hour.keys())}")
                if 'wind' in first_hour:
                    print(f"  Wind data: {first_hour['wind']}")
                    print(f"  Wind data type: {type(first_hour['wind'])}")
                    if isinstance(first_hour['wind'], dict):
                        print(f"  Wind keys: {list(first_hour['wind'].keys())}")
                        for key, value in first_hour['wind'].items():
                            print(f"    {key}: {value} (type: {type(value)})")

if __name__ == "__main__":
    main() 