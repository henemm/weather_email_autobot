#!/usr/bin/env python3
"""
Debug Night Temperature - Check MeteoFrance data structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml
from datetime import datetime

def main():
    print("🔍 DEBUG NIGHT TEMPERATURE")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "Vergio"
    date_str = "2025-08-02"
    report_type = "morning"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {date_str}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    try:
        # Get weather data
        print("🔍 Fetching weather data...")
        from datetime import date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        print("📊 WEATHER DATA STRUCTURE:")
        print("=" * 40)
        
        # Check daily_forecast structure
        daily_forecast = weather_data.get('daily_forecast', {})
        print(f"daily_forecast keys: {list(daily_forecast.keys())}")
        
        if 'daily' in daily_forecast:
            daily_data = daily_forecast['daily']
            print(f"daily_data type: {type(daily_data)}")
            print(f"daily_data length: {len(daily_data)}")
            
            # Show first few entries
            print("\n📅 FIRST 3 DAILY ENTRIES:")
            for i, entry in enumerate(daily_data[:3]):
                print(f"Entry {i}:")
                print(f"  dt: {entry.get('dt')}")
                print(f"  T: {entry.get('T')}")
                print(f"  temperature: {entry.get('temperature')}")
                print()
            
            # Find target date entry
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            target_date_str = target_date.strftime('%Y-%m-%d')
            
            print(f"🎯 LOOKING FOR TARGET DATE: {target_date_str}")
            print("-" * 30)
            
            found_entry = None
            for entry in daily_data:
                dt = entry.get('dt')
                if dt:
                    entry_date = datetime.fromtimestamp(dt).date()
                    entry_date_str = entry_date.strftime('%Y-%m-%d')
                    
                    if entry_date_str == target_date_str:
                        found_entry = entry
                        print(f"✅ FOUND TARGET DATE ENTRY!")
                        print(f"  dt: {dt}")
                        print(f"  entry_date: {entry_date_str}")
                        print(f"  T: {entry.get('T')}")
                        print(f"  temperature: {entry.get('temperature')}")
                        break
            
            if not found_entry:
                print("❌ TARGET DATE NOT FOUND!")
                print("Available dates:")
                for entry in daily_data[:5]:
                    dt = entry.get('dt')
                    if dt:
                        entry_date = datetime.fromtimestamp(dt).date()
                        print(f"  {entry_date}")
        
        # Test the data extractor
        print("\n🧪 TESTING DATA EXTRACTOR:")
        print("-" * 30)
        
        if found_entry:
            # Test the lambda function used in process_night_data
            data_extractor = lambda d: d.get('T', {}).get('min')
            extracted_value = data_extractor(found_entry)
            print(f"data_extractor result: {extracted_value}")
            
            # Test alternative extractors
            print("\nAlternative extractors:")
            print(f"d.get('T'): {found_entry.get('T')}")
            print(f"d.get('temperature'): {found_entry.get('temperature')}")
            t_data = found_entry.get('T', {})
            temp_data = found_entry.get('temperature', {})
            print(f"d.get('T', {{}}).get('min'): {t_data.get('min')}")
            print(f"d.get('temperature', {{}}).get('min'): {temp_data.get('min')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 