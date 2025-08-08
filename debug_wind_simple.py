#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml
import traceback

def debug_wind_simple():
    """Simple debug for process_wind_data function"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Simple Wind Debug for {stage_name} on {target_date}")
    print("=" * 50)
    
    try:
        # Fetch weather data directly
        print("Step 1: Fetching weather data...")
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        print("✅ Weather data fetched")
        
        # Test process_wind_data function
        print("Step 2: Calling process_wind_data...")
        wind_result = refactor.process_wind_data(weather_data, stage_name, target_date, report_type)
        print("✅ process_wind_data completed")
        
        print(f"Result:")
        print(f"  Threshold time: {wind_result.threshold_time}")
        print(f"  Threshold value: {wind_result.threshold_value}")
        print(f"  Max time: {wind_result.max_time}")
        print(f"  Max value: {wind_result.max_value}")
        
    except Exception as e:
        print(f"❌ Exception caught: {e}")
        print(f"Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_wind_simple() 