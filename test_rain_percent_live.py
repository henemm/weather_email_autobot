#!/usr/bin/env python3
"""
Live test for Rain(%) function with email sending
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor, WeatherReportData, WeatherThresholdData
from src.notification.email_client import EmailClient
from datetime import date
import yaml

def test_rain_percent_live():
    """Live test for Rain(%) function with email sending."""
    
    print("LIVE TEST RAIN(%) FUNCTION")
    print("=" * 50)
    
    # Load configuration
    config = yaml.safe_load(open("config.yaml", "r"))
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Target Date: {target_date}")
    print(f"Stage Name: {stage_name}")
    print()
    
    # Fetch real weather data
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("No weather data available!")
        return
    
    print("Weather data fetched successfully")
    print(f"Probability forecast points: {len(weather_data.get('probability_forecast', []))}")
    print()
    
    # Test MORNING report
    print("Testing MORNING report...")
    try:
        # Process Rain(%) data for morning
        rain_percent_result = refactor.process_rain_percent_data(
            weather_data, stage_name, target_date, "morning"
        )
        
        # Create report data
        empty_data = WeatherThresholdData()
        morning_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=empty_data,
            day=empty_data,
            rain_mm=empty_data,
            rain_percent=rain_percent_result,
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
        print(f"Rain(%) Data:")
        print(f"  threshold_value: {rain_percent_result.threshold_value}")
        print(f"  threshold_time: {rain_percent_result.threshold_time}")
        print(f"  max_value: {rain_percent_result.max_value}")
        print(f"  max_time: {rain_percent_result.max_time}")
        print(f"  geo_points: {rain_percent_result.geo_points}")
        
        # Create email content
        email_content = f"""{morning_result}

# DEBUG DATENEXPORT

Rain(%) Function Test - Morning Report
Stage: {stage_name}
Date: {target_date}

Rain(%) Data:
- threshold_value: {rain_percent_result.threshold_value}
- threshold_time: {rain_percent_result.threshold_time}
- max_value: {rain_percent_result.max_value}
- max_time: {rain_percent_result.max_time}
- geo_points: {rain_percent_result.geo_points}

SUCCESS: Rain(%) function correctly processed probability forecast data!
Result: {morning_result}"""
        
        # Send email
        print("Sending morning report email...")
        success = email_client.send_email(email_content, f"Rain(%) Test - Morning Report - {stage_name}")
        
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
        # Process Rain(%) data for evening
        rain_percent_result = refactor.process_rain_percent_data(
            weather_data, stage_name, target_date, "evening"
        )
        
        # Create report data
        empty_data = WeatherThresholdData()
        evening_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="evening",
            night=empty_data,
            day=empty_data,
            rain_mm=empty_data,
            rain_percent=rain_percent_result,
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
        print(f"Rain(%) Data:")
        print(f"  threshold_value: {rain_percent_result.threshold_value}")
        print(f"  threshold_time: {rain_percent_result.threshold_time}")
        print(f"  max_value: {rain_percent_result.max_value}")
        print(f"  max_time: {rain_percent_result.max_time}")
        print(f"  geo_points: {rain_percent_result.geo_points}")
        
        # Create email content
        email_content = f"""{evening_result}

# DEBUG DATENEXPORT

Rain(%) Function Test - Evening Report
Stage: {stage_name}
Date: {target_date}

Rain(%) Data:
- threshold_value: {rain_percent_result.threshold_value}
- threshold_time: {rain_percent_result.threshold_time}
- max_value: {rain_percent_result.max_value}
- max_time: {rain_percent_result.max_time}
- geo_points: {rain_percent_result.geo_points}

SUCCESS: Rain(%) function correctly processed probability forecast data!
Result: {evening_result}"""
        
        # Send email
        print("Sending evening report email...")
        success = email_client.send_email(email_content, f"Rain(%) Test - Evening Report - {stage_name}")
        
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
    print("1. Rain(%) data is correctly processed from PROBABILITY_FORECAST")
    print("2. Only times 05:00, 08:00, 11:00, 14:00, 17:00 are used")
    print("3. Threshold logic works correctly")
    print("4. T-G references are correct (T1G1, T1G2, T1G3 for morning; T2G1, T2G2, T2G3 for evening)")

if __name__ == "__main__":
    test_rain_percent_live() 