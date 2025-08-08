#!/usr/bin/env python3

import sys
import os
import json
sys.path.append('src')

from datetime import date, timedelta, datetime
from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def get_stage_for_date(target_date: date, config: dict) -> str:
    """
    Get the correct stage name for a given date.
    
    Args:
        target_date: Target date
        config: Configuration with startdatum
        
    Returns:
        Stage name for the given date
    """
    start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
    days_since_start = (target_date - start_date).days
    
    # Load etappen.json
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    if days_since_start < len(etappen_data):
        stage = etappen_data[days_since_start]
        return stage['name']
    else:
        return "Unknown"

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create instance
refactor = MorningEveningRefactor(config)

# Test with tomorrow's date (Evening Report)
target_date = date.today() + timedelta(days=1)
stage_name = get_stage_for_date(target_date, config)

print(f"🌧️ TESTING EVENING REPORT Rain(%) for {target_date}")
print(f"📍 Stage: {stage_name}")
print("=" * 60)

# Process rain percent data for evening report
weather_data = refactor.fetch_weather_data(stage_name, target_date)
rain_percent_data = refactor.process_rain_percent_data(weather_data, stage_name, target_date, 'evening')

print(f"🌧️ Rain percent data: {rain_percent_data}")
print(f"  Geo points: {len(rain_percent_data.geo_points) if rain_percent_data.geo_points else 0}")
print(f"  Threshold: {rain_percent_data.threshold_time} | {rain_percent_data.threshold_value}")
print(f"  Maximum: {rain_percent_data.max_time} | {rain_percent_data.max_value}")

# Show geo points data
if rain_percent_data.geo_points:
    for i, point_data in enumerate(rain_percent_data.geo_points):
        print(f"  Point {i}: {point_data}") 