#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def debug_unified_detailed():
    """Detailed debug for _process_unified_hourly_data function"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Detailed Unified Debug for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Fetch weather data directly
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    # Test wind processing
    wind_threshold = config['thresholds']['wind_speed']
    wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
    
    print(f"Wind threshold: {wind_threshold}")
    print(f"Target date: {target_date}")
    print(f"Report type: {report_type}")
    
    # Test the unified processing function directly
    print(f"\n🔍 Testing _process_unified_hourly_data...")
    result = refactor._process_unified_hourly_data(weather_data, target_date, wind_extractor, wind_threshold, report_type, 'wind')
    
    print(f"\n📊 Result:")
    print(f"Threshold time: {result.threshold_time}")
    print(f"Threshold value: {result.threshold_value}")
    print(f"Max time: {result.max_time}")
    print(f"Max value: {result.max_value}")
    print(f"Geo points count: {len(result.geo_points)}")
    
    # Check if result is None
    if result is None:
        print("❌ Result is None!")
    else:
        print("✅ Result is not None")
    
    # Check if result is a WeatherThresholdData object
    from src.weather.core.morning_evening_refactor import WeatherThresholdData
    if isinstance(result, WeatherThresholdData):
        print("✅ Result is WeatherThresholdData object")
    else:
        print(f"❌ Result is not WeatherThresholdData object, it's {type(result)}")
    
    # Check individual attributes
    print(f"\n🔍 Individual attributes:")
    print(f"result.threshold_time: {result.threshold_time} (type: {type(result.threshold_time)})")
    print(f"result.threshold_value: {result.threshold_value} (type: {type(result.threshold_value)})")
    print(f"result.max_time: {result.max_time} (type: {type(result.max_time)})")
    print(f"result.max_value: {result.max_value} (type: {type(result.max_value)})")
    print(f"result.geo_points: {result.geo_points} (type: {type(result.geo_points)})")

if __name__ == "__main__":
    debug_unified_detailed() 