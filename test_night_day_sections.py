#!/usr/bin/env python3
"""
Unit Test: Night and Day Sections Analysis
==========================================
Tests the functionality and output quality of Night and Day sections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
import yaml

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_mock_weather_data():
    """Create mock weather data for testing"""
    return {
        'daily_forecast': [
            {
                'date': '2025-08-02',
                'temp_min': 15.2,
                'temp_max': 28.7
            },
            {
                'date': '2025-08-03', 
                'temp_min': 16.8,
                'temp_max': 31.4
            }
        ],
        'hourly_data': [
            {
                'timestamp': datetime(2025, 8, 2, 4, 0),
                'temperature': 16.1,
                'rain_amount': 0.0
            },
            {
                'timestamp': datetime(2025, 8, 2, 6, 0),
                'temperature': 15.2,  # Minimum temperature
                'rain_amount': 0.0
            },
            {
                'timestamp': datetime(2025, 8, 2, 14, 0),
                'temperature': 28.7,  # Maximum temperature
                'rain_amount': 0.0
            }
        ]
    }

def test_night_section():
    """Test Night section functionality"""
    print("=" * 60)
    print("🧪 UNIT TEST: NIGHT SECTION")
    print("=" * 60)
    
    config = load_config()
    refactor = MorningEveningRefactor(config)
    
    # Test data
    weather_data = create_mock_weather_data()
    stage_name = "Test"
    target_date = date(2025, 8, 2)
    report_type = "morning"
    
    print(f"📅 Test Date: {target_date}")
    print(f"📍 Stage: {stage_name}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    # Test Night data processing
    print("1. NIGHT DATA PROCESSING:")
    print("-" * 30)
    
    try:
        night_data = refactor.process_night_data(weather_data, stage_name, target_date, report_type)
        
        print(f"✅ Night data processing successful")
        print(f"   Threshold value: {night_data.threshold_value}")
        print(f"   Threshold time: {night_data.threshold_time}")
        print(f"   Max value: {night_data.max_value}")
        print(f"   Max time: {night_data.max_time}")
        print(f"   Geo points: {len(night_data.geo_points)}")
        
        # Validate Night data
        if night_data.threshold_value is not None:
            print(f"   ✅ Night temperature found: {night_data.threshold_value}°C")
        else:
            print(f"   ❌ No night temperature data")
            
    except Exception as e:
        print(f"   ❌ Night data processing failed: {e}")
    
    print()

def test_day_section():
    """Test Day section functionality"""
    print("=" * 60)
    print("🧪 UNIT TEST: DAY SECTION")
    print("=" * 60)
    
    config = load_config()
    refactor = MorningEveningRefactor(config)
    
    # Test data
    weather_data = create_mock_weather_data()
    stage_name = "Test"
    target_date = date(2025, 8, 2)
    report_type = "morning"
    
    print(f"📅 Test Date: {target_date}")
    print(f"📍 Stage: {stage_name}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    # Test Day data processing
    print("1. DAY DATA PROCESSING:")
    print("-" * 30)
    
    try:
        day_data = refactor.process_day_data(weather_data, stage_name, target_date, report_type)
        
        print(f"✅ Day data processing successful")
        print(f"   Threshold value: {day_data.threshold_value}")
        print(f"   Threshold time: {day_data.threshold_time}")
        print(f"   Max value: {day_data.max_value}")
        print(f"   Max time: {day_data.max_time}")
        print(f"   Geo points: {len(day_data.geo_points)}")
        
        # Validate Day data
        if day_data.threshold_value is not None:
            print(f"   ✅ Day temperature found: {day_data.threshold_value}°C")
        else:
            print(f"   ❌ No day temperature data")
            
    except Exception as e:
        print(f"   ❌ Day data processing failed: {e}")
    
    print()

def test_night_day_output_format():
    """Test Night and Day output formatting"""
    print("=" * 60)
    print("🧪 UNIT TEST: NIGHT & DAY OUTPUT FORMAT")
    print("=" * 60)
    
    config = load_config()
    refactor = MorningEveningRefactor(config)
    
    # Test data
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    report_type = "morning"
    
    print(f"📅 Test Date: {target_date}")
    print(f"📍 Stage: {stage_name}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    # Test complete report generation
    print("1. COMPLETE REPORT GENERATION:")
    print("-" * 40)
    
    try:
        result_output, debug_output = refactor.generate_report(target_date, stage_name, report_type)
        
        print(f"✅ Report generation successful")
        print(f"   Result output length: {len(result_output)} characters")
        print(f"   Debug output length: {len(debug_output)} characters")
        
        # Analyze Result Output
        print()
        print("2. RESULT OUTPUT ANALYSIS:")
        print("-" * 30)
        print(f"   Result: {result_output}")
        
        # Check for Night and Day values
        if "N" in result_output and result_output.split()[1] != "N-":
            print(f"   ✅ Night value found in result output")
        else:
            print(f"   ❌ No Night value in result output")
            
        if "D" in result_output and result_output.split()[2] != "D-":
            print(f"   ✅ Day value found in result output")
        else:
            print(f"   ❌ No Day value in result output")
        
        # Analyze Debug Output
        print()
        print("3. DEBUG OUTPUT ANALYSIS:")
        print("-" * 30)
        
        debug_lines = debug_output.split('\n')
        
        # Check for NIGHT section
        night_section_found = False
        for i, line in enumerate(debug_lines):
            if "NIGHT" in line:
                night_section_found = True
                print(f"   ✅ NIGHT section found at line {i+1}: {line.strip()}")
                # Show next few lines
                for j in range(i+1, min(i+5, len(debug_lines))):
                    if debug_lines[j].strip() and not debug_lines[j].startswith('='):
                        print(f"      {debug_lines[j].strip()}")
                break
        
        if not night_section_found:
            print(f"   ❌ NIGHT section not found in debug output")
        
        # Check for DAY section
        day_section_found = False
        for i, line in enumerate(debug_lines):
            if "DAY" in line and "RAIN" not in line:
                day_section_found = True
                print(f"   ✅ DAY section found at line {i+1}: {line.strip()}")
                # Show next few lines
                for j in range(i+1, min(i+5, len(debug_lines))):
                    if debug_lines[j].strip() and not debug_lines[j].startswith('='):
                        print(f"      {debug_lines[j].strip()}")
                break
        
        if not day_section_found:
            print(f"   ❌ DAY section not found in debug output")
            
    except Exception as e:
        print(f"   ❌ Report generation failed: {e}")
    
    print()

def test_api_data_quality():
    """Test API data quality for Night and Day sections"""
    print("=" * 60)
    print("🧪 UNIT TEST: API DATA QUALITY")
    print("=" * 60)
    
    config = load_config()
    api = EnhancedMeteoFranceAPI()
    
    # Test coordinates from Test stage
    test_coordinates = [
        (47.638699, 6.846891),  # T1G1
        (47.246166, -1.652276), # T1G2
        (43.283255, 5.370061)   # T1G3
    ]
    
    print(f"📍 Testing coordinates: {len(test_coordinates)} points")
    print()
    
    for i, (lat, lon) in enumerate(test_coordinates, 1):
        print(f"Point {i} ({lat}, {lon}):")
        print("-" * 20)
        
        try:
            # Use the correct API method
            weather_data = api.get_forecast(lat, lon)
            
            # Check daily forecast data
            if weather_data and hasattr(weather_data, 'daily_forecast'):
                daily_entries = len(weather_data.daily_forecast) if weather_data.daily_forecast else 0
                print(f"   ✅ Daily forecast: {daily_entries} entries")
                
                # Check for today's data
                if weather_data.daily_forecast:
                    today_data = None
                    for entry in weather_data.daily_forecast:
                        if hasattr(entry, 'date') and entry.date == date(2025, 8, 2):
                            today_data = entry
                            break
                    
                    if today_data:
                        temp_min = getattr(today_data, 'temp_min', None)
                        temp_max = getattr(today_data, 'temp_max', None)
                        print(f"   ✅ Today's data found:")
                        print(f"      temp_min: {temp_min}°C")
                        print(f"      temp_max: {temp_max}°C")
                        
                        # Validate temperature values
                        if temp_min is not None and temp_max is not None:
                            if temp_min <= temp_max:
                                print(f"      ✅ Temperature range valid: {temp_min}°C - {temp_max}°C")
                            else:
                                print(f"      ❌ Temperature range invalid: min > max")
                        else:
                            print(f"      ❌ Missing temperature data")
                    else:
                        print(f"   ❌ No data for 2025-08-02")
                else:
                    print(f"   ❌ No daily forecast data")
            else:
                print(f"   ❌ No daily forecast data")
            
            # Check hourly data
            if weather_data and hasattr(weather_data, 'hourly_forecast'):
                hourly_entries = len(weather_data.hourly_forecast) if weather_data.hourly_forecast else 0
                print(f"   ✅ Hourly data: {hourly_entries} entries")
                
                # Check temperature range in hourly data
                if weather_data.hourly_forecast:
                    temperatures = []
                    for entry in weather_data.hourly_forecast:
                        temp = getattr(entry, 'temperature', None)
                        if temp is not None:
                            temperatures.append(temp)
                    
                    if temperatures:
                        min_temp = min(temperatures)
                        max_temp = max(temperatures)
                        print(f"   ✅ Hourly temperature range: {min_temp}°C - {max_temp}°C")
                    else:
                        print(f"   ❌ No temperature data in hourly entries")
                else:
                    print(f"   ❌ No hourly data")
            else:
                print(f"   ❌ No hourly data")
                
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
        
        print()

def main():
    """Run all Night and Day section tests"""
    print("🧪 NIGHT & DAY SECTIONS - COMPREHENSIVE UNIT TESTS")
    print("=" * 80)
    print()
    
    # Run individual tests
    test_night_section()
    test_day_section()
    test_night_day_output_format()
    test_api_data_quality()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main() 