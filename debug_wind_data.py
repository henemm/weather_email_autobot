#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def debug_wind_data():
    """Debug wind data processing to see what's in geo_points"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    report_type = "evening"
    target_date = date(2025, 8, 3)  # Tomorrow
    
    print(f"🔍 Debugging Wind Data for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Generate report
    result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
    
    print("📊 Result Output:")
    print(result_output)
    print("\n" + "=" * 50)
    
    # Extract wind data from debug output
    debug_lines = debug_output.split('\n')
    wind_section = False
    wind_data_lines = []
    
    for line in debug_lines:
        if "Wind Data:" in line:
            wind_section = True
            wind_data_lines.append(line)
        elif wind_section and line.strip() == "":
            wind_section = False
        elif wind_section:
            wind_data_lines.append(line)
    
    print("🌬️ Wind Debug Section:")
    for line in wind_data_lines:
        print(line)
    
    print("\n" + "=" * 50)
    
    # Now let's inspect the actual data structure
    print("🔍 Inspecting Wind Data Structure:")
    
    # Fetch weather data directly
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    # Process wind data
    wind_result = refactor.process_wind_data(weather_data, stage_name, target_date, report_type)
    
    print(f"Wind threshold_time: {wind_result.threshold_time}")
    print(f"Wind threshold_value: {wind_result.threshold_value}")
    print(f"Wind max_time: {wind_result.max_time}")
    print(f"Wind max_value: {wind_result.max_value}")
    print(f"Wind geo_points count: {len(wind_result.geo_points)}")
    
    for i, point in enumerate(wind_result.geo_points):
        print(f"\nPoint {i}:")
        print(f"  Type: {type(point)}")
        print(f"  Keys: {list(point.keys())}")
        for key, value in point.items():
            print(f"  {key}: {type(value)} = {value}")
            if isinstance(value, dict):
                print(f"    Keys: {list(value.keys())}")
                print(f"    Sample values: {dict(list(value.items())[:5])}")

if __name__ == "__main__":
    debug_wind_data() 