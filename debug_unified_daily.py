#!/usr/bin/env python3
"""
Debug Unified Daily Processing - Test _process_unified_daily_data function
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml
from datetime import datetime

def main():
    print("🔍 DEBUG UNIFIED DAILY PROCESSING")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "Vergio"
    date_str = "2025-08-02"
    report_type = "evening"
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {date_str}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    try:
        # Fetch weather data
        print("🔍 Fetching weather data...")
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        print(f"📊 Weather data keys: {list(weather_data.keys())}")
        
        # Check daily_data structure
        daily_data = weather_data.get('daily_data', [])
        print(f"📊 Daily data length: {len(daily_data)}")
        
        for i, point_data in enumerate(daily_data):
            print(f"📊 Point {i}: {list(point_data.keys())}")
            if 'data' in point_data:
                print(f"📊 Point {i} data length: {len(point_data['data'])}")
                if point_data['data']:
                    print(f"📊 Point {i} first entry: {point_data['data'][0]}")
        
        # Test unified daily processing
        print("\n🔍 Testing _process_unified_daily_data...")
        data_extractor = lambda d: d.get('temperature', {}).get('min')
        
        result = refactor._process_unified_daily_data(
            weather_data=weather_data,
            target_date=target_date,
            data_extractor=data_extractor,
            report_type=report_type,
            data_type='night'
        )
        
        print(f"📊 Result: {result}")
        print(f"📊 Threshold value: {result.threshold_value}")
        print(f"📊 Max value: {result.max_value}")
        print(f"📊 Geo points: {result.geo_points}")
        
        # Check if geo_points are empty
        if not result.geo_points:
            print("❌ PROBLEM: Geo points are empty!")
        else:
            print(f"✅ Geo points found: {len(result.geo_points)}")
            for i, point in enumerate(result.geo_points):
                print(f"📊 Point {i}: {point}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 