#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from datetime import date
from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create instance
refactor = MorningEveningRefactor(config)

# Test with today's date
target_date = date.today()
stage_name = "Vergio"  # Use a real stage name

print(f"Testing Rain(%) data for {target_date}")

# Fetch weather data
weather_data = refactor.fetch_weather_data(stage_name, target_date)

if weather_data:
    print("✅ Weather data fetched successfully")
    
    # Check probability_forecast
    probability_forecast = weather_data.get('probability_forecast', [])
    print(f"📊 Probability forecast data: {len(probability_forecast)} points")
    
    if probability_forecast:
        for i, point_data in enumerate(probability_forecast):
            print(f"  Point {i}: {len(point_data.get('data', []))} entries")
            if point_data.get('data'):
                first_entry = point_data['data'][0]
                print(f"    First entry: {first_entry}")
    else:
        print("❌ No probability_forecast data found")
    
    # Process rain percent data
    rain_percent_data = refactor.process_rain_percent_data(weather_data, stage_name, target_date, 'morning')
    print(f"🌧️ Rain percent data: {rain_percent_data}")
    print(f"  Geo points: {len(rain_percent_data.geo_points) if rain_percent_data.geo_points else 0}")
    print(f"  Threshold: {rain_percent_data.threshold_time} | {rain_percent_data.threshold_value}")
    print(f"  Maximum: {rain_percent_data.max_time} | {rain_percent_data.max_value}")
else:
    print("❌ No weather data available") 