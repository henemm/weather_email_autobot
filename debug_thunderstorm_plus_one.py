#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta
import yaml

def debug_thunderstorm_plus_one():
    """Debug thunderstorm plus one data processing"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Debugging Thunderstorm (+1) for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Calculate +1 day
    plus_one_date = target_date + timedelta(days=1)
    
    # For Evening report: Thunderstorm (+1) = thunderstorm maximum of all points of over-tomorrow's stage for over-tomorrow
    # For Morning report: Thunderstorm (+1) = thunderstorm maximum of all points of tomorrow's stage for tomorrow
    if report_type == 'evening':
        stage_date = plus_one_date + timedelta(days=1)  # Over-tomorrow's date
    else:  # morning
        stage_date = plus_one_date  # Tomorrow's date
    
    print(f"Target date: {target_date}")
    print(f"Plus one date: {plus_one_date}")
    print(f"Stage date: {stage_date}")
    print(f"Report type: {report_type}")
    
    # Fetch weather data for target_date (this is the problem!)
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    print(f"\n📊 Weather Data Structure:")
    print(f"Keys: {list(weather_data.keys())}")
    
    hourly_data = weather_data.get('hourly_data', [])
    print(f"Hourly data count: {len(hourly_data)}")
    
    if hourly_data:
        print(f"\n📊 First hourly data point:")
        first_point = hourly_data[0]
        print(f"Keys: {list(first_point.keys())}")
        
        if 'data' in first_point:
            print(f"Data count: {len(first_point['data'])}")
            
            if first_point['data']:
                print(f"\n📊 First hour data:")
                first_hour = first_point['data'][0]
                print(f"Keys: {list(first_hour.keys())}")
                
                # Check for weather condition
                condition = first_hour.get('condition', '')
                if not condition and 'weather' in first_hour:
                    weather_data_hour = first_hour['weather']
                    condition = weather_data_hour.get('desc', '')
                
                print(f"Weather condition: {condition}")
                
                # Check all available dates in the data
                print(f"\n📅 Available dates in data:")
                dates_found = set()
                for i, point_data in enumerate(hourly_data):
                    if 'data' in point_data:
                        for hour_data in point_data['data']:
                            if 'dt' in hour_data:
                                from datetime import datetime
                                hour_time = datetime.fromtimestamp(hour_data['dt'])
                                dates_found.add(hour_time.date())
                
                print(f"Dates found: {sorted(dates_found)}")
                print(f"Looking for stage_date: {stage_date}")
                print(f"Stage_date in data: {stage_date in dates_found}")
    
    # Test the actual process_thunderstorm_plus_one_data function
    print(f"\n🔍 Testing process_thunderstorm_plus_one_data function:")
    thunderstorm_plus_one_result = refactor.process_thunderstorm_plus_one_data(weather_data, stage_name, target_date, report_type)
    
    print(f"Thunderstorm (+1) result:")
    print(f"  Threshold time: {thunderstorm_plus_one_result.threshold_time}")
    print(f"  Threshold value: {thunderstorm_plus_one_result.threshold_value}")
    print(f"  Max time: {thunderstorm_plus_one_result.max_time}")
    print(f"  Max value: {thunderstorm_plus_one_result.max_value}")
    print(f"  Geo points count: {len(thunderstorm_plus_one_result.geo_points)}")

if __name__ == "__main__":
    debug_thunderstorm_plus_one() 