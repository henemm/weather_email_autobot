#!/usr/bin/env python3
"""
Debug Rain(mm) threshold logic
"""

import json
from datetime import date, datetime, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.config.config_loader import load_config

def create_debug_mock_data():
    """Create mock data for debugging threshold logic"""
    
    # Create mock hourly data for 3 points with rain values from specification
    mock_hourly_data = []
    
    # Point 1: T1G1/T2G1 - matches specification example
    point1_data = {
        'data': []
    }
    
    # Generate hourly data for 2025-08-02
    base_timestamp = int(datetime(2025, 8, 2, 4, 0).timestamp())
    
    # Rain values: 0.00, 0.00, 0.20, 0.00, ..., 1.40, 0.80, 0.00
    # Array indices: 0=4:00, 1=5:00, 2=6:00, ..., 12=16:00, 13=17:00, 14=18:00, 15=19:00
    rain_values = [0.00, 0.00, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.40, 0.80, 0.00, 0.00]
    
    for hour in range(4, 20):  # 4:00 to 19:00
        timestamp = base_timestamp + (hour - 4) * 3600
        array_index = hour - 4
        rain_value = rain_values[array_index] if array_index < len(rain_values) else 0.00
        
        hour_data = {
            'dt': timestamp,
            'rain': {
                '1h': rain_value
            }
        }
        point1_data['data'].append(hour_data)
    
    mock_hourly_data.append(point1_data)
    
    # Point 2: T1G2/T2G2 - matches specification example
    point2_data = {
        'data': []
    }
    
    # Rain values: 0.00, 0.00, 0.20, 0.80, ..., 1.20, 0.80, 0.00
    rain_values_2 = [0.00, 0.00, 0.20, 0.80, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.20, 0.80, 0.00, 0.00]
    
    for hour in range(4, 20):  # 4:00 to 19:00
        timestamp = base_timestamp + (hour - 4) * 3600
        array_index = hour - 4
        rain_value = rain_values_2[array_index] if array_index < len(rain_values_2) else 0.00
        
        hour_data = {
            'dt': timestamp,
            'rain': {
                '1h': rain_value
            }
        }
        point2_data['data'].append(hour_data)
    
    mock_hourly_data.append(point2_data)
    
    # Point 3: T1G3/T2G3 - matches specification example
    point3_data = {
        'data': []
    }
    
    # Rain values: 0.00, 0.00, 0.00, 0.80, ..., 1.10, 0.80, 0.00
    rain_values_3 = [0.00, 0.00, 0.00, 0.80, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.10, 0.80, 0.00, 0.00]
    
    for hour in range(4, 20):  # 4:00 to 19:00
        timestamp = base_timestamp + (hour - 4) * 3600
        array_index = hour - 4
        rain_value = rain_values_3[array_index] if array_index < len(rain_values_3) else 0.00
        
        hour_data = {
            'dt': timestamp,
            'rain': {
                '1h': rain_value
            }
        }
        point3_data['data'].append(hour_data)
    
    mock_hourly_data.append(point3_data)
    
    # Create complete mock weather data
    mock_weather_data = {
        'hourly_data': mock_hourly_data,
        'probability_forecast': [],
        'daily_forecast': []
    }
    
    return mock_weather_data

def debug_rain_threshold_logic():
    """Debug the rain threshold logic step by step"""
    
    print("=" * 80)
    print("DEBUGGING RAIN(MM) THRESHOLD LOGIC")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    target_date = date(2025, 8, 2)
    rain_threshold = config.get('thresholds', {}).get('rain_amount', 0.2)
    
    print(f"Rain threshold: {rain_threshold}")
    print(f"Target date: {target_date}")
    
    # Create mock data
    mock_weather_data = create_debug_mock_data()
    
    print("\nMock data created:")
    for i, point_data in enumerate(mock_weather_data['hourly_data']):
        print(f"\nPoint {i+1}:")
        for hour_data in point_data['data']:
            timestamp = datetime.fromtimestamp(hour_data['dt'])
            rain_value = hour_data['rain']['1h']
            hour = timestamp.hour
            print(f"  {hour:2d}:00 | {rain_value:5.2f} | {'≥ threshold' if rain_value >= rain_threshold else '< threshold'}")
    
    # Debug threshold logic manually
    print("\n" + "=" * 60)
    print("MANUAL THRESHOLD LOGIC DEBUG")
    print("=" * 60)
    
    for i, point_data in enumerate(mock_weather_data['hourly_data']):
        print(f"\nPoint {i+1} threshold analysis:")
        point_threshold_time = None
        point_threshold_value = None
        point_max_value = None
        point_max_time = None
        
        for hour_data in point_data['data']:
            timestamp = datetime.fromtimestamp(hour_data['dt'])
            hour_date = timestamp.date()
            hour = timestamp.hour
            rain_value = hour_data['rain']['1h']
            
            # Apply time filter: only 4:00 - 19:00 Uhr
            if hour < 4 or hour > 19:
                continue
            
            # Check if this is the target date
            if hour_date == target_date:
                print(f"  {hour:2d}:00 | {rain_value:5.2f} | ", end="")
                
                # Check threshold (earliest time when rain >= threshold)
                if rain_value >= rain_threshold and point_threshold_time is None:
                    point_threshold_time = str(hour)
                    point_threshold_value = rain_value
                    print(f"FIRST THRESHOLD! time={hour}, value={rain_value}")
                else:
                    print(f"not threshold (already found: {point_threshold_time})" if point_threshold_time else "not threshold")
                
                # Track maximum for this point
                if point_max_value is None or rain_value > point_max_value:
                    point_max_value = rain_value
                    point_max_time = str(hour)
        
        print(f"  Point {i+1} result:")
        print(f"    Threshold: {point_threshold_value}@{point_threshold_time}")
        print(f"    Max: {point_max_value}@{point_max_time}")

if __name__ == "__main__":
    debug_rain_threshold_logic() 