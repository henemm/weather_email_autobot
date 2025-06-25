#!/usr/bin/env python3
"""
Demo script for live Météo-France API summary for Conca, Corsica.

This script fetches weather data from multiple Météo-France APIs and provides
a comprehensive summary including current conditions, warnings, and risk analysis.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Set up Python path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
os.environ['PYTHONPATH'] = str(project_root) + os.pathsep + os.environ.get('PYTHONPATH', '')

from src.auth.meteo_token_provider import MeteoTokenProvider
from src.utils.env_loader import get_required_env_var
from src.wetter.fetch_arome_wcs import fetch_weather_for_position
from src.wetter.warning import fetch_warnings
from src.logic.analyse_weather import analyze_weather_data_english, get_default_thresholds


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Conca, Corsica coordinates
CONCA_LATITUDE = 41.7577
CONCA_LONGITUDE = 9.3420


def get_weather_data() -> Dict:
    """
    Fetch weather data from all available sources.
    
    Returns:
        Dict: Dictionary containing all weather data and metadata
    """
    logger.info("Starting weather data collection for Conca, Corsica...")
    
    result = {
        "metadata": {
            "location": "Conca, Corsica",
            "latitude": CONCA_LATITUDE,
            "longitude": CONCA_LONGITUDE,
            "timestamp": datetime.now().isoformat(),
            "data_sources": []
        },
        "weather_data": None,
        "warnings": [],
        "analysis": None,
        "errors": []
    }
    
    # Fetch AROME WCS weather data
    try:
        logger.info("Fetching AROME WCS weather data...")
        weather_data = fetch_weather_for_position(CONCA_LATITUDE, CONCA_LONGITUDE)
        result["weather_data"] = weather_data
        result["metadata"]["data_sources"].append("AROME_WCS")
        logger.info("AROME WCS data fetched successfully")
    except Exception as e:
        error_msg = f"Failed to fetch AROME WCS data: {str(e)}"
        logger.error(error_msg)
        result["errors"].append(error_msg)
    
    # Fetch weather warnings
    try:
        logger.info("Fetching weather warnings...")
        warnings = fetch_warnings(CONCA_LATITUDE, CONCA_LONGITUDE)
        result["warnings"] = warnings
        result["metadata"]["data_sources"].append("VIGILANCE")
        logger.info(f"Fetched {len(warnings)} weather warnings")
    except Exception as e:
        error_msg = f"Failed to fetch weather warnings: {str(e)}"
        logger.error(error_msg)
        result["errors"].append(error_msg)
    
    # Perform weather analysis if we have weather data
    if result["weather_data"]:
        try:
            logger.info("Performing weather analysis...")
            config = {"thresholds": get_default_thresholds()}
            analysis = analyze_weather_data_english(result["weather_data"], config)
            result["analysis"] = analysis
            result["metadata"]["data_sources"].append("RISK_ANALYSIS")
            logger.info("Weather analysis completed")
        except Exception as e:
            error_msg = f"Failed to perform weather analysis: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
    
    return result


def format_warning_level(level: int) -> str:
    """
    Convert warning level number to human-readable string.
    
    Args:
        level: Warning level (1-4)
        
    Returns:
        str: Human-readable warning level
    """
    levels = {
        1: "Green",
        2: "Yellow", 
        3: "Orange",
        4: "Red"
    }
    return levels.get(level, f"Unknown ({level})")


def print_terminal_summary(data: Dict) -> None:
    """
    Print a concise terminal summary of the weather data.
    
    Args:
        data: Weather data dictionary
    """
    print("\n" + "="*60)
    print("🌍 WEATHER SUMMARY FOR CONCA, CORSICA")
    print("="*60)
    
    # Location info
    print(f"📍 Location: {data['metadata']['location']} ({data['metadata']['latitude']}, {data['metadata']['longitude']})")
    print(f"🕐 Timestamp: {data['metadata']['timestamp']}")
    print(f"📡 Data Sources: {', '.join(data['metadata']['data_sources'])}")
    
    # Weather data summary
    if data["weather_data"] and data["weather_data"].points:
        latest_point = data["weather_data"].points[0]  # Most recent point
        print(f"\n🌦️  CURRENT CONDITIONS:")
        print(f"   Temperature: {latest_point.temperature:.1f}°C")
        print(f"   Precipitation: {latest_point.precipitation:.1f}mm")
        print(f"   Wind Speed: {latest_point.wind_speed:.1f}m/s")
        print(f"   Cloud Cover: {latest_point.cloud_cover:.0f}%")
        if latest_point.thunderstorm_probability:
            print(f"   Thunderstorm Probability: {latest_point.thunderstorm_probability:.0f}%")
    
    # Warnings summary
    if data["warnings"]:
        print(f"\n🚨 ACTIVE WARNINGS ({len(data['warnings'])}):")
        for warning in data["warnings"]:
            level_emoji = {"Green": "🟢", "Yellow": "🟡", "Orange": "🟠", "Red": "🔴"}
            emoji = level_emoji.get(format_warning_level(warning.level), "⚪")
            print(f"   {emoji} {warning.type}: {format_warning_level(warning.level)}")
            print(f"      Valid: {warning.start.strftime('%Y-%m-%d %H:%M')} - {warning.end.strftime('%Y-%m-%d %H:%M')}")
    else:
        print(f"\n✅ NO ACTIVE WARNINGS")
    
    # Risk analysis summary
    if data["analysis"]:
        analysis = data["analysis"]
        print(f"\n🧠 RISK ANALYSIS:")
        print(f"   Risk Score: {analysis.risk:.0f}/100")
        print(f"   Max Precipitation: {analysis.max_precipitation:.1f}mm")
        print(f"   Max Wind Speed: {analysis.max_wind_speed:.1f}m/s")
        print(f"   Max Temperature: {analysis.max_temperature:.1f}°C")
        if analysis.max_thunderstorm_probability:
            print(f"   Max Thunderstorm Probability: {analysis.max_thunderstorm_probability:.0f}%")
        
        if analysis.risks:
            print(f"   Active Risks: {len(analysis.risks)}")
            for risk in analysis.risks[:3]:  # Show top 3 risks
                level_emoji = {"low": "🟢", "moderate": "🟡", "high": "🟠", "very_high": "🔴"}
                emoji = level_emoji.get(risk.level.value, "⚪")
                print(f"      {emoji} {risk.risk_type.value}: {risk.level.value} ({risk.value:.1f})")
    
    # Error summary
    if data["errors"]:
        print(f"\n❌ ERRORS ({len(data['errors'])}):")
        for error in data["errors"]:
            print(f"   • {error}")
    
    print(f"\n📄 Detailed data saved to: output/conca_weather_summary.json")
    print("="*60)


def save_json_output(data: Dict) -> None:
    """
    Save weather data to JSON file.
    
    Args:
        data: Weather data dictionary
    """
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "conca_weather_summary.json"
    
    # Convert datetime objects to strings for JSON serialization
    def datetime_converter(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=datetime_converter, ensure_ascii=False)
    
    logger.info(f"Weather data saved to {output_file}")


def main():
    """
    Main function to execute the weather summary demo.
    """
    try:
        # Verify environment variables
        logger.info("Verifying environment variables...")
        get_required_env_var("METEOFRANCE_CLIENT_ID")
        get_required_env_var("METEOFRANCE_CLIENT_SECRET")
        logger.info("Environment variables verified")
        
        # Fetch weather data
        weather_data = get_weather_data()
        
        # Save to JSON file
        save_json_output(weather_data)
        
        # Print terminal summary
        print_terminal_summary(weather_data)
        
        # Exit with error code if there were errors
        if weather_data["errors"]:
            logger.warning(f"Completed with {len(weather_data['errors'])} errors")
            sys.exit(1)
        else:
            logger.info("Weather summary completed successfully")
            
    except RuntimeError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ CONFIGURATION ERROR: {e}")
        print("Please ensure METEOFRANCE_CLIENT_ID and METEOFRANCE_CLIENT_SECRET are set in your .env file")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 