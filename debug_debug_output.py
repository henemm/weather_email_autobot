#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def debug_debug_output():
    """Debug the debug output generation for wind threshold table"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Debugging Debug Output for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Generate report to set _last_weather_data
    result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
    
    print(f"📊 Result Output: {result_output}")
    print("\n" + "=" * 50)
    
    # Check if _last_weather_data is set
    print(f"🔍 _last_weather_data set: {hasattr(refactor, '_last_weather_data')}")
    if hasattr(refactor, '_last_weather_data'):
        print(f"   Keys: {list(refactor._last_weather_data.keys())}")
        hourly_data = refactor._last_weather_data.get('hourly_data', [])
        print(f"   Hourly data count: {len(hourly_data)}")
        
        if hourly_data:
            print(f"\n📊 First hourly data point:")
            first_point = hourly_data[0]
            print(f"   Keys: {list(first_point.keys())}")
            
            if 'data' in first_point:
                print(f"   Data count: {len(first_point['data'])}")
                
                if first_point['data']:
                    print(f"\n📊 First hour data:")
                    first_hour = first_point['data'][0]
                    print(f"   Keys: {list(first_hour.keys())}")
                    
                    # Test wind extractor
                    wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
                    wind_value = wind_extractor(first_hour)
                    print(f"   Wind value: {wind_value}")
    
    print("\n" + "=" * 50)
    
    # Test the debug output generation directly
    print("🔍 Testing Debug Output Generation:")
    
    # Get the report data
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    # Process wind data
    wind_data = refactor.process_wind_data(weather_data, stage_name, target_date, report_type)
    
    print(f"Wind threshold_time: {wind_data.threshold_time}")
    print(f"Wind threshold_value: {wind_data.threshold_value}")
    print(f"Wind max_time: {wind_data.max_time}")
    print(f"Wind max_value: {wind_data.max_value}")
    print(f"Wind geo_points count: {len(wind_data.geo_points)}")
    
    # Create report data
    from src.weather.core.morning_evening_refactor import WeatherReportData
    report_data = WeatherReportData(
        stage_name=stage_name,
        report_date=target_date,
        report_type=report_type,
        wind=wind_data,
        night=refactor.process_night_data(weather_data, stage_name, target_date, report_type),
        day=refactor.process_day_data(weather_data, stage_name, target_date, report_type),
        rain_mm=refactor.process_rain_mm_data(weather_data, stage_name, target_date, report_type),
        rain_percent=refactor.process_rain_percent_data(weather_data, stage_name, target_date, report_type),
        gust=refactor.process_gust_data(weather_data, stage_name, target_date, report_type),
        thunderstorm=refactor.process_thunderstorm_data(weather_data, stage_name, target_date, report_type),
        thunderstorm_plus_one=refactor.process_thunderstorm_plus_one_data(weather_data, stage_name, target_date, report_type),
        risks=refactor.process_risks_data(weather_data, stage_name, target_date, report_type),
        risk_zonal=refactor.process_risk_zonal_data(weather_data, stage_name, target_date, report_type)
    )
    
    # Set _last_weather_data
    refactor._last_weather_data = weather_data
    
    # Generate debug output
    debug_output = refactor.generate_debug_output(report_data)
    
    # Extract wind section
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
    
    print("\n🌬️ Wind Debug Section:")
    for line in wind_data_lines:
        print(line)

if __name__ == "__main__":
    debug_debug_output() 