#!/usr/bin/env python3
"""
Test Rain(mm) with different dates to find one with actual rain data
"""

import json
from datetime import date, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.config.config_loader import load_config

def test_rain_mm_with_different_dates():
    """Test Rain(mm) with different dates to find one with actual rain data"""
    
    print("=" * 80)
    print("TESTING RAIN(MM) WITH DIFFERENT DATES")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    stage_name = "Test"
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test different dates
    test_dates = [
        date(2025, 8, 2),   # Original test date
        date(2025, 8, 3),   # Tomorrow
        date(2025, 8, 4),   # Day after tomorrow
        date(2025, 8, 5),   # 3 days ahead
        date(2025, 8, 6),   # 4 days ahead
        date(2025, 8, 7),   # 5 days ahead
        date(2025, 8, 8),   # 6 days ahead
        date(2025, 8, 9),   # 7 days ahead
        date(2025, 8, 10),  # 8 days ahead
        date(2025, 8, 11),  # 9 days ahead
    ]
    
    for test_date in test_dates:
        print(f"\n{'='*60}")
        print(f"TESTING DATE: {test_date}")
        print(f"{'='*60}")
        
        # Fetch weather data
        print("Fetching weather data...")
        weather_data = refactor.fetch_weather_data(stage_name, test_date)
        
        if not weather_data:
            print("❌ Failed to fetch weather data")
            continue
        
        print("✅ Weather data fetched successfully")
        
        # Process Rain(mm) data
        rain_mm_data = refactor.process_rain_mm_data(weather_data, stage_name, test_date, "morning")
        
        # Check if we have any rain data
        has_rain = False
        max_rain = 0
        
        if hasattr(refactor, '_last_weather_data') and refactor._last_weather_data:
            hourly_data = refactor._last_weather_data.get('hourly_data', [])
            
            for i, point_data in enumerate(hourly_data):
                if 'data' in point_data:
                    for hour_data in point_data['data']:
                        if 'dt' in hour_data:
                            from datetime import datetime
                            hour_time = datetime.fromtimestamp(hour_data['dt'])
                            hour_date = hour_time.date()
                            if hour_date == test_date:
                                rain_value = hour_data.get('rain', {}).get('1h', 0)
                                if rain_value > 0:
                                    has_rain = True
                                    max_rain = max(max_rain, rain_value)
        
        print(f"Has rain data: {has_rain}")
        print(f"Max rain value: {max_rain}")
        
        if has_rain:
            print("🎉 FOUND DATE WITH RAIN DATA!")
            print(f"Date: {test_date}")
            print(f"Max rain: {max_rain} mm")
            
            # Show some sample data
            print("\nSample rain data:")
            if hasattr(refactor, '_last_weather_data') and refactor._last_weather_data:
                hourly_data = refactor._last_weather_data.get('hourly_data', [])
                
                for i, point_data in enumerate(hourly_data):
                    if 'data' in point_data:
                        print(f"\nPoint {i+1}:")
                        for hour_data in point_data['data']:
                            if 'dt' in hour_data:
                                from datetime import datetime
                                hour_time = datetime.fromtimestamp(hour_data['dt'])
                                hour_date = hour_time.date()
                                if hour_date == test_date:
                                    rain_value = hour_data.get('rain', {}).get('1h', 0)
                                    if rain_value > 0:
                                        print(f"  {hour_time.hour:02d}:00 - {rain_value} mm")
            
            return test_date
        
        print("❌ No rain data found for this date")
    
    print("\n" + "="*80)
    print("NO DATE WITH RAIN DATA FOUND!")
    print("="*80)
    print("All tested dates have 0mm rain. This might be:")
    print("1. A dry period in the forecast")
    print("2. An issue with the API data")
    print("3. The test coordinates are in a dry area")
    
    return None

if __name__ == "__main__":
    test_rain_mm_with_different_dates() 