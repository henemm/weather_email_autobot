#!/usr/bin/env python3
"""
Simple test script for Rain(mm) function - isolate the issue
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

def simple_rain_mm_test():
    """Simple test for Rain(mm) function."""
    
    print("Rain(mm) FUNCTION - SIMPLE TEST")
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
    print("Testing MORNING report...")
    try:
        # Fetch weather data first
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        print(f"Weather data fetched successfully")
        
        # Test Rain(mm) function directly
        print(f"\nTesting Rain(mm) function directly...")
        rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        
        print(f"Rain(mm) result:")
        print(f"  threshold_value: {rain_mm_result.threshold_value}")
        print(f"  threshold_time: {rain_mm_result.threshold_time}")
        print(f"  max_value: {rain_mm_result.max_value}")
        print(f"  max_time: {rain_mm_result.max_time}")
        print(f"  geo_points: {rain_mm_result.geo_points}")
        
        # Test format_result_output
        print(f"\nTesting format_result_output...")
        
        # Create minimal report data for testing
        from src.weather.core.morning_evening_refactor import WeatherReportData, WeatherThresholdData
        
        # Create empty data for other elements
        empty_data = WeatherThresholdData()
        
        report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=empty_data,
            day=empty_data,
            rain_mm=rain_mm_result,  # Use the actual rain_mm result
            rain_percent=empty_data,
            wind=empty_data,
            gust=empty_data,
            thunderstorm=empty_data,
            thunderstorm_plus_one=empty_data,
            risks=empty_data,
            risk_zonal=empty_data
        )
        
        # Test result output formatting
        result_output = refactor.format_result_output(report_data)
        print(f"Result Output: {result_output}")
        
        # Check if Rain(mm) is present
        if "R" in result_output:
            rain_part = result_output.split("R")[1].split()[0]  # Extract R{value}
            print(f"Rain(mm) Result: R{rain_part}")
            
            if rain_part != "-":
                print("SUCCESS: Rain(mm) detected and formatted correctly!")
            else:
                print("FAILURE: No rain detected")
        else:
            print("No 'R' found in Result Output")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_rain_mm_test() 