#!/usr/bin/env python3
"""
Debug script for Rain(mm) function - analyze why it's not detecting rain in Belfort
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, datetime
import yaml
import json

def load_config():
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def debug_rain_mm_data():
    """Debug Rain(mm) function to understand why it's not detecting rain."""
    
    print("Rain(mm) FUNCTION - DEBUG ANALYSIS")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"  # Use "Test" stage which should include Belfort
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print(f"Rain threshold: {config.get('thresholds', {}).get('rain_amount', 0.5)}")
    print()
    
    # Test MORNING report
    print("Debugging MORNING report...")
    try:
        # Fetch weather data first
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        print(f"Weather data keys: {list(weather_data.keys())}")
        
        # Check hourly data
        hourly_data = weather_data.get('hourly_data', [])
        print(f"Number of hourly data points: {len(hourly_data)}")
        
        for i, point_data in enumerate(hourly_data):
            print(f"\nPoint {i+1}:")
            if 'data' in point_data:
                data = point_data['data']
                print(f"  Number of hourly entries: {len(data)}")
                
                # Check for rain data
                rain_values = []
                for hour_data in data:
                    if 'dt' in hour_data:
                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                        hour_date = hour_time.date()
                        
                        if hour_date == target_date:
                            # Check time filter (4:00-19:00)
                            hour = hour_time.hour
                            if 4 <= hour <= 19:
                                rain_value = hour_data.get('rain', {}).get('1h', 0)
                                rain_values.append((hour, rain_value))
                
                print(f"  Rain values (4:00-19:00): {rain_values}")
                
                # Check if any rain above threshold
                threshold = config.get('thresholds', {}).get('rain_amount', 0.5)
                above_threshold = [h for h, r in rain_values if r >= threshold]
                print(f"  Rain above threshold ({threshold}mm): {above_threshold}")
        
        # Now test the Rain(mm) function directly
        print(f"\nTesting Rain(mm) function directly...")
        rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        
        print(f"Rain(mm) result:")
        print(f"  threshold_value: {rain_mm_result.threshold_value}")
        print(f"  threshold_time: {rain_mm_result.threshold_time}")
        print(f"  max_value: {rain_mm_result.max_value}")
        print(f"  max_time: {rain_mm_result.max_time}")
        print(f"  geo_points: {rain_mm_result.geo_points}")
        
        # Generate full report to see what happens
        print(f"\nGenerating full report...")
        try:
            result_output, debug_output = refactor.generate_report(stage_name, "morning", target_date.strftime('%Y-%m-%d'))
            
            print(f"Result Output: {result_output}")
            
            # Check if Rain(mm) section is in debug output
            if "RAIN(MM)" in debug_output:
                print("Rain(mm) section found in debug output")
            else:
                print("Rain(mm) section NOT found in debug output")
                
        except Exception as e:
            print(f"Error generating report: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rain_mm_data() 