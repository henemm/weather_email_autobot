#!/usr/bin/env python3
"""
DEBUG CORRECT DATE
==================
Find the correct available date and test with that date.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
import yaml
import json

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def debug_correct_date():
    """Debug with correct available date"""
    print("🔍 DEBUG CORRECT DATE")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        config = load_config()
        refactor = MorningEveningRefactor(config)
        api = EnhancedMeteoFranceAPI()
        
        # Test coordinates
        lat, lon = 43.283255, 5.370061  # Last point of Test stage
        
        print(f"📍 Testing coordinate: ({lat}, {lon})")
        print()
        
        # Get available dates
        print("📅 FINDING AVAILABLE DATES:")
        print("-" * 30)
        
        try:
            weather_data = api.get_complete_forecast_data(lat, lon, "TestPoint")
            
            if weather_data and 'daily_forecast' in weather_data:
                daily_forecast = weather_data['daily_forecast']
                daily_data = daily_forecast.get('daily', [])
                
                print(f"Available dates:")
                available_dates = []
                for i, entry in enumerate(daily_data):
                    entry_dt = entry.get('dt')
                    if entry_dt:
                        entry_date = datetime.fromtimestamp(entry_dt).date()
                        available_dates.append(entry_date)
                        print(f"  {i}: {entry_date}")
                
                if available_dates:
                    # Use the first available date
                    correct_date = available_dates[0]
                    print(f"\n✅ Using correct date: {correct_date}")
                    
                    # Test with correct date
                    print(f"\n🧪 TESTING WITH CORRECT DATE:")
                    print("-" * 30)
                    
                    # Test Night data processing
                    print("Testing Night data processing...")
                    night_data = refactor.process_night_data(weather_data, "Test", correct_date, "morning")
                    print(f"   Night result: threshold={night_data.threshold_value}, max={night_data.max_value}")
                    
                    # Test Day data processing
                    print("Testing Day data processing...")
                    day_data = refactor.process_day_data(weather_data, "Test", correct_date, "morning")
                    print(f"   Day result: threshold={day_data.threshold_value}, max={day_data.max_value}")
                    
                    # Test complete report generation
                    print(f"\n📧 TESTING COMPLETE REPORT:")
                    print("-" * 30)
                    
                    result_output, debug_output = refactor.generate_report("Test", "morning", str(correct_date))
                    
                    print(f"   Result Output: {result_output}")
                    print(f"   Debug Output Length: {len(debug_output)} characters")
                    
                    # Check for Night and Day values
                    if "N" in result_output and result_output.split()[1] != "N-":
                        print(f"   ✅ Night value found in result output")
                    else:
                        print(f"   ❌ No Night value in result output")
                        
                    if "D" in result_output and result_output.split()[2] != "D-":
                        print(f"   ✅ Day value found in result output")
                    else:
                        print(f"   ❌ No Day value in result output")
                    
                else:
                    print(f"❌ No available dates found")
                    
        except Exception as e:
            print(f"❌ Date finding failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        print("=" * 60)
        print("🎯 DEBUG SUMMARY:")
        print("=" * 60)
        print("1. Available dates identified")
        print("2. Correct date selected")
        print("3. Methods tested with correct date")
        print("4. Complete report tested")
        print()
        print("Next: Use correct date in production!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_correct_date() 