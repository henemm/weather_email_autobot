#!/usr/bin/env python3
"""
Simple debug output function that works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def load_config():
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def generate_simple_debug_output():
    """Generate simple debug output that works correctly."""
    
    print("GENERATING SIMPLE DEBUG OUTPUT")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print()
    
    try:
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        # Process Rain(mm) data
        rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        
        print("Rain(mm) Data:")
        print(f"  threshold_value: {rain_mm_result.threshold_value}")
        print(f"  threshold_time: {rain_mm_result.threshold_time}")
        print(f"  max_value: {rain_mm_result.max_value}")
        print(f"  max_time: {rain_mm_result.max_time}")
        print(f"  geo_points: {rain_mm_result.geo_points}")
        print()
        
        # Generate simple debug output
        debug_lines = []
        debug_lines.append("# DEBUG DATENEXPORT")
        debug_lines.append("")
        debug_lines.append(f"Berichts-Typ: morning")
        debug_lines.append("")
        debug_lines.append(f"heute: {target_date.strftime('%Y-%m-%d')}, {stage_name}, 3 Punkte")
        debug_lines.append("  T1G1 \"lat\": 47.638699, \"lon\": 6.846891")
        debug_lines.append("  T1G2 \"lat\": 47.246166, \"lon\": -1.652276")
        debug_lines.append("  T1G3 \"lat\": 43.283255, \"lon\": 5.370061")
        debug_lines.append("")
        
        # Add Rain(mm) section
        if rain_mm_result.geo_points:
            debug_lines.append("RAIN(MM)")
            for i, point in enumerate(rain_mm_result.geo_points):
                for geo, value in point.items():
                    debug_lines.append(f"{geo} | {value}")
            debug_lines.append("=========")
            if rain_mm_result.threshold_time is not None and rain_mm_result.threshold_value is not None:
                debug_lines.append(f"Threshold | {rain_mm_result.threshold_time} | {rain_mm_result.threshold_value}")
            if rain_mm_result.max_time is not None and rain_mm_result.max_value is not None:
                debug_lines.append(f"Maximum | {rain_mm_result.max_time} | {rain_mm_result.max_value}")
            debug_lines.append("")
        
        # Join debug lines
        debug_output = "\n".join(debug_lines)
        
        print("SIMPLE DEBUG OUTPUT:")
        print(debug_output)
        print()
        
        # Check if RAIN(MM) section is present
        if "RAIN(MM)" in debug_output:
            print("✅ RAIN(MM) section found in debug output")
        else:
            print("❌ RAIN(MM) section NOT found in debug output")
        
        return debug_output
        
    except Exception as e:
        print(f"Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    generate_simple_debug_output() 