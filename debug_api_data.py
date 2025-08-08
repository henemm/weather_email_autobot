#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from datetime import date, datetime
from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml
import json

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create instance
refactor = MorningEveningRefactor(config)

# Test with today's date
target_date = date.today()
stage_name = "Vergio"

print(f"🔍 API DATA DATE ANALYSIS for {target_date}")
print("=" * 60)

# Fetch weather data
weather_data = refactor.fetch_weather_data(stage_name, target_date)

if weather_data:
    print("✅ Weather data fetched successfully")
    
    # Check probability_forecast
    probability_forecast = weather_data.get('probability_forecast', [])
    print(f"📊 Probability forecast data: {len(probability_forecast)} points")
    
    if probability_forecast:
        for i, point_data in enumerate(probability_forecast):
            print(f"\n📍 Point {i}:")
            data_entries = point_data.get('data', [])
            
            # Check all dates in the data
            dates_in_data = set()
            for entry in data_entries:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    dates_in_data.add(entry_time.date())
            
            print(f"  📅 Dates in API data: {sorted(dates_in_data)}")
            
            # Show data for today specifically
            print(f"  🌧️ Data for today ({target_date}):")
            today_data = []
            for entry in data_entries:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    if entry_time.date() == target_date:
                        hour = entry_time.hour
                        rain_3h = entry.get('rain', {}).get('3h', 0)
                        rain_6h = entry.get('rain', {}).get('6h', 0)
                        today_data.append(f"{hour:02d}:00 -> rain_3h: {rain_3h}%, rain_6h: {rain_6h}%")
            
            if today_data:
                for data in today_data:
                    print(f"    {data}")
            else:
                print(f"    ❌ No data for today!")
            
            # Show 3-hour intervals for today
            print(f"  🕐 3-hour intervals for today (05:00, 08:00, 11:00, 14:00, 17:00):")
            for entry in data_entries:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    if entry_time.date() == target_date:
                        hour = entry_time.hour
                        if hour in [5, 8, 11, 14, 17]:
                            rain_3h = entry.get('rain', {}).get('3h', 0)
                            rain_6h = entry.get('rain', {}).get('6h', 0)
                            print(f"    {hour:02d}:00 -> rain_3h: {rain_3h}%, rain_6h: {rain_6h}%")
    else:
        print("❌ No probability_forecast data found")
else:
    print("❌ No weather data available") 