#!/usr/bin/env python3
"""
DEBUG WIND DATA STRUCTURE
=========================
Check the actual wind data structure from the API to understand correct field names.
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def debug_wind_structure():
    """Debug the wind data structure."""
    print("🔍 DEBUG WIND DATA STRUCTURE")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Fetch weather data
    stage_name = "Test"
    target_date = date(2025, 8, 3)
    
    print(f"📅 Target Date: {target_date}")
    print(f"📍 Stage: {stage_name}")
    print()
    
    try:
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if weather_data and 'hourly_data' in weather_data:
            print("✅ Weather data fetched successfully")
            print(f"   Hourly data points: {len(weather_data['hourly_data'])}")
            
            # Check first geo point
            if weather_data['hourly_data']:
                first_point = weather_data['hourly_data'][0]
                print(f"   First point data keys: {list(first_point.keys())}")
                
                if 'data' in first_point and first_point['data']:
                    first_hour = first_point['data'][0]
                    print(f"   First hour data keys: {list(first_hour.keys())}")
                    
                    # Check for wind-related fields
                    wind_fields = [key for key in first_hour.keys() if 'wind' in key.lower()]
                    print(f"   Wind-related fields: {wind_fields}")
                    
                    # Show actual wind data
                    print("\n🌬️ ACTUAL WIND DATA:")
                    print("-" * 30)
                    
                    for field in wind_fields:
                        value = first_hour.get(field)
                        print(f"   {field}: {value}")
                    
                    # Check for speed-related fields
                    speed_fields = [key for key in first_hour.keys() if 'speed' in key.lower()]
                    print(f"\n💨 SPEED-RELATED FIELDS:")
                    print("-" * 30)
                    for field in speed_fields:
                        value = first_hour.get(field)
                        print(f"   {field}: {value}")
                    
                    # Check for gust-related fields
                    gust_fields = [key for key in first_hour.keys() if 'gust' in key.lower()]
                    print(f"\n💨 GUST-RELATED FIELDS:")
                    print("-" * 30)
                    for field in gust_fields:
                        value = first_hour.get(field)
                        print(f"   {field}: {value}")
                    
                    # Show complete hour data structure
                    print(f"\n📋 COMPLETE HOUR DATA STRUCTURE:")
                    print("-" * 30)
                    for key, value in first_hour.items():
                        print(f"   {key}: {value}")
                    
                else:
                    print("❌ No hourly data found")
            else:
                print("❌ No geo points found")
        else:
            print("❌ No weather data or hourly_data found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_wind_structure() 