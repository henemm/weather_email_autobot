#!/usr/bin/env python3
"""
Debug Daily Forecast Structure - Check actual MeteoFrance API response
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
from datetime import datetime

def main():
    print("🔍 DEBUG DAILY FORECAST STRUCTURE")
    print("=" * 50)
    
    # Test with Belfort coordinates (T1G1)
    lat, lon = 47.638699, 6.846891
    point_name = "Belfort_debug"
    
    print(f"📍 Testing: {point_name}")
    print(f"📍 Coordinates: {lat}, {lon}")
    print()
    
    try:
        # Initialize API
        api = EnhancedMeteoFranceAPI()
        
        # Fetch data
        print("🔍 Fetching data from MeteoFrance...")
        data = api.get_complete_forecast_data(lat, lon, point_name)
        
        print("📊 COMPLETE DATA STRUCTURE:")
        print("=" * 40)
        print(f"Top-level keys: {list(data.keys())}")
        print()
        
        # Check daily_forecast
        daily_forecast = data.get('daily_forecast', {})
        print(f"daily_forecast keys: {list(daily_forecast.keys())}")
        print()
        
        # Check each key in daily_forecast
        for key, value in daily_forecast.items():
            print(f"📅 {key}:")
            if isinstance(value, list):
                print(f"  Type: list, Length: {len(value)}")
                if len(value) > 0:
                    print(f"  First item: {value[0]}")
                    if len(value) > 1:
                        print(f"  Second item: {value[1]}")
            elif isinstance(value, dict):
                print(f"  Type: dict, Keys: {list(value.keys())}")
                print(f"  Content: {value}")
            else:
                print(f"  Type: {type(value)}, Value: {value}")
            print()
        
        # Look for temperature data
        print("🌡️ LOOKING FOR TEMPERATURE DATA:")
        print("=" * 40)
        
        # Check if 'daily' exists
        if 'daily' in daily_forecast:
            daily_data = daily_forecast['daily']
            print(f"Found 'daily' key with {len(daily_data)} entries")
            
            # Check first few entries
            for i, entry in enumerate(daily_data[:3]):
                print(f"Entry {i}:")
                print(f"  Keys: {list(entry.keys())}")
                print(f"  Content: {entry}")
                print()
        else:
            print("❌ No 'daily' key found!")
            
            # Check other possible keys
            for key, value in daily_forecast.items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"Checking {key}:")
                    first_item = value[0]
                    print(f"  First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                    print(f"  First item: {first_item}")
                    print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 