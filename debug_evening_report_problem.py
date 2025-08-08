#!/usr/bin/env python3
"""
DEBUG EVENING REPORT PROBLEM
============================
Debug the specific evening report problem with day and rain percent data.
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def debug_evening_report_problem():
    """Debug the evening report problem."""
    print("🔍 DEBUG EVENING REPORT PROBLEM")
    print("=" * 50)
    
    try:
        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
        stage_name = "Test"
        target_date = date(2025, 8, 3)
        report_type = "evening"
        
        print(f"📅 Target Date: {target_date}")
        print(f"📍 Stage: {stage_name}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Fetch weather data first
        print("1️⃣ FETCHING WEATHER DATA:")
        print("-" * 30)
        
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if weather_data:
            print("✅ Weather data fetched successfully")
            print(f"   Keys: {list(weather_data.keys())}")
        else:
            print("❌ No weather data fetched")
            return
        
        print()
        
        # Test day data processing specifically
        print("2️⃣ TESTING DAY DATA PROCESSING:")
        print("-" * 30)
        
        try:
            day_data = refactor.process_day_data(weather_data, stage_name, target_date, report_type)
            print(f"✅ Day processing successful")
            print(f"   Threshold value: {day_data.threshold_value}")
            print(f"   Threshold time: {day_data.threshold_time}")
            print(f"   Max value: {day_data.max_value}")
            print(f"   Max time: {day_data.max_time}")
            print(f"   Geo points: {len(day_data.geo_points) if day_data.geo_points else 0}")
            
            if day_data.geo_points:
                print("   Geo points data:")
                for i, point in enumerate(day_data.geo_points):
                    print(f"     Point {i+1}: {point}")
                    
        except Exception as e:
            print(f"❌ Day processing failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        print()
        
        # Test rain percent data processing specifically
        print("3️⃣ TESTING RAIN PERCENT DATA PROCESSING:")
        print("-" * 30)
        
        try:
            rain_percent_data = refactor.process_rain_percent_data(weather_data, stage_name, target_date, report_type)
            print(f"✅ Rain percent processing successful")
            print(f"   Threshold value: {rain_percent_data.threshold_value}")
            print(f"   Threshold time: {rain_percent_data.threshold_time}")
            print(f"   Max value: {rain_percent_data.max_value}")
            print(f"   Max time: {rain_percent_data.max_time}")
            print(f"   Geo points: {len(rain_percent_data.geo_points) if rain_percent_data.geo_points else 0}")
            
            if rain_percent_data.geo_points:
                print("   Geo points data:")
                for i, point in enumerate(rain_percent_data.geo_points):
                    print(f"     Point {i+1}: {point}")
                    
        except Exception as e:
            print(f"❌ Rain percent processing failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        print()
        
        # Compare with morning report
        print("4️⃣ COMPARING WITH MORNING REPORT:")
        print("-" * 30)
        
        try:
            morning_day_data = refactor.process_day_data(weather_data, stage_name, target_date, "morning")
            print(f"Morning Day - Threshold: {morning_day_data.threshold_value}, Max: {morning_day_data.max_value}")
            
            evening_day_data = refactor.process_day_data(weather_data, stage_name, target_date, "evening")
            print(f"Evening Day - Threshold: {evening_day_data.threshold_value}, Max: {evening_day_data.max_value}")
            
            if morning_day_data.threshold_value != evening_day_data.threshold_value:
                print("❌ DIFFERENCE FOUND: Day data differs between morning and evening!")
            else:
                print("✅ Day data is identical between morning and evening")
                
        except Exception as e:
            print(f"❌ Comparison failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_evening_report_problem() 