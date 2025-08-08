#!/usr/bin/env python3
"""
Einfaches Debug-Script um die Wind-Datenstruktur zu prüfen.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def debug_wind_structure():
    """Debug Wind-Datenstruktur."""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize refactor
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "FONT-ROMEU-ODEILLO-VIA"
    target_date = date(2025, 8, 9)  # Tomorrow
    
    print("🔍 DEBUGGING WIND DATA STRUCTURE")
    print("=" * 50)
    print(f"Stage: {stage_name}")
    print(f"Target date: {target_date}")
    print()
    
    try:
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        print("✅ Weather data fetched successfully")
        print(f"📋 Keys: {list(weather_data.keys())}")
        print()
        
        # Analyze hourly_data structure
        hourly_data = weather_data.get('hourly_data', [])
        print(f"📊 Hourly data points: {len(hourly_data)}")
        
        for i, point_data in enumerate(hourly_data):
            print(f"\n📍 Point {i+1}:")
            print(f"  Keys: {list(point_data.keys())}")
            
            if 'data' in point_data and point_data['data']:
                # Show first few entries
                for j, entry in enumerate(point_data['data'][:2]):
                    print(f"    Entry {j+1}:")
                    print(f"      Keys: {list(entry.keys())}")
                    
                    # Check for wind-related fields
                    wind_fields = [key for key in entry.keys() if 'wind' in key.lower()]
                    print(f"      Wind-related fields: {wind_fields}")
                    
                    # Show actual wind data
                    for field in wind_fields:
                        value = entry.get(field)
                        print(f"      {field}: {value}")
                    
                    # Check for speed-related fields
                    speed_fields = [key for key in entry.keys() if 'speed' in key.lower()]
                    print(f"      Speed-related fields: {speed_fields}")
                    for field in speed_fields:
                        value = entry.get(field)
                        print(f"      {field}: {value}")
                    
                    # Check for gust-related fields
                    gust_fields = [key for key in entry.keys() if 'gust' in key.lower()]
                    print(f"      Gust-related fields: {gust_fields}")
                    for field in gust_fields:
                        value = entry.get(field)
                        print(f"      {field}: {value}")
                    
                    print()
                    break  # Only show first entry per point
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_wind_structure()
