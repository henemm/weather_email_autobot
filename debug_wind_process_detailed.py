#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def debug_wind_process_detailed():
    """Debug the process_wind_data function step by step"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Debugging Wind Process Detailed for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Fetch weather data directly
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    print(f"📊 Weather Data Structure:")
    print(f"Keys: {list(weather_data.keys())}")
    
    hourly_data = weather_data.get('hourly_data', [])
    print(f"Hourly data count: {len(hourly_data)}")
    
    # Test wind processing step by step
    print(f"\n💨 Wind Processing Step by Step:")
    
    # Step 1: Get stage date
    start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
    days_since_start = (target_date - start_date).days
    
    if report_type == 'evening':
        stage_date = target_date  # Use target_date (tomorrow) directly
    else:  # morning
        stage_date = target_date  # Today's date
    
    print(f"Step 1 - Stage date: {stage_date}")
    
    # Step 2: Get wind threshold
    wind_threshold = config['thresholds']['wind_speed']
    print(f"Step 2 - Wind threshold: {wind_threshold}")
    
    # Step 3: Create wind extractor
    wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
    print(f"Step 3 - Wind extractor created")
    
    # Step 4: Call unified processing
    print(f"Step 4 - Calling _process_unified_hourly_data...")
    result = refactor._process_unified_hourly_data(weather_data, stage_date, wind_extractor, wind_threshold, report_type, 'wind')
    
    print(f"Step 4 Result:")
    print(f"  Threshold time: {result.threshold_time}")
    print(f"  Threshold value: {result.threshold_value}")
    print(f"  Max time: {result.max_time}")
    print(f"  Max value: {result.max_value}")
    print(f"  Geo points count: {len(result.geo_points)}")
    
    # Step 5: Round values
    print(f"Step 5 - Rounding values...")
    if result.threshold_value is not None:
        result.threshold_value = round(result.threshold_value, 1)
        print(f"  Rounded threshold value: {result.threshold_value}")
    if result.max_value is not None:
        result.max_value = round(result.max_value, 1)
        print(f"  Rounded max value: {result.max_value}")
    
    print(f"Step 5 Result:")
    print(f"  Threshold time: {result.threshold_time}")
    print(f"  Threshold value: {result.threshold_value}")
    print(f"  Max time: {result.max_time}")
    print(f"  Max value: {result.max_value}")
    
    # Step 6: Return result
    print(f"Step 6 - Returning result")
    print(f"Final result:")
    print(f"  Threshold time: {result.threshold_time}")
    print(f"  Threshold value: {result.threshold_value}")
    print(f"  Max time: {result.max_time}")
    print(f"  Max value: {result.max_value}")
    
    # Now test the actual process_wind_data function
    print(f"\n🔍 Testing actual process_wind_data function:")
    wind_result = refactor.process_wind_data(weather_data, stage_name, target_date, report_type)
    
    print(f"Process wind data result:")
    print(f"  Threshold time: {wind_result.threshold_time}")
    print(f"  Threshold value: {wind_result.threshold_value}")
    print(f"  Max time: {wind_result.max_time}")
    print(f"  Max value: {wind_result.max_value}")

if __name__ == "__main__":
    from datetime import datetime
    debug_wind_process_detailed() 