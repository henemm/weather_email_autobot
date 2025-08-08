#!/usr/bin/env python3
"""
DEBUG NIGHT AND DAY IMPLEMENTATION
==================================
Check and document the current Night and Day implementation to understand:
1. Which API is used
2. Which data fields are accessed
3. How the data is structured
4. What the current implementation does
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def debug_night_day_implementation():
    """Debug the Night and Day implementation."""
    print("🔍 DEBUG NIGHT AND DAY IMPLEMENTATION")
    print("=" * 50)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "Test"
    target_date = date(2025, 8, 3)
    report_type = "morning"
    
    print(f"📅 Target Date: {target_date}")
    print(f"📍 Stage: {stage_name}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    try:
        # Fetch weather data
        print("1️⃣ FETCHING WEATHER DATA:")
        print("-" * 30)
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if weather_data:
            print("✅ Weather data fetched successfully")
            print(f"   Keys: {list(weather_data.keys())}")
            
            # Check for daily data
            if 'daily_data' in weather_data:
                print(f"   Daily data points: {len(weather_data['daily_data'])}")
                if weather_data['daily_data']:
                    first_daily = weather_data['daily_data'][0]
                    print(f"   First daily data keys: {list(first_daily.keys())}")
            else:
                print("   ❌ No daily_data found")
                
            # Check for hourly data
            if 'hourly_data' in weather_data:
                print(f"   Hourly data points: {len(weather_data['hourly_data'])}")
            else:
                print("   ❌ No hourly_data found")
        else:
            print("❌ No weather data fetched")
            return
        
        print()
        
        # Test Night implementation
        print("2️⃣ NIGHT IMPLEMENTATION:")
        print("-" * 30)
        try:
            night_data = refactor.process_night_data(weather_data, stage_name, target_date, report_type)
            print(f"✅ Night processing successful")
            print(f"   Threshold value: {night_data.threshold_value}")
            print(f"   Threshold time: {night_data.threshold_time}")
            print(f"   Max value: {night_data.max_value}")
            print(f"   Max time: {night_data.max_time}")
            print(f"   Geo points: {len(night_data.geo_points) if night_data.geo_points else 0}")
            
            # Show geo points data
            if night_data.geo_points:
                print("   Geo points data:")
                for i, point in enumerate(night_data.geo_points):
                    print(f"     Point {i+1}: {point}")
                    
        except Exception as e:
            print(f"❌ Night processing failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        print()
        
        # Test Day implementation
        print("3️⃣ DAY IMPLEMENTATION:")
        print("-" * 30)
        try:
            day_data = refactor.process_day_data(weather_data, stage_name, target_date, report_type)
            print(f"✅ Day processing successful")
            print(f"   Threshold value: {day_data.threshold_value}")
            print(f"   Threshold time: {day_data.threshold_time}")
            print(f"   Max value: {day_data.max_value}")
            print(f"   Max time: {day_data.max_time}")
            print(f"   Geo points: {len(day_data.geo_points) if day_data.geo_points else 0}")
            
            # Show geo points data
            if day_data.geo_points:
                print("   Geo points data:")
                for i, point in enumerate(day_data.geo_points):
                    print(f"     Point {i+1}: {point}")
                    
        except Exception as e:
            print(f"❌ Day processing failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        print()
        
        # Check data structure
        print("4️⃣ DATA STRUCTURE ANALYSIS:")
        print("-" * 30)
        
        if 'daily_data' in weather_data and weather_data['daily_data']:
            first_daily = weather_data['daily_data'][0]
            print("Daily data structure:")
            for key, value in first_daily.items():
                print(f"   {key}: {value}")
        
        if 'hourly_data' in weather_data and weather_data['hourly_data']:
            first_hourly = weather_data['hourly_data'][0]
            if 'data' in first_hourly and first_hourly['data']:
                first_hour = first_hourly['data'][0]
                print("Hourly data structure:")
                for key, value in first_hour.items():
                    print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_night_day_implementation() 