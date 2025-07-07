#!/usr/bin/env python3
"""
Debug script to check weather_data values for report formatting.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from wetter.weather_data_processor import process_weather_data_for_report
from position.etappenlogik import get_current_stage, get_stage_coordinates
from config.config_loader import load_config

def debug_report_format():
    """Debug weather_data values for report formatting."""
    print("Debugging weather_data values for report formatting...")
    
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
    
    # Process weather data for today
    processed_weather_data = process_weather_data_for_report(latitude, longitude, current_stage, config)
    
    print(f"\nWeather data keys: {list(processed_weather_data.keys())}")
    
    # Check thunderstorm values
    thunderstorm_threshold_pct = processed_weather_data.get("thunderstorm_threshold_pct")
    thunderstorm_threshold_time = processed_weather_data.get("thunderstorm_threshold_time")
    max_thunderstorm_probability = processed_weather_data.get("max_thunderstorm_probability")
    thunderstorm_max_time = processed_weather_data.get("thunderstorm_max_time")
    
    print(f"\nThunderstorm values:")
    print(f"  thunderstorm_threshold_pct: {thunderstorm_threshold_pct}")
    print(f"  thunderstorm_threshold_time: {thunderstorm_threshold_time}")
    print(f"  max_thunderstorm_probability: {max_thunderstorm_probability}")
    print(f"  thunderstorm_max_time: {thunderstorm_max_time}")
    
    # Check rain values
    rain_threshold_pct = processed_weather_data.get("rain_threshold_pct")
    rain_threshold_time = processed_weather_data.get("rain_threshold_time")
    max_rain_probability = processed_weather_data.get("max_rain_probability")
    rain_max_time = processed_weather_data.get("rain_max_time")
    
    print(f"\nRain values:")
    print(f"  rain_threshold_pct: {rain_threshold_pct}")
    print(f"  rain_threshold_time: {rain_threshold_time}")
    print(f"  max_rain_probability: {max_rain_probability}")
    print(f"  rain_max_time: {rain_max_time}")
    
    # Simulate report formatting
    print(f"\nSimulated report formatting:")
    
    # Thunderstorm part
    if (thunderstorm_threshold_pct == 0 or thunderstorm_threshold_pct is None) and max_thunderstorm_probability > 0:
        thunder_part = f"Gew.{max_thunderstorm_probability:.0f}%@{thunderstorm_max_time}"
    elif thunderstorm_threshold_pct == 0 or thunderstorm_threshold_pct is None:
        thunder_part = "Gew. -"
    else:
        thunder_part = f"Gew.{thunderstorm_threshold_pct:.0f}%@{thunderstorm_threshold_time}"
        if max_thunderstorm_probability > thunderstorm_threshold_pct:
            thunder_part += f"({max_thunderstorm_probability:.0f}%@{thunderstorm_max_time})"
    
    print(f"  thunder_part: {thunder_part}")
    
    # Rain part
    if (rain_threshold_pct == 0 or rain_threshold_pct is None) and max_rain_probability > 0:
        rain_part = f"Regen{max_rain_probability:.0f}%@{rain_max_time}"
    elif rain_threshold_pct == 0 or rain_threshold_pct is None:
        rain_part = "Regen -"
    else:
        rain_part = f"Regen{rain_threshold_pct:.0f}%@{rain_threshold_time}"
        if max_rain_probability > rain_threshold_pct:
            rain_part += f"({max_rain_probability:.0f}%@{rain_max_time})"
    
    print(f"  rain_part: {rain_part}")

if __name__ == "__main__":
    debug_report_format() 