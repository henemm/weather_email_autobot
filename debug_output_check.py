#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.wetter.fetch_meteofrance import get_forecast_with_fallback
from src.notification.email_client import EmailClient
from src.config.config_loader import load_config
import json

def check_debug_output():
    """Check the complete debug output including RAIN(MM) section"""
    
    # Load configuration
    config = load_config()
    target_date = date(2025, 8, 3)  # Use tomorrow to get non-zero rain data for testing
    stage_name = "Test"
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    
    # Load etappen.json for coordinates
    with open('etappen.json', 'r') as f:
        etappen_data = json.load(f)
    
    test_stage_idx = 6  # Test stage
    stage_points = etappen_data[test_stage_idx]['punkte']
    
    # Fetch weather data for each point
    print("Fetching weather data...")
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    if not weather_data:
        print("❌ Failed to fetch weather data")
        return
    
    print("✅ Weather data fetched successfully")
    
    # Process weather data
    night_data = refactor.process_night_data(weather_data, stage_name, target_date, "morning")
    day_data = refactor.process_day_data(weather_data, stage_name, target_date, "morning")
    rain_mm_data = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
    
    # Store weather data for debug output
    refactor._last_weather_data = weather_data
    
    # Generate debug output
    debug_lines = []
    debug_lines.append("# DEBUG DATENEXPORT")
    debug_lines.append("")
    debug_lines.append(f"Berichts-Typ: morning")
    debug_lines.append("")
    debug_lines.append(f"heute: {target_date.strftime('%Y-%m-%d')}, {stage_name}, 3 Punkte")
    
    # Load etappen.json for coordinates
    with open('etappen.json', 'r') as f:
        etappen_data = json.load(f)
    
    test_stage_idx = 6  # Test stage
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
    
            # Add Rain(mm) section with detailed hourly data
        debug_lines.append("RAIN(MM)")
        
        # Show hourly data for each point FIRST (as per specification)
        if hasattr(refactor, '_last_weather_data') and refactor._last_weather_data:
            hourly_data = refactor._last_weather_data.get('hourly_data', [])
            
            # Show data for each point (T1G1, T1G2, T1G3 for morning)
            for i in range(3):  # Always show 3 points
                geo = f"T1G{i+1}"
                debug_lines.append(f"{geo}")
                debug_lines.append("Time | Rain (mm)")
                
                if i < len(hourly_data) and 'data' in hourly_data[i]:
                    # Create a dictionary of all hours with default value 0
                    all_hours = {str(hour): 0 for hour in range(24)}
                    
                    # Fill in actual data
                    for hour_data in hourly_data[i]['data']:
                        if 'dt' in hour_data:
                            from datetime import datetime
                            hour_time = datetime.fromtimestamp(hour_data['dt'])
                            hour_date = hour_time.date()
                            if hour_date == target_date:
                                time_str = str(hour_time.hour)
                                rain_value = hour_data.get('rain', {}).get('1h', 0)
                                all_hours[time_str] = rain_value
                    
                # Display only hours 4:00 - 19:00 (as per specification)
                for hour in range(4, 20):  # 4 to 19 inclusive
                    time_str = f"{hour:02d}"  # Format with leading zero
                    rain_value = all_hours[str(hour)]
                    debug_lines.append(f"{time_str}:00 | {rain_value:.2f}")
            else:
                # Show default values if no data available
                for hour in range(4, 20):
                    time_str = f"{hour:02d}"  # Format with leading zero
                    debug_lines.append(f"{time_str}:00 | 0.00")
                
                debug_lines.append("=========")
                # Get individual point data
                point_data = None
                for point in rain_mm_data.geo_points:
                    if geo in point:
                        point_data = point[geo]
                        break
                
                if point_data:
                    threshold_time = point_data.get('threshold_time')
                    threshold_value = point_data.get('threshold_value')
                    max_time = point_data.get('max_time')
                    max_value = point_data.get('max_value')
                    
                    if threshold_time is not None and threshold_value is not None:
                        debug_lines.append(f"{threshold_time}:00 | {threshold_value:.2f} (Threshold)")
                    if max_time is not None and max_value is not None:
                        debug_lines.append(f"{max_time}:00 | {max_value:.2f} (Max)")
                debug_lines.append("")
        
        # Add threshold and maximum tables AFTER individual point data (as per specification)
        debug_lines.append("Theshold")  # Match specification typo
        debug_lines.append("GEO | Time | mm")
        for i in range(3):
            geo_ref = f"G{i+1}"  # Use G1, G2, G3 as per specification
            # Get individual point data
            point_data = None
            for point in rain_mm_data.geo_points:
                if f"T1G{i+1}" in point:
                    point_data = point[f"T1G{i+1}"]
                    break
            
            if point_data and point_data.get('threshold_time') is not None and point_data.get('threshold_value') is not None:
                threshold_time = point_data.get('threshold_time')
                threshold_value = point_data.get('threshold_value')
                debug_lines.append(f"{geo_ref} | {threshold_time}:00 | {threshold_value:.2f}")
            else:
                debug_lines.append(f"{geo_ref} | - | -")
        debug_lines.append("=========")
        if rain_mm_data.threshold_time is not None and rain_mm_data.threshold_value is not None:
            debug_lines.append(f"Threshold | {rain_mm_data.threshold_time}:00 | {rain_mm_data.threshold_value:.2f}")
        else:
            debug_lines.append("Threshold | - | -")
        debug_lines.append("")
        
        debug_lines.append("Maximum:")
        debug_lines.append("GEO | Time | Max")
        for i in range(3):
            geo_ref = f"G{i+1}"  # Use G1, G2, G3 as per specification
            # Get individual point data
            point_data = None
            for point in rain_mm_data.geo_points:
                if f"T1G{i+1}" in point:
                    point_data = point[f"T1G{i+1}"]
                    break
            
            if point_data and point_data.get('max_time') is not None and point_data.get('max_value') is not None:
                max_time = point_data.get('max_time')
                max_value = point_data.get('max_value')
                debug_lines.append(f"{geo_ref} | {max_time}:00 | {max_value:.2f}")
            else:
                debug_lines.append(f"{geo_ref} | - | -")
        debug_lines.append("=========")
        if rain_mm_data.max_time is not None and rain_mm_data.max_value is not None:
            debug_lines.append(f"MAX | {rain_mm_data.max_time}:00 | {rain_mm_data.max_value:.2f}")
        else:
            debug_lines.append("MAX | - | -")
        debug_lines.append("")
    
    # Print complete debug output
    complete_debug = "\n".join(debug_lines)
    print("\n" + "="*80)
    print("COMPLETE DEBUG OUTPUT:")
    print("="*80)
    print(complete_debug)
    print("="*80)
    
    # Show RAIN(MM) section specifically
    print("\n" + "="*80)
    print("RAIN(MM) SECTION DETAILS:")
    print("="*80)
    rain_section_start = complete_debug.find("RAIN(MM)")
    if rain_section_start != -1:
        rain_section = complete_debug[rain_section_start:]
        # Find the end of RAIN(MM) section (before next section or end)
        next_section = rain_section.find("\n\n")
        if next_section != -1:
            rain_section = rain_section[:next_section]
        print(rain_section)
    else:
        print("RAIN(MM) section not found!")

if __name__ == "__main__":
    check_debug_output() 