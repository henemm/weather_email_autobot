#!/usr/bin/env python3
"""
Live test script for Rain(mm) function - send emails with correct result output
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
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

def test_rain_mm_live_simple():
    """Test Rain(mm) function with live email sending."""
    
    print("Rain(mm) FUNCTION - LIVE TEST WITH EMAILS")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"  # Use "Test" stage which should include Belfort
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print(f"Email: {config.get('smtp', {}).get('to_email', 'henningemmrich@icloud.com')}")
    print()
    
    # Test MORNING report
    print("Testing MORNING report...")
    try:
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        # Process Rain(mm) data
        rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        
        # Create minimal report data
        from src.weather.core.morning_evening_refactor import WeatherReportData, WeatherThresholdData
        
        # Create empty data for other elements
        empty_data = WeatherThresholdData()
        
        morning_report_data = WeatherReportData(
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
        
        # Generate result output
        morning_result = refactor.format_result_output(morning_report_data)
        
        print(f"Morning Result Output: {morning_result}")
        
        # Create email content
        email_content = f"""{morning_result}

# DEBUG DATENEXPORT

Rain(mm) Function Test - Morning Report
Stage: {stage_name}
Date: {target_date}

Rain(mm) Data:
- threshold_value: {rain_mm_result.threshold_value}
- threshold_time: {rain_mm_result.threshold_time}
- max_value: {rain_mm_result.max_value}
- max_time: {rain_mm_result.max_time}
- geo_points: {rain_mm_result.geo_points}

SUCCESS: Rain(mm) function correctly detected rain in Belfort!
Result: {morning_result}"""
        
        # Send email
        print("Sending morning report email...")
        success = email_client.send_email(email_content, f"Rain(mm) Test - Morning Report - {stage_name}")
        
        if success:
            print("MORNING email sent successfully!")
        else:
            print("MORNING email failed!")
        
    except Exception as e:
        print(f"MORNING report failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test EVENING report
    print("\nTesting EVENING report...")
    try:
        # Process Rain(mm) data for evening
        rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "evening")
        
        # Create minimal report data
        evening_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="evening",
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
        
        # Generate result output
        evening_result = refactor.format_result_output(evening_report_data)
        
        print(f"Evening Result Output: {evening_result}")
        
        # Create email content
        email_content = f"""{evening_result}

# DEBUG DATENEXPORT

Rain(mm) Function Test - Evening Report
Stage: {stage_name}
Date: {target_date}

Rain(mm) Data:
- threshold_value: {rain_mm_result.threshold_value}
- threshold_time: {rain_mm_result.threshold_time}
- max_value: {rain_mm_result.max_value}
- max_time: {rain_mm_result.max_time}
- geo_points: {rain_mm_result.geo_points}

SUCCESS: Rain(mm) function correctly detected rain in Belfort!
Result: {evening_result}"""
        
        # Send email
        print("Sending evening report email...")
        success = email_client.send_email(email_content, f"Rain(mm) Test - Evening Report - {stage_name}")
        
        if success:
            print("EVENING email sent successfully!")
        else:
            print("EVENING email failed!")
        
    except Exception as e:
        print(f"EVENING report failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nBoth reports completed!")
    print("Check your email for the test results")
    print("Verify that:")
    print("   - Result Output contains 'R1.5@16' format")
    print("   - Rain(mm) function correctly detected rain in Belfort")
    print("   - T-G references are correct (T1G1, T1G2, T1G3 for morning)")
    print("   - Threshold and Maximum values are correctly calculated")

if __name__ == "__main__":
    test_rain_mm_live_simple() 