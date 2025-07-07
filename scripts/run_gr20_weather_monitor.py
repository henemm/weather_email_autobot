#!/usr/bin/env python3
"""
GR20 Weather Report Monitor.

This script runs the GR20 weather report system, checking for scheduled
and dynamic report conditions and sending reports via email and SMS.
"""

import sys
import os
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logic.report_scheduler import ReportScheduler, get_nearest_stage_location, should_send_dynamic_report
from notification.email_client import EmailClient
from notification.modular_sms_client import ModularSmsClient
from logic.analyse_weather import analyze_weather_data, compute_risk
from wetter.fetch_meteofrance import get_forecast, get_thunderstorm, get_alerts, ForecastResult, get_tomorrow_forecast
from wetter.fetch_openmeteo import fetch_openmeteo_forecast, fetch_tomorrow_openmeteo_forecast
from wetter.weather_data_processor import process_weather_data_for_report
from position.etappenlogik import get_stage_info, get_stage_coordinates, get_next_stage, get_day_after_tomorrow_stage
from utils.env_loader import get_env_var
from config.config_loader import load_config as load_config_with_env
from model.datatypes import WeatherData, WeatherPoint


def convert_openmeteo_to_weather_data(openmeteo_dict: dict) -> WeatherData:
    """
    Convert OpenMeteo API response dictionary to WeatherData object.
    Uses hourly data for today (05:00-17:00) to get maximum values.
    
    Args:
        openmeteo_dict: Dictionary response from fetch_openmeteo_forecast
        
    Returns:
        WeatherData object with weather points for today
    """
    hourly = openmeteo_dict.get("hourly", {})
    times = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    precipitations = hourly.get("precipitation", [])
    rain_probabilities = hourly.get("precipitation_probability", [])
    wind_speeds = hourly.get("wind_speed_10m", [])
    wind_gusts = hourly.get("wind_gusts_10m", [])
    cloud_covers = hourly.get("cloud_cover", [])
    
    weather_points = []
    today = datetime.now().date()
    
    for i, time_str in enumerate(times):
        try:
            time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            time_date = time_obj.date()
            time_hour = time_obj.hour
            
            # Check if it's today and between 05:00-17:00
            if time_date == today and 5 <= time_hour <= 17:
                # Get values for this time slot
                temp = temperatures[i] if i < len(temperatures) and temperatures[i] is not None else 0.0
                precip = precipitations[i] if i < len(precipitations) and precipitations[i] is not None else 0.0
                rain_prob = rain_probabilities[i] if i < len(rain_probabilities) and rain_probabilities[i] is not None else None
                wind_speed = wind_speeds[i] if i < len(wind_speeds) and wind_speeds[i] is not None else 0.0
                wind_gust = wind_gusts[i] if i < len(wind_gusts) and wind_gusts[i] is not None else None
                cloud_cover = cloud_covers[i] if i < len(cloud_covers) and cloud_covers[i] is not None else 0.0
                
                weather_point = WeatherPoint(
                    latitude=openmeteo_dict.get("location", {}).get("latitude", 0.0),
                    longitude=openmeteo_dict.get("location", {}).get("longitude", 0.0),
                    elevation=0.0,  # OpenMeteo doesn't provide elevation
                    time=time_obj,
                    temperature=temp,
                    feels_like=temp,  # Use temperature as feels_like
                    precipitation=precip,
                    rain_probability=rain_prob,  # NEW: map to rain_probability
                    thunderstorm_probability=None,  # OpenMeteo doesn't provide this
                    wind_speed=wind_speed,
                    wind_gusts=wind_gust,
                    wind_direction=0.0,  # Not critical for our analysis
                    cloud_cover=cloud_cover
                )
                weather_points.append(weather_point)
                
        except (ValueError, IndexError):
            continue
    
    # If no hourly data available, fall back to current data
    if not weather_points:
        current = openmeteo_dict.get("current", {})
        weather_point = WeatherPoint(
            latitude=openmeteo_dict.get("location", {}).get("latitude", 0.0),
            longitude=openmeteo_dict.get("location", {}).get("longitude", 0.0),
            elevation=0.0,
            time=datetime.fromisoformat(current.get("time", datetime.now().isoformat())),
            temperature=current.get("temperature_2m", 0.0),
            feels_like=current.get("apparent_temperature", 0.0),
            precipitation=current.get("precipitation", 0.0),
            rain_probability=None,  # Not available in current
            thunderstorm_probability=None,
            wind_speed=current.get("wind_speed_10m", 0.0),
            wind_gusts=current.get("wind_gusts_10m"),
            wind_direction=current.get("wind_direction_10m", 0.0),
            cloud_cover=current.get("cloud_cover", 0.0)
        )
        weather_points = [weather_point]
    
    return WeatherData(points=weather_points)


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
        precipitation=forecast.precipitation or 0.0,  # Use precipitation from ForecastResult
        rain_probability=forecast.precipitation_probability,  # Use precipitation probability from ForecastResult
        thunderstorm_probability=forecast.thunderstorm_probability,  # Use thunderstorm probability from ForecastResult
        wind_speed=forecast.wind_speed or 0.0,  # Use wind speed from ForecastResult
        wind_gusts=forecast.wind_gusts,  # Use wind gusts from ForecastResult
        cloud_cover=0.0  # Not available in ForecastResult
    )
    return WeatherData(points=[point])


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file with environment variable injection."""
    try:
        return load_config_with_env(config_path)
    except ImportError:
        # Fallback to simple YAML loading if config_loader not available
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Manually inject GMAIL_APP_PW if not present
            if "smtp" in config and "password" not in config["smtp"]:
                gmail_pw = get_env_var("GMAIL_APP_PW")
                if gmail_pw:
                    config["smtp"]["password"] = gmail_pw
            
            return config
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


def get_tomorrow_weather_data(config: dict) -> list:
    """Fetch weather data for all coordinates of tomorrow's stage (05:00-17:00)."""
    weather_data_list = []
    
    try:
        # Get tomorrow's stage
        tomorrow_stage = get_next_stage(config)
        if not tomorrow_stage:
            print("No tomorrow stage available")
            return weather_data_list
        
        print(f"Fetching weather data for tomorrow's stage: {tomorrow_stage['name']}")
        
        # Get all coordinates for tomorrow's stage
        coordinates = get_stage_coordinates(tomorrow_stage)
        
        for i, (latitude, longitude) in enumerate(coordinates):
            print(f"Fetching weather for point {i+1}/{len(coordinates)}: {latitude}, {longitude}")
            
            try:
                # Fetch MeteoFrance tomorrow data
                meteofrance_data_list = get_tomorrow_forecast(latitude, longitude)
                if meteofrance_data_list:
                    for forecast_result in meteofrance_data_list:
                        weather_data = forecast_result_to_weather_data(forecast_result, latitude, longitude)
                        weather_data_list.append(weather_data)
                    print(f"MeteoFrance tomorrow data fetched for point {i+1} ({len(meteofrance_data_list)} entries)")
            except Exception as e:
                print(f"Failed to fetch MeteoFrance tomorrow data for point {i+1}: {e}")
            
            try:
                # Fetch OpenMeteo tomorrow data as fallback
                openmeteo_dict = fetch_tomorrow_openmeteo_forecast(latitude, longitude)
                if openmeteo_dict:
                    openmeteo_data = convert_tomorrow_openmeteo_to_weather_data(openmeteo_dict)
                    weather_data_list.append(openmeteo_data)
                    print(f"OpenMeteo tomorrow data fetched for point {i+1}")
            except Exception as e:
                print(f"Failed to fetch OpenMeteo tomorrow data for point {i+1}: {e}")
        
        print(f"Total tomorrow weather data sources: {len(weather_data_list)}")
        
    except Exception as e:
        print(f"Failed to fetch tomorrow's weather data: {e}")
    
    return weather_data_list


def get_day_after_tomorrow_thunderstorm_data(config: dict) -> list:
    """Fetch only thunderstorm data for all coordinates of day after tomorrow's stage."""
    weather_data_list = []
    
    try:
        # Get day after tomorrow's stage
        day_after_tomorrow_stage = get_day_after_tomorrow_stage(config)
        if not day_after_tomorrow_stage:
            print("No day after tomorrow stage available")
            return weather_data_list
        
        print(f"Fetching thunderstorm data for day after tomorrow's stage: {day_after_tomorrow_stage['name']}")
        
        # Get all coordinates for day after tomorrow's stage
        coordinates = get_stage_coordinates(day_after_tomorrow_stage)
        
        for i, (latitude, longitude) in enumerate(coordinates):
            print(f"Fetching thunderstorm data for point {i+1}/{len(coordinates)}: {latitude}, {longitude}")
            
            try:
                # Fetch MeteoFrance thunderstorm data
                meteofrance_data = get_forecast(latitude, longitude)
                if meteofrance_data:
                    weather_data = forecast_result_to_weather_data(meteofrance_data, latitude, longitude)
                    weather_data_list.append(weather_data)
                    print(f"MeteoFrance thunderstorm data fetched for point {i+1}")
            except Exception as e:
                print(f"Failed to fetch MeteoFrance thunderstorm data for point {i+1}: {e}")
            
            try:
                # Fetch OpenMeteo thunderstorm data as fallback
                openmeteo_dict = fetch_openmeteo_forecast(latitude, longitude)
                if openmeteo_dict:
                    openmeteo_data = convert_openmeteo_to_weather_data(openmeteo_dict)
                    weather_data_list.append(openmeteo_data)
                    print(f"OpenMeteo thunderstorm data fetched for point {i+1}")
            except Exception as e:
                print(f"Failed to fetch OpenMeteo thunderstorm data for point {i+1}: {e}")
        
        print(f"Total thunderstorm data sources for day after tomorrow: {len(weather_data_list)}")
        
    except Exception as e:
        print(f"Failed to fetch day after tomorrow's thunderstorm data: {e}")
    
    return weather_data_list


def convert_tomorrow_openmeteo_to_weather_data(openmeteo_dict: dict) -> WeatherData:
    """
    Convert tomorrow's OpenMeteo API response dictionary to WeatherData object.
    
    Args:
        openmeteo_dict: Dictionary response from fetch_tomorrow_openmeteo_forecast
        
    Returns:
        WeatherData object with tomorrow's weather points (05:00-17:00)
    """
    tomorrow_data = openmeteo_dict.get("tomorrow", {})
    times = tomorrow_data.get("time", [])
    temperatures = tomorrow_data.get("temperature_2m", [])
    precipitations = tomorrow_data.get("precipitation", [])
    wind_speeds = tomorrow_data.get("wind_speed_10m", [])
    wind_gusts = tomorrow_data.get("wind_gusts_10m", [])  # Add wind gusts data
    cloud_covers = tomorrow_data.get("cloud_cover", [])
    
    weather_points = []
    
    for i, time_str in enumerate(times):
        if i < len(temperatures) and temperatures[i] is not None:
            try:
                weather_point = WeatherPoint(
                    latitude=openmeteo_dict.get("location", {}).get("latitude", 0.0),
                    longitude=openmeteo_dict.get("location", {}).get("longitude", 0.0),
                    elevation=0.0,  # OpenMeteo doesn't provide elevation
                    time=datetime.fromisoformat(time_str.replace('Z', '+00:00')),
                    temperature=temperatures[i],
                    feels_like=temperatures[i],  # Use temperature as feels_like
                    precipitation=precipitations[i] if i < len(precipitations) else 0.0,
                    thunderstorm_probability=None,  # OpenMeteo doesn't provide this
                    wind_speed=wind_speeds[i] if i < len(wind_speeds) else 0.0,
                    wind_gusts=wind_gusts[i] if i < len(wind_gusts) else None,  # Add wind gusts
                    wind_direction=0.0,  # Not critical for analysis
                    cloud_cover=cloud_covers[i] if i < len(cloud_covers) else 0.0
                )
                weather_points.append(weather_point)
            except (ValueError, IndexError) as e:
                # Skip invalid entries
                continue
    
    if not weather_points:
        # Create a default point if no valid data
        weather_point = WeatherPoint(
            latitude=openmeteo_dict.get("location", {}).get("latitude", 0.0),
            longitude=openmeteo_dict.get("location", {}).get("longitude", 0.0),
            elevation=0.0,
            time=datetime.now(),
            temperature=0.0,
            feels_like=0.0,
            precipitation=0.0,
            thunderstorm_probability=None,
            wind_speed=0.0,
            wind_gusts=None,  # Add wind gusts
            wind_direction=0.0,
            cloud_cover=0.0
        )
        weather_points = [weather_point]
    
    return WeatherData(points=weather_points)


def main():
    """Main function for GR20 weather monitor."""
    parser = argparse.ArgumentParser(description="GR20 Weather Report Monitor")
    parser.add_argument("--modus", choices=["morning", "evening", "dynamic"], 
                       help="Manual mode selection (overrides automatic scheduling)")
    parser.add_argument("--sms", choices=["test", "production"], 
                       help="Override SMS mode (test/production) from config.yaml")
    args = parser.parse_args()
    
    print("Starting GR20 Weather Report Monitor...")
    
    try:
        # Load configuration
        config = load_config()
        print("Configuration loaded successfully")
        
        # Override SMS mode if specified via command line
        if args.sms and "sms" in config:
            original_mode = config["sms"].get("mode", "test")
            config["sms"]["mode"] = args.sms
            print(f"SMS mode overridden: {original_mode} -> {args.sms}")
        
        # Initialize components
        # Note: State file is hardcoded here, not using config["state_file"]
        # The config entry "state_file" is deprecated and not used in production
        scheduler = ReportScheduler("data/gr20_report_state.json", config)
        email_client = EmailClient(config)
        
        # Initialize SMS client (will be None if SMS is disabled)
        sms_client = None
        try:
            sms_client = ModularSmsClient(config)
            print("SMS client initialized successfully")
            print(f"SMS mode: {config['sms'].get('mode', 'unknown')}")
            print(f"SMS recipient: {sms_client.recipient_number}")
        except Exception as e:
            print(f"SMS client initialization failed: {e}")
            sms_client = None
        
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
            
            # Send email notification
            email_success = email_client.send_gr20_report(report_data)
            if email_success:
                print("Email notification sent: No stages available")
            else:
                print("Failed to send email notification")
            
            # Send SMS notification if available
            if sms_client:
                sms_success = sms_client.send_gr20_report(report_data)
                if sms_success:
                    print("SMS notification sent: No stages available")
                else:
                    print("Failed to send SMS notification")
            
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
                # For manual dynamic mode, bypass constraints for testing
                print("Manual dynamic mode - bypassing constraints for testing")
                report_type = "dynamic"
                should_send = True
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
        
        # For evening reports, also get tomorrow's weather data
        tomorrow_weather_data_list = []
        day_after_tomorrow_thunderstorm_data_list = []
        
        if report_type == "evening":
            print("Getting tomorrow's weather data for evening report...")
            tomorrow_weather_data_list = get_tomorrow_weather_data(config)
            
            print("Getting day after tomorrow's thunderstorm data for evening report...")
            day_after_tomorrow_thunderstorm_data_list = get_day_after_tomorrow_thunderstorm_data(config)
        
        # For evening reports, also analyze tomorrow's weather
        tomorrow_weather_analysis = None
        day_after_tomorrow_thunderstorm_analysis = None
        
        if report_type == "evening":
            if tomorrow_weather_data_list:
                print("Analyzing tomorrow's weather data...")
                tomorrow_weather_analysis = analyze_weather_data(tomorrow_weather_data_list, config)
            
            if day_after_tomorrow_thunderstorm_data_list:
                print("Analyzing day after tomorrow's thunderstorm data...")
                day_after_tomorrow_thunderstorm_analysis = analyze_weather_data(day_after_tomorrow_thunderstorm_data_list, config)
        
        if should_send:
            print(f"Report should be sent (type: {report_type})")
            
            # Generate risk description
            risk_description = generate_risk_description(weather_analysis)
            
            # Prepare report data using the new weather data processor
            if report_type == "evening":
                tomorrow_stage = get_next_stage(config)
                location_name = tomorrow_stage["name"] if tomorrow_stage else location_name
            
            # Use the new weather data processor to get correct report data
            processed_weather_data = process_weather_data_for_report(latitude, longitude, location_name, config, report_type)
            
            # REMOVED: Hardcoded values override - this was causing all evening reports to have identical weather data
            # The weather data should be calculated correctly per stage by process_weather_data_for_report

            # --- NEU: Gewitter +1 (nächster Tag) für Morgenbericht ---
            if report_type == "morning":
                try:
                    # Hole nächste Etappe (morgen)
                    next_stage = get_next_stage(config)
                    if next_stage:
                        coords = get_stage_coordinates(next_stage)
                        next_lat, next_lon = coords[0]
                        # Verwende die gleiche Funktion wie für heute
                        tomorrow_processed_data = process_weather_data_for_report(next_lat, next_lon, next_stage["name"], config)
                        # Übernehme die Gewitterdaten für morgen
                        processed_weather_data["thunderstorm_next_day"] = tomorrow_processed_data.get("max_thunderstorm_probability", 0)
                        processed_weather_data["thunderstorm_next_day_threshold_time"] = tomorrow_processed_data.get("thunderstorm_threshold_time", "")
                    else:
                        processed_weather_data["thunderstorm_next_day"] = 0
                        processed_weather_data["thunderstorm_next_day_threshold_time"] = ""
                except Exception as e:
                    print(f"Fehler beim Berechnen von Gewitter +1: {e}")
                    processed_weather_data["thunderstorm_next_day"] = 0
                    processed_weather_data["thunderstorm_next_day_threshold_time"] = ""
            # --- ENDE NEU ---
            
            # Add vigilance alerts to the processed weather data
            try:
                print("Fetching vigilance alerts...")
                vigilance_alerts = get_alerts(latitude, longitude)
                if vigilance_alerts:
                    # Convert Alert objects to dictionaries for JSON serialization
                    alert_dicts = []
                    for alert in vigilance_alerts:
                        alert_dict = {
                            "phenomenon": alert.phenomenon,
                            "level": alert.level,
                            "description": alert.description
                        }
                        alert_dicts.append(alert_dict)
                    
                    processed_weather_data["vigilance_alerts"] = alert_dicts
                    print(f"Added {len(alert_dicts)} vigilance alerts to report data")
                else:
                    processed_weather_data["vigilance_alerts"] = []
                    print("No vigilance alerts found")
            except Exception as e:
                print(f"Failed to fetch vigilance alerts: {e}")
                processed_weather_data["vigilance_alerts"] = []
            
            report_data = {
                "location": location_name,
                "risk_percentage": int(current_risk * 100),
                "risk_description": risk_description,
                "report_time": current_time,
                "report_type": report_type,
                "weather_analysis": weather_analysis,  # Add weather analysis for dynamic subject
                "weather_data": processed_weather_data
            }
            
            # Add stage names for proper formatting
            if report_type == "morning":
                # Morning report: today's stage
                report_data["stage_names"] = [location_name]
            elif report_type == "evening":
                # Evening report: tomorrow's stage
                tomorrow_stage = get_next_stage(config)
                tomorrow_stage_name = tomorrow_stage["name"] if tomorrow_stage else "Unknown"
                report_data["stage_names"] = [tomorrow_stage_name]
            elif report_type == "dynamic":
                # Dynamic report: today's stage
                report_data["stage_names"] = [location_name]
            
            # Weather data processor already handles all threshold calculations
            # No additional processing needed here
            
            # Add min_temperature for evening reports
            if report_type == "evening":
                # Calculate min temperature from weather data points
                min_temp = float('inf')
                for weather_data in weather_data_list:
                    for point in weather_data.points:
                        if point.temperature is not None:
                            min_temp = min(min_temp, point.temperature)
                
                if min_temp == float('inf'):
                    min_temp = 0  # Fallback if no temperature data
                
                report_data["weather_data"]["min_temperature"] = min_temp
                
                # Add tomorrow's weather data for evening reports
                if tomorrow_weather_analysis:
                    report_data["weather_data"].update({
                        "tomorrow_thunderstorm_probability": tomorrow_weather_analysis.max_thunderstorm_probability or 0,
                        "tomorrow_rain_probability": tomorrow_weather_analysis.max_rain_probability or 0,  # Add tomorrow's rain probability
                        "tomorrow_precipitation": tomorrow_weather_analysis.max_precipitation or 0,
                        "tomorrow_temperature": tomorrow_weather_analysis.max_temperature or 0,
                        "tomorrow_wind_speed": tomorrow_weather_analysis.max_wind_speed or 0,
                        "tomorrow_wind_gusts": tomorrow_weather_analysis.max_wind_gusts,  # Add tomorrow's wind gusts
                    })
                    
                    # Load threshold values from config
                    thunderstorm_threshold = config["thresholds"]["thunderstorm_probability"]
                    rain_probability_threshold = config["thresholds"]["rain_probability"]
                    rain_threshold = config["thresholds"]["rain_amount"]
                    
                    # Add threshold time tracking for tomorrow's weather data
                    tomorrow_thunderstorm_threshold_time = ""
                    tomorrow_thunderstorm_max_time = ""
                    tomorrow_rain_threshold_time = ""
                    tomorrow_rain_max_time = ""
                    
                    for weather_data in tomorrow_weather_data_list:
                        for point in weather_data.points:
                            # Thunderstorm threshold time (first time threshold is exceeded)
                            if (point.thunderstorm_probability and 
                                point.thunderstorm_probability > thunderstorm_threshold and 
                                not tomorrow_thunderstorm_threshold_time):
                                tomorrow_thunderstorm_threshold_time = point.time.strftime("%H")
                            
                            # Thunderstorm maximum time
                            if (point.thunderstorm_probability and 
                                point.thunderstorm_probability == tomorrow_weather_analysis.max_thunderstorm_probability and 
                                not tomorrow_thunderstorm_max_time):
                                tomorrow_thunderstorm_max_time = point.time.strftime("%H")
                            
                            # Rain probability threshold time (first time threshold is exceeded)
                            if (point.rain_probability and 
                                point.rain_probability > rain_probability_threshold and 
                                not tomorrow_rain_threshold_time):
                                tomorrow_rain_threshold_time = point.time.strftime("%H")
                            
                            # Rain amount threshold time (first time threshold is exceeded)
                            if (point.precipitation > rain_threshold and 
                                not tomorrow_rain_threshold_time):
                                tomorrow_rain_threshold_time = point.time.strftime("%H")
                            
                            # Rain maximum time
                            if (point.precipitation == tomorrow_weather_analysis.max_precipitation and 
                                not tomorrow_rain_max_time):
                                tomorrow_rain_max_time = point.time.strftime("%H")
                    
                    # Add tomorrow's threshold times to report data
                    report_data["weather_data"].update({
                        "tomorrow_thunderstorm_threshold_time": tomorrow_thunderstorm_threshold_time,
                        "tomorrow_thunderstorm_threshold_pct": tomorrow_weather_analysis.max_thunderstorm_probability or 0,  # Add tomorrow's threshold percentage
                        "tomorrow_thunderstorm_max_time": tomorrow_thunderstorm_max_time,
                        "tomorrow_rain_threshold_time": tomorrow_rain_threshold_time,
                        "tomorrow_rain_threshold_pct": tomorrow_weather_analysis.max_rain_probability or 0,  # Add tomorrow's rain probability threshold percentage
                        "tomorrow_rain_max_time": tomorrow_rain_max_time,  # Add tomorrow's rain probability maximum time
                        "tomorrow_rain_total_time": tomorrow_rain_max_time,  # Add tomorrow's rain amount maximum time
                    })
                    
                    # Add tomorrow's stage name for evening reports
                    tomorrow_stage = get_next_stage(config)
                    if tomorrow_stage:
                        report_data["tomorrow_location"] = tomorrow_stage["name"]
                
                # Add day after tomorrow's thunderstorm data for evening reports
                if day_after_tomorrow_thunderstorm_analysis:
                    report_data["weather_data"]["day_after_tomorrow_thunderstorm_probability"] = day_after_tomorrow_thunderstorm_analysis.max_thunderstorm_probability or 0
            
            # Send email report
            print("Sending email weather report...")
            email_success = email_client.send_gr20_report(report_data)
            
            if email_success:
                print("Email weather report sent successfully")
            else:
                print("Failed to send email weather report")
            
            # Send SMS report if available
            sms_success = False
            if sms_client:
                print("Sending SMS weather report...")
                sms_success = sms_client.send_gr20_report(report_data)
                
                if sms_success:
                    print("SMS weather report sent successfully")
                else:
                    print("Failed to send SMS weather report")
            else:
                print("SMS client not available, skipping SMS report")
            
            # Update scheduler state if either email or SMS was sent successfully
            if email_success or sms_success:
                is_dynamic = (report_type == "dynamic")
                scheduler.update_state_after_report(current_time, current_risk, is_dynamic)
                print("Scheduler state updated")
            else:
                print("No reports sent successfully, scheduler state not updated")
            
    except Exception as e:
        print(f"Error in GR20 weather monitor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 