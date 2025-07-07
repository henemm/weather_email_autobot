#!/usr/bin/env python3
"""
Debug script to check time points and their values.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from wetter.fetch_meteofrance import get_forecast
from position.etappenlogik import get_current_stage, get_stage_coordinates
from config.config_loader import load_config

def debug_time_points():
    """Debug time points and their values."""
    print("Debugging time points and their values...")
    
    # Load config
    config = load_config()
    
    # Get current stage coordinates (Paliri)
    current_stage_obj = get_current_stage(config)
    if not current_stage_obj:
        print("No current stage found")
        return
    coords = get_stage_coordinates(current_stage_obj)
    latitude, longitude = coords[0]
    current_stage = current_stage_obj["name"]
    
    print(f"Current stage: {current_stage}")
    print(f"Current coordinates: {latitude}, {longitude}")
    
    # Get raw forecast data
    forecast = get_forecast(latitude, longitude)
    
    print(f"\nRaw forecast entries:")
    for i, entry in enumerate(forecast.forecast_data[:10]):  # First 10 entries
        dt_timestamp = entry.get('dt')
        if dt_timestamp:
            entry_datetime = datetime.fromtimestamp(dt_timestamp)
            hour = entry_datetime.hour
            
            weather_condition = entry.get('weather', {}).get('desc') if isinstance(entry.get('weather'), dict) else entry.get('weather')
            precipitation_probability = entry.get('precipitation_probability')
            
            print(f"  Entry {i}: {entry_datetime.strftime('%Y-%m-%d %H:%M')} (hour: {hour})")
            print(f"    Weather: {weather_condition}")
            print(f"    Precipitation probability: {precipitation_probability}%")
            
            # Check if this is in stage time (14-17 Uhr)
            if 14 <= hour <= 17:
                print(f"    -> STAGE TIME (14-17 Uhr)")
            else:
                print(f"    -> Outside stage time")
    
    # Check thresholds
    thunderstorm_threshold = config.get("thresholds", {}).get("thunderstorm_probability", 20.0)
    rain_threshold = config.get("thresholds", {}).get("rain_probability", 25.0)
    
    print(f"\nThresholds:")
    print(f"  Thunderstorm threshold: {thunderstorm_threshold}%")
    print(f"  Rain threshold: {rain_threshold}%")

if __name__ == "__main__":
    debug_time_points() 