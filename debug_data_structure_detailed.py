#!/usr/bin/env python3
"""
DEBUG DATA STRUCTURE DETAILED
=============================
Understand the exact structure of the API data to fix my extraction code.
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

def debug_data_structure_detailed():
    """Debug the exact data structure"""
    print("🔍 DEBUG DATA STRUCTURE DETAILED")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        config = load_config()
        api = EnhancedMeteoFranceAPI()
        
        # Test with one coordinate
        lat, lon = 47.638699, 6.846891
        
        print(f"📍 Testing coordinate: ({lat}, {lon})")
        print()
        
        try:
            # Call API
            weather_data = api.get_complete_forecast_data(lat, lon, "TestPoint")
            
            print(f"✅ API call successful")
            print(f"   Data type: {type(weather_data)}")
            print()
            
            if weather_data:
                print("📊 DATA STRUCTURE ANALYSIS:")
                print("-" * 40)
                
                # Check all keys
                print(f"Available keys: {list(weather_data.keys())}")
                print()
                
                # Analyze daily_forecast specifically
                if 'daily_forecast' in weather_data:
                    daily_data = weather_data['daily_forecast']
                    print(f"📅 DAILY_FORECAST ANALYSIS:")
                    print(f"   Type: {type(daily_data)}")
                    print(f"   Length: {len(daily_data) if hasattr(daily_data, '__len__') else 'No length'}")
                    
                    if isinstance(daily_data, dict):
                        print(f"   Keys: {list(daily_data.keys())}")
                        
                        # Check if it's a single entry or multiple entries
                        if len(daily_data) == 1:
                            # Single entry - get the first (and only) key
                            first_key = list(daily_data.keys())[0]
                            first_entry = daily_data[first_key]
                            print(f"   Single entry key: {first_key}")
                            print(f"   Entry type: {type(first_entry)}")
                            
                            if isinstance(first_entry, dict):
                                print(f"   Entry keys: {list(first_entry.keys())}")
                                
                                # Check for temperature data
                                if 'temp_min' in first_entry:
                                    print(f"   ✅ temp_min: {first_entry['temp_min']}")
                                else:
                                    print(f"   ❌ temp_min missing")
                                    
                                if 'temp_max' in first_entry:
                                    print(f"   ✅ temp_max: {first_entry['temp_max']}")
                                else:
                                    print(f"   ❌ temp_max missing")
                                    
                                if 'date' in first_entry:
                                    print(f"   ✅ date: {first_entry['date']}")
                                else:
                                    print(f"   ❌ date missing")
                        else:
                            # Multiple entries
                            print(f"   Multiple entries: {list(daily_data.keys())}")
                            
                    elif isinstance(daily_data, list):
                        print(f"   List structure with {len(daily_data)} items")
                        if daily_data:
                            first_item = daily_data[0]
                            print(f"   First item type: {type(first_item)}")
                            if isinstance(first_item, dict):
                                print(f"   First item keys: {list(first_item.keys())}")
                    else:
                        print(f"   Unknown structure: {daily_data}")
                        
                else:
                    print(f"   ❌ No daily_forecast in data")
                
                print()
                
                # Analyze hourly_data specifically
                if 'hourly_data' in weather_data:
                    hourly_data = weather_data['hourly_data']
                    print(f"⏰ HOURLY_DATA ANALYSIS:")
                    print(f"   Type: {type(hourly_data)}")
                    print(f"   Length: {len(hourly_data) if hasattr(hourly_data, '__len__') else 'No length'}")
                    
                    if isinstance(hourly_data, list) and hourly_data:
                        first_item = hourly_data[0]
                        print(f"   First item type: {type(first_item)}")
                        if isinstance(first_item, dict):
                            print(f"   First item keys: {list(first_item.keys())}")
                            
                            # Check for rain data
                            if 'rain_amount' in first_item:
                                print(f"   ✅ rain_amount: {first_item['rain_amount']}")
                            else:
                                print(f"   ❌ rain_amount missing")
                                
                            if 'temperature' in first_item:
                                print(f"   ✅ temperature: {first_item['temperature']}")
                            else:
                                print(f"   ❌ temperature missing")
                    else:
                        print(f"   Unknown structure: {hourly_data}")
                        
                else:
                    print(f"   ❌ No hourly_data in data")
                
                print()
                
                # Show raw data for debugging
                print("🔍 RAW DATA SAMPLE:")
                print("-" * 30)
                
                # Show daily_forecast structure
                if 'daily_forecast' in weather_data:
                    daily_raw = weather_data['daily_forecast']
                    print(f"Daily forecast raw: {type(daily_raw)}")
                    if isinstance(daily_raw, dict):
                        print(f"Keys: {list(daily_raw.keys())}")
                        for key, value in daily_raw.items():
                            print(f"  {key}: {type(value)} = {value}")
                    elif isinstance(daily_raw, list):
                        print(f"List with {len(daily_raw)} items")
                        if daily_raw:
                            print(f"  First item: {daily_raw[0]}")
                
                print()
                
                # Test my extraction logic
                print("🔧 TESTING MY EXTRACTION LOGIC:")
                print("-" * 40)
                
                # Simulate what my code should do
                if 'daily_forecast' in weather_data:
                    daily_data = weather_data['daily_forecast']
                    
                    if isinstance(daily_data, dict):
                        # Handle dict structure
                        print("Handling dict structure...")
                        
                        # Get the first (and probably only) entry
                        if daily_data:
                            first_key = list(daily_data.keys())[0]
                            entry = daily_data[first_key]
                            
                            if isinstance(entry, dict):
                                temp_min = entry.get('temp_min')
                                temp_max = entry.get('temp_max')
                                entry_date = entry.get('date')
                                
                                print(f"✅ Extracted: temp_min={temp_min}, temp_max={temp_max}, date={entry_date}")
                            else:
                                print(f"❌ Entry is not a dict: {type(entry)}")
                        else:
                            print(f"❌ Daily data is empty")
                            
                    elif isinstance(daily_data, list):
                        # Handle list structure
                        print("Handling list structure...")
                        
                        if daily_data:
                            entry = daily_data[0]
                            if isinstance(entry, dict):
                                temp_min = entry.get('temp_min')
                                temp_max = entry.get('temp_max')
                                entry_date = entry.get('date')
                                
                                print(f"✅ Extracted: temp_min={temp_min}, temp_max={temp_max}, date={entry_date}")
                            else:
                                print(f"❌ Entry is not a dict: {type(entry)}")
                        else:
                            print(f"❌ Daily data list is empty")
                    else:
                        print(f"❌ Unknown daily_data structure: {type(daily_data)}")
                        
        except Exception as e:
            print(f"❌ API call failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        print("=" * 60)
        print("🎯 DEBUG SUMMARY:")
        print("=" * 60)
        print("1. Exact data structure identified")
        print("2. My extraction logic tested")
        print("3. Correct approach determined")
        print()
        print("Next: Fix the extraction code in MorningEveningRefactor!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_structure_detailed() 