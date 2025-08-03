#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
from src.config.config_loader import load_config

def debug_rain_values():
    """Debug the actual values returned by process_rain_mm_data"""
    
    # Load configuration
    config = load_config()
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Fetch weather data
    print("Fetching weather data...")
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("❌ Failed to fetch weather data")
        return
    
    print("✅ Weather data fetched successfully")
    
    # Process rain mm data
    rain_mm_data = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
    
    print("\n" + "="*80)
    print("RAIN MM DATA DEBUG:")
    print("="*80)
    
    print(f"rain_mm_data.geo_points: {rain_mm_data.geo_points}")
    print(f"rain_mm_data.threshold_value: {rain_mm_data.threshold_value}")
    print(f"rain_mm_data.threshold_time: {rain_mm_data.threshold_time}")
    print(f"rain_mm_data.max_value: {rain_mm_data.max_value}")
    print(f"rain_mm_data.max_time: {rain_mm_data.max_time}")
    
    print("\n" + "="*80)
    print("GEO POINTS DETAILS:")
    print("="*80)
    
    for i, point_data in enumerate(rain_mm_data.geo_points):
        print(f"Point {i+1}: {point_data}")
        for geo, value in point_data.items():
            print(f"  {geo}: {value} (type: {type(value)})")

if __name__ == "__main__":
    debug_rain_values() 