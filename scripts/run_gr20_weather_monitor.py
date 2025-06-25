#!/usr/bin/env python3
"""
GR20 Weather Report Monitor.

This script runs the GR20 weather report system, checking for scheduled
and dynamic report conditions and sending reports via email.
"""

import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logic.report_scheduler import ReportScheduler, get_nearest_stage_location, should_send_dynamic_report
from notification.email_client import EmailClient
from logic.analyse_weather import analyze_weather_data, compute_risk
from wetter.fetch_meteofrance import get_forecast, get_thunderstorm, get_alerts, ForecastResult
from wetter.fetch_openmeteo import fetch_openmeteo_forecast
from position.etappenlogik import get_stage_info, get_stage_coordinates
from utils.env_loader import get_env_var
from model.datatypes import WeatherData, WeatherPoint


def convert_openmeteo_to_weather_data(openmeteo_dict: dict) -> WeatherData:
    """
    Convert OpenMeteo API response dictionary to WeatherData object.
    
    Args:
        openmeteo_dict: Dictionary response from fetch_openmeteo_forecast
        
    Returns:
        WeatherData object with current weather point
    """
    current = openmeteo_dict.get("current", {})
    
    # Create weather point from current data
    weather_point = WeatherPoint(
        latitude=openmeteo_dict.get("location", {}).get("latitude", 0.0),
        longitude=openmeteo_dict.get("location", {}).get("longitude", 0.0),
        elevation=0.0,  # OpenMeteo doesn't provide elevation
        time=datetime.fromisoformat(current.get("time", datetime.now().isoformat())),
        temperature=current.get("temperature_2m", 0.0),
        feels_like=current.get("apparent_temperature", 0.0),
        precipitation=current.get("precipitation", 0.0),
        thunderstorm_probability=None,  # OpenMeteo doesn't provide this
        wind_speed=current.get("wind_speed_10m", 0.0),
        wind_direction=current.get("wind_direction_10m", 0.0),
        cloud_cover=current.get("cloud_cover", 0.0)
    )
    
    return WeatherData(points=[weather_point])


def forecast_result_to_weather_data(forecast: ForecastResult, lat: float, lon: float) -> WeatherData:
    """
    Convert a ForecastResult to a WeatherData object with a single WeatherPoint.
    Args:
        forecast: ForecastResult object
        lat: Latitude
        lon: Longitude
    Returns:
        WeatherData object
    """
    point = WeatherPoint(
        latitude=lat,
        longitude=lon,
        elevation=0.0,
        time=datetime.fromisoformat(forecast.timestamp) if forecast.timestamp else datetime.now(),
        temperature=forecast.temperature,
        feels_like=forecast.temperature,  # No separate feels_like in ForecastResult
        precipitation=0.0,  # Not available in ForecastResult
        thunderstorm_probability=forecast.precipitation_probability,
        wind_speed=0.0,  # Not available in ForecastResult
        wind_direction=0.0,  # Not available in ForecastResult
        cloud_cover=0.0  # Not available in ForecastResult
    )
    return WeatherData(points=[point])


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in configuration file: {e}")


def get_current_weather_data(config: dict, latitude: float, longitude: float) -> list:
    """Fetch current weather data from multiple sources."""
    weather_data_list = []
    
    try:
        # Fetch MeteoFrance data
        print("Fetching MeteoFrance weather data...")
        meteofrance_data = get_forecast(latitude, longitude)
        if meteofrance_data:
            weather_data = forecast_result_to_weather_data(meteofrance_data, latitude, longitude)
            weather_data_list.append(weather_data)
            print("MeteoFrance data fetched and converted successfully")
    except Exception as e:
        print(f"Failed to fetch MeteoFrance data: {e}")
    
    try:
        # Fetch OpenMeteo data as fallback
        print("Fetching OpenMeteo weather data...")
        openmeteo_dict = fetch_openmeteo_forecast(
            latitude,
            longitude
        )
        if openmeteo_dict:
            openmeteo_data = convert_openmeteo_to_weather_data(openmeteo_dict)
            weather_data_list.append(openmeteo_data)
            print("OpenMeteo data fetched successfully")
    except Exception as e:
        print(f"Failed to fetch OpenMeteo data: {e}")
    
    return weather_data_list


def get_current_position(config: dict) -> tuple:
    """Get current position from stage logic."""
    try:
        # Get current stage info
        stage_info = get_stage_info(config)
        
        if not stage_info:
            print("No stages available - tour may be completed or not started")
            return None, None
        
        # Use the first point of the stage as current position
        coordinates = stage_info["coordinates"]
        if not coordinates:
            print("No coordinates found in current stage")
            return None, None
        
        latitude, longitude = coordinates[0]
        print(f"Current stage: {stage_info['name']}")
        print(f"Using first point: {latitude}, {longitude}")
        
        return latitude, longitude
        
    except Exception as e:
        print(f"Failed to get current position: {e}")
        return None, None


def generate_risk_description(weather_analysis) -> str:
    """Generate risk description from weather analysis."""
    if not weather_analysis.risks:
        return "Geringes Risiko"
    
    # Find the highest risk
    highest_risk = max(weather_analysis.risks, key=lambda r: r.value)
    
    risk_descriptions = {
        "thunderstorm": "Gewitterwahrscheinlichkeit",
        "heavy_rain": "Starkregen",
        "high_wind": "Starker Wind",
        "heat_wave": "Hitzewelle",
        "overcast": "Bewölkung",
        "regen": "Regenwahrscheinlichkeit",
        "gewitter": "Gewitterwahrscheinlichkeit",
        "wind": "Windgeschwindigkeit",
        "bewoelkung": "Bewölkung",
        "hitze": "Hitzewelle"
    }
    
    return risk_descriptions.get(highest_risk.risk_type.value, "Wetterrisiko")


def main():
    """Main function for GR20 weather monitor."""
    parser = argparse.ArgumentParser(description="GR20 Weather Report Monitor")
    parser.add_argument("--modus", choices=["morning", "evening", "dynamic"], 
                       help="Manual mode selection (overrides automatic scheduling)")
    args = parser.parse_args()
    
    print("Starting GR20 Weather Report Monitor...")
    
    try:
        # Load configuration
        config = load_config()
        print("Configuration loaded successfully")
        
        # Initialize components
        scheduler = ReportScheduler("data/gr20_report_state.json", config)
        email_client = EmailClient(config)
        print("Components initialized successfully")
        
        # Get current position from stage logic
        latitude, longitude = get_current_position(config)
        
        if latitude is None or longitude is None:
            print("No valid position available - cannot generate weather report")
            # Send notification about no stages available
            report_data = {
                "location": "Keine Etappe",
                "risk_percentage": 0,
                "risk_description": "Keine Etappen mehr konfiguriert",
                "report_time": datetime.now(),
                "report_type": "no_stages"
            }
            
            success = email_client.send_gr20_report(report_data)
            if success:
                print("Notification sent: No stages available")
            else:
                print("Failed to send notification")
            return
        
        print(f"Current position: {latitude}, {longitude}")
        
        # Get current stage info for location name
        stage_info = get_stage_info(config)
        location_name = stage_info["name"] if stage_info else "Unbekannt"
        print(f"Current stage: {location_name}")
        
        # Get current weather data
        weather_data_list = get_current_weather_data(config, latitude, longitude)
        
        if not weather_data_list:
            print("No weather data available, skipping report")
            return
        
        # Analyze weather data
        print("Analyzing weather data...")
        weather_analysis = analyze_weather_data(weather_data_list, config)
        
        # Compute risk score
        risk_metrics = {
            "thunderstorm_probability": weather_analysis.max_thunderstorm_probability or 0.0,
            "wind_speed": weather_analysis.max_wind_speed,
            "precipitation": weather_analysis.max_precipitation,
            "temperature": weather_analysis.max_temperature,
            "cape": weather_analysis.max_cape_shear or 0.0
        }
        
        current_risk = compute_risk(risk_metrics, config)
        print(f"Current risk score: {current_risk:.2f}")
        
        current_time = datetime.now()
        
        # Handle manual mode vs automatic mode
        if args.modus:
            print(f"Manual mode: {args.modus}")
            
            if args.modus == "dynamic":
                # For dynamic mode, still check the constraints
                should_send = should_send_dynamic_report(
                    current_risk,
                    scheduler.current_state.last_risk_value,
                    scheduler.current_state.last_dynamic_report,
                    scheduler.current_state.daily_dynamic_report_count,
                    config
                )
                if not should_send:
                    print("Dynamic report constraints not met (time interval or daily limit)")
                    return
                report_type = "dynamic"
            else:
                # For morning/evening, always send
                report_type = args.modus
                should_send = True
        else:
            # Automatic mode - check if report should be sent
            should_send = scheduler.should_send_report(current_time, current_risk)
            if should_send:
                report_type = scheduler.get_report_type(current_time, current_risk)
            else:
                print("No report needed at this time")
                return
        
        if should_send:
            print(f"Report should be sent (type: {report_type})")
            
            # Generate risk description
            risk_description = generate_risk_description(weather_analysis)
            
            # Prepare report data
            report_data = {
                "location": location_name,
                "risk_percentage": int(current_risk * 100),
                "risk_description": risk_description,
                "report_time": current_time,
                "report_type": report_type
            }
            
            # Send report
            print("Sending weather report...")
            success = email_client.send_gr20_report(report_data)
            
            if success:
                print("Weather report sent successfully")
                # Update scheduler state
                is_dynamic = (report_type == "dynamic")
                scheduler.update_state_after_report(current_time, current_risk, is_dynamic)
                print("Scheduler state updated")
            else:
                print("Failed to send weather report")
            
    except Exception as e:
        print(f"Error in GR20 weather monitor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 