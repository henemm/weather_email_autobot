#!/usr/bin/env python3
"""
Test script for compact formatter integration.
Demonstrates how the new MorningEveningFormatter integrates with the existing system.
"""

import sys
import os
from datetime import datetime, date

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.models import ReportConfig, AggregatedWeatherData
from weather.core.formatter import WeatherFormatter
from weather.core.morning_evening_formatter import MorningEveningFormatter

def create_sample_weather_data():
    """Create sample weather data for testing."""
    return AggregatedWeatherData(
        location_name="Paliri",
        latitude=42.0,
        longitude=9.0,
        target_date=date(2025, 8, 1),
        time_window="morning",
        data_source="meteo_france",
        processed_at=datetime.now(),
        
        # Night temperature (minimum)
        min_temperature=8.0,
        
        # Day temperature (maximum)
        max_temperature=24.0,
        
        # Rain data
        rain_threshold_pct=20.0,
        rain_threshold_time="11:00",
        max_rain_probability=100.0,
        rain_max_time="17:00",
        max_precipitation=1.4,
        precipitation_max_time="16:00",
        
        # Wind data
        wind_threshold_kmh=10.0,
        wind_threshold_time="11:00",
        max_wind_speed=15.0,
        wind_max_time="17:00",
        
        # Gust data
        max_wind_gusts=30.0,
        wind_gusts_max_time="17:00",
        
        # Thunderstorm data
        thunderstorm_threshold_pct=50.0,
        thunderstorm_threshold_time="16:00",
        max_thunderstorm_probability=80.0,
        thunderstorm_max_time="18:00",
        
        # Tomorrow thunderstorm data
        tomorrow_max_thunderstorm_probability=70.0,
        tomorrow_thunderstorm_threshold_time="14:00",
        tomorrow_thunderstorm_max_time="17:00"
    )

def test_formatter_integration():
    """Test the integration of compact formatter with existing system."""
    
    print("🧪 Testing Compact Formatter Integration")
    print("=" * 60)
    
    # Create sample data
    weather_data = create_sample_weather_data()
    stage_names = {
        'today': 'Paliri',
        'tomorrow': 'Vizzavona',
        'day_after_tomorrow': 'Corte'
    }
    
    # Test 1: Standard formatter (default)
    print("\n📋 Test 1: Standard Formatter (default)")
    print("-" * 40)
    
    config_standard = ReportConfig(
        rain_probability_threshold=25.0,
        thunderstorm_probability_threshold=20.0,
        rain_amount_threshold=0.2,
        wind_speed_threshold=10.0,
        temperature_threshold=32.0,
        use_compact_formatter=False  # Use standard formatter
    )
    
    standard_formatter = WeatherFormatter(config_standard)
    
    try:
        from weather.core.models import ReportType
        morning_report_standard = standard_formatter.format_report_text(
            weather_data, 
            ReportType.MORNING, 
            stage_names
        )
        print(f"✅ Standard Morning Report:")
        print(f"   {morning_report_standard}")
        print(f"   Length: {len(morning_report_standard)} chars")
    except Exception as e:
        print(f"❌ Standard formatter error: {e}")
    
    # Test 2: Compact formatter (new)
    print("\n📋 Test 2: Compact Formatter (new)")
    print("-" * 40)
    
    config_compact = ReportConfig(
        rain_probability_threshold=25.0,
        thunderstorm_probability_threshold=20.0,
        rain_amount_threshold=0.2,
        wind_speed_threshold=10.0,
        temperature_threshold=32.0,
        use_compact_formatter=True  # Use compact formatter
    )
    
    compact_formatter = WeatherFormatter(config_compact)
    
    try:
        from weather.core.models import ReportType
        morning_report_compact = compact_formatter.format_report_text(
            weather_data, 
            ReportType.MORNING, 
            stage_names
        )
        print(f"✅ Compact Morning Report:")
        print(f"   {morning_report_compact}")
        print(f"   Length: {len(morning_report_compact)} chars")
    except Exception as e:
        print(f"❌ Compact formatter error: {e}")
    
    # Test 3: Direct compact formatter usage
    print("\n📋 Test 3: Direct Compact Formatter Usage")
    print("-" * 40)
    
    try:
        direct_compact = MorningEveningFormatter(config_compact)
        direct_morning = direct_compact.format_morning_report('Paliri', weather_data)
        direct_evening = direct_compact.format_evening_report('Paliri', weather_data)
        
        print(f"✅ Direct Morning Report:")
        print(f"   {direct_morning}")
        print(f"   Length: {len(direct_morning)} chars")
        
        print(f"✅ Direct Evening Report:")
        print(f"   {direct_evening}")
        print(f"   Length: {len(direct_evening)} chars")
        
    except Exception as e:
        print(f"❌ Direct compact formatter error: {e}")
    
    # Test 4: Comparison
    print("\n📋 Test 4: Comparison")
    print("-" * 40)
    
    try:
        print("🔍 Format Comparison:")
        print(f"   Standard: {len(morning_report_standard)} chars")
        print(f"   Compact:  {len(morning_report_compact)} chars")
        print(f"   Difference: {len(morning_report_standard) - len(morning_report_compact)} chars")
        
        if len(morning_report_compact) <= 160:
            print("✅ Compact format within 160 character limit")
        else:
            print("⚠️  Compact format exceeds 160 character limit")
            
    except Exception as e:
        print(f"❌ Comparison error: {e}")

if __name__ == "__main__":
    test_formatter_integration() 