#!/usr/bin/env python3
"""
Detailed debug of Rain(%) function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, datetime
import yaml
import json

def debug_rain_percent_detailed():
    """Detailed debug of Rain(%) function."""
    
    print("DETAILED DEBUG RAIN(%) FUNCTION")
    print("=" * 60)
    
    # Load configuration
    config = yaml.safe_load(open("config.yaml", "r"))
    refactor = MorningEveningRefactor(config)
    
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Target Date: {target_date}")
    print(f"Stage Name: {stage_name}")
    print(f"Rain probability threshold: {config.get('thresholds', {}).get('rain_probability', 15)}")
    print()
    
    # Mock data with correct timestamps
    mock_weather_data = {
        'probability_forecast': [
            {
                'data': [
                    {'dt': 1735686000, 'rain': {'3h': 10}},  # 2025-08-02 05:00
                    {'dt': 1735696800, 'rain': {'3h': 0}},   # 2025-08-02 08:00
                    {'dt': 1735707600, 'rain': {'3h': 20}},  # 2025-08-02 11:00
                    {'dt': 1735718400, 'rain': {'3h': 30}},  # 2025-08-02 14:00
                    {'dt': 1735729200, 'rain': {'3h': 80}},  # 2025-08-02 17:00
                ]
            }
        ]
    }
    
    print("Step 1: Check stage calculation")
    start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
    days_since_start = (target_date - start_date).days
    stage_idx = days_since_start
    stage_date = target_date
    
    print(f"  start_date: {start_date}")
    print(f"  days_since_start: {days_since_start}")
    print(f"  stage_idx: {stage_idx}")
    print(f"  stage_date: {stage_date}")
    
    # Load etappen.json
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    print(f"  Total stages: {len(etappen_data)}")
    if stage_idx < len(etappen_data):
        stage = etappen_data[stage_idx]
        print(f"  Stage: {stage['name']}")
        print(f"  Stage points: {len(stage['punkte'])}")
    else:
        print(f"  Stage index {stage_idx} out of range!")
        return
    
    print("\nStep 2: Check probability forecast data")
    probability_forecast = mock_weather_data.get('probability_forecast', [])
    print(f"  probability_forecast points: {len(probability_forecast)}")
    
    for i, point_data in enumerate(probability_forecast):
        print(f"  Point {i+1}:")
        if 'data' in point_data:
            print(f"    Data entries: {len(point_data['data'])}")
            for entry in point_data['data']:
                if 'dt' in entry and 'rain' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    rain_3h_raw = entry.get('rain', {}).get('3h', 0)
                    rain_3h = rain_3h_raw if rain_3h_raw is not None else 0
                    
                    print(f"      {entry_time.strftime('%Y-%m-%d %H:%M')} - date: {entry_date}, rain_3h: {rain_3h}")
                    
                    # Check if this entry matches our criteria
                    if entry_date == stage_date:
                        hour = entry_time.hour
                        if hour in [5, 8, 11, 14, 17]:
                            print(f"        ✅ MATCHES: date={entry_date}, hour={hour}, rain_3h={rain_3h}")
                        else:
                            print(f"        ❌ WRONG HOUR: date={entry_date}, hour={hour}, rain_3h={rain_3h}")
                    else:
                        print(f"        ❌ WRONG DATE: date={entry_date}, rain_3h={rain_3h}")
    
    print("\nStep 3: Manual processing simulation")
    rain_prob_threshold = config.get('thresholds', {}).get('rain_probability', 15)
    print(f"  Rain probability threshold: {rain_prob_threshold}")
    
    # Simulate the processing logic
    for i, point_data in enumerate(probability_forecast):
        print(f"  Processing point {i+1}:")
        point_max_prob = None
        point_max_time = None
        point_threshold_prob = None
        point_threshold_time = None
        point_prob_data = {}
        
        if 'data' in point_data:
            for entry in point_data['data']:
                if 'dt' in entry and 'rain' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    if entry_date == stage_date:
                        rain_3h_raw = entry.get('rain', {}).get('3h', 0)
                        rain_3h = rain_3h_raw if rain_3h_raw is not None else 0
                        
                        hour = entry_time.hour
                        if hour in [5, 8, 11, 14, 17]:
                            hour_str = str(hour)
                            point_prob_data[hour_str] = rain_3h
                            
                            print(f"    Hour {hour_str}: rain_3h={rain_3h}")
                            
                            # Track maximum
                            if point_max_prob is None or rain_3h > point_max_prob:
                                point_max_prob = rain_3h
                                point_max_time = hour_str
                                print(f"      New max: {point_max_prob} at {point_max_time}")
                            
                            # Track threshold
                            if rain_3h >= rain_prob_threshold and point_threshold_time is None:
                                point_threshold_prob = rain_3h
                                point_threshold_time = hour_str
                                print(f"      New threshold: {point_threshold_prob} at {point_threshold_time}")
        
        print(f"  Point {i+1} result:")
        print(f"    point_prob_data: {point_prob_data}")
        print(f"    point_max_prob: {point_max_prob}")
        print(f"    point_max_time: {point_max_time}")
        print(f"    point_threshold_prob: {point_threshold_prob}")
        print(f"    point_threshold_time: {point_threshold_time}")
    
    print("\nStep 4: Call actual function")
    rain_percent_result = refactor.process_rain_percent_data(
        mock_weather_data, stage_name, target_date, "morning"
    )
    
    print("Actual function result:")
    print(f"  threshold_value: {rain_percent_result.threshold_value}")
    print(f"  threshold_time: {rain_percent_result.threshold_time}")
    print(f"  max_value: {rain_percent_result.max_value}")
    print(f"  max_time: {rain_percent_result.max_time}")
    print(f"  geo_points: {rain_percent_result.geo_points}")

if __name__ == "__main__":
    debug_rain_percent_detailed() 