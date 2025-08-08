#!/usr/bin/env python3
"""
Exact specification verification for Rain(mm) debug output
Compares actual output with specification and highlights differences
"""

import json
from datetime import date, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
# from src.email.email_client import EmailClient  # Not needed for this verification
from src.config.config_loader import load_config

def create_expected_rain_mm_debug_output():
    """Create the exact expected debug output according to specification"""
    expected_lines = [
        "RAIN(MM)",
        "T2G1",
        "Time | Rain (mm)",
        "04:00 | 0.00",
        "05:00 | 0.00", 
        "06:00 | 0.00",
        "07:00 | 0.80",
        "08:00 | 0.00",
        "09:00 | 0.00",
        "10:00 | 0.00",
        "11:00 | 0.00",
        "12:00 | 0.00",
        "13:00 | 0.00",
        "14:00 | 0.00",
        "15:00 | 0.00",
        "16:00 | 1.20",
        "17:00 | 0.80",
        "18:00 | 0.00",
        "19:00 | 0.00",
        "=========",
        "07:00 | 0.80 (Threshold)",
        "16:00 | 1.20 (Max)",
        "",
        "",
        "T2G2",
        "Time | Rain (mm)",
        "04:00 | 0.00",
        "05:00 | 0.00",
        "06:00 | 0.20",
        "07:00 | 0.80",
        "08:00 | 0.00",
        "09:00 | 0.00",
        "10:00 | 0.00",
        "11:00 | 0.00",
        "12:00 | 0.00",
        "13:00 | 0.00",
        "14:00 | 0.00",
        "15:00 | 0.00",
        "16:00 | 1.40",
        "17:00 | 0.80",
        "18:00 | 0.00",
        "19:00 | 0.00",
        "=========",
        "06:00 | 0.20 (Threshold)",
        "16:00 | 1.40 (Max)",
        "",
        "",
        "T2G3",
        "Time | Rain (mm)",
        "04:00 | 0.00",
        "05:00 | 0.00",
        "06:00 | 0.00",
        "07:00 | 0.80",
        "08:00 | 0.00",
        "09:00 | 0.00",
        "10:00 | 0.00",
        "11:00 | 0.00",
        "12:00 | 0.00",
        "13:00 | 0.00",
        "14:00 | 0.00",
        "15:00 | 0.00",
        "16:00 | 1.10",
        "17:00 | 0.80",
        "18:00 | 0.00",
        "19:00 | 0.00",
        "=========",
        "07:00 | 0.80 (Threshold)",
        "16:00 | 1.10 (Max)",
        "",
        "Theshold",
        "GEO | Time | mm",
        "G1 | 07:00 | 0.80",
        "G2 | 06:00 | 0.20",
        "G3 | 07:00 | 0.80",
        "=========",
        "Threshold | 06:00 | 0.20",
        "",
        "Maximum:",
        "GEO | Time | Max",
        "G1 | 16:00 | 1.20",
        "G2 | 16:00 | 1.40",
        "G3 | 16:00 | 1.10",
        "=========",
        "MAX | 16:00 | 1.40",
        ""
    ]
    return expected_lines

def verify_rain_mm_debug_output():
    """Verify Rain(mm) debug output against exact specification"""
    
    print("=" * 80)
    print("EXACT RAIN(MM) SPECIFICATION VERIFICATION")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    target_date = date(2025, 8, 3)  # Use tomorrow for testing
    stage_name = "Test"
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
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
    rain_mm_data = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
    
    # Store weather data for debug output
    refactor._last_weather_data = weather_data
    
    # Generate actual debug output
    debug_lines = []
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
                    time_str = str(hour)
                    rain_value = all_hours[time_str]
                    debug_lines.append(f"{time_str}:00 | {rain_value:.2f}")
            else:
                # Show default values if no data available
                for hour in range(4, 20):
                    debug_lines.append(f"{hour}:00 | 0.00")
            
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
            debug_lines.append("")
    
    # Add threshold and maximum tables AFTER individual point data (as per specification)
    debug_lines.append("Threshold")
    debug_lines.append("GEO | Time | mm")
    for i in range(3):
        geo = f"T1G{i+1}"
        # Get individual point data
        point_data = None
        for point in rain_mm_data.geo_points:
            if geo in point:
                point_data = point[geo]
                break
        
        if point_data and point_data.get('threshold_time') is not None and point_data.get('threshold_value') is not None:
            threshold_time = point_data.get('threshold_time')
            threshold_value = point_data.get('threshold_value')
            debug_lines.append(f"{geo} | {threshold_time}:00 | {threshold_value:.2f}")
        else:
            debug_lines.append(f"{geo} | - | -")
    debug_lines.append("=========")
    if rain_mm_data.threshold_time is not None and rain_mm_data.threshold_value is not None:
        debug_lines.append(f"Threshold | {rain_mm_data.threshold_time}:00 | {rain_mm_data.threshold_value:.2f}")
    else:
        debug_lines.append("Threshold | - | -")
    debug_lines.append("")
    
    debug_lines.append("Maximum:")
    debug_lines.append("GEO | Time | Max")
    for i in range(3):
        geo = f"T1G{i+1}"
        # Get individual point data
        point_data = None
        for point in rain_mm_data.geo_points:
            if geo in point:
                point_data = point[geo]
                break
        
        if point_data and point_data.get('max_time') is not None and point_data.get('max_value') is not None:
            max_time = point_data.get('max_time')
            max_value = point_data.get('max_value')
            debug_lines.append(f"{geo} | {max_time}:00 | {max_value:.2f}")
        else:
            debug_lines.append(f"{geo} | - | -")
    debug_lines.append("=========")
    if rain_mm_data.max_time is not None and rain_mm_data.max_value is not None:
        debug_lines.append(f"MAX | {rain_mm_data.max_time}:00 | {rain_mm_data.max_value:.2f}")
    else:
        debug_lines.append("MAX | - | -")
    debug_lines.append("")
    
    # Get expected output
    expected_lines = create_expected_rain_mm_debug_output()
    
    # Compare actual vs expected
    print("\n" + "=" * 80)
    print("COMPARISON: ACTUAL vs EXPECTED")
    print("=" * 80)
    
    actual_output = "\n".join(debug_lines)
    expected_output = "\n".join(expected_lines)
    
    print("ACTUAL OUTPUT:")
    print("-" * 40)
    print(actual_output)
    print("\n" + "=" * 80)
    print("EXPECTED OUTPUT (from specification):")
    print("-" * 40)
    print(expected_output)
    
    # Detailed line-by-line comparison
    print("\n" + "=" * 80)
    print("DETAILED LINE-BY-LINE COMPARISON")
    print("=" * 80)
    
    max_lines = max(len(debug_lines), len(expected_lines))
    differences_found = 0
    
    for i in range(max_lines):
        actual_line = debug_lines[i] if i < len(debug_lines) else "MISSING"
        expected_line = expected_lines[i] if i < len(expected_lines) else "MISSING"
        
        if actual_line != expected_line:
            differences_found += 1
            print(f"❌ Line {i+1:3d}:")
            print(f"   Expected: '{expected_line}'")
            print(f"   Actual:   '{actual_line}'")
            print()
        else:
            print(f"✅ Line {i+1:3d}: '{actual_line}'")
    
    print("=" * 80)
    print(f"SUMMARY: {differences_found} differences found")
    
    if differences_found == 0:
        print("🎉 PERFECT MATCH! Rain(mm) debug output exactly matches specification!")
    else:
        print("❌ DIFFERENCES DETECTED! Rain(mm) debug output does not match specification.")
        print("\nKey differences to fix:")
        print("1. Check time format (should be '07:00' not '7:00')")
        print("2. Check individual point threshold/max values")
        print("3. Check summary table format")
        print("4. Check T-G references (should be G1, G2, G3 not T1G1, T1G2, T1G3)")

if __name__ == "__main__":
    verify_rain_mm_debug_output() 