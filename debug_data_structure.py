#!/usr/bin/env python3
"""
Debug Data Structure - Examine weather_data structure in detail
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml
from datetime import datetime
import json

def main():
    print("🔍 DEBUG DATA STRUCTURE")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "Vergio"
    date_str = "2025-08-02"
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {date_str}")
    print()
    
    try:
        # Fetch weather data
        print("🔍 Fetching weather data...")
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        print(f"📊 Weather data keys: {list(weather_data.keys())}")
        print()
        
        # Examine each key in detail
        for key in weather_data.keys():
            print(f"📊 Key: {key}")
            data = weather_data[key]
            print(f"📊 Type: {type(data)}")
            print(f"📊 Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"📊 First item type: {type(data[0])}")
                print(f"📊 First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                if isinstance(data[0], dict) and 'data' in data[0]:
                    print(f"📊 First item data length: {len(data[0]['data'])}")
                    if data[0]['data']:
                        print(f"📊 First item data[0]: {data[0]['data'][0]}")
            print()
        
        # Check if daily_forecast has the expected structure
        daily_forecast = weather_data.get('daily_forecast', [])
        print(f"📊 Daily forecast length: {len(daily_forecast)}")
        
        if len(daily_forecast) > 0:
            print(f"📊 Daily forecast[0] keys: {list(daily_forecast[0].keys())}")
            if 'data' in daily_forecast[0]:
                print(f"📊 Daily forecast[0]['data'] length: {len(daily_forecast[0]['data'])}")
                if daily_forecast[0]['data']:
                    print(f"📊 Daily forecast[0]['data'][0]: {daily_forecast[0]['data'][0]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 