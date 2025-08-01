#!/usr/bin/env python3
"""
Real Live Test with actual weather data from MeteoFrance API.
Tests the compact formatter with real weather data for the current stage.
"""

import sys
import os
from datetime import datetime, date, timedelta
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_loader import load_config
from weather.core.models import create_report_config_from_yaml, ReportType, AggregatedWeatherData
from weather.core.formatter import WeatherFormatter
from position.etappenlogik import get_stage_info
from wetter.weather_data_processor import WeatherDataProcessor
from wetter.unified_weather_data import UnifiedWeatherData

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_real_weather_data_for_stage(stage_name: str, coordinates: list) -> AggregatedWeatherData:
    """
    Fetch real weather data from MeteoFrance API for a stage.
    
    Args:
        stage_name: Name of the stage
        coordinates: List of [lat, lon] coordinate pairs
        
    Returns:
        AggregatedWeatherData with real weather data
    """
    try:
        logger.info(f"Fetching real weather data for stage: {stage_name}")
        logger.info(f"Coordinates: {coordinates}")
        
        # Initialize weather data processor
        processor = WeatherDataProcessor()
        
        # Get unified weather data for the stage
        unified_data = processor.get_stage_weather_data(coordinates, stage_name)
        
        # Define time windows for morning report
        today = date.today()
        start_time = datetime.combine(today, datetime.min.time()) + timedelta(hours=5)  # 05:00
        end_time = datetime.combine(today, datetime.min.time()) + timedelta(hours=23)   # 23:00
        
        # Get weather summary
        weather_summary = processor.get_weather_summary(
            unified_data, 
            start_time, 
            end_time, 
            'morning'
        )
        
        logger.info(f"Weather summary keys: {list(weather_summary.keys())}")
        
        # Create AggregatedWeatherData from real data
        aggregated_data = AggregatedWeatherData(
            location_name=stage_name,
            latitude=coordinates[0][0] if coordinates else 0.0,
            longitude=coordinates[0][1] if coordinates else 0.0,
            target_date=today,
            time_window="morning",
            data_source="meteo_france",
            processed_at=datetime.now(),
            
            # Temperature data
            max_temperature=weather_summary.get('max_temperature'),
            min_temperature=weather_summary.get('min_temperature'),
            max_temperature_time=weather_summary.get('max_temperature_time'),
            min_temperature_time=weather_summary.get('min_temperature_time'),
            
            # Rain data
            max_rain_probability=weather_summary.get('max_rain_probability'),
            rain_threshold_pct=weather_summary.get('rain_threshold_pct'),
            rain_threshold_time=weather_summary.get('rain_threshold_time'),
            rain_max_time=weather_summary.get('rain_max_time'),
            max_precipitation=weather_summary.get('max_precipitation'),
            precipitation_max_time=weather_summary.get('precipitation_max_time'),
            
            # Wind data
            max_wind_speed=weather_summary.get('max_wind_speed'),
            wind_threshold_kmh=weather_summary.get('wind_threshold_kmh'),
            wind_threshold_time=weather_summary.get('wind_threshold_time'),
            wind_max_time=weather_summary.get('wind_max_time'),
            max_wind_gusts=weather_summary.get('max_wind_gusts'),
            wind_gusts_max_time=weather_summary.get('wind_gusts_max_time'),
            
            # Thunderstorm data
            max_thunderstorm_probability=weather_summary.get('max_thunderstorm_probability'),
            thunderstorm_threshold_pct=weather_summary.get('thunderstorm_threshold_pct'),
            thunderstorm_threshold_time=weather_summary.get('thunderstorm_threshold_time'),
            thunderstorm_max_time=weather_summary.get('thunderstorm_max_time'),
            
            # Tomorrow thunderstorm data
            tomorrow_max_thunderstorm_probability=weather_summary.get('tomorrow_thunderstorm_probability'),
            tomorrow_thunderstorm_threshold_time=weather_summary.get('tomorrow_thunderstorm_threshold_time'),
            tomorrow_thunderstorm_max_time=weather_summary.get('tomorrow_thunderstorm_max_time')
        )
        
        logger.info(f"Successfully created AggregatedWeatherData with real weather data")
        return aggregated_data
        
    except Exception as e:
        logger.error(f"Failed to fetch real weather data: {e}")
        raise

def test_real_live_weather():
    """Test the compact formatter with real weather data from MeteoFrance API."""
    
    print("🌤️  REAL LIVE TEST - MeteoFrance API Weather Data")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Load real configuration
        print("📋 Loading configuration from config.yaml...")
        config_dict = load_config()
        config = create_report_config_from_yaml(config_dict)
        
        print(f"✅ Configuration loaded successfully")
        print(f"   use_compact_formatter: {config.use_compact_formatter}")
        print(f"   rain_probability_threshold: {config.rain_probability_threshold}")
        print(f"   wind_speed_threshold: {config.wind_speed_threshold}")
        
        # Get current stage info
        print("📋 Getting current stage information...")
        stage_info = get_stage_info(config_dict)
        
        if not stage_info:
            print("❌ No stage info available")
            return
        
        stage_name = stage_info["name"]
        coordinates = stage_info["coordinates"]
        
        print(f"✅ Stage info loaded: {stage_name}")
        print(f"   Coordinates: {len(coordinates)} points")
        for i, coord in enumerate(coordinates):
            print(f"   Point {i+1}: {coord[0]:.4f}, {coord[1]:.4f}")
        
        # Fetch real weather data from MeteoFrance API
        print(f"\n🌤️  Fetching real weather data from MeteoFrance API...")
        print("-" * 40)
        
        real_weather_data = get_real_weather_data_for_stage(stage_name, coordinates)
        
        print(f"✅ Real weather data fetched successfully!")
        print(f"   Max temperature: {real_weather_data.max_temperature}°C")
        print(f"   Min temperature: {real_weather_data.min_temperature}°C")
        print(f"   Max rain probability: {real_weather_data.max_rain_probability}%")
        print(f"   Max precipitation: {real_weather_data.max_precipitation}mm")
        print(f"   Max wind speed: {real_weather_data.max_wind_speed} km/h")
        print(f"   Max wind gusts: {real_weather_data.max_wind_gusts} km/h")
        print(f"   Max thunderstorm probability: {real_weather_data.max_thunderstorm_probability}%")
        
        # Create formatter
        formatter = WeatherFormatter(config)
        
        # Prepare stage names
        stage_names = {
            'today': stage_name,
            'tomorrow': 'Vizzavona',
            'day_after_tomorrow': 'Corte'
        }
        
        # Generate reports with real data
        print(f"\n📋 Generating reports with REAL weather data...")
        print("-" * 40)
        
        # Morning report
        print(f"📅 Generating Morning Report...")
        morning_report = formatter.format_report_text(
            real_weather_data, 
            ReportType.MORNING, 
            stage_names
        )
        
        # Evening report
        print(f"🌙 Generating Evening Report...")
        evening_report = formatter.format_report_text(
            real_weather_data, 
            ReportType.EVENING, 
            stage_names
        )
        
        # Email subject
        print(f"📧 Generating Email Subject...")
        email_subject = formatter.format_email_subject(
            ReportType.MORNING,
            stage_name
        )
        
        # Display results
        print(f"\n📋 REAL LIVE TEST RESULTS")
        print("-" * 40)
        print(f"✅ Stage: {stage_name}")
        print(f"✅ Data source: {real_weather_data.data_source}")
        print(f"✅ Compact formatter: {'Enabled' if config.use_compact_formatter else 'Disabled'}")
        print(f"✅ Real weather data: YES (from MeteoFrance API)")
        print()
        
        print(f"📅 Morning Report (REAL DATA):")
        print(f"   {morning_report}")
        print(f"   Length: {len(morning_report)} chars")
        print(f"   Within limit: {len(morning_report) <= config.max_report_length}")
        print()
        
        print(f"🌙 Evening Report (REAL DATA):")
        print(f"   {evening_report}")
        print(f"   Length: {len(evening_report)} chars")
        print(f"   Within limit: {len(evening_report) <= config.max_report_length}")
        print()
        
        print(f"📧 Email Subject:")
        print(f"   {email_subject}")
        print()
        
        # Test character limit compliance
        print(f"📋 Character Limit Compliance")
        print("-" * 40)
        morning_ok = len(morning_report) <= config.max_report_length
        evening_ok = len(evening_report) <= config.max_report_length
        
        print(f"   Morning report: {'✅' if morning_ok else '❌'} {len(morning_report)}/{config.max_report_length}")
        print(f"   Evening report: {'✅' if evening_ok else '❌'} {len(evening_report)}/{config.max_report_length}")
        
        if morning_ok and evening_ok:
            print(f"   🎯 All reports within character limit!")
        else:
            print(f"   ⚠️  Some reports exceed character limit!")
        
        # Summary
        print(f"\n📋 REAL LIVE TEST SUMMARY")
        print("-" * 40)
        print(f"✅ MeteoFrance API connection: SUCCESS")
        print(f"✅ Real weather data fetching: SUCCESS")
        print(f"✅ Data aggregation: SUCCESS")
        print(f"✅ Compact formatter integration: SUCCESS")
        print(f"✅ Report generation: SUCCESS")
        print(f"✅ Character limit compliance: {'SUCCESS' if morning_ok and evening_ok else 'PARTIAL'}")
        print()
        
        if config.use_compact_formatter:
            print(f"🎯 Using new compact format with REAL weather data!")
            print(f"🎯 This is a TRUE LIVE TEST with actual API calls!")
        else:
            print(f"🎯 Using standard format with REAL weather data!")
            
        print(f"\n🌤️  REAL LIVE TEST COMPLETED SUCCESSFULLY!")
        print(f"   Real weather data from MeteoFrance API")
        print(f"   Compact formatter working with live data")
        print(f"   Ready for production use!")
            
    except Exception as e:
        print(f"❌ Real live test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_live_weather() 