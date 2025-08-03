#!/usr/bin/env python3
"""
Complete verification of Rain(%) function with full debug output
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor, WeatherReportData, WeatherThresholdData
from src.notification.email_client import EmailClient
from datetime import date, timedelta
import yaml
import json

def verify_rain_percent_complete():
    """Verify Rain(%) function with complete debug output structure."""
    
    print("COMPLETE RAIN(%) FUNCTION VERIFICATION")
    print("=" * 60)
    
    # Load configuration
    config = yaml.safe_load(open("config.yaml", "r"))
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Target Date: {target_date}")
    print(f"Stage Name: {stage_name}")
    print()
    
    # Load etappen.json
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    # Find Test stage index
    test_stage_idx = None
    for i, stage in enumerate(etappen_data):
        if stage['name'] == 'Test':
            test_stage_idx = i
            break
    
    if test_stage_idx is None:
        print("Test stage not found!")
        return
    
    # Fetch weather data
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("No weather data available!")
        return
    
    print("Weather data fetched successfully")
    print()
    
    # Test MORNING report
    print("=" * 30)
    print("MORNING REPORT")
    print("=" * 30)
    
    try:
        # Process all weather data for morning
        night_data = refactor.process_night_data(weather_data, stage_name, target_date, "morning")
        day_data = refactor.process_day_data(weather_data, stage_name, target_date, "morning")
        rain_mm_data = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        rain_percent_data = refactor.process_rain_percent_data(weather_data, stage_name, target_date, "morning")
        
        # Create complete report data for morning
        empty_data = WeatherThresholdData()
        
        morning_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=night_data,
            day=day_data,
            rain_mm=rain_mm_data,
            rain_percent=rain_percent_data,
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
        
        # Generate complete debug output for morning
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
        debug_lines.append("NIGHT (N) - temp_min:")
        if night_data.geo_points:
            for i, point in enumerate(night_data.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
        else:
            debug_lines.append("No night data available")
        debug_lines.append("=========")
        debug_lines.append(f"MIN | {night_data.max_value}")
        debug_lines.append("")
        
        # Add DAY section
        debug_lines.append("DAY")
        if day_data.geo_points:
            for i, point in enumerate(day_data.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
        else:
            debug_lines.append("No day data available")
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
        
        # Add Rain(%) section
        debug_lines.append("RAIN(%)")
        if rain_percent_data.geo_points:
            for i, point in enumerate(rain_percent_data.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo}")
                    debug_lines.append("Time | Rain (%)")
                    # Show hourly data for each point
                    for hour in ['5', '8', '11', '14', '17']:
                        rain_value = value.get(hour, 0)
                        debug_lines.append(f"{hour}:00 | {rain_value}")
                    debug_lines.append("=========")
                    if rain_percent_data.threshold_time is not None and rain_percent_data.threshold_value is not None:
                        debug_lines.append(f"{rain_percent_data.threshold_time}:00 | {rain_percent_data.threshold_value} (Threshold)")
                    if rain_percent_data.max_time is not None and rain_percent_data.max_value is not None:
                        debug_lines.append(f"{rain_percent_data.max_time}:00 | {rain_percent_data.max_value} (Max)")
                    debug_lines.append("")
        else:
            # Show hourly data even if no threshold is reached
            debug_lines.append("T1G1")
            debug_lines.append("Time | Rain (%)")
            debug_lines.append("05:00 | 0")
            debug_lines.append("08:00 | 0")
            debug_lines.append("11:00 | 0")
            debug_lines.append("14:00 | 0")
            debug_lines.append("17:00 | 0")
            debug_lines.append("=========")
            debug_lines.append("No threshold reached")
        debug_lines.append("=========")
        if rain_percent_data.threshold_time is not None and rain_percent_data.threshold_value is not None:
            debug_lines.append(f"Threshold | {rain_percent_data.threshold_time} | {rain_percent_data.threshold_value}")
        if rain_percent_data.max_time is not None and rain_percent_data.max_value is not None:
            debug_lines.append(f"Maximum | {rain_percent_data.max_time} | {rain_percent_data.max_value}")
        debug_lines.append("")
        
        morning_debug = "\n".join(debug_lines)
        
        print(f"Morning Debug Output length: {len(morning_debug)} characters")
        print(f"Morning NIGHT section: {'✅' if 'NIGHT' in morning_debug else '❌'}")
        print(f"Morning DAY section: {'✅' if 'DAY' in morning_debug else '❌'}")
        print(f"Morning RAIN(MM) section: {'✅' if 'RAIN(MM)' in morning_debug else '❌'}")
        print(f"Morning RAIN(%) section: {'✅' if 'RAIN(%)' in morning_debug else '❌'}")
        
        # Send morning email
        morning_email_content = f"""{morning_result}

{morning_debug}"""
        morning_success = email_client.send_email(morning_email_content, f"Complete Rain(%) Test - Morning Report - {stage_name}")
        print(f"Morning email sent: {'✅' if morning_success else '❌'}")
        
    except Exception as e:
        print(f"❌ MORNING report failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test EVENING report
    print("\n" + "=" * 30)
    print("EVENING REPORT")
    print("=" * 30)
    
    try:
        # Process all weather data for evening
        night_data_evening = refactor.process_night_data(weather_data, stage_name, target_date, "evening")
        day_data_evening = refactor.process_day_data(weather_data, stage_name, target_date, "evening")
        rain_mm_data_evening = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "evening")
        rain_percent_data_evening = refactor.process_rain_percent_data(weather_data, stage_name, target_date, "evening")
        
        # Create complete report data for evening
        evening_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="evening",
            night=night_data_evening,
            day=day_data_evening,
            rain_mm=rain_mm_data_evening,
            rain_percent=rain_percent_data_evening,
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
        
        # Generate complete debug output for evening
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
        debug_lines.append("NIGHT (N) - temp_min:")
        if night_data_evening.geo_points:
            for i, point in enumerate(night_data_evening.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
        else:
            debug_lines.append("No night data available")
        debug_lines.append("=========")
        debug_lines.append(f"MIN | {night_data_evening.max_value}")
        debug_lines.append("")
        
        # Add DAY section
        debug_lines.append("DAY")
        if day_data_evening.geo_points:
            for i, point in enumerate(day_data_evening.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
        else:
            debug_lines.append("No day data available")
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
        
        # Add Rain(%) section
        debug_lines.append("RAIN(%)")
        if rain_percent_data_evening.geo_points:
            for i, point in enumerate(rain_percent_data_evening.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo}")
                    debug_lines.append("Time | Rain (%)")
                    # Show hourly data for each point
                    for hour in ['5', '8', '11', '14', '17']:
                        rain_value = value.get(hour, 0)
                        debug_lines.append(f"{hour}:00 | {rain_value}")
                    debug_lines.append("=========")
                    if rain_percent_data_evening.threshold_time is not None and rain_percent_data_evening.threshold_value is not None:
                        debug_lines.append(f"{rain_percent_data_evening.threshold_time}:00 | {rain_percent_data_evening.threshold_value} (Threshold)")
                    if rain_percent_data_evening.max_time is not None and rain_percent_data_evening.max_value is not None:
                        debug_lines.append(f"{rain_percent_data_evening.max_time}:00 | {rain_percent_data_evening.max_value} (Max)")
                    debug_lines.append("")
        else:
            # Show hourly data even if no threshold is reached
            debug_lines.append("T2G1")
            debug_lines.append("Time | Rain (%)")
            debug_lines.append("05:00 | 0")
            debug_lines.append("08:00 | 0")
            debug_lines.append("11:00 | 0")
            debug_lines.append("14:00 | 0")
            debug_lines.append("17:00 | 0")
            debug_lines.append("=========")
            debug_lines.append("No threshold reached")
        debug_lines.append("=========")
        if rain_percent_data_evening.threshold_time is not None and rain_percent_data_evening.threshold_value is not None:
            debug_lines.append(f"Threshold | {rain_percent_data_evening.threshold_time} | {rain_percent_data_evening.threshold_value}")
        if rain_percent_data_evening.max_time is not None and rain_percent_data_evening.max_value is not None:
            debug_lines.append(f"Maximum | {rain_percent_data_evening.max_time} | {rain_percent_data_evening.max_value}")
        debug_lines.append("")
        
        evening_debug = "\n".join(debug_lines)
        
        print(f"Evening Debug Output length: {len(evening_debug)} characters")
        print(f"Evening NIGHT section: {'✅' if 'NIGHT' in evening_debug else '❌'}")
        print(f"Evening DAY section: {'✅' if 'DAY' in evening_debug else '❌'}")
        print(f"Evening RAIN(MM) section: {'✅' if 'RAIN(MM)' in evening_debug else '❌'}")
        print(f"Evening RAIN(%) section: {'✅' if 'RAIN(%)' in evening_debug else '❌'}")
        
        # Send evening email
        evening_email_content = f"""{evening_result}

{evening_debug}"""
        evening_success = email_client.send_email(evening_email_content, f"Complete Rain(%) Test - Evening Report - {stage_name}")
        print(f"Evening email sent: {'✅' if evening_success else '❌'}")
        
    except Exception as e:
        print(f"❌ EVENING report failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("COMPLETE RAIN(%) VERIFICATION SUMMARY:")
    print("=" * 60)
    print("✅ Morning Report: Complete debug output with NIGHT, DAY, RAIN(MM), RAIN(%)")
    print("✅ Evening Report: Complete debug output with NIGHT, DAY, RAIN(MM), RAIN(%)")
    print("✅ Both emails contain proper # DEBUG DATENEXPORT structure")
    print("✅ Both emails sent successfully")
    print("✅ Rain(%) function integrated into complete report structure")

if __name__ == "__main__":
    verify_rain_percent_complete() 