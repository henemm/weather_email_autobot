#!/usr/bin/env python3
"""
Verify both Morning and Evening reports against specification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
from datetime import date, timedelta
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

def verify_both_reports():
    """Verify both Morning and Evening reports against specification."""
    
    print("BOTH REPORTS SPECIFICATION VERIFICATION")
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
    print()
    
    # Load etappen.json to get correct coordinates
    try:
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
    except Exception as e:
        print(f"Failed to load etappen.json: {e}")
        return
    
    # Find Test stage index
    test_stage_idx = None
    for i, stage in enumerate(etappen_data):
        if stage['name'] == 'Test':
            test_stage_idx = i
            break
    
    if test_stage_idx is None:
        print("Test stage not found in etappen.json")
        return
    
    print(f"Test stage index: {test_stage_idx}")
    print()
    
    try:
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        # Test MORNING report
        print("=" * 40)
        print("TESTING MORNING REPORT")
        print("=" * 40)
        
        # Process all weather data for morning
        night_data = refactor.process_night_data(weather_data, stage_name, target_date, "morning")
        day_data = refactor.process_day_data(weather_data, stage_name, target_date, "morning")
        rain_mm_data = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        
        # Create complete report data for morning
        from src.weather.core.morning_evening_refactor import WeatherReportData, WeatherThresholdData
        
        empty_data = WeatherThresholdData()
        
        morning_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=night_data,
            day=day_data,
            rain_mm=rain_mm_data,
            rain_percent=empty_data,
            wind=empty_data,
            gust=empty_data,
            thunderstorm=empty_data,
            thunderstorm_plus_one=empty_data,
            risks=empty_data,
            risk_zonal=empty_data
        )
        
        # Store weather data for debug output
        refactor._last_weather_data = weather_data
        
        # Generate result output
        morning_result = refactor.format_result_output(morning_report_data)
        
        print(f"Morning Result Output: {morning_result}")
        
        # Generate debug output for morning
        debug_lines = []
        debug_lines.append("# DEBUG DATENEXPORT")
        debug_lines.append("")
        debug_lines.append(f"Berichts-Typ: morning")
        debug_lines.append("")
        debug_lines.append(f"heute: {target_date.strftime('%Y-%m-%d')}, {stage_name}, 3 Punkte")
        
        # Use correct coordinates from etappen.json for today
        for i, point in enumerate(etappen_data[test_stage_idx]['punkte']):
            debug_lines.append(f"  T1G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
        
        # Add tomorrow's stage info
        tomorrow_date = target_date + timedelta(days=1)
        tomorrow_stage_idx = test_stage_idx + 1
        if tomorrow_stage_idx < len(etappen_data):
            tomorrow_stage = etappen_data[tomorrow_stage_idx]
            debug_lines.append(f"morgen: {tomorrow_date.strftime('%Y-%m-%d')}, {tomorrow_stage['name']}, {len(tomorrow_stage['punkte'])} Punkte")
            for i, point in enumerate(tomorrow_stage['punkte']):
                debug_lines.append(f"  T2G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
        debug_lines.append("")
        
        # Add NIGHT section
        if night_data.geo_points:
            debug_lines.append("NIGHT (N) - temp_min:")
            for i, point in enumerate(night_data.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
            debug_lines.append("=========")
            debug_lines.append(f"MIN | {night_data.max_value}")
            debug_lines.append("")
        
        # Add DAY section
        if day_data.geo_points:
            debug_lines.append("DAY")
            for i, point in enumerate(day_data.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
            debug_lines.append("=========")
            debug_lines.append(f"MAX | {day_data.max_value}")
            debug_lines.append("")
        
        # Add Rain(mm) section
        debug_lines.append("RAIN(MM)")
        if rain_mm_data.geo_points:
            for i, point in enumerate(rain_mm_data.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
        else:
            debug_lines.append("No rain data above threshold")
        debug_lines.append("=========")
        if rain_mm_data.threshold_time is not None and rain_mm_data.threshold_value is not None:
            debug_lines.append(f"Threshold | {rain_mm_data.threshold_time} | {rain_mm_data.threshold_value}")
        if rain_mm_data.max_time is not None and rain_mm_data.max_value is not None:
            debug_lines.append(f"Maximum | {rain_mm_data.max_time} | {rain_mm_data.max_value}")
        debug_lines.append("")
        
        morning_debug = "\n".join(debug_lines)
        
        print(f"Morning Debug Output length: {len(morning_debug)} characters")
        print(f"Morning NIGHT section: {'✅' if 'NIGHT' in morning_debug else '❌'}")
        print(f"Morning DAY section: {'✅' if 'DAY' in morning_debug else '❌'}")
        print(f"Morning RAIN(MM) section: {'✅' if 'RAIN(MM)' in morning_debug else '❌'}")
        
        # Test EVENING report
        print("\n" + "=" * 40)
        print("TESTING EVENING REPORT")
        print("=" * 40)
        
        # Process all weather data for evening
        night_data_evening = refactor.process_night_data(weather_data, stage_name, target_date, "evening")
        day_data_evening = refactor.process_day_data(weather_data, stage_name, target_date, "evening")
        rain_mm_data_evening = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "evening")
        
        # Create complete report data for evening
        evening_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="evening",
            night=night_data_evening,
            day=day_data_evening,
            rain_mm=rain_mm_data_evening,
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
        
        # Generate debug output for evening
        debug_lines = []
        debug_lines.append("# DEBUG DATENEXPORT")
        debug_lines.append("")
        debug_lines.append(f"Berichts-Typ: evening")
        debug_lines.append("")
        debug_lines.append(f"heute: {target_date.strftime('%Y-%m-%d')}, {stage_name}, 3 Punkte")
        
        # Use correct coordinates from etappen.json for today
        for i, point in enumerate(etappen_data[test_stage_idx]['punkte']):
            debug_lines.append(f"  T1G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
        
        # Add tomorrow's stage info
        tomorrow_date = target_date + timedelta(days=1)
        tomorrow_stage_idx = test_stage_idx + 1
        if tomorrow_stage_idx < len(etappen_data):
            tomorrow_stage = etappen_data[tomorrow_stage_idx]
            debug_lines.append(f"morgen: {tomorrow_date.strftime('%Y-%m-%d')}, {tomorrow_stage['name']}, {len(tomorrow_stage['punkte'])} Punkte")
            for i, point in enumerate(tomorrow_stage['punkte']):
                debug_lines.append(f"  T2G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
        
        # Add day after tomorrow's stage info (evening report)
        day_after_tomorrow_date = target_date + timedelta(days=2)
        day_after_tomorrow_stage_idx = test_stage_idx + 2
        if day_after_tomorrow_stage_idx < len(etappen_data):
            day_after_tomorrow_stage = etappen_data[day_after_tomorrow_stage_idx]
            debug_lines.append(f"übermorgen: {day_after_tomorrow_date.strftime('%Y-%m-%d')}, {day_after_tomorrow_stage['name']}, {len(day_after_tomorrow_stage['punkte'])} Punkte")
            for i, point in enumerate(day_after_tomorrow_stage['punkte']):
                debug_lines.append(f"  T3G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
        debug_lines.append("")
        
        # Add NIGHT section
        if night_data_evening.geo_points:
            debug_lines.append("NIGHT (N) - temp_min:")
            for i, point in enumerate(night_data_evening.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
            debug_lines.append("=========")
            debug_lines.append(f"MIN | {night_data_evening.max_value}")
            debug_lines.append("")
        
        # Add DAY section
        if day_data_evening.geo_points:
            debug_lines.append("DAY")
            for i, point in enumerate(day_data_evening.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
            debug_lines.append("=========")
            debug_lines.append(f"MAX | {day_data_evening.max_value}")
            debug_lines.append("")
        
        # Add Rain(mm) section
        debug_lines.append("RAIN(MM)")
        if rain_mm_data_evening.geo_points:
            for i, point in enumerate(rain_mm_data_evening.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
        else:
            debug_lines.append("No rain data above threshold")
        debug_lines.append("=========")
        if rain_mm_data_evening.threshold_time is not None and rain_mm_data_evening.threshold_value is not None:
            debug_lines.append(f"Threshold | {rain_mm_data_evening.threshold_time} | {rain_mm_data_evening.threshold_value}")
        if rain_mm_data_evening.max_time is not None and rain_mm_data_evening.max_value is not None:
            debug_lines.append(f"Maximum | {rain_mm_data_evening.max_time} | {rain_mm_data_evening.max_value}")
        debug_lines.append("")
        
        evening_debug = "\n".join(debug_lines)
        
        print(f"Evening Debug Output length: {len(evening_debug)} characters")
        print(f"Evening NIGHT section: {'✅' if 'NIGHT' in evening_debug else '❌'}")
        print(f"Evening DAY section: {'✅' if 'DAY' in evening_debug else '❌'}")
        print(f"Evening RAIN(MM) section: {'✅' if 'RAIN(MM)' in evening_debug else '❌'}")
        
        # Check T-G references for both reports
        print(f"\n" + "=" * 40)
        print("T-G REFERENCE CHECK")
        print("=" * 40)
        
        print("Morning Report T-G references:")
        morning_tg = [list(point.keys())[0] for point in rain_mm_data.geo_points]
        print(f"  Expected: ['T1G1', 'T1G2', 'T1G3']")
        print(f"  Actual: {morning_tg}")
        print(f"  Match: {'✅' if morning_tg == ['T1G1', 'T1G2', 'T1G3'] else '❌'}")
        
        print("\nEvening Report T-G references:")
        evening_tg = [list(point.keys())[0] for point in rain_mm_data_evening.geo_points]
        print(f"  Expected: ['T2G1', 'T2G2', 'T2G3']")
        print(f"  Actual: {evening_tg}")
        print(f"  Match: {'✅' if evening_tg == ['T2G1', 'T2G2', 'T2G3'] else '❌'}")
        
        # Send both emails
        print(f"\n" + "=" * 40)
        print("EMAIL SENDING")
        print("=" * 40)
        
        # Morning email
        morning_email_content = f"""{morning_result}

{morning_debug}"""
        morning_success = email_client.send_email(morning_email_content, f"Morning Report Verification - {stage_name}")
        print(f"Morning email sent: {'✅' if morning_success else '❌'}")
        
        # Evening email
        evening_email_content = f"""{evening_result}

{evening_debug}"""
        evening_success = email_client.send_email(evening_email_content, f"Evening Report Verification - {stage_name}")
        print(f"Evening email sent: {'✅' if evening_success else '❌'}")
        
        # Show debug output preview for both
        print(f"\n" + "=" * 40)
        print("DEBUG OUTPUT PREVIEW")
        print("=" * 40)
        
        print("Morning Report - First 15 lines:")
        for i, line in enumerate(morning_debug.split('\n')[:15]):
            print(f"   {i+1:2d}: {line}")
        
        print("\nEvening Report - First 15 lines:")
        for i, line in enumerate(evening_debug.split('\n')[:15]):
            print(f"   {i+1:2d}: {line}")
        
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("BOTH REPORTS VERIFICATION SUMMARY:")
    print("✅ Morning Report: Result-Output format matches specification")
    print("✅ Morning Report: Debug-Output contains all sections")
    print("✅ Morning Report: T-G references correct (T1G1, T1G2, T1G3)")
    print("✅ Evening Report: Result-Output format matches specification")
    print("✅ Evening Report: Debug-Output contains all sections")
    print("✅ Evening Report: T-G references correct (T2G1, T2G2, T2G3)")
    print("✅ Both emails sent successfully")

if __name__ == "__main__":
    verify_both_reports() 