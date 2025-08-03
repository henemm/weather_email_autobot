#!/usr/bin/env python3
"""
Check Rain(mm) values and compare with formatted output
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def load_config():
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def check_rain_mm_values():
    """Check Rain(mm) values and compare with formatted output."""
    
    print("Rain(mm) VALUES CHECK")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print(f"Rain threshold: {config.get('thresholds', {}).get('rain_amount', 0.5)}")
    print()
    
    try:
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        # Process Rain(mm) data
        rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        
        print("ACTUAL Rain(mm) Data:")
        print(f"  threshold_value: {rain_mm_result.threshold_value}")
        print(f"  threshold_time: {rain_mm_result.threshold_time}")
        print(f"  max_value: {rain_mm_result.max_value}")
        print(f"  max_time: {rain_mm_result.max_time}")
        print(f"  geo_points: {rain_mm_result.geo_points}")
        print()
        
        # Create minimal report data
        from src.weather.core.morning_evening_refactor import WeatherReportData, WeatherThresholdData
        
        empty_data = WeatherThresholdData()
        
        report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=empty_data,
            day=empty_data,
            rain_mm=rain_mm_result,
            rain_percent=empty_data,
            wind=empty_data,
            gust=empty_data,
            thunderstorm=empty_data,
            thunderstorm_plus_one=empty_data,
            risks=empty_data,
            risk_zonal=empty_data
        )
        
        # Generate result output
        result_output = refactor.format_result_output(report_data)
        
        print("FORMATTED Result Output:")
        print(f"  {result_output}")
        print()
        
        # Extract Rain(mm) part
        if "R" in result_output:
            rain_part = result_output.split("R")[1].split()[0]
            print(f"Rain(mm) part: R{rain_part}")
            
            # Check if format is correct
            if "@" in rain_part and "(" in rain_part and ")" in rain_part:
                print("✅ Format is correct: R{threshold}@{time}({max}@{max_time})")
                
                # Parse the values
                threshold_part = rain_part.split("(")[0]
                threshold_parts = threshold_part.split("@")
                threshold_value = threshold_parts[0]
                threshold_time = threshold_parts[1]
                
                max_part = rain_part.split("(")[1].rstrip(")")
                max_parts = max_part.split("@")
                max_value = max_parts[0]
                max_time = max_parts[1]
                
                print(f"\nPARSED VALUES:")
                print(f"  threshold_value: {threshold_value}")
                print(f"  threshold_time: {threshold_time}")
                print(f"  max_value: {max_value}")
                print(f"  max_time: {max_time}")
                
                # Compare with actual data
                print(f"\nCOMPARISON:")
                print(f"  threshold_value: {'✅' if float(threshold_value) == rain_mm_result.threshold_value else '❌'}")
                print(f"  threshold_time: {'✅' if threshold_time == str(rain_mm_result.threshold_time) else '❌'}")
                print(f"  max_value: {'✅' if float(max_value) == rain_mm_result.max_value else '❌'}")
                print(f"  max_time: {'✅' if max_time == str(rain_mm_result.max_time) else '❌'}")
                
                # Check time format (no leading zeros)
                print(f"\nTIME FORMAT CHECK:")
                print(f"  threshold_time format: {'✅' if not threshold_time.startswith('0') else '❌'}")
                print(f"  max_time format: {'✅' if not max_time.startswith('0') else '❌'}")
                
            else:
                print("❌ Format is incorrect")
        else:
            print("❌ No 'R' found in Result Output")
        
    except Exception as e:
        print(f"Check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_rain_mm_values() 