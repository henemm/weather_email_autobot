#!/usr/bin/env python3
"""
Test script for real integration with config.yaml.
Tests the compact formatter with actual configuration settings.
"""

import sys
import os
from datetime import datetime, date

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_loader import load_config
from weather.core.models import create_report_config_from_yaml, AggregatedWeatherData, ReportType
from weather.core.formatter import WeatherFormatter

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

def test_real_integration():
    """Test integration with real config.yaml."""
    
    print("🧪 Testing Real Integration with config.yaml")
    print("=" * 60)
    
    try:
        # Load real configuration
        print("📋 Loading configuration from config.yaml...")
        config_dict = load_config()
        config = create_report_config_from_yaml(config_dict)
        
        print(f"✅ Configuration loaded successfully")
        print(f"   use_compact_formatter: {config.use_compact_formatter}")
        print(f"   rain_probability_threshold: {config.rain_probability_threshold}")
        print(f"   wind_speed_threshold: {config.wind_speed_threshold}")
        print(f"   max_report_length: {config.max_report_length}")
        
        # Create sample data
        weather_data = create_sample_weather_data()
        stage_names = {
            'today': 'Paliri',
            'tomorrow': 'Vizzavona',
            'day_after_tomorrow': 'Corte'
        }
        
        # Create formatter with real config
        formatter = WeatherFormatter(config)
        
        # Test morning report
        print(f"\n📋 Testing Morning Report Generation")
        print("-" * 40)
        
        morning_report = formatter.format_report_text(
            weather_data, 
            ReportType.MORNING, 
            stage_names
        )
        
        print(f"✅ Morning Report Generated:")
        print(f"   {morning_report}")
        print(f"   Length: {len(morning_report)} chars")
        print(f"   Within limit: {len(morning_report) <= config.max_report_length}")
        
        # Test evening report
        print(f"\n📋 Testing Evening Report Generation")
        print("-" * 40)
        
        evening_report = formatter.format_report_text(
            weather_data, 
            ReportType.EVENING, 
            stage_names
        )
        
        print(f"✅ Evening Report Generated:")
        print(f"   {evening_report}")
        print(f"   Length: {len(evening_report)} chars")
        print(f"   Within limit: {len(evening_report) <= config.max_report_length}")
        
        # Test email subject
        print(f"\n📋 Testing Email Subject Generation")
        print("-" * 40)
        
        email_subject = formatter.format_email_subject(
            ReportType.MORNING,
            'Paliri'
        )
        
        print(f"✅ Email Subject Generated:")
        print(f"   {email_subject}")
        
        # Summary
        print(f"\n📋 Integration Summary")
        print("-" * 40)
        print(f"✅ Compact formatter: {'Enabled' if config.use_compact_formatter else 'Disabled'}")
        print(f"✅ Morning report: {len(morning_report)} chars")
        print(f"✅ Evening report: {len(evening_report)} chars")
        print(f"✅ Email subject: {email_subject}")
        
        if config.use_compact_formatter:
            print(f"🎯 Using new compact format (morning-evening-refactor.md specification)")
        else:
            print(f"🎯 Using standard format (email_format.mdc specification)")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_integration() 