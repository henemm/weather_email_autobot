#!/usr/bin/env python3
"""
Demo script for MorningEveningFormatter
Shows how to use the new compact weather report formatter
"""

from src.weather.core.morning_evening_formatter import MorningEveningFormatter
from src.weather.core.models import ReportConfig, AggregatedWeatherData
from datetime import datetime, date

def demo_formatter():
    """Demonstrate the MorningEveningFormatter functionality"""
    
    # Create configuration
    config = ReportConfig(
        rain_probability_threshold=25.0,
        thunderstorm_probability_threshold=20.0,
        rain_amount_threshold=0.2,
        wind_speed_threshold=10.0,
        temperature_threshold=32.0
    )
    
    # Create sample weather data
    weather_data = AggregatedWeatherData(
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
    
    # Create formatter
    formatter = MorningEveningFormatter(config)
    
    # Generate reports
    stage_name = "Paliri"
    
    print("🌤️  MorningEveningFormatter Demo")
    print("=" * 50)
    
    # Morning report
    morning_report = formatter.format_morning_report(stage_name, weather_data)
    print(f"📅 Morning Report:")
    print(f"   {morning_report}")
    print(f"   Length: {len(morning_report)} chars")
    print()
    
    # Evening report
    evening_report = formatter.format_evening_report(stage_name, weather_data)
    print(f"🌙 Evening Report:")
    print(f"   {evening_report}")
    print(f"   Length: {len(evening_report)} chars")
    print()
    
    # Individual field examples
    print("🔍 Individual Fields:")
    print(f"   Night: {formatter._format_night_field(weather_data)}")
    print(f"   Day: {formatter._format_day_field(weather_data)}")
    print(f"   Rain(mm): {formatter._format_rain_mm_field(weather_data)}")
    print(f"   Rain(%): {formatter._format_rain_percentage_field(weather_data)}")
    print(f"   Wind: {formatter._format_wind_field(weather_data)}")
    print(f"   Gust: {formatter._format_gust_field(weather_data)}")
    print(f"   Thunderstorm: {formatter._format_thunderstorm_field(weather_data)}")
    print(f"   Thunderstorm+1: {formatter._format_thunderstorm_plus_one_field(weather_data)}")

if __name__ == "__main__":
    demo_formatter() 