#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def debug_unified_processing():
    """Debug the _process_unified_hourly_data function for wind"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Debugging Unified Processing for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Fetch weather data directly
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    # Test wind processing
    wind_threshold = config['thresholds']['wind_speed']
    wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
    
    print(f"Wind threshold: {wind_threshold}")
    print(f"Target date: {target_date}")
    
    # Test the unified processing function directly
    result = refactor._process_unified_hourly_data(weather_data, target_date, wind_extractor, wind_threshold, report_type, 'wind')
    
    print(f"\n📊 Processing Result:")
    print(f"Threshold time: {result.threshold_time}")
    print(f"Threshold value: {result.threshold_value}")
    print(f"Max time: {result.max_time}")
    print(f"Max value: {result.max_value}")
    print(f"Geo points count: {len(result.geo_points)}")
    
    # Debug the processing step by step
    print(f"\n🔍 Step-by-step debugging:")
    
    hourly_data = weather_data.get('hourly_data', [])
    print(f"Hourly data count: {len(hourly_data)}")
    
    for i, point_data in enumerate(hourly_data):
        if 'data' in point_data:
            print(f"\nPoint {i}:")
            point_threshold_time = None
            point_threshold_value = None
            point_max_value = None
            point_max_time = None
            
            for hour_data in point_data['data']:
                if 'dt' in hour_data:
                    from datetime import datetime
                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                    hour_date = hour_time.date()
                    
                    if hour_date == target_date:
                        value = wind_extractor(hour_data)
                        hour_str = hour_time.strftime('%H')
                        
                        print(f"  {hour_str}:00 = {value} km/h")
                        
                        # Check threshold
                        if value >= wind_threshold and point_threshold_time is None:
                            point_threshold_time = hour_str
                            point_threshold_value = value
                            print(f"    -> THRESHOLD REACHED at {hour_str}:00 = {value}")
                        
                        # Track maximum
                        if point_max_value is None or value > point_max_value:
                            point_max_value = value
                            point_max_time = hour_str
            
            print(f"  Point {i} result:")
            print(f"    Threshold: {point_threshold_time}:00 = {point_threshold_value}")
            print(f"    Maximum: {point_max_time}:00 = {point_max_value}")

if __name__ == "__main__":
    debug_unified_processing() 