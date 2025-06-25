#!/usr/bin/env python3
"""
Weather Warning Monitor Script.

This script monitors weather conditions based on current GPS position and planned route,
generating warnings only when significant changes are detected compared to previous state.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from position.fetch_sharemap import fetch_sharemap_position
from wetter.fetch_arome_wcs import fetch_weather_for_position
from logic.analyse_weather import analyze_weather_data
from wetter.warntext_generator import generate_warntext
from state.tracker import WarningStateTracker
from config.config_loader import load_config


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/warning_monitor.log'),
            logging.StreamHandler()
        ]
    )


def get_current_position(config: Dict[str, Any]) -> Optional[Any]:
    """
    Get current GPS position from ShareMap.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        CurrentPosition object or None if unavailable
    """
    sharemap_url = config.get("sharemap_url")
    if not sharemap_url:
        logging.warning("No ShareMap URL configured, skipping position check")
        return None
    
    try:
        position = fetch_sharemap_position(sharemap_url)
        if position:
            logging.info(f"Current position: {position.latitude}, {position.longitude}")
        else:
            logging.warning("No position data available from ShareMap")
        return position
    except Exception as e:
        logging.error(f"Failed to fetch position: {e}")
        return None


def get_planned_route(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get planned route information from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Route information dictionary or None if not configured
    """
    route = config.get("route")
    if not route:
        logging.warning("No route configuration found")
        return None
    
    logging.info(f"Planned route: {route.get('name', 'Unknown')}")
    return route


def analyze_weather_for_location(latitude: float, longitude: float, config: Dict[str, Any]) -> Any:
    """
    Analyze weather data for a specific location.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        config: Configuration dictionary
        
    Returns:
        WeatherAnalysis object
    """
    try:
        # Fetch weather data
        weather_data = fetch_weather_for_position(latitude, longitude)
        
        # Analyze weather data
        analysis = analyze_weather_data(weather_data, config)
        
        logging.info(f"Weather analysis for {latitude}, {longitude}: {analysis.summary}")
        return analysis
        
    except Exception as e:
        logging.error(f"Failed to analyze weather for {latitude}, {longitude}: {e}")
        raise


def generate_warning_text(analysis: Any, location_name: str) -> str:
    """
    Generate warning text from weather analysis.
    
    Args:
        analysis: WeatherAnalysis object
        location_name: Name of the location
        
    Returns:
        Formatted warning text
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    text_lines = [
        f"WEATHER WARNING - {location_name}",
        f"Time: {timestamp}",
        "",
        f"Thunderstorm probability: {analysis.max_thunderstorm_probability or 0:.1f}%",
        f"Max precipitation: {analysis.max_precipitation:.1f} mm",
        f"Max wind speed: {analysis.max_wind_speed:.1f} km/h",
        f"Max temperature: {analysis.max_temperature:.1f}°C",
        f"Max cloud cover: {analysis.max_cloud_cover:.1f}%",
        "",
        f"Summary: {analysis.summary}",
        "",
        "Stay safe and monitor conditions!"
    ]
    
    return "\n".join(text_lines)


def save_warning_text(text: str, output_file: str) -> None:
    """
    Save warning text to output file.
    
    Args:
        text: Warning text to save
        output_file: Path to output file
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logging.info(f"Warning saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Failed to save warning text: {e}")
        raise


def run_warning_monitor() -> None:
    """
    Main function to run the weather warning monitor.
    
    This function:
    1. Gets current position from ShareMap
    2. Gets planned route from configuration
    3. Analyzes weather for both locations
    4. Compares with previous state
    5. Generates warning if significant changes detected
    """
    # Setup logging
    setup_logging()
    logging.info("Starting weather warning monitor")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize state tracker
        state_file = config.get("state_file", "data/warning_state.json")
        tracker = WarningStateTracker(state_file)
        
        # Get current position
        current_position = get_current_position(config)
        
        # Get planned route
        planned_route = get_planned_route(config)
        
        # Analyze weather for available locations
        weather_analyses = []
        
        if current_position:
            try:
                position_analysis = analyze_weather_for_location(
                    current_position.latitude, 
                    current_position.longitude, 
                    config
                )
                weather_analyses.append(position_analysis)
                logging.info("Weather analysis completed for current position")
            except Exception as e:
                logging.error(f"Failed to analyze weather for current position: {e}")
        
        if planned_route:
            route_coords = planned_route.get("coordinates", [])
            for i, coord in enumerate(route_coords):
                try:
                    route_analysis = analyze_weather_for_location(
                        coord["latitude"], 
                        coord["longitude"], 
                        config
                    )
                    weather_analyses.append(route_analysis)
                    logging.info(f"Weather analysis completed for route point {i+1}")
                except Exception as e:
                    logging.error(f"Failed to analyze weather for route point {i+1}: {e}")
        
        if not weather_analyses:
            logging.error("No weather analyses available, cannot proceed")
            return
        
        # Use worst-case analysis (highest risk values)
        worst_case_analysis = weather_analyses[0]
        for analysis in weather_analyses[1:]:
            if analysis.max_thunderstorm_probability > worst_case_analysis.max_thunderstorm_probability:
                worst_case_analysis.max_thunderstorm_probability = analysis.max_thunderstorm_probability
            if analysis.max_precipitation > worst_case_analysis.max_precipitation:
                worst_case_analysis.max_precipitation = analysis.max_precipitation
            if analysis.max_wind_speed > worst_case_analysis.max_wind_speed:
                worst_case_analysis.max_wind_speed = analysis.max_wind_speed
            if analysis.max_temperature > worst_case_analysis.max_temperature:
                worst_case_analysis.max_temperature = analysis.max_temperature
            if analysis.max_cloud_cover > worst_case_analysis.max_cloud_cover:
                worst_case_analysis.max_cloud_cover = analysis.max_cloud_cover
        
        # Check for significant changes
        if tracker.has_significant_change(worst_case_analysis, config):
            logging.info("Significant weather change detected, generating warning")
            
            # Generate warning text using risk-based thresholds
            warning_text = generate_warntext(worst_case_analysis.risk, config)
            
            if warning_text:
                # Save warning text
                output_file = config.get("warning_output_file", "output/inreach_warnung.txt")
                save_warning_text(warning_text, output_file)
                
                # Update state with warning time
                tracker.set_warning_time(datetime.now())
                
                logging.info("Risk-based warning generated and saved")
            else:
                logging.info("Risk below threshold, no warning generated")
        else:
            logging.info("No significant weather changes detected")
        
        # Update state with current analysis
        tracker.update_state(worst_case_analysis)
        
    except Exception as e:
        logging.error(f"Error in warning monitor: {e}")
        raise


if __name__ == "__main__":
    run_warning_monitor() 