#!/usr/bin/env python3
"""
Debug script to check thunderstorm_next_day calculation.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from wetter.fetch_meteofrance import get_forecast
from wetter.weather_data_processor import process_weather_data_for_report
from position.etappenlogik import get_next_stage, get_stage_coordinates
from logic.analyse_weather import analyze_weather_data
from config.config_loader import load_config

def debug_thunderstorm_next_day():
    """Debug thunderstorm_next_day calculation."""
    print("Debugging thunderstorm_next_day calculation...")
    
    # Load config
    config = load_config()
    
    # Get current stage coordinates (Paliri)
    current_stage = config.get("current_stage", "Paliri")
    coords = get_stage_coordinates(current_stage)
    latitude, longitude = coords[0]
    
    print(f"Current stage: {current_stage}")
    print(f"Current coordinates: {latitude}, {longitude}")
    
    # Process weather data for today
    processed_weather_data = process_weather_data_for_report(latitude, longitude, current_stage, config)
    print(f"\nToday's weather data keys: {list(processed_weather_data.keys())}")
    
    # Check if thunderstorm_next_day exists
    if "thunderstorm_next_day" in processed_weather_data:
        print(f"thunderstorm_next_day: {processed_weather_data['thunderstorm_next_day']}")
    else:
        print("thunderstorm_next_day NOT found in processed_weather_data")
    
    # Get next stage
    next_stage = get_next_stage(config)
    if next_stage:
        print(f"\nNext stage: {next_stage.get('name', 'Unknown')}")
        next_coords = get_stage_coordinates(next_stage)
        next_lat, next_lon = next_coords[0]
        print(f"Next stage coordinates: {next_lat}, {next_lon}")
        
        # Get weather data for tomorrow
        tomorrow_forecast = get_forecast(next_lat, next_lon)
        print(f"Tomorrow forecast data source: {tomorrow_forecast.data_source}")
        
        # Analyze tomorrow's weather data
        tomorrow_weather_data = tomorrow_forecast.to_weather_data()
        tomorrow_analysis = analyze_weather_data(tomorrow_weather_data, config)
        
        print(f"Tomorrow max thunderstorm probability: {tomorrow_analysis.max_thunderstorm_probability}")
        print(f"Tomorrow thunderstorm threshold time: {tomorrow_analysis.thunderstorm_threshold_time}")
        
        # Calculate what should be stored
        thunderstorm_next_day = tomorrow_analysis.max_thunderstorm_probability
        thunderstorm_next_day_threshold_time = tomorrow_analysis.thunderstorm_threshold_time
        
        print(f"\nCalculated values for tomorrow:")
        print(f"  thunderstorm_next_day: {thunderstorm_next_day}")
        print(f"  thunderstorm_next_day_threshold_time: {thunderstorm_next_day_threshold_time}")
        
        # Add to processed_weather_data
        processed_weather_data["thunderstorm_next_day"] = thunderstorm_next_day
        processed_weather_data["thunderstorm_next_day_threshold_time"] = thunderstorm_next_day_threshold_time
        
        print(f"\nAfter adding to processed_weather_data:")
        print(f"  thunderstorm_next_day: {processed_weather_data.get('thunderstorm_next_day')}")
        print(f"  thunderstorm_next_day_threshold_time: {processed_weather_data.get('thunderstorm_next_day_threshold_time')}")

if __name__ == "__main__":
    debug_thunderstorm_next_day() 