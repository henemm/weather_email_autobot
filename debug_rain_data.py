#!/usr/bin/env python3
"""
Debug script to investigate WeatherEntry structure for rain data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI

def debug_weather_entry_structure():
    """Debug the WeatherEntry structure to find rain attribute."""
    
    print("🔍 DEBUGGING WEATHERENTRY STRUCTURE")
    print("=" * 50)
    
    # Initialize API
    api = EnhancedMeteoFranceAPI()
    
    # Fetch data for a test point
    lat, lon = 42.219882, 8.980494  # Petra point 1
    point_name = "Petra_point_1"
    
    print(f"📡 Fetching data for {point_name} ({lat}, {lon})...")
    
    try:
        point_data = api.get_complete_forecast_data(lat, lon, point_name)
        
        # Get hourly data
        hourly_data = point_data.get('hourly_data', [])
        print(f"📊 Found {len(hourly_data)} hourly entries")
        
        if hourly_data:
            # Examine first entry
            first_entry = hourly_data[0]
            print(f"\n🔍 First entry type: {type(first_entry)}")
            print(f"🔍 First entry: {first_entry}")
            
            # List all attributes
            if hasattr(first_entry, '__dict__'):
                print(f"\n📋 All attributes:")
                for attr_name, attr_value in first_entry.__dict__.items():
                    print(f"  {attr_name}: {attr_value}")
            
            # Check for rain-related attributes
            print(f"\n🌧️  Rain-related attributes:")
            for attr_name in dir(first_entry):
                if 'rain' in attr_name.lower() or 'precip' in attr_name.lower():
                    try:
                        attr_value = getattr(first_entry, attr_name)
                        print(f"  {attr_name}: {attr_value}")
                    except Exception as e:
                        print(f"  {attr_name}: ERROR - {e}")
            
            # Check for timestamp
            print(f"\n⏰ Timestamp attributes:")
            for attr_name in dir(first_entry):
                if 'time' in attr_name.lower() or 'date' in attr_name.lower():
                    try:
                        attr_value = getattr(first_entry, attr_name)
                        print(f"  {attr_name}: {attr_value}")
                    except Exception as e:
                        print(f"  {attr_name}: ERROR - {e}")
            
            # Try to access common weather attributes
            print(f"\n🌤️  Common weather attributes:")
            common_attrs = ['temperature', 'humidity', 'pressure', 'wind_speed', 'wind_direction']
            for attr_name in common_attrs:
                try:
                    attr_value = getattr(first_entry, attr_name, None)
                    print(f"  {attr_name}: {attr_value}")
                except Exception as e:
                    print(f"  {attr_name}: ERROR - {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_weather_entry_structure() 