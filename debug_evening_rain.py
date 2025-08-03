#!/usr/bin/env python3
"""
Debug Evening Report Rain Data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta
import yaml
import json

def debug_evening_rain():
    """Debug why evening report rain data is empty."""
    
    print("DEBUG EVENING REPORT RAIN DATA")
    print("=" * 50)
    
    # Load configuration
    config = yaml.safe_load(open("config.yaml", "r"))
    refactor = MorningEveningRefactor(config)
    
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Target Date: {target_date}")
    print(f"Stage Name: {stage_name}")
    print()
    
    # Fetch weather data
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("No weather data available!")
        return
    
    print("Weather data keys:", list(weather_data.keys()))
    print()
    
    # Check hourly data structure
    hourly_data = weather_data.get('hourly_data', [])
    print(f"Hourly data points: {len(hourly_data)}")
    
    for i, point_data in enumerate(hourly_data[:3]):  # Check first 3 points
        print(f"\nPoint {i+1}:")
        if 'data' in point_data:
            print(f"  Data points: {len(point_data['data'])}")
            
            # Check date range
            dates = set()
            for hour_data in point_data['data']:
                if 'dt' in hour_data:
                    from datetime import datetime
                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                    dates.add(hour_time.date())
            
            print(f"  Available dates: {sorted(dates)}")
            
            # Check tomorrow's data specifically
            tomorrow = target_date + timedelta(days=1)
            tomorrow_data = []
            for hour_data in point_data['data']:
                if 'dt' in hour_data:
                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                    if hour_time.date() == tomorrow:
                        tomorrow_data.append(hour_data)
            
            print(f"  Tomorrow ({tomorrow}) data points: {len(tomorrow_data)}")
            
            # Check rain values for tomorrow
            rain_values = []
            for hour_data in tomorrow_data:
                rain_value = hour_data.get('rain', {}).get('1h', 0)
                hour_time = datetime.fromtimestamp(hour_data['dt'])
                rain_values.append((hour_time.hour, rain_value))
            
            print(f"  Tomorrow rain values: {rain_values}")
        else:
            print("  No 'data' key found")
    
    print("\n" + "=" * 50)
    print("PROCESSING EVENING REPORT")
    print("=" * 50)
    
    # Process evening rain data
    rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "evening")
    
    print(f"Evening Rain Result:")
    print(f"  threshold_value: {rain_mm_result.threshold_value}")
    print(f"  threshold_time: {rain_mm_result.threshold_time}")
    print(f"  max_value: {rain_mm_result.max_value}")
    print(f"  max_time: {rain_mm_result.max_time}")
    print(f"  geo_points: {rain_mm_result.geo_points}")
    
    # Check stage calculation
    start_date = date(2025, 7, 27)
    days_since_start = (target_date - start_date).days
    evening_stage_idx = days_since_start + 1
    evening_stage_date = target_date + timedelta(days=1)
    
    print(f"\nStage calculation:")
    print(f"  start_date: {start_date}")
    print(f"  days_since_start: {days_since_start}")
    print(f"  evening_stage_idx: {evening_stage_idx}")
    print(f"  evening_stage_date: {evening_stage_date}")
    
    # Load etappen.json
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    print(f"  Total stages: {len(etappen_data)}")
    if evening_stage_idx < len(etappen_data):
        evening_stage = etappen_data[evening_stage_idx]
        print(f"  Evening stage: {evening_stage['name']}")
        print(f"  Evening stage points: {len(evening_stage['punkte'])}")
    else:
        print(f"  Evening stage index {evening_stage_idx} out of range!")

if __name__ == "__main__":
    debug_evening_rain() 