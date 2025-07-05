#!/usr/bin/env python3
"""
Test script to generate a morning report for the final GR20 stage "Conca".

This script demonstrates the morning report generation for the last stage
of the GR20 trail using real weather data.
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.wetter.fetch_meteofrance import get_forecast, get_thunderstorm, get_alerts
from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast
from src.wetter.analyse import analysiere_regen_risiko, WetterDaten
from src.logic.analyse_weather import analyze_weather_data
from src.model.datatypes import WeatherData, WeatherPoint
from src.notification.email_client import EmailClient
from src.position.etappenlogik import load_etappen_data, get_stage_coordinates

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> Dict:
    """Load configuration from YAML file."""
    import yaml
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        return {}


def get_conca_stage() -> Dict:
    """Get the final stage (Conca) from etappen.json."""
    etappen = load_etappen_data()
    if not etappen:
        raise ValueError("No stages found in etappen.json")
    
    # Get the last stage (Conca)
    final_stage = etappen[-1]
    logger.info(f"Using final stage: {final_stage['name']}")
    return final_stage


def fetch_weather_for_coordinates(coordinates: List[tuple]) -> List[WeatherData]:
    """Fetch weather data for multiple coordinates."""
    weather_data_list = []
    
    for lat, lon in coordinates:
        try:
            logger.info(f"Fetching weather data for coordinates: {lat}, {lon}")
            
            # Try Météo-France first
            try:
                forecast_result = get_forecast(lat, lon)
                if forecast_result:
                    # Convert to WeatherData format
                    weather_point = WeatherPoint(
                        latitude=lat,
                        longitude=lon,
                        elevation=0.0,  # Default elevation
                        time=datetime.now(),
                        temperature=forecast_result.temperature,
                        feels_like=forecast_result.temperature,
                        precipitation=forecast_result.precipitation or 0.0,
                        wind_speed=forecast_result.wind_speed or 0.0,
                        cloud_cover=50.0,  # Default cloud cover
                        rain_probability=forecast_result.precipitation_probability or 0.0,
                        thunderstorm_probability=forecast_result.thunderstorm_probability or 0.0
                    )
                    
                    weather_data = WeatherData(points=[weather_point])
                    weather_data_list.append(weather_data)
                    logger.info(f"✅ Météo-France data fetched for {lat}, {lon}")
                    continue
                    
            except Exception as e:
                logger.warning(f"Météo-France failed for {lat}, {lon}: {e}")
            
            # Fallback to Open-Meteo
            try:
                openmeteo_data = fetch_openmeteo_forecast(lat, lon)
                if openmeteo_data and "current" in openmeteo_data:
                    # Convert Open-Meteo dict to WeatherData format
                    current = openmeteo_data["current"]
                    weather_point = WeatherPoint(
                        latitude=lat,
                        longitude=lon,
                        elevation=0.0,
                        time=datetime.now(),
                        temperature=current.get("temperature_2m", 0.0),
                        feels_like=current.get("apparent_temperature", 0.0),
                        precipitation=current.get("precipitation", 0.0),
                        wind_speed=current.get("wind_speed_10m", 0.0),
                        cloud_cover=current.get("cloud_cover", 0.0),
                        rain_probability=0.0,  # Not available in current data
                        thunderstorm_probability=0.0  # Not available in current data
                    )
                    
                    weather_data = WeatherData(points=[weather_point])
                    weather_data_list.append(weather_data)
                    logger.info(f"✅ Open-Meteo data fetched for {lat}, {lon}")
                else:
                    logger.warning(f"No Open-Meteo data for {lat}, {lon}")
                    
            except Exception as e:
                logger.error(f"Open-Meteo failed for {lat}, {lon}: {e}")
                
        except Exception as e:
            logger.error(f"Failed to fetch weather data for {lat}, {lon}: {e}")
    
    return weather_data_list


def generate_morning_report_text(stage_name: str, analysis_result) -> str:
    """Generate morning report text based on weather analysis."""
    
    # Extract key values from analysis, defaulting None to 0
    def safe(val):
        return 0 if val is None else val

    max_temp = safe(getattr(analysis_result, "max_temperature", 0))
    max_rain_prob = safe(getattr(analysis_result, "max_rain_probability", 0))
    max_precip = safe(getattr(analysis_result, "max_precipitation", 0))
    max_wind = safe(getattr(analysis_result, "max_wind_speed", 0))
    max_thunderstorm = safe(getattr(analysis_result, "max_thunderstorm_probability", 0))
    
    # Build report text
    report_parts = []
    
    # Stage name
    report_parts.append(f"GR20 {stage_name}")
    
    # Temperature
    if max_temp > 0:
        report_parts.append(f"T: {max_temp:.0f}°C")
    
    # Rain probability
    if max_rain_prob >= 25:
        report_parts.append(f"Regen: {max_rain_prob:.0f}%")
    
    # Rain amount
    if max_precip >= 2.0:
        report_parts.append(f"Niederschlag: {max_precip:.1f}mm")
    
    # Wind
    if max_wind >= 40:
        report_parts.append(f"Wind: {max_wind:.0f}km/h")
    
    # Thunderstorm
    if max_thunderstorm >= 20:
        report_parts.append(f"Gewitter: {max_thunderstorm:.0f}%")
    
    # Join parts
    report_text = " | ".join(report_parts)
    
    # Ensure it fits within 160 characters
    if len(report_text) > 160:
        # Truncate if too long
        report_text = report_text[:157] + "..."
    
    return report_text


def main():
    """Main function to generate morning report for Conca stage."""
    print("🌅 GR20 Morning Report Test - Final Stage (Conca)")
    print("=" * 60)
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        if not config:
            print("❌ Failed to load configuration")
            return False
        print("✅ Configuration loaded")
        
        # Get Conca stage
        print("Getting Conca stage data...")
        stage_data = get_conca_stage()
        stage_name = stage_data["name"]
        coordinates = get_stage_coordinates(stage_data)
        print(f"✅ Stage: {stage_name}")
        print(f"✅ Coordinates: {len(coordinates)} points")
        
        # Fetch weather data for all coordinates
        print("Fetching weather data...")
        weather_data_list = fetch_weather_for_coordinates(coordinates)
        
        if not weather_data_list:
            print("❌ No weather data available")
            return False
        
        print(f"✅ Weather data fetched for {len(weather_data_list)} points")
        
        # Analyze weather data
        print("Analyzing weather data...")
        if weather_data_list:
            # Use the first weather data for analysis (simplified)
            weather_data = weather_data_list[0]
            analysis_result = analyze_weather_data(weather_data, config)
            print("✅ Weather analysis complete")
        else:
            print("❌ No weather data to analyze")
            return False
        
        # Generate report text
        print("Generating morning report...")
        report_text = generate_morning_report_text(stage_name, analysis_result)
        print(f"✅ Morning report generated")
        print(f"📝 Report text: {report_text}")
        print(f"📏 Length: {len(report_text)} characters")

        # VIGILANCE/ALERTS OUTPUT
        print("\n🚨 VIGILANCE/ALERTS for first coordinate:")
        first_lat, first_lon = coordinates[0]
        try:
            alerts = get_alerts(first_lat, first_lon)
            if alerts:
                for alert in alerts:
                    print(f"  - {alert.phenomenon}: {alert.level} ({alert.description if alert.description else ''})")
            else:
                print("  No active alerts.")
        except Exception as e:
            print(f"  Error fetching alerts: {e}")
        
        # Check constraints
        if len(report_text) > 160:
            print("⚠️  Warning: Report exceeds 160 characters")
        
        if 'http' in report_text.lower():
            print("⚠️  Warning: Report contains links")
        
        # Display analysis details
        print("\n📊 Analysis Details:")
        print(f"   Max Temperature: {analysis_result.get('max_temperature', 'N/A')}°C")
        print(f"   Max Rain Probability: {analysis_result.get('max_rain_probability', 'N/A')}%")
        print(f"   Max Precipitation: {analysis_result.get('max_precipitation', 'N/A')}mm")
        print(f"   Max Wind Speed: {analysis_result.get('max_wind_speed', 'N/A')} km/h")
        print(f"   Max Thunderstorm Probability: {analysis_result.get('max_thunderstorm_probability', 'N/A')}%")
        
        # Optional: Send email (commented out for testing)
        # print("\nSending email...")
        # email_client = EmailClient(config)
        # email_success = email_client.send_gr20_report({
        #     "location": stage_name,
        #     "report_text": report_text,
        #     "report_time": datetime.now(),
        #     "report_type": "morning"
        # })
        # if email_success:
        #     print("✅ Email sent successfully")
        # else:
        #     print("❌ Failed to send email")
        
        print("\n🎯 Morning report test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during morning report generation: {e}")
        logger.exception("Morning report generation failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 