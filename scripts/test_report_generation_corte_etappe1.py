#!/usr/bin/env python3
"""
Live-Test: Morgen- und Abendbericht mit echten Daten

This script validates the output formats for morning and evening reports
using real weather data for fixed positions (Corte) and the first stage
from etappen.json.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from wetter.fetch_meteofrance import get_forecast, get_thunderstorm, get_alerts
from wetter.fetch_openmeteo import fetch_openmeteo_forecast
from notification.email_client import generate_gr20_report_text
from config.config_loader import load_config
from utils.logging_setup import setup_logging, get_logger


# Test positions
CORTE_LAT = 42.3035
CORTE_LON = 9.1440
LUCCIANA_LAT = 42.5453
LUCCIANA_LON = 9.4189

# Output directory
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_etappen_data() -> List[Dict[str, Any]]:
    """Load etappen data from JSON file."""
    try:
        with open("etappen.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("etappen.json not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in etappen.json: {e}")


def get_first_stage_position() -> tuple:
    """Get the first stage position from etappen.json."""
    etappen = load_etappen_data()
    if not etappen:
        raise ValueError("No stages found in etappen.json")
    
    first_stage = etappen[0]
    stage_name = first_stage["name"]
    points = first_stage["punkte"]
    
    if not points:
        raise ValueError("No points found in first stage")
    
    # Use the first point of the stage
    first_point = points[0]
    return stage_name, first_point["lat"], first_point["lon"]


def fetch_weather_data_for_position(lat: float, lon: float, location_name: str) -> Dict[str, Any]:
    """
    Fetch weather data for a specific position using meteofrance-api and open-meteo fallback.
    
    Args:
        lat: Latitude
        lon: Longitude
        location_name: Name of the location
        
    Returns:
        Dictionary containing weather data
    """
    logger = get_logger(__name__)
    logger.info(f"Fetching weather data for {location_name} ({lat}, {lon})")
    
    weather_data = {
        "location": location_name,
        "forecast": None,
        "thunderstorm": None,
        "alerts": [],
        "openmeteo_data": None,
        "data_source": "unknown"
    }
    
    # Try meteofrance-api first
    try:
        logger.info("Trying meteofrance-api...")
        forecast = get_forecast(lat, lon)
        thunderstorm = get_thunderstorm(lat, lon)
        alerts = get_alerts(lat, lon)
        
        if forecast:
            weather_data["forecast"] = forecast
            weather_data["data_source"] = "meteofrance-api"
            logger.info("Successfully fetched data from meteofrance-api")
        
        if thunderstorm:
            weather_data["thunderstorm"] = thunderstorm
            logger.info(f"Thunderstorm data: {thunderstorm}")
        
        if alerts:
            weather_data["alerts"] = alerts
            logger.info(f"Found {len(alerts)} weather alerts")
            
    except Exception as e:
        logger.warning(f"meteofrance-api failed: {e}")
    
    # Fallback to open-meteo if meteofrance-api failed
    if not weather_data["forecast"]:
        try:
            logger.info("Falling back to open-meteo...")
            openmeteo_data = fetch_openmeteo_forecast(lat, lon)
            if openmeteo_data:
                weather_data["openmeteo_data"] = openmeteo_data
                weather_data["data_source"] = "open-meteo"
                logger.info("Successfully fetched data from open-meteo")
        except Exception as e:
            logger.error(f"open-meteo fallback also failed: {e}")
    
    return weather_data


def prepare_weather_data_for_report(weather_data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
    """
    Prepare weather data for report generation.
    
    Args:
        weather_data: Raw weather data from API
        report_type: "morning" or "evening"
        
    Returns:
        Processed weather data for report generation
    """
    logger = get_logger(__name__)
    
    # Initialize report data structure
    report_data = {
        "location": weather_data["location"],
        "report_type": report_type,
        "weather_data": {},
        "report_time": datetime.now()
    }
    
    # Define time periods for different report types
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    if report_type == "morning":
        # Morning report: Today 05:00-17:00
        start_time = datetime.combine(today, datetime.min.time().replace(hour=5))
        end_time = datetime.combine(today, datetime.min.time().replace(hour=17))
        logger.info(f"Morning report time period: {start_time} to {end_time}")
    else:  # evening
        # Evening report: Tomorrow 05:00-17:00
        start_time = datetime.combine(tomorrow, datetime.min.time().replace(hour=5))
        end_time = datetime.combine(tomorrow, datetime.min.time().replace(hour=17))
        logger.info(f"Evening report time period: {start_time} to {end_time}")
    
    # Process meteofrance-api data
    if weather_data["forecast"]:
        forecast = weather_data["forecast"]
        
        # Extract daily forecast data for the target day
        if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
            target_day = 0 if report_type == "morning" else 1  # Today or tomorrow
            if len(forecast.daily_forecast) > target_day:
                daily = forecast.daily_forecast[target_day]
                
                report_data["weather_data"].update({
                    "max_temperature": daily.max_temperature if hasattr(daily, 'max_temperature') else 0.0,
                    "min_temperature": daily.min_temperature if hasattr(daily, 'min_temperature') else 0.0,
                    "max_precipitation": daily.precipitation if hasattr(daily, 'precipitation') else 0.0,
                    "max_precipitation_probability": daily.precipitation_probability if hasattr(daily, 'precipitation_probability') else 0.0,
                    "max_wind_speed": daily.wind_speed if hasattr(daily, 'wind_speed') else 0.0,
                })
        
        # Extract hourly forecast data for the specific time period
        if hasattr(forecast, 'forecast') and forecast.forecast:
            hourly_data = forecast.forecast
            
            # Filter data for the target time period
            period_data = []
            for hour_data in hourly_data:
                if hasattr(hour_data, 'date') and hour_data.date:
                    if start_time <= hour_data.date <= end_time:
                        period_data.append(hour_data)
            
            logger.info(f"Found {len(period_data)} hourly data points for {report_type} report period")
            
            # Find maximum values and threshold times within the period
            max_thunderstorm = 0.0
            max_rain = 0.0
            max_temp = 0.0
            max_wind = 0.0
            thunderstorm_threshold_time = ""
            rain_threshold_time = ""
            
            for hour_data in period_data:
                # Temperature
                if hasattr(hour_data, 'temperature') and hour_data.temperature:
                    if hour_data.temperature > max_temp:
                        max_temp = hour_data.temperature
                
                # Wind speed
                if hasattr(hour_data, 'wind_speed') and hour_data.wind_speed:
                    if hour_data.wind_speed > max_wind:
                        max_wind = hour_data.wind_speed
                
                # Thunderstorm probability
                if hasattr(hour_data, 'thunderstorm_probability') and hour_data.thunderstorm_probability:
                    if hour_data.thunderstorm_probability > max_thunderstorm:
                        max_thunderstorm = hour_data.thunderstorm_probability
                    if hour_data.thunderstorm_probability >= 20.0 and not thunderstorm_threshold_time:
                        thunderstorm_threshold_time = hour_data.date.strftime("%H:%M")
                
                # Rain probability
                if hasattr(hour_data, 'precipitation_probability') and hour_data.precipitation_probability:
                    if hour_data.precipitation_probability > max_rain:
                        max_rain = hour_data.precipitation_probability
                    if hour_data.precipitation_probability >= 25.0 and not rain_threshold_time:
                        rain_threshold_time = hour_data.date.strftime("%H:%M")
            
            # Update with period-specific data
            report_data["weather_data"].update({
                "max_temperature": max_temp if max_temp > 0 else report_data["weather_data"].get("max_temperature", 0.0),
                "max_wind_speed": max_wind if max_wind > 0 else report_data["weather_data"].get("max_wind_speed", 0.0),
                "max_thunderstorm_probability": max_thunderstorm,
                "thunderstorm_threshold_time": thunderstorm_threshold_time,
                "thunderstorm_threshold_pct": 20.0 if thunderstorm_threshold_time else 0.0,
                "max_precipitation_probability": max_rain,
                "rain_threshold_time": rain_threshold_time,
                "rain_threshold_pct": 25.0 if rain_threshold_time else 0.0,
            })
    
    # Process open-meteo fallback data with time period filtering
    elif weather_data["openmeteo_data"]:
        openmeteo = weather_data["openmeteo_data"]
        
        # Extract hourly data for the target period
        hourly = openmeteo.get("hourly", {})
        if hourly:
            # Find indices for the target time period
            times = hourly.get("time", [])
            period_indices = []
            
            for i, time_str in enumerate(times):
                try:
                    time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    if start_time <= time_obj <= end_time:
                        period_indices.append(i)
                except (ValueError, TypeError):
                    continue
            
            logger.info(f"Found {len(period_indices)} hourly data points for {report_type} report period in open-meteo")
            
            if period_indices:
                # Extract data for the period
                temperatures = hourly.get("temperature_2m", [])
                wind_speeds = hourly.get("wind_speed_10m", [])
                precipitations = hourly.get("precipitation", [])
                precipitation_probs = hourly.get("precipitation_probability", [])
                
                # Calculate max values for the period
                period_temps = [temperatures[i] for i in period_indices if i < len(temperatures)]
                period_winds = [wind_speeds[i] for i in period_indices if i < len(wind_speeds)]
                period_precip = [precipitations[i] for i in period_indices if i < len(precipitations)]
                period_precip_probs = [precipitation_probs[i] for i in period_indices if i < len(precipitation_probs)]
                
                max_temp = max(period_temps) if period_temps else 0.0
                max_wind = max(period_winds) if period_winds else 0.0
                max_precip = max(period_precip) if period_precip else 0.0
                max_precip_prob = max(period_precip_probs) if period_precip_probs else 0.0
                
                report_data["weather_data"].update({
                    "max_temperature": max_temp,
                    "max_wind_speed": max_wind,
                    "max_precipitation": max_precip,
                    "max_precipitation_probability": max_precip_prob,
                    "max_thunderstorm_probability": 0.0,  # open-meteo doesn't provide this
                    "thunderstorm_threshold_time": "",
                    "thunderstorm_threshold_pct": 0.0,
                    "rain_threshold_time": "",
                    "rain_threshold_pct": 0.0,
                })
            else:
                # Fallback to current data if no hourly data available
                current = openmeteo.get("current", {})
                if current:
                    report_data["weather_data"].update({
                        "max_temperature": current.get("temperature_2m", 0.0),
                        "max_wind_speed": current.get("wind_speed_10m", 0.0),
                        "max_precipitation": current.get("precipitation", 0.0),
                        "max_precipitation_probability": current.get("precipitation_probability", 0.0),
                        "max_thunderstorm_probability": 0.0,
                        "thunderstorm_threshold_time": "",
                        "thunderstorm_threshold_pct": 0.0,
                        "rain_threshold_time": "",
                        "rain_threshold_pct": 0.0,
                    })
    
    # Add thunderstorm data
    if weather_data["thunderstorm"]:
        report_data["weather_data"]["thunderstorm_next_day"] = 0.0  # Placeholder
    
    # Add vigilance alerts
    if weather_data["alerts"]:
        report_data["weather_data"]["vigilance_alerts"] = weather_data["alerts"]
    else:
        report_data["weather_data"]["vigilance_alerts"] = []
    
    # Add default values for missing data
    defaults = {
        "max_temperature": 0.0,
        "min_temperature": 0.0,
        "max_precipitation": 0.0,
        "max_precipitation_probability": 0.0,
        "max_wind_speed": 0.0,
        "max_thunderstorm_probability": 0.0,
        "thunderstorm_threshold_time": "",
        "thunderstorm_threshold_pct": 0.0,
        "rain_threshold_time": "",
        "rain_threshold_pct": 0.0,
        "thunderstorm_next_day": 0.0,
        "vigilance_alerts": [],
    }
    
    for key, default_value in defaults.items():
        if key not in report_data["weather_data"]:
            report_data["weather_data"][key] = default_value
    
    logger.info(f"Prepared weather data for {report_type} report: {report_data['weather_data']}")
    return report_data


def generate_and_save_report(weather_data: Dict[str, Any], report_type: str, location_name: str) -> str:
    """
    Generate and save a weather report.
    
    Args:
        weather_data: Weather data dictionary
        report_type: "morning" or "evening"
        location_name: Name of the location
        
    Returns:
        Generated report text
    """
    logger = get_logger(__name__)
    
    # Load configuration
    config = load_config()
    
    # Prepare weather data for report
    report_data = prepare_weather_data_for_report(weather_data, report_type)
    
    # Generate report text
    report_text = generate_gr20_report_text(report_data, config)
    
    # Save to file
    filename = f"report_{report_type}_{location_name.lower().replace(' ', '_')}.txt"
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    logger.info(f"Generated {report_type} report for {location_name}:")
    logger.info(f"Text: {report_text}")
    logger.info(f"Length: {len(report_text)} characters")
    logger.info(f"Saved to: {filepath}")
    
    return report_text


def validate_report(report_text: str, report_type: str) -> bool:
    """
    Validate generated report against requirements.
    
    Args:
        report_text: Generated report text
        report_type: "morning" or "evening"
        
    Returns:
        True if report is valid, False otherwise
    """
    logger = get_logger(__name__)
    
    # Check character limit
    if len(report_text) > 160:
        logger.error(f"Report too long: {len(report_text)} characters (max 160)")
        return False
    
    # Check for required components
    required_components = ["Gewitter", "Regen", "Wind"]
    
    if report_type == "morning":
        required_components.append("Gewitter +1")
    elif report_type == "evening":
        required_components.append("Nacht")
    
    missing_components = []
    for component in required_components:
        if component not in report_text:
            missing_components.append(component)
    
    if missing_components:
        logger.error(f"Missing required components: {missing_components}")
        return False
    
    # Check for forbidden content
    forbidden_content = ["http", "www", ".com", ".fr"]
    for content in forbidden_content:
        if content in report_text.lower():
            logger.error(f"Report contains forbidden content: {content}")
            return False
    
    logger.info(f"Report validation passed for {report_type} report")
    return True


def main():
    """Main function for live test."""
    # Setup logging
    setup_logging(log_level="INFO", console_output=True)
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting Live Test: Morgen- und Abendbericht mit echten Daten")
    logger.info(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    try:
        # Get first stage data
        stage_name, stage_lat, stage_lon = get_first_stage_position()
        logger.info(f"📍 First stage: {stage_name} ({stage_lat}, {stage_lon})")
        logger.info(f"📍 Corte position: ({CORTE_LAT}, {CORTE_LON})")
        logger.info(f"📍 Lucciana position: ({LUCCIANA_LAT}, {LUCCIANA_LON})")
        logger.info("")
        
        # Test positions
        test_positions = [
            ("Corte", CORTE_LAT, CORTE_LON),
            (stage_name, stage_lat, stage_lon),
            ("Lucciana", LUCCIANA_LAT, LUCCIANA_LON)
        ]
        
        # Test report types
        report_types = ["morning", "evening"]
        
        results = []
        
        for location_name, lat, lon in test_positions:
            logger.info(f"🌤️ Testing {location_name}...")
            
            # Fetch weather data
            weather_data = fetch_weather_data_for_position(lat, lon, location_name)
            logger.info(f"Data source: {weather_data['data_source']}")
            logger.info("")
            
            for report_type in report_types:
                # Skip morning report for Lucciana (only evening report requested)
                if location_name == "Lucciana" and report_type == "morning":
                    logger.info(f"⏭️ Skipping morning report for {location_name} (evening only)")
                    continue
                
                logger.info(f"📋 Generating {report_type} report for {location_name}...")
                
                try:
                    # Generate and save report
                    report_text = generate_and_save_report(weather_data, report_type, location_name)
                    
                    # Validate report
                    is_valid = validate_report(report_text, report_type)
                    
                    results.append({
                        "location": location_name,
                        "report_type": report_type,
                        "text": report_text,
                        "length": len(report_text),
                        "valid": is_valid,
                        "data_source": weather_data["data_source"]
                    })
                    
                    logger.info(f"✅ {report_type} report for {location_name}: {'VALID' if is_valid else 'INVALID'}")
                    logger.info("")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate {report_type} report for {location_name}: {e}")
                    results.append({
                        "location": location_name,
                        "report_type": report_type,
                        "text": "",
                        "length": 0,
                        "valid": False,
                        "error": str(e)
                    })
        
        # Summary
        logger.info("📊 TEST SUMMARY:")
        logger.info("=" * 60)
        
        valid_reports = [r for r in results if r["valid"]]
        total_reports = len(results)
        
        logger.info(f"Total reports generated: {total_reports}")
        logger.info(f"Valid reports: {len(valid_reports)}")
        logger.info(f"Invalid reports: {total_reports - len(valid_reports)}")
        logger.info("")
        
        for result in results:
            status = "✅ VALID" if result["valid"] else "❌ INVALID"
            logger.info(f"{status} {result['report_type']} report for {result['location']}")
            if result["valid"]:
                logger.info(f"   Length: {result['length']} chars")
                logger.info(f"   Data source: {result['data_source']}")
                logger.info(f"   Text: {result['text']}")
            else:
                if "error" in result:
                    logger.info(f"   Error: {result['error']}")
            logger.info("")
        
        # Check if all required files were created
        expected_files = [
            "output/report_morning_corte.txt",
            "output/report_evening_corte.txt",
            f"output/report_morning_{stage_name.lower().replace(' ', '_')}.txt",
            f"output/report_evening_{stage_name.lower().replace(' ', '_')}.txt",
            "output/report_evening_lucciana.txt"
        ]
        
        logger.info("📁 Checking output files:")
        for filepath in expected_files:
            if Path(filepath).exists():
                logger.info(f"   ✅ {filepath}")
            else:
                logger.info(f"   ❌ {filepath} (missing)")
        
        logger.info("")
        logger.info("🎉 Live test completed!")
        
        return len(valid_reports) == total_reports
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 