#!/usr/bin/env python3
"""
Debug script to check Thunderstorm +1 section.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def main():
    print("🔍 THUNDERSTORM +1 DEBUG")
    print("=" * 50)
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize refactor
    refactor = MorningEveningRefactor(config)
    
    # Test stage and date
    stage_name = "Test"
    target_date = date(2025, 8, 3)
    
    print(f"📅 Test Date: {target_date}")
    print(f"📍 Stage: {stage_name}")
    print()
    
    # Fetch weather data
    print("🌤️ Fetching weather data...")
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("❌ No weather data available")
        return
    
    print("✅ Weather data fetched successfully")
    print()
    
    # Process Thunderstorm +1 data
    print("⛈️ PROCESSING THUNDERSTORM +1 DATA:")
    print("-" * 30)
    
    thunderstorm_plus_one_data = refactor.process_thunderstorm_plus_one_data(
        weather_data, stage_name, target_date, "morning"
    )
    
    print(f"Threshold Value: {thunderstorm_plus_one_data.threshold_value}")
    print(f"Threshold Time: {thunderstorm_plus_one_data.threshold_time}")
    print(f"Max Value: {thunderstorm_plus_one_data.max_value}")
    print(f"Max Time: {thunderstorm_plus_one_data.max_time}")
    print(f"Geo Points: {len(thunderstorm_plus_one_data.geo_points)}")
    
    for i, point in enumerate(thunderstorm_plus_one_data.geo_points):
        print(f"  Point {i+1}: {point}")
    
    print()
    
    # Generate debug output
    print("🔍 GENERATING DEBUG OUTPUT:")
    print("-" * 30)
    
    # Create a minimal report data for testing
    from src.weather.core.morning_evening_refactor import WeatherReportData, WeatherThresholdData
    
    report_data = WeatherReportData(
        stage_name=stage_name,
        report_date=target_date,
        report_type="morning",
        night=WeatherThresholdData(),
        day=WeatherThresholdData(),
        rain_mm=WeatherThresholdData(),
        rain_percent=WeatherThresholdData(),
        wind=WeatherThresholdData(),
        gust=WeatherThresholdData(),
        thunderstorm=WeatherThresholdData(),
        thunderstorm_plus_one=thunderstorm_plus_one_data,
        risks=WeatherThresholdData(),
        risk_zonal=WeatherThresholdData()
    )
    
    # Store weather data for debug output generation
    refactor._last_weather_data = weather_data
    
    debug_output = refactor.generate_debug_output(report_data)
    
    # Extract Thunderstorm +1 section
    lines = debug_output.split('\n')
    in_thunderstorm_plus_one = False
    thunderstorm_plus_one_lines = []
    
    for line in lines:
        if "####### THUNDERSTORM +1 (TH+1) #######" in line:
            in_thunderstorm_plus_one = True
            thunderstorm_plus_one_lines.append(line)
        elif in_thunderstorm_plus_one and line.startswith("#######"):
            break
        elif in_thunderstorm_plus_one:
            thunderstorm_plus_one_lines.append(line)
    
    print("THUNDERSTORM +1 DEBUG OUTPUT:")
    for line in thunderstorm_plus_one_lines:
        print(f"  {line}")

if __name__ == "__main__":
    main() 