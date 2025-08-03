#!/usr/bin/env python3
"""
Test Rain(mm) with mock data containing realistic rain values
"""

import json
from datetime import date, datetime, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.config.config_loader import load_config

def create_mock_weather_data_with_rain():
    """Create mock weather data with realistic rain values"""
    
    target_date = date(2025, 8, 3)
    
    # Create mock hourly data with realistic rain values
    mock_hourly_data = []
    
    # Create 3 points with different rain patterns
    for point_idx in range(3):
        point_data = {
            'point_name': f'Test_point_{point_idx + 1}',
            'coordinates': {'lat': 42.0 + point_idx * 0.1, 'lon': 8.8 + point_idx * 0.1},
            'data': []
        }
        
        # Create 24 hours of data for the target date
        for hour in range(24):
            # Start with the target date at 00:00
            dt = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour)
            timestamp = int(dt.timestamp())
            
            # Create realistic rain pattern
            if point_idx == 0:  # Point 1: Rain in morning and evening
                if hour in [7, 16, 17]:  # 07:00, 16:00, 17:00
                    rain_value = 0.8 if hour == 7 else 1.2 if hour == 16 else 0.8
                else:
                    rain_value = 0.0
            elif point_idx == 1:  # Point 2: Rain in early morning and afternoon
                if hour in [6, 16]:  # 06:00, 16:00
                    rain_value = 0.2 if hour == 6 else 1.4
                else:
                    rain_value = 0.0
            else:  # Point 3: Rain in morning and late afternoon
                if hour in [7, 16, 17]:  # 07:00, 16:00, 17:00
                    rain_value = 0.8 if hour == 7 else 1.1 if hour == 16 else 0.8
                else:
                    rain_value = 0.0
            
            entry = {
                'dt': timestamp,
                'rain': {'1h': rain_value}
            }
            
            point_data['data'].append(entry)
        
        mock_hourly_data.append(point_data)
    
    return {
        'hourly_data': mock_hourly_data
    }

def test_rain_mm_with_mock_data():
    """Test Rain(mm) with mock data containing realistic rain values"""
    
    print("=" * 80)
    print("TESTING RAIN(MM) WITH MOCK DATA")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    stage_name = "Test"
    target_date = date(2025, 8, 3)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Create mock weather data with rain
    print("Creating mock weather data with realistic rain values...")
    mock_weather_data = create_mock_weather_data_with_rain()
    
    # Store the mock data
    refactor._last_weather_data = mock_weather_data
    
    print("✅ Mock weather data created successfully")
    
    # Show the mock data structure
    print("\nMock data structure:")
    for i, point_data in enumerate(mock_weather_data['hourly_data']):
        print(f"\nPoint {i+1} ({point_data['point_name']}):")
        print(f"  Coordinates: lat={point_data['coordinates']['lat']}, lon={point_data['coordinates']['lon']}")
        print(f"  Number of entries: {len(point_data['data'])}")
        
        # Show rain data for the target date
        print("  Rain data for 2025-08-03:")
        for entry in point_data['data']:
            dt = datetime.fromtimestamp(entry['dt'])
            rain_value = entry.get('rain', {}).get('1h', 0)
            if rain_value > 0:
                print(f"    {dt.hour:02d}:00 - {rain_value} mm")
    
    # Process Rain(mm) data
    print("\n" + "="*60)
    print("PROCESSING RAIN(MM) DATA")
    print("="*60)
    
    rain_mm_data = refactor.process_rain_mm_data(mock_weather_data, stage_name, target_date, "morning")
    
    print(f"Threshold value: {rain_mm_data.threshold_value}")
    print(f"Threshold time: {rain_mm_data.threshold_time}")
    print(f"Max value: {rain_mm_data.max_value}")
    print(f"Max time: {rain_mm_data.max_time}")
    
    print("\nGeo points data:")
    for i, point in enumerate(rain_mm_data.geo_points):
        for geo, data in point.items():
            print(f"  {geo}:")
            print(f"    threshold_time: {data.get('threshold_time')}")
            print(f"    threshold_value: {data.get('threshold_value')}")
            print(f"    max_time: {data.get('max_time')}")
            print(f"    max_value: {data.get('max_value')}")
    
    # Generate debug output
    print("\n" + "="*60)
    print("GENERATING DEBUG OUTPUT")
    print("="*60)
    
    debug_lines = []
    debug_lines.append("RAIN(MM)")
    
    # Show hourly data for each point
    for i in range(3):
        geo = f"T1G{i+1}"
        debug_lines.append(f"{geo}")
        debug_lines.append("Time | Rain (mm)")
        
        # Get data for this point
        point_data = mock_weather_data['hourly_data'][i]
        
        # Display only hours 4:00 - 19:00
        for hour in range(4, 20):
            # Find the entry for this hour
            rain_value = 0.0
            for entry in point_data['data']:
                dt = datetime.fromtimestamp(entry['dt'])
                if dt.hour == hour:
                    rain_value = entry.get('rain', {}).get('1h', 0)
                    break
            
            time_str = f"{hour:02d}"
            debug_lines.append(f"{time_str}:00 | {rain_value:.2f}")
        
        debug_lines.append("=========")
        
        # Get individual point data
        point_threshold_data = None
        for point in rain_mm_data.geo_points:
            if geo in point:
                point_threshold_data = point[geo]
                break
        
        if point_threshold_data:
            threshold_time = point_threshold_data.get('threshold_time')
            threshold_value = point_threshold_data.get('threshold_value')
            max_time = point_threshold_data.get('max_time')
            max_value = point_threshold_data.get('max_value')
            
            if threshold_time is not None and threshold_value is not None:
                debug_lines.append(f"{threshold_time}:00 | {threshold_value:.2f} (Threshold)")
            if max_time is not None and max_value is not None:
                debug_lines.append(f"{max_time}:00 | {max_value:.2f} (Max)")
        
        debug_lines.append("")
        debug_lines.append("")
    
    # Add summary tables
    debug_lines.append("Theshold")
    debug_lines.append("GEO | Time | mm")
    for i in range(3):
        geo_ref = f"G{i+1}"
        point_threshold_data = None
        for point in rain_mm_data.geo_points:
            if f"T1G{i+1}" in point:
                point_threshold_data = point[f"T1G{i+1}"]
                break
        
        if point_threshold_data and point_threshold_data.get('threshold_time') is not None:
            threshold_time = point_threshold_data.get('threshold_time')
            threshold_value = point_threshold_data.get('threshold_value')
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
        geo_ref = f"G{i+1}"
        point_threshold_data = None
        for point in rain_mm_data.geo_points:
            if f"T1G{i+1}" in point:
                point_threshold_data = point[f"T1G{i+1}"]
                break
        
        if point_threshold_data and point_threshold_data.get('max_time') is not None:
            max_time = point_threshold_data.get('max_time')
            max_value = point_threshold_data.get('max_value')
            debug_lines.append(f"{geo_ref} | {max_time}:00 | {max_value:.2f}")
        else:
            debug_lines.append(f"{geo_ref} | - | -")
    
    debug_lines.append("=========")
    if rain_mm_data.max_time is not None and rain_mm_data.max_value is not None:
        debug_lines.append(f"MAX | {rain_mm_data.max_time}:00 | {rain_mm_data.max_value:.2f}")
    else:
        debug_lines.append("MAX | - | -")
    debug_lines.append("")
    
    # Print the debug output
    print("\n" + "="*60)
    print("GENERATED DEBUG OUTPUT")
    print("="*60)
    print("\n".join(debug_lines))
    
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Verify the output matches expected pattern
    expected_patterns = [
        "07:00 | 0.80 (Threshold)",  # Point 1
        "16:00 | 1.20 (Max)",        # Point 1
        "06:00 | 0.20 (Threshold)",  # Point 2
        "16:00 | 1.40 (Max)",        # Point 2
        "07:00 | 0.80 (Threshold)",  # Point 3
        "16:00 | 1.10 (Max)",        # Point 3
    ]
    
    debug_output = "\n".join(debug_lines)
    
    for pattern in expected_patterns:
        if pattern in debug_output:
            print(f"✅ Found: {pattern}")
        else:
            print(f"❌ Missing: {pattern}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_rain_mm_with_mock_data() 