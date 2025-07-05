#!/usr/bin/env python3
"""
Example script demonstrating debug integration in report workflow.

This script shows how to use the ReportDebugger to add debug functionality
to the regular weather report generation process.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.wetter.report_debug import ReportDebugger, ReportDebugInfo, create_report_debugger
from src.wetter.fetch_meteofrance import get_forecast, get_thunderstorm
from src.logic.analyse_weather import analyze_weather_data
from src.model.datatypes import WeatherData, WeatherPoint
from src.config.config_loader import load_config


def generate_weather_report_with_debug(
    latitude: float,
    longitude: float,
    location_name: str
) -> Dict[str, Any]:
    """
    Generate a weather report with integrated debug functionality.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        location_name: Human-readable location name
        
    Returns:
        Dictionary containing report data and debug information
    """
    # Load configuration
    config = load_config()
    
    # Create debugger
    debugger = create_report_debugger(config)
    
    # Initialize debug info
    debug_info = ReportDebugInfo(
        timestamp=datetime.now(),
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        raw_data=None,
        weather_analysis=None,
        report_values={},
        comparison_results=None,
        debug_files=[]
    )
    
    print(f"🌤️ Generating weather report for {location_name}")
    print(f"Debug mode: {'Enabled' if debugger.should_debug() else 'Disabled'}")
    
    try:
        # Step 1: Collect weather data
        print(f"📡 Collecting weather data...")
        
        # Get current forecast
        forecast = get_forecast(latitude, longitude)
        thunderstorm = get_thunderstorm(latitude, longitude)
        
        # Create WeatherData object for analysis
        weather_point = WeatherPoint(
            latitude=latitude,
            longitude=longitude,
            elevation=0.0,
            time=datetime.now(),
            temperature=forecast.temperature,
            feels_like=forecast.temperature,
            precipitation=0.0,  # Not available in current forecast
            wind_speed=forecast.wind_speed or 0.0,
            cloud_cover=0.0,  # Not available in current forecast
            rain_probability=forecast.precipitation_probability,
            thunderstorm_probability=None,  # Will be determined from thunderstorm data
            wind_gusts=forecast.wind_gusts
        )
        
        weather_data = WeatherData(points=[weather_point])
        
        # Debug: Collect raw data
        if debugger.should_debug():
            debug_info.raw_data = debugger.debug_weather_data_collection(
                latitude, longitude, location_name
            )
        
        # Step 2: Analyze weather data
        print(f"📊 Analyzing weather data...")
        weather_analysis = analyze_weather_data(weather_data, config)
        
        # Debug: Analyze weather data
        if debugger.should_debug():
            debug_info.weather_analysis = debugger.debug_weather_analysis(
                weather_data, location_name
            )
        
        # Step 3: Generate report values
        report_values = {
            "temperature": forecast.temperature,
            "weather_condition": forecast.weather_condition,
            "precipitation_probability": forecast.precipitation_probability,
            "wind_speed": forecast.wind_speed,
            "wind_gusts": forecast.wind_gusts,
            "thunderstorm": thunderstorm,
            "max_rain_probability": weather_analysis.max_rain_probability,
            "max_thunderstorm_probability": weather_analysis.max_thunderstorm_probability,
            "max_precipitation": weather_analysis.max_precipitation,
            "max_wind_speed": weather_analysis.max_wind_speed,
            "risk_score": weather_analysis.risk
        }
        
        debug_info.report_values = report_values
        
        # Step 4: Debug comparison (if raw data available)
        if debugger.should_debug() and debug_info.raw_data:
            debug_info.comparison_results = debugger.debug_report_comparison(
                debug_info.raw_data, report_values, location_name
            )
        
        # Step 5: Debug threshold validation
        if debugger.should_debug():
            threshold_results = debugger.debug_threshold_validation(
                weather_data, location_name
            )
            if threshold_results:
                debug_info.debug_files.append(f"thresholds_{location_name.lower()}.json")
        
        # Step 6: Generate report text
        report_text = generate_report_text(report_values, location_name)
        
        # Step 7: Log debug information
        if debugger.should_debug():
            debugger.log_debug_info(debug_info)
        
        return {
            "location": location_name,
            "timestamp": datetime.now().isoformat(),
            "report_text": report_text,
            "report_values": report_values,
            "debug_enabled": debugger.should_debug(),
            "debug_info": debug_info if debugger.should_debug() else None
        }
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return {
            "location": location_name,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "debug_enabled": debugger.should_debug()
        }


def generate_report_text(report_values: Dict[str, Any], location_name: str) -> str:
    """
    Generate a simple report text from report values.
    
    Args:
        report_values: Report values dictionary
        location_name: Location name
        
    Returns:
        Formatted report text
    """
    lines = []
    lines.append(f"Wetterbericht für {location_name}")
    lines.append(f"Zeit: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    lines.append("")
    
    # Temperature
    temp = report_values.get("temperature")
    if temp is not None:
        lines.append(f"Temperatur: {temp}°C")
    
    # Weather condition
    weather = report_values.get("weather_condition")
    if weather:
        lines.append(f"Wetter: {weather}")
    
    # Precipitation probability
    precip_prob = report_values.get("precipitation_probability")
    if precip_prob is not None:
        lines.append(f"Regenwahrscheinlichkeit: {precip_prob}%")
    
    # Wind
    wind_speed = report_values.get("wind_speed")
    wind_gusts = report_values.get("wind_gusts")
    if wind_speed is not None:
        wind_text = f"Wind: {wind_speed} km/h"
        if wind_gusts is not None:
            wind_text += f" (Böen: {wind_gusts} km/h)"
        lines.append(wind_text)
    
    # Thunderstorm
    thunderstorm = report_values.get("thunderstorm")
    if thunderstorm:
        lines.append(f"Gewitter: {thunderstorm}")
    
    # Risk score
    risk_score = report_values.get("risk_score")
    if risk_score is not None:
        lines.append(f"Risiko-Score: {risk_score:.2f}")
    
    return "\n".join(lines)


def main():
    """Main function demonstrating debug integration."""
    print("🌤️ Weather Report with Debug Integration Example")
    print("=" * 50)
    
    # Test locations
    test_locations = [
        (42.15, 9.15, "Corte"),
        (42.23, 9.15, "Asco"),
        (42.45, 9.03, "Calenzana")
    ]
    
    # Load configuration to check debug settings
    config = load_config()
    debug_config = config.get("debug", {})
    
    print(f"Debug configuration:")
    print(f"  Enabled: {debug_config.get('enabled', False)}")
    print(f"  Raw data output: {debug_config.get('raw_data_output', True)}")
    print(f"  Threshold validation: {debug_config.get('threshold_validation', True)}")
    print(f"  Comparison with report: {debug_config.get('comparison_with_report', True)}")
    print(f"  Save debug files: {debug_config.get('save_debug_files', True)}")
    print(f"  Output directory: {debug_config.get('output_directory', 'output/debug')}")
    print()
    
    # Generate reports for each location
    for latitude, longitude, name in test_locations:
        print(f"📍 Processing {name}...")
        
        result = generate_weather_report_with_debug(latitude, longitude, name)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Report generated successfully")
            print(f"📄 Report text:")
            print("-" * 30)
            print(result["report_text"])
            print("-" * 30)
            
            if result.get("debug_enabled") and result.get("debug_info"):
                debug_info = result["debug_info"]
                print(f"🔍 Debug info collected:")
                print(f"  - Raw data points: {len(debug_info.raw_data.time_points) if debug_info.raw_data else 0}")
                print(f"  - Weather analysis: {'Yes' if debug_info.weather_analysis else 'No'}")
                print(f"  - Comparison results: {'Yes' if debug_info.comparison_results else 'No'}")
                print(f"  - Debug files: {len(debug_info.debug_files)}")
        
        print()
    
    print("🎉 Example completed!")
    print("\nTo enable debug mode, set 'debug.enabled: true' in config.yaml")


if __name__ == "__main__":
    main() 