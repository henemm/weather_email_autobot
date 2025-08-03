#!/usr/bin/env python3
"""
Debug script to check RISKS section output.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def main():
    print("🔍 RISKS DEBUG")
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
    
    # Process RISKS data
    print("⚠️ PROCESSING RISKS DATA:")
    print("-" * 30)
    
    risks_data = refactor.process_risks_data(
        weather_data, stage_name, target_date, "morning"
    )
    
    print(f"Threshold Value: {risks_data.threshold_value}")
    print(f"Threshold Time: {risks_data.threshold_time}")
    print(f"Max Value: {risks_data.max_value}")
    print(f"Max Time: {risks_data.max_time}")
    print(f"Geo Points: {len(risks_data.geo_points)}")
    
    print("\nDebug Info:")
    print(f"  HRain Threshold: {risks_data.debug_info.get('hrain_threshold_value')}")
    print(f"  HRain Threshold Time: {risks_data.debug_info.get('hrain_threshold_time')}")
    print(f"  HRain Max: {risks_data.debug_info.get('hrain_max_value')}")
    print(f"  HRain Max Time: {risks_data.debug_info.get('hrain_max_time')}")
    print(f"  Storm Threshold: {risks_data.debug_info.get('storm_threshold_value')}")
    print(f"  Storm Threshold Time: {risks_data.debug_info.get('storm_threshold_time')}")
    print(f"  Storm Max: {risks_data.debug_info.get('storm_max_value')}")
    print(f"  Storm Max Time: {risks_data.debug_info.get('storm_max_time')}")
    
    print("\nGeo Points Details:")
    for i, point in enumerate(risks_data.geo_points):
        print(f"  Point {i+1}:")
        print(f"    HRain Threshold: {point.get('hrain_threshold_value')} @ {point.get('hrain_threshold_time')}")
        print(f"    HRain Max: {point.get('hrain_max_value')} @ {point.get('hrain_max_time')}")
        print(f"    Storm Threshold: {point.get('storm_threshold_value')} @ {point.get('storm_threshold_time')}")
        print(f"    Storm Max: {point.get('storm_max_value')} @ {point.get('storm_max_time')}")
    
    print()
    
    # Check weather conditions in the data
    print("🌤️ WEATHER CONDITIONS IN DATA:")
    print("-" * 30)
    
    hourly_data = weather_data.get('hourly_data', [])
    
    for geo_index, geo_data in enumerate(hourly_data):
        if not geo_data or 'data' not in geo_data:
            continue
            
        print(f"\n📍 GEO Point {geo_index + 1}:")
        
        conditions_found = set()
        
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
            
            # Extract weather condition
            condition = hour_data.get('condition', '')
            if not condition and 'weather' in hour_data:
                weather_data_hour = hour_data['weather']
                condition = weather_data_hour.get('desc', '')
            
            if condition:
                conditions_found.add(condition)
        
        print(f"  Conditions found: {sorted(conditions_found)}")

if __name__ == "__main__":
    main() 