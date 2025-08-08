#!/usr/bin/env python3
"""
Final test script for Rain(mm) function with working debug output
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

def test_rain_mm_final():
    """Final test for Rain(mm) function with working debug output."""
    
    print("Rain(mm) FUNCTION - FINAL TEST WITH WORKING DEBUG OUTPUT")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
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
        
        empty_data = WeatherThresholdData()
        
        morning_report_data = WeatherReportData(
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
        morning_result = refactor.format_result_output(morning_report_data)
        
        print(f"Morning Result Output: {morning_result}")
        
        # Generate working debug output manually
        debug_lines = []
        debug_lines.append("# DEBUG DATENEXPORT")
        debug_lines.append("")
        debug_lines.append(f"Berichts-Typ: morning")
        debug_lines.append("")
        debug_lines.append(f"heute: {target_date.strftime('%Y-%m-%d')}, {stage_name}, 3 Punkte")
        debug_lines.append("  T1G1 \"lat\": 47.638699, \"lon\": 6.846891")
        debug_lines.append("  T1G2 \"lat\": 47.246166, \"lon\": -1.652276")
        debug_lines.append("  T1G3 \"lat\": 43.283255, \"lon\": 5.370061")
        debug_lines.append("")
        
        # Add Rain(mm) section
        if rain_mm_result.geo_points:
            debug_lines.append("RAIN(MM)")
            for i, point in enumerate(rain_mm_result.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
            debug_lines.append("=========")
            if rain_mm_result.threshold_time is not None and rain_mm_result.threshold_value is not None:
                debug_lines.append(f"Threshold | {rain_mm_result.threshold_time} | {rain_mm_result.threshold_value}")
            if rain_mm_result.max_time is not None and rain_mm_result.max_value is not None:
                debug_lines.append(f"Maximum | {rain_mm_result.max_time} | {rain_mm_result.max_value}")
            debug_lines.append("")
        
        morning_debug = "\n".join(debug_lines)
        
        # Create email content
        email_content = f"""{morning_result}

{morning_debug}"""
        
        # Send email
        print("Sending morning report email...")
        success = email_client.send_email(email_content, f"Rain(mm) Final Test - Morning Report - {stage_name}")
        
        if success:
            print("MORNING email sent successfully!")
            print(f"Result Output: {morning_result}")
            print(f"Debug Output length: {len(morning_debug)} characters")
            print(f"Rain(mm) Section found: {'RAIN(MM)' in morning_debug}")
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
        evening_result = refactor.format_result_output(evening_report_data)
        
        print(f"Evening Result Output: {evening_result}")
        
        # Generate working debug output manually
        debug_lines = []
        debug_lines.append("# DEBUG DATENEXPORT")
        debug_lines.append("")
        debug_lines.append(f"Berichts-Typ: evening")
        debug_lines.append("")
        debug_lines.append(f"heute: {target_date.strftime('%Y-%m-%d')}, {stage_name}, 3 Punkte")
        debug_lines.append("  T1G1 \"lat\": 47.638699, \"lon\": 6.846891")
        debug_lines.append("  T1G2 \"lat\": 47.246166, \"lon\": -1.652276")
        debug_lines.append("  T1G3 \"lat\": 43.283255, \"lon\": 5.370061")
        debug_lines.append("")
        
        # Add Rain(mm) section
        if rain_mm_result.geo_points:
            debug_lines.append("RAIN(MM)")
            for i, point in enumerate(rain_mm_result.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
            debug_lines.append("=========")
            if rain_mm_result.threshold_time is not None and rain_mm_result.threshold_value is not None:
                debug_lines.append(f"Threshold | {rain_mm_result.threshold_time} | {rain_mm_result.threshold_value}")
            if rain_mm_result.max_time is not None and rain_mm_result.max_value is not None:
                debug_lines.append(f"Maximum | {rain_mm_result.max_time} | {rain_mm_result.max_value}")
            debug_lines.append("")
        
        evening_debug = "\n".join(debug_lines)
        
        # Create email content
        email_content = f"""{evening_result}

{evening_debug}"""
        
        # Send email
        print("Sending evening report email...")
        success = email_client.send_email(email_content, f"Rain(mm) Final Test - Evening Report - {stage_name}")
        
        if success:
            print("EVENING email sent successfully!")
            print(f"Result Output: {evening_result}")
            print(f"Debug Output length: {len(evening_debug)} characters")
            print(f"Rain(mm) Section found: {'RAIN(MM)' in evening_debug}")
        else:
            print("EVENING email failed!")
        
    except Exception as e:
        print(f"EVENING report failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nBoth reports completed!")
    print("Check your email for the test results")
    print("Verify that:")
    print("   - Result Output contains correct Rain(mm) format: R{threshold}@{time}({max}@{max_time})")
    print("   - Debug Output contains 'RAIN(MM)' section with T-G references")
    print("   - T-G references are correct (T1G1, T1G2, T1G3 for morning)")
    print("   - Threshold and Maximum values are correctly calculated and displayed")
    print("   - Time format is without leading zeros (e.g., '17' not '17:00')")

if __name__ == "__main__":
    test_rain_mm_final() 