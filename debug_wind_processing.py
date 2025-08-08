#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def debug_wind_processing():
    """Debug the process_wind_data function directly"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Debugging Wind Processing for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Fetch weather data directly
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    print(f"📊 Weather Data Structure:")
    print(f"Keys: {list(weather_data.keys())}")
    
    hourly_data = weather_data.get('hourly_data', [])
    print(f"Hourly data count: {len(hourly_data)}")
    
    # Test wind processing
    wind_threshold = config['thresholds']['wind_speed']
    wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
    
    print(f"\n💨 Wind Processing:")
    print(f"Wind threshold: {wind_threshold}")
    print(f"Target date: {target_date}")
    print(f"Report type: {report_type}")
    
    # Test the unified processing function directly
    result = refactor._process_unified_hourly_data(weather_data, target_date, wind_extractor, wind_threshold, report_type, 'wind')
    
    print(f"\n📊 Unified Processing Result:")
    print(f"Threshold time: {result.threshold_time}")
    print(f"Threshold value: {result.threshold_value}")
    print(f"Max time: {result.max_time}")
    print(f"Max value: {result.max_value}")
    print(f"Geo points count: {len(result.geo_points)}")
    
    # Test the process_wind_data function
    wind_result = refactor.process_wind_data(weather_data, stage_name, target_date, report_type)
    
    print(f"\n📊 Process Wind Data Result:")
    print(f"Threshold time: {wind_result.threshold_time}")
    print(f"Threshold value: {wind_result.threshold_value}")
    print(f"Max time: {wind_result.max_time}")
    print(f"Max value: {wind_result.max_value}")
    print(f"Geo points count: {len(wind_result.geo_points)}")
    
    # Compare the results
    print(f"\n🔍 Comparison:")
    print(f"Unified threshold_time: {result.threshold_time} vs Wind threshold_time: {wind_result.threshold_time}")
    print(f"Unified threshold_value: {result.threshold_value} vs Wind threshold_value: {wind_result.threshold_value}")
    print(f"Unified max_time: {result.max_time} vs Wind max_time: {wind_result.max_time}")
    print(f"Unified max_value: {result.max_value} vs Wind max_value: {wind_result.max_value}")

if __name__ == "__main__":
    debug_wind_processing() 