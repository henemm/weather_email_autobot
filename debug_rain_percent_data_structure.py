#!/usr/bin/env python3
"""
Debug script to check the actual data structure for rain percentage data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def main():
    print("🔍 RAIN PERCENT DATA STRUCTURE DEBUG")
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
    
    # Check weather data structure
    print("🌧️ WEATHER DATA STRUCTURE:")
    print("-" * 30)
    
    print(f"Keys in weather_data: {list(weather_data.keys())}")
    
    # Check probability_forecast
    probability_forecast = weather_data.get('probability_forecast', [])
    print(f"\nProbability forecast count: {len(probability_forecast)}")
    
    if probability_forecast:
        print(f"First probability forecast keys: {list(probability_forecast[0].keys())}")
        
        if 'data' in probability_forecast[0]:
            print(f"First probability forecast data count: {len(probability_forecast[0]['data'])}")
            
            if probability_forecast[0]['data']:
                first_entry = probability_forecast[0]['data'][0]
                print(f"First entry keys: {list(first_entry.keys())}")
                
                if 'rain' in first_entry:
                    print(f"Rain data: {first_entry['rain']}")
    
    # Check probability_data (alternative key)
    probability_data = weather_data.get('probability_data', [])
    print(f"\nProbability data count: {len(probability_data)}")
    
    if probability_data:
        print(f"First probability data keys: {list(probability_data[0].keys())}")
    
    # Check hourly_data for rain_3h
    hourly_data = weather_data.get('hourly_data', [])
    print(f"\nHourly data count: {len(hourly_data)}")
    
    if hourly_data and 'data' in hourly_data[0]:
        print(f"First hourly data entry keys: {list(hourly_data[0]['data'][0].keys())}")
        
        # Look for rain_3h in hourly data
        rain_3h_found = False
        for entry in hourly_data[0]['data']:
            if 'rain_3h' in entry:
                rain_3h_found = True
                print(f"Found rain_3h: {entry['rain_3h']}")
                break
        
        if not rain_3h_found:
            print("No rain_3h found in hourly data")
    
    print()
    
    # Test the actual process_rain_percent_data method
    print("🌧️ TESTING PROCESS_RAIN_PERCENT_DATA:")
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

if __name__ == "__main__":
    main() 