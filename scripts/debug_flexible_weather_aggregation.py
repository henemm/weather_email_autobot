#!/usr/bin/env python3
"""
Debug script for flexible weather data aggregation.

This script tests the new flexible date-based weather data aggregation
that handles different report types (morning, evening, update) correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from datetime import datetime, timedelta
from src.wetter.weather_data_processor import WeatherDataProcessor


def load_config():
    """Load configuration from config.yaml."""
    config_path = "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def test_flexible_weather_aggregation():
    """Test flexible weather data aggregation for different report types."""
    print("🌤️ Testing Flexible Weather Data Aggregation")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    processor = WeatherDataProcessor(config)
    
    # Test coordinates (Corte, Corsica)
    test_coords = {
        'latitude': 42.3069,
        'longitude': 9.1497,
        'location_name': 'Corte'
    }
    
    # Test different report types
    report_types = ['morning', 'evening', 'update']
    
    for report_type in report_types:
        print(f"\n📊 Testing {report_type.upper()} Report")
        print("-" * 40)
        
        try:
            # Process weather data for this report type
            result = processor.process_weather_data(
                latitude=test_coords['latitude'],
                longitude=test_coords['longitude'],
                location_name=test_coords['location_name'],
                report_type=report_type
            )
            
            # Display results
            print(f"📍 Location: {result['location']}")
            print(f"📅 Report Type: {result['report_type']}")
            print(f"📅 Target Date: {result['target_date']}")
            print(f"📅 Thunderstorm Next Day Date: {result['thunderstorm_next_day_date']}")
            
            print(f"\n🌡️ Temperature Data:")
            print(f"   Max Temperature: {result['max_temperature']}°C")
            if report_type == 'evening':
                print(f"   Min Temperature (Night): {result['min_temperature']}°C")
            
            print(f"\n⛈️ Thunderstorm Data:")
            print(f"   Max Thunderstorm Probability: {result['max_thunderstorm_probability']}%")
            print(f"   Threshold Crossing: {result['thunderstorm_threshold_pct']}% @ {result['thunderstorm_threshold_time']}")
            print(f"   Max Time: {result['thunderstorm_max_time']}")
            print(f"   Next Day: {result['thunderstorm_next_day']}% @ {result['thunderstorm_next_day_threshold_time']}")
            
            print(f"\n🌧️ Rain Data:")
            print(f"   Max Rain Probability: {result['max_rain_probability']}%")
            print(f"   Threshold Crossing: {result['rain_threshold_pct']}% @ {result['rain_threshold_time']}")
            print(f"   Max Time: {result['rain_max_time']}")
            print(f"   Max Precipitation: {result['max_precipitation']}mm @ {result['rain_total_time']}")
            
            print(f"\n💨 Wind Data:")
            print(f"   Average Wind Speed: {result['wind_speed']} km/h")
            print(f"   Max Wind Gusts: {result['max_wind_speed']} km/h")
            
            if result['fire_risk_warning']:
                print(f"\n🔥 Fire Risk Warning: {result['fire_risk_warning']}")
            
            print(f"\n📊 Metadata:")
            print(f"   Data Source: {result['data_source']}")
            print(f"   Processed At: {result['processed_at']}")
            
        except Exception as e:
            print(f"❌ Error processing {report_type} report: {e}")
            import traceback
            traceback.print_exc()


def test_specific_date_calculation():
    """Test weather data calculation for specific dates."""
    print(f"\n\n🎯 Testing Specific Date Calculations")
    print("=" * 60)
    
    config = load_config()
    processor = WeatherDataProcessor(config)
    
    test_coords = {
        'latitude': 42.3069,
        'longitude': 9.1497,
        'location_name': 'Corte'
    }
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    test_dates = [
        ('Today', today),
        ('Tomorrow', tomorrow),
        ('Day After Tomorrow', day_after_tomorrow)
    ]
    
    for date_name, target_date in test_dates:
        print(f"\n📅 Testing {date_name} ({target_date})")
        print("-" * 30)
        
        try:
            result = processor._calculate_weather_data_for_day(
                latitude=test_coords['latitude'],
                longitude=test_coords['longitude'],
                location_name=test_coords['location_name'],
                target_date=target_date,
                start_hour=5,
                end_hour=17
            )
            
            print(f"   Max Temperature: {result['max_temperature']}°C")
            print(f"   Max Thunderstorm: {result['max_thunderstorm_probability']}%")
            print(f"   Max Rain: {result['max_rain_probability']}%")
            print(f"   Max Wind: {result['max_wind_speed']} km/h")
            print(f"   Time Window: {result['time_window']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_thunderstorm_next_day_logic():
    """Test thunderstorm next day logic for different report types."""
    print(f"\n\n⚡ Testing Thunderstorm Next Day Logic")
    print("=" * 60)
    
    config = load_config()
    processor = WeatherDataProcessor(config)
    
    test_coords = {
        'latitude': 42.3069,
        'longitude': 9.1497,
        'location_name': 'Corte'
    }
    
    report_types = ['morning', 'evening', 'update']
    today = datetime.now().date()
    
    for report_type in report_types:
        print(f"\n📊 {report_type.upper()} Report - Gewitter +1")
        print("-" * 35)
        
        try:
            result = processor._calculate_thunderstorm_next_day(
                latitude=test_coords['latitude'],
                longitude=test_coords['longitude'],
                location_name=test_coords['location_name'],
                report_type=report_type
            )
            
            expected_date = None
            if report_type == 'evening':
                expected_date = today + timedelta(days=2)  # übermorgen
                print(f"   Expected: übermorgen ({expected_date})")
            else:
                expected_date = today + timedelta(days=1)  # morgen
                print(f"   Expected: morgen ({expected_date})")
            
            print(f"   Actual: {result['target_date']}")
            print(f"   Thunderstorm Probability: {result['thunderstorm_next_day']}%")
            print(f"   Threshold Time: {result['thunderstorm_next_day_threshold_time']}")
            print(f"   Max Time: {result['thunderstorm_next_day_max_time']}")
            
            # Verify the logic
            if result['target_date'] == expected_date.isoformat():
                print(f"   ✅ Date logic correct")
            else:
                print(f"   ❌ Date logic incorrect")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Flexible Weather Data Aggregation Debug")
    print("=" * 60)
    
    # Test main aggregation logic
    test_flexible_weather_aggregation()
    
    # Test specific date calculations
    test_specific_date_calculation()
    
    # Test thunderstorm next day logic
    test_thunderstorm_next_day_logic()
    
    print(f"\n✅ Debug completed successfully!") 