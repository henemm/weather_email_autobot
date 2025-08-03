#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, datetime
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
from src.config.config_loader import load_config
import json

def debug_rain_logic():
    """Debug the rain processing logic step by step"""
    
    # Load configuration
    config = load_config()
    target_date = date(2025, 8, 3)  # Use tomorrow to get more data
    stage_name = "Test"
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Load etappen.json for coordinates
    with open('etappen.json', 'r') as f:
        etappen_data = json.load(f)
    
    test_stage_idx = 6  # Test stage
    stage_points = etappen_data[test_stage_idx]['punkte']
    
    # Fetch weather data
    print("Fetching weather data...")
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("❌ Failed to fetch weather data")
        return
    
    print("✅ Weather data fetched successfully")
    
    # Get hourly data from weather_data
    hourly_data = weather_data.get('hourly_data', [])
    rain_threshold = config.get('thresholds', {}).get('rain_amount', 0.2)
    
    print(f"\nRain threshold: {rain_threshold}")
    print(f"Number of hourly data points: {len(hourly_data)}")
    
    # Simulate the processing logic
    for i, point_data in enumerate(hourly_data):
        if i >= len(stage_points):
            break
        
        print(f"\nProcessing point {i+1} (T1G{i+1}):")
        print(f"  Coordinates: lat={stage_points[i]['lat']}, lon={stage_points[i]['lon']}")
        
        point_max_value = None
        point_max_time = None
        point_threshold_value = None
        point_threshold_time = None
        
        if 'data' in point_data:
            data_entries = point_data['data']
            print(f"  Number of data entries: {len(data_entries)}")
            
            # Process hourly data for this point
            for hour_data in data_entries:
                if 'dt' in hour_data:
                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                    hour_date = hour_time.date()
                    
                    if hour_date == target_date:
                        # Apply time filter: only 4:00 - 19:00 Uhr
                        hour = hour_time.hour
                        if hour < 4 or hour > 19:
                            continue
                        
                        # Extract rain value
                        rain_value = hour_data.get('rain', {}).get('1h', 0)
                        hour_str = str(hour)
                        
                        print(f"    {hour_str}:00 - rain: {rain_value}")
                        
                        # Check threshold (earliest time when rain >= threshold)
                        if rain_value >= rain_threshold and point_threshold_time is None:
                            point_threshold_time = hour_str
                            point_threshold_value = rain_value
                            print(f"      → Threshold reached: {rain_value} at {hour_str}:00")
                        
                        # Track maximum for this point (including 0 values)
                        if point_max_value is None or rain_value > point_max_value:
                            point_max_value = rain_value
                            point_max_time = hour_str
                            print(f"      → New max: {rain_value} at {hour_str}:00")
        
        print(f"  Final point_max_value: {point_max_value}")
        print(f"  Final point_max_time: {point_max_time}")
        print(f"  Final point_threshold_value: {point_threshold_value}")
        print(f"  Final point_threshold_time: {point_threshold_time}")

if __name__ == "__main__":
    debug_rain_logic() 