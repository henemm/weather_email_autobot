#!/usr/bin/env python3
"""
Debug Daily Forecast - Examine daily_forecast structure in detail
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml
from datetime import datetime
import json

def main():
    print("🔍 DEBUG DAILY FORECAST")
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
        
        # Examine daily_forecast in detail
        daily_forecast = weather_data.get('daily_forecast', {})
        print(f"📊 Daily forecast type: {type(daily_forecast)}")
        print(f"📊 Daily forecast keys: {list(daily_forecast.keys())}")
        print()
        
        if 'daily' in daily_forecast:
            daily_data = daily_forecast['daily']
            print(f"📊 Daily data type: {type(daily_data)}")
            print(f"📊 Daily data length: {len(daily_data)}")
            print()
            
            if len(daily_data) > 0:
                print(f"📊 First daily entry: {daily_data[0]}")
                print()
                
                # Look for target date
                target_date_str = target_date.strftime('%Y-%m-%d')
                print(f"📊 Looking for date: {target_date_str}")
                print()
                
                found_entry = None
                for i, entry in enumerate(daily_data):
                    entry_dt = entry.get('dt')
                    if entry_dt:
                        entry_date = datetime.fromtimestamp(entry_dt).date()
                        entry_date_str = entry_date.strftime('%Y-%m-%d')
                        print(f"📊 Entry {i} date: {entry_date_str}")
                        
                        if entry_date_str == target_date_str:
                            found_entry = entry
                            print(f"✅ Found matching entry at index {i}")
                            break
                    else:
                        print(f"📊 Entry {i} date: None (no dt)")
                
                if found_entry:
                    print(f"📊 Found entry: {found_entry}")
                    
                    # Test data extractor
                    data_extractor = lambda d: d.get('T', {}).get('min')
                    temp_min = data_extractor(found_entry)
                    print(f"📊 Extracted temp_min: {temp_min}")
                else:
                    print("❌ No matching entry found")
                    
                    # Show available dates
                    print("\n📊 Available dates:")
                    for i, entry in enumerate(daily_data):
                        entry_dt = entry.get('dt')
                        if entry_dt:
                            entry_date = datetime.fromtimestamp(entry_dt).date()
                            print(f"📊 Entry {i}: {entry_date}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 