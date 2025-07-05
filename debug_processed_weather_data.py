#!/usr/bin/env python3
"""
Debug script to check processed_weather_data values.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from wetter.weather_data_processor import process_weather_data_for_report
from position.etappenlogik import get_next_stage, get_stage_coordinates
from config.config_loader import load_config

def debug_processed_weather_data():
    """Debug processed_weather_data values."""
    print("Debugging processed_weather_data values...")
    
    # Load config
    config = load_config()
    
    # Get current stage coordinates (Paliri)
    from position.etappenlogik import get_current_stage
    current_stage_obj = get_current_stage(config)
    if not current_stage_obj:
        print("No current stage found")
        return
    coords = get_stage_coordinates(current_stage_obj)
    latitude, longitude = coords[0]
    current_stage = current_stage_obj["name"]
    
    print(f"Current stage: {current_stage}")
    print(f"Current coordinates: {latitude}, {longitude}")
    
    # Process weather data for today
    processed_weather_data = process_weather_data_for_report(latitude, longitude, current_stage, config)
    print(f"\nToday's weather data keys: {list(processed_weather_data.keys())}")
    
    # Check thunderstorm_next_day values
    thunderstorm_next_day = processed_weather_data.get("thunderstorm_next_day")
    thunderstorm_next_day_threshold_time = processed_weather_data.get("thunderstorm_next_day_threshold_time")
    
    print(f"\nthunderstorm_next_day: {thunderstorm_next_day}")
    print(f"thunderstorm_next_day_threshold_time: {thunderstorm_next_day_threshold_time}")
    
    # Get next stage
    next_stage = get_next_stage(config)
    if next_stage:
        print(f"\nNext stage: {next_stage.get('name', 'Unknown')}")
        next_coords = get_stage_coordinates(next_stage)
        next_lat, next_lon = next_coords[0]
        print(f"Next stage coordinates: {next_lat}, {next_lon}")
        
        # Process weather data for tomorrow
        tomorrow_processed_data = process_weather_data_for_report(next_lat, next_lon, next_stage["name"], config)
        print(f"\nTomorrow's weather data keys: {list(tomorrow_processed_data.keys())}")
        
        # Check what values are available for tomorrow
        max_thunderstorm_probability = tomorrow_processed_data.get("max_thunderstorm_probability")
        thunderstorm_threshold_time = tomorrow_processed_data.get("thunderstorm_threshold_time")
        
        print(f"\nTomorrow's values:")
        print(f"  max_thunderstorm_probability: {max_thunderstorm_probability}")
        print(f"  thunderstorm_threshold_time: {thunderstorm_threshold_time}")
        
        # Simulate what should be stored
        processed_weather_data["thunderstorm_next_day"] = max_thunderstorm_probability
        processed_weather_data["thunderstorm_next_day_threshold_time"] = thunderstorm_threshold_time
        
        print(f"\nAfter adding to processed_weather_data:")
        print(f"  thunderstorm_next_day: {processed_weather_data.get('thunderstorm_next_day')}")
        print(f"  thunderstorm_next_day_threshold_time: {processed_weather_data.get('thunderstorm_next_day_threshold_time')}")

if __name__ == "__main__":
    debug_processed_weather_data() 