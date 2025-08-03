#!/usr/bin/env python3
"""
Debug script to check rain inconsistency between mm and percentage.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def main():
    print("🔍 RAIN INCONSISTENCY DEBUG")
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
    
    # Process Rain(mm) data
    print("🌧️ PROCESSING RAIN(MM) DATA:")
    print("-" * 30)
    
    rain_mm_data = refactor.process_rain_mm_data(
        weather_data, stage_name, target_date, "evening"
    )
    
    print(f"Threshold Value: {rain_mm_data.threshold_value}")
    print(f"Threshold Time: {rain_mm_data.threshold_time}")
    print(f"Max Value: {rain_mm_data.max_value}")
    print(f"Max Time: {rain_mm_data.max_time}")
    print(f"Geo Points: {len(rain_mm_data.geo_points)}")
    
    for i, point in enumerate(rain_mm_data.geo_points):
        print(f"  Point {i+1}: {point}")
    
    print()
    
    # Process Rain(%) data
    print("🌧️ PROCESSING RAIN(%) DATA:")
    print("-" * 30)
    
    rain_percent_data = refactor.process_rain_percent_data(
        weather_data, stage_name, target_date, "evening"
    )
    
    print(f"Threshold Value: {rain_percent_data.threshold_value}")
    print(f"Threshold Time: {rain_percent_data.threshold_time}")
    print(f"Max Value: {rain_percent_data.max_value}")
    print(f"Max Time: {rain_percent_data.max_time}")
    print(f"Geo Points: {len(rain_percent_data.geo_points)}")
    
    for i, point in enumerate(rain_percent_data.geo_points):
        print(f"  Point {i+1}: {point}")
    
    print()
    
    # Check raw data
    print("🌧️ RAW RAIN DATA:")
    print("-" * 30)
    
    hourly_data = weather_data.get('hourly_data', [])
    probability_data = weather_data.get('probability_data', [])
    
    print(f"Hourly data count: {len(hourly_data)}")
    print(f"Probability data count: {len(probability_data)}")
    
    for geo_index, geo_data in enumerate(hourly_data):
        if not geo_data or 'data' not in geo_data:
            continue
            
        print(f"\n📍 GEO Point {geo_index + 1} (Hourly):")
        
        rain_samples = []
        
        for hour_data in geo_data['data']:
            if not hour_data or 'dt' not in hour_data:
                continue
                
            hour_time = datetime.fromtimestamp(hour_data['dt'])
            hour_date = hour_time.date()
            
            # Only process data for the target date
            if hour_date != target_date:
                continue
            
            # Apply time filter: only 4:00 - 19:00 Uhr
            hour = hour_time.hour
            if hour < 4 or hour > 19:
                continue
            
            # Extract rain data
            rain_1h = hour_data.get('rain', {}).get('1h', 0)
            
            if rain_1h > 0:
                rain_samples.append({
                    'time': hour_time.strftime('%H:%M'),
                    'rain_1h': rain_1h
                })
        
        print(f"  Rain samples: {rain_samples}")
    
    for geo_index, geo_data in enumerate(probability_data):
        if not geo_data or 'data' not in geo_data:
            continue
            
        print(f"\n📍 GEO Point {geo_index + 1} (Probability):")
        
        rain_3h_samples = []
        
        for hour_data in geo_data['data']:
            if not hour_data or 'dt' not in hour_data:
                continue
                
            hour_time = datetime.fromtimestamp(hour_data['dt'])
            hour_date = hour_time.date()
            
            # Only process data for the target date
            if hour_date != target_date:
                continue
            
            # Apply time filter: only 4:00 - 19:00 Uhr
            hour = hour_time.hour
            if hour < 4 or hour > 19:
                continue
            
            # Extract rain_3h data
            rain_3h = hour_data.get('rain_3h', 0)
            
            if rain_3h > 0:
                rain_3h_samples.append({
                    'time': hour_time.strftime('%H:%M'),
                    'rain_3h': rain_3h
                })
        
        print(f"  Rain_3h samples: {rain_3h_samples}")

if __name__ == "__main__":
    main() 