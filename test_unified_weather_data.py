#!/usr/bin/env python3
"""
Test script for unified weather data structure.
"""

import sys
import os
sys.path.append('src')

from datetime import datetime, timedelta
from meteofrance_api.client import MeteoFranceClient
from wetter.unified_weather_data import WeatherEntry, WeatherDataPoint, UnifiedWeatherData

def test_unified_weather_data():
    """Test the unified weather data structure with real meteofrance-api data."""
    
    print("Testing unified weather data structure")
    print("=" * 50)
    
    # Test coordinate: Conca, Corsica
    lat = 41.79418
    lon = 9.259567
    location_name = "Conca"
    
    try:
        # Fetch data from meteofrance-api
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        print(f"Fetched {len(forecast.forecast)} entries from meteofrance-api")
        
        # Create unified weather data structure
        unified_data = UnifiedWeatherData()
        unified_data.stage_name = location_name
        unified_data.stage_date = datetime.now().strftime('%Y-%m-%d')
        
        # Create data point
        data_point = WeatherDataPoint(
            latitude=lat,
            longitude=lon,
            location_name=location_name
        )
        
        # Convert meteofrance entries to unified format
        for entry in forecast.forecast:
            weather_entry = WeatherEntry.from_meteofrance_entry(entry)
            data_point.add_entry(weather_entry)
        
        unified_data.add_data_point(data_point)
        
        print(f"Converted {len(data_point.entries)} entries to unified format")
        
        # Test time range queries
        now = datetime.now()
        start_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        print(f"\nAnalyzing data for time range: {start_time} to {end_time}")
        
        # Get temperature stats
        temp_stats = data_point.get_temperature_stats(start_time, end_time)
        print(f"Temperature stats: {temp_stats}")
        
        # Get rain stats
        rain_stats = data_point.get_rain_stats(start_time, end_time)
        print(f"Rain stats: {rain_stats}")
        
        # Get wind stats
        wind_stats = data_point.get_wind_stats(start_time, end_time)
        print(f"Wind stats: {wind_stats}")
        
        # Get thunderstorm info
        thunderstorm_info = data_point.get_thunderstorm_info(start_time, end_time)
        print(f"Thunderstorm info: {thunderstorm_info}")
        
        # Test aggregated stats
        aggregated_stats = unified_data.get_aggregated_stats(start_time, end_time)
        print(f"\nAggregated stats: {aggregated_stats}")
        
        # Test debug output format
        print("\n" + "=" * 50)
        print("DEBUG OUTPUT FORMAT:")
        print(f"Stage: {unified_data.stage_name}")
        print(f"Date: {unified_data.stage_date}")
        print(f"Data points: {len(unified_data.data_points)}")
        
        for i, point in enumerate(unified_data.data_points):
            print(f"\nData Point {i+1}:")
            print(f"  Location: {point.location_name} ({point.latitude}, {point.longitude})")
            print(f"  Entries: {len(point.entries)}")
            
            # Show first few entries
            for j, entry in enumerate(point.entries[:3]):
                print(f"    Entry {j+1}: {entry.timestamp.strftime('%H:%M')} - "
                      f"Temp: {entry.temperature}°C, "
                      f"Rain: {entry.rain_amount}mm/h, "
                      f"Wind: {entry.wind_speed}km/h, "
                      f"Weather: {entry.weather_description}")
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error testing unified weather data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unified_weather_data() 