#!/usr/bin/env python3
"""
Debug script to show exactly what process_night_data is doing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def debug_night_method():
    """Show exactly what process_night_data is doing."""
    
    print("🔍 DEBUG: PROCESS_NIGHT_DATA METHOD")
    print("=" * 50)
    
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
        
        # Test process_night_data directly
        print("🧪 TESTING PROCESS_NIGHT_DATA DIRECTLY:")
        print("-" * 40)
        
        from datetime import datetime
        target_date = datetime.strptime(test_date, '%Y-%m-%d').date()
        
        result = refactor.process_night_data(weather_data, stage_name, target_date, "morning")
        
        print(f"📊 Result:")
        print(f"   threshold_value: {result.threshold_value}")
        print(f"   threshold_time: {result.threshold_time}")
        print(f"   max_value: {result.max_value}")
        print(f"   max_time: {result.max_time}")
        print(f"   geo_points: {result.geo_points}")
        print()
        
        # Check what's in the weather_data
        print("📊 WEATHER_DATA CONTENT:")
        print("-" * 30)
        daily_forecast = weather_data.get('daily_forecast', {})
        print(f"daily_forecast type: {type(daily_forecast)}")
        print(f"daily_forecast keys: {list(daily_forecast.keys())}")
        
        if 'daily' in daily_forecast:
            daily_data = daily_forecast['daily']
            print(f"daily_data type: {type(daily_data)}")
            print(f"daily_data length: {len(daily_data)}")
            
            if len(daily_data) > 0:
                print(f"\n📊 First daily entry:")
                first_daily = daily_data[0]
                print(f"Keys: {list(first_daily.keys())}")
                print(f"T: {first_daily.get('T', {})}")
        
        print()
        
        # Check etappen.json
        print("📊 ETAPPEN.JSON CONTENT:")
        print("-" * 30)
        import json
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
        
        print(f"Etappen length: {len(etappen_data)}")
        
        # Find current stage
        start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
        days_since_start = (target_date - start_date).days
        stage_idx = days_since_start
        
        print(f"days_since_start: {days_since_start}")
        print(f"stage_idx: {stage_idx}")
        
        if stage_idx < len(etappen_data):
            stage = etappen_data[stage_idx]
            print(f"Stage name: {stage.get('name', 'Unknown')}")
            stage_points = stage.get('punkte', [])
            print(f"Stage points: {len(stage_points)}")
            
            if stage_points:
                print(f"First point: {stage_points[0]}")
                print(f"Last point: {stage_points[-1]}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("🎯 DEBUG COMPLETED!")

if __name__ == "__main__":
    debug_night_method() 