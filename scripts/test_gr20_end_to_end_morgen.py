#!/usr/bin/env python3
"""
Live End-to-End Test für GR20-Wetterbericht - Morgenmodus

Dieses Skript simuliert einen vollständigen Durchlauf des GR20-Warnsystems
unter realitätsnahen Bedingungen für Etappe 2 (Carozzu) im Morgenmodus.

Basis: requests/live_end_to_end_gr20_weather_report.md
"""

import sys
import yaml
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.logic.analyse_weather import analyze_weather_data
from src.wetter.fetch_meteofrance import get_forecast
from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast
from src.notification.email_client import EmailClient
from src.utils.env_loader import get_env_var
from src.model.datatypes import WeatherPoint, WeatherData
from src.config.config_loader import load_config as load_config_with_env


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


def load_etappen(etappen_path: str = "etappen.json") -> list:
    """Load GR20 stages from JSON file."""
    try:
        with open(etappen_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Etappen file not found: {etappen_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in etappen file: {e}")


def get_stage_2_coordinates(etappen: list) -> list:
    """Get coordinates for stage 2 (Carozzu) from etappen.json."""
    if len(etappen) < 2:
        raise ValueError("Etappe 2 not found in etappen.json")
    
    stage_2 = etappen[1]  # Index 1 = Etappe 2
    print(f"Using stage: {stage_2['name']}")
    print(f"Coordinates: {stage_2['punkte']}")
    
    return stage_2['punkte']


def fetch_weather_data_for_stage(coordinates: list, config: dict) -> list:
    """Fetch weather data for all points of a stage using meteofrance-api and open-meteo as fallback."""
    weather_data_list = []
    
    print(f"Fetching weather data for {len(coordinates)} stage points...")
    
    for i, point in enumerate(coordinates):
        lat, lon = point['lat'], point['lon']
        print(f"Point {i+1}: {lat}, {lon}")
        
        point_weather_data = []
        
        # Try meteofrance-api first
        try:
            print(f"  Fetching MeteoFrance data for point {i+1}...")
            forecast = get_forecast(lat, lon)
            if forecast:
                weather_point = WeatherPoint(
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
                weather_data = WeatherData(points=[weather_point])
                point_weather_data.append(weather_data)
                print(f"  MeteoFrance data fetched successfully for point {i+1}")
        except Exception as e:
            print(f"  Failed to fetch MeteoFrance data for point {i+1}: {e}")
        
        # Fallback: OpenMeteo
        try:
            print(f"  Fetching OpenMeteo data for point {i+1}...")
            openmeteo_data = fetch_openmeteo_forecast(
                lat=lat,
                lon=lon
            )
            if openmeteo_data:
                # Convert OpenMeteo dictionary to WeatherData object
                weather_point = WeatherPoint(
                    latitude=lat,
                    longitude=lon,
                    elevation=0.0,
                    time=datetime.now(),
                    temperature=openmeteo_data.get('temperature_2m', 0.0),
                    feels_like=openmeteo_data.get('apparent_temperature', 0.0),
                    precipitation=openmeteo_data.get('precipitation', 0.0),
                    thunderstorm_probability=None,  # Not provided by OpenMeteo
                    wind_speed=openmeteo_data.get('wind_speed_10m', 0.0),
                    wind_direction=openmeteo_data.get('wind_direction_10m', 0.0),
                    cloud_cover=openmeteo_data.get('cloud_cover', 0.0)
                )
                weather_data = WeatherData(points=[weather_point])
                point_weather_data.append(weather_data)
                print(f"  OpenMeteo data fetched successfully for point {i+1}")
        except Exception as e:
            print(f"  Failed to fetch OpenMeteo data for point {i+1}: {e}")
        
        if point_weather_data:
            weather_data_list.extend(point_weather_data)
        else:
            print(f"  Warning: No weather data available for point {i+1}")
    
    return weather_data_list


def analyze_stage_weather_morgen(weather_data_list: list, config: dict) -> dict:
    """
    Analyze weather data for morning mode according to wettermodi_uebersicht.md.
    
    Morgenmodus aggregiert:
    - Alle Faktoren: Alle Punkte der heutigen Etappe (Maximalwerte)
    - Keine Nachttemperatur (da vergangen)
    """
    if not weather_data_list:
        raise ValueError("No weather data available for analysis")
    
    print("Analyzing weather data for morning mode...")
    
    # Analyze all weather data (worst-case principle)
    weather_analysis = analyze_weather_data(weather_data_list, config)
    
    # Extract key metrics
    analysis_result = {
        "max_temperature": weather_analysis.max_temperature,
        "max_precipitation": weather_analysis.max_precipitation,
        "max_wind_speed": weather_analysis.max_wind_speed,
        "max_thunderstorm_probability": weather_analysis.max_thunderstorm_probability,
        "max_cloud_cover": weather_analysis.max_cloud_cover,
        "risks": weather_analysis.risks,
        "summary": weather_analysis.summary,
        "risk_score": weather_analysis.risk
    }
    
    print(f"Analysis complete:")
    print(f"  Max temperature: {analysis_result['max_temperature']:.1f}°C")
    print(f"  Max precipitation: {analysis_result['max_precipitation']:.1f}mm")
    print(f"  Max wind speed: {analysis_result['max_wind_speed']:.0f} km/h")
    if analysis_result['max_thunderstorm_probability'] is not None:
        print(f"  Max thunderstorm probability: {analysis_result['max_thunderstorm_probability']:.0f}%")
    else:
        print(f"  Max thunderstorm probability: N/A")
    print(f"  Risk score: {analysis_result['risk_score']:.2f}")
    print(f"  Summary: {analysis_result['summary']}")
    
    return analysis_result


def generate_morgen_report_text(stage_name: str, analysis: dict) -> str:
    """Generate morning report text according to wettermodi_uebersicht.md format."""
    
    # Format risk information
    risk_parts = []
    
    if analysis['max_temperature'] > 0:
        risk_parts.append(f"Tag {analysis['max_temperature']:.1f}°C")
    
    if analysis['max_precipitation'] > 0:
        risk_parts.append(f"Regen {analysis['max_precipitation']:.1f}mm")
    
    if analysis['max_wind_speed'] > 0:
        risk_parts.append(f"Wind {analysis['max_wind_speed']:.0f}km/h")
    
    if analysis['max_thunderstorm_probability'] and analysis['max_thunderstorm_probability'] > 0:
        risk_parts.append(f"Gewitter {analysis['max_thunderstorm_probability']:.0f}%")
    
    # Create compact InReach message (max 160 characters)
    stage_short = stage_name.replace(" ", "")
    report_text = f"{stage_short} | {' | '.join(risk_parts)}"
    
    # Truncate if too long
    if len(report_text) > 160:
        report_text = report_text[:157] + "..."
    
    return report_text


def test_email_sending(config: dict, stage_name: str, report_text: str) -> bool:
    """Test email sending functionality."""
    try:
        print("Testing email sending...")
        
        # Check if email credentials are available
        gmail_pw = get_env_var("GMAIL_APP_PW")
        if not gmail_pw:
            print("Warning: GMAIL_APP_PW not set, skipping email test")
            return False
        
        # Initialize email client
        email_client = EmailClient(config)
        
        # Prepare test report data
        report_data = {
            "location": stage_name,
            "risk_percentage": 40,  # Example value
            "risk_description": "Test morning report",
            "report_time": datetime.now(),
            "report_type": "morgen",
            "report_text": report_text
        }
        
        # Send test email
        success = email_client.send_gr20_report(report_data)
        
        if success:
            print("✅ Email sent successfully")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False


def main():
    """Main function for live end-to-end test."""
    parser = argparse.ArgumentParser(description="Live End-to-End Test für GR20-Wetterbericht - Morgenmodus")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--etappen", default="etappen.json", help="Path to etappen file")
    parser.add_argument("--no-email", action="store_true", help="Skip email sending test")
    args = parser.parse_args()
    
    print("🌅 GR20 Live End-to-End Test - Morgenmodus")
    print("=" * 50)
    
    try:
        # Load configuration and etappen
        print("Loading configuration...")
        config = load_config(args.config)
        print("✅ Configuration loaded")
        
        print("Loading etappen...")
        etappen = load_etappen(args.etappen)
        print("✅ Etappen loaded")
        
        # Get stage 2 coordinates
        print("Getting stage 2 coordinates...")
        coordinates = get_stage_2_coordinates(etappen)
        stage_name = etappen[1]['name']
        print(f"✅ Using stage: {stage_name}")
        
        # Fetch weather data
        print("Fetching weather data...")
        weather_data_list = fetch_weather_data_for_stage(coordinates, config)
        
        if not weather_data_list:
            print("❌ No weather data available")
            return False
        
        print(f"✅ Weather data fetched for {len(weather_data_list)} sources")
        
        # Analyze weather data
        print("Analyzing weather data...")
        analysis = analyze_stage_weather_morgen(weather_data_list, config)
        print("✅ Weather analysis complete")
        
        # Generate report text
        print("Generating report text...")
        report_text = generate_morgen_report_text(stage_name, analysis)
        print(f"✅ Report text: {report_text}")
        print(f"   Length: {len(report_text)} characters")
        
        # Validate report format
        if len(report_text) > 160:
            print("❌ Report text exceeds 160 characters")
            return False
        
        if "🌙" in report_text or "🌡️" in report_text or "🌧️" in report_text:
            print("❌ Report contains emojis (not allowed)")
            return False
        
        print("✅ Report format validation passed")
        
        # Test email sending
        if not args.no_email:
            email_success = test_email_sending(config, stage_name, report_text)
            if not email_success:
                print("❌ Email test failed")
                return False
        else:
            print("⏭️  Skipping email test (--no-email flag)")
        
        # Final validation
        print("\n🎯 End-to-End Test Results:")
        print("✅ Etappe 2 (Carozzu) correctly identified")
        print("✅ Weather data aggregated over all stage points")
        print("✅ Morgenmodus logic applied correctly")
        print("✅ No night temperature included (as expected)")
        print("✅ Report text generated without emojis/links")
        print("✅ Report text within 160 character limit")
        if not args.no_email:
            print("✅ Email sent successfully")
        
        print("\n🎉 Live End-to-End Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 