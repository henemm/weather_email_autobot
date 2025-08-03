#!/usr/bin/env python3
"""
DEBUG API DATA STRUCTURE
========================
Understand the actual API data structure to fix my data extraction code.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
import yaml
import json

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def debug_api_data_structure():
    """Debug the actual API data structure"""
    print("🔍 DEBUG API DATA STRUCTURE")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        config = load_config()
        api = EnhancedMeteoFranceAPI()
        
        # Test coordinates from Test stage
        test_coordinates = [
            (47.638699, 6.846891),  # T1G1
            (47.246166, -1.652276), # T1G2  
            (43.283255, 5.370061)   # T1G3
        ]
        
        print(f"📍 Testing coordinates: {len(test_coordinates)} points")
        print()
        
        for i, (lat, lon) in enumerate(test_coordinates, 1):
            print(f"Point {i} ({lat}, {lon}):")
            print("-" * 40)
            
            try:
                # Call the correct API method
                weather_data = api.get_complete_forecast_data(lat, lon, f"TestPoint{i}")
                
                print(f"✅ API call successful")
                print(f"   Data type: {type(weather_data)}")
                
                # Debug the data structure
                if weather_data:
                    print(f"   Keys available: {list(weather_data.keys()) if isinstance(weather_data, dict) else 'Not a dict'}")
                    
                    # Check daily forecast
                    if 'daily_forecast' in weather_data:
                        daily_data = weather_data['daily_forecast']
                        print(f"   ✅ Daily forecast found: {len(daily_data)} entries")
                        
                        # Show first entry structure
                        if daily_data:
                            first_entry = daily_data[0]
                            print(f"   First entry type: {type(first_entry)}")
                            print(f"   First entry keys: {list(first_entry.keys()) if isinstance(first_entry, dict) else 'Not a dict'}")
                            
                            # Check for temperature data
                            if isinstance(first_entry, dict):
                                if 'temp_min' in first_entry:
                                    print(f"   ✅ temp_min found: {first_entry['temp_min']}")
                                else:
                                    print(f"   ❌ temp_min missing")
                                    
                                if 'temp_max' in first_entry:
                                    print(f"   ✅ temp_max found: {first_entry['temp_max']}")
                                else:
                                    print(f"   ❌ temp_max missing")
                                    
                                if 'date' in first_entry:
                                    print(f"   ✅ date found: {first_entry['date']}")
                                else:
                                    print(f"   ❌ date missing")
                    else:
                        print(f"   ❌ No daily_forecast in data")
                    
                    # Check hourly forecast
                    if 'hourly_forecast' in weather_data:
                        hourly_data = weather_data['hourly_forecast']
                        print(f"   ✅ Hourly forecast found: {len(hourly_data)} entries")
                        
                        # Show first entry structure
                        if hourly_data:
                            first_entry = hourly_data[0]
                            print(f"   First entry type: {type(first_entry)}")
                            print(f"   First entry keys: {list(first_entry.keys()) if isinstance(first_entry, dict) else 'Not a dict'}")
                            
                            # Check for rain data
                            if isinstance(first_entry, dict):
                                if 'rain_amount' in first_entry:
                                    print(f"   ✅ rain_amount found: {first_entry['rain_amount']}")
                                else:
                                    print(f"   ❌ rain_amount missing")
                                    
                                if 'temperature' in first_entry:
                                    print(f"   ✅ temperature found: {first_entry['temperature']}")
                                else:
                                    print(f"   ❌ temperature missing")
                    else:
                        print(f"   ❌ No hourly_forecast in data")
                        
                    # Check probability forecast
                    if 'probability_forecast' in weather_data:
                        prob_data = weather_data['probability_forecast']
                        print(f"   ✅ Probability forecast found: {len(prob_data)} entries")
                    else:
                        print(f"   ❌ No probability_forecast in data")
                        
                else:
                    print(f"   ❌ No data returned")
                    
            except Exception as e:
                print(f"   ❌ API call failed: {e}")
                import traceback
                traceback.print_exc()
            
            print()
        
        # Test specific date extraction
        print("📅 TESTING SPECIFIC DATE EXTRACTION:")
        print("-" * 40)
        
        try:
            # Get data for specific date
            weather_data = api.get_complete_forecast_data(47.638699, 6.846891, "TestDate")
            
            if weather_data and 'daily_forecast' in weather_data:
                daily_entries = weather_data['daily_forecast']
                target_date = "2025-08-02"
                
                print(f"Looking for date: {target_date}")
                print(f"Available dates: {[entry.get('date', 'NO_DATE') for entry in daily_entries]}")
                
                # Find entry for target date
                target_entry = None
                for entry in daily_entries:
                    if isinstance(entry, dict) and entry.get('date') == target_date:
                        target_entry = entry
                        break
                
                if target_entry:
                    print(f"✅ Found entry for {target_date}")
                    print(f"   temp_min: {target_entry.get('temp_min', 'MISSING')}")
                    print(f"   temp_max: {target_entry.get('temp_max', 'MISSING')}")
                else:
                    print(f"❌ No entry found for {target_date}")
                    
        except Exception as e:
            print(f"❌ Date extraction test failed: {e}")
        
        print()
        
        # Test my current extraction code
        print("🔧 TESTING MY CURRENT EXTRACTION CODE:")
        print("-" * 40)
        
        try:
            from src.weather.core.morning_evening_refactor import MorningEveningRefactor
            
            refactor = MorningEveningRefactor(config)
            
            # Test with mock data structure
            mock_weather_data = {
                'daily_forecast': [
                    {
                        'date': '2025-08-02',
                        'temp_min': 15.2,
                        'temp_max': 28.7
                    }
                ],
                'hourly_forecast': [
                    {
                        'timestamp': '2025-08-02T06:00:00',
                        'temperature': 16.1,
                        'rain_amount': 0.0
                    }
                ]
            }
            
            print("Testing with mock data structure...")
            
            # Test Night data processing
            try:
                night_data = refactor.process_night_data(mock_weather_data, "Test", date(2025, 8, 2), "morning")
                print(f"✅ Night processing: threshold={night_data.threshold_value}, max={night_data.max_value}")
            except Exception as e:
                print(f"❌ Night processing failed: {e}")
            
            # Test Day data processing
            try:
                day_data = refactor.process_day_data(mock_weather_data, "Test", date(2025, 8, 2), "morning")
                print(f"✅ Day processing: threshold={day_data.threshold_value}, max={day_data.max_value}")
            except Exception as e:
                print(f"❌ Day processing failed: {e}")
                
        except Exception as e:
            print(f"❌ Extraction code test failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        print("=" * 60)
        print("🎯 DEBUG SUMMARY:")
        print("=" * 60)
        print("1. API data structure analyzed")
        print("2. Date extraction tested")
        print("3. My extraction code tested")
        print("4. Issues identified in MY code")
        print()
        print("Next: Fix the data extraction logic in MY code!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_data_structure() 