#!/usr/bin/env python3
"""
Dynamic Warning End-to-End Test für GR20-Wetterbericht

Dieses Skript simuliert eine signifikante Wetterverschlechterung und testet
die dynamische Warnlogik des GR20-Warnsystems.

Basis: requests/live_end_to_end_gr20_weather_report.md
"""

import sys
import yaml
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logic.analyse_weather import analyze_weather_data, compute_risk
from src.model.datatypes import WeatherData, WeatherPoint
from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast
from src.notification.email_client import EmailClient
from src.utils.env_loader import get_env_var
from src.state.tracker import WarningStateTracker


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
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
    return stage_2['punkte']


def create_manipulated_weather_data(coordinates: list, base_data: List[WeatherData]) -> List[WeatherData]:
    """
    Create manipulated weather data with high risk values to trigger warnings.
    
    Args:
        coordinates: List of stage coordinates
        base_data: Original weather data from OpenMeteo
        
    Returns:
        List of WeatherData objects with manipulated high-risk values
    """
    manipulated_data = []
    
    print("Creating manipulated weather data with high risk values...")
    
    for i, point in enumerate(coordinates):
        lat, lon = point['lat'], point['lon']
        
        # Create multiple time points to simulate forecast
        time_points = []
        for hour in range(0, 24, 3):  # Every 3 hours for 24 hours
            time = datetime.now() + timedelta(hours=hour)
            
            # Manipulate values to trigger warnings:
            # - High thunderstorm probability (60% - above 20% threshold)
            # - High precipitation (5mm - above 2mm threshold)
            # - High wind speed (50 km/h - above 40km/h threshold)
            # - High temperature (35°C - above 30°C threshold)
            
            weather_point = WeatherPoint(
                latitude=lat,
                longitude=lon,
                elevation=0.0,
                time=time,
                temperature=35.0,  # High temperature
                feels_like=38.0,
                precipitation=5.0,  # High precipitation
                thunderstorm_probability=60.0,  # High thunderstorm probability
                wind_speed=50.0,  # High wind speed
                wind_direction=180.0,
                cloud_cover=95.0,  # High cloud cover
                cape=1500.0,  # High CAPE value
                shear=20.0
            )
            time_points.append(weather_point)
        
        weather_data = WeatherData(points=time_points)
        manipulated_data.append(weather_data)
        print(f"  Point {i+1}: Created {len(time_points)} time points with high risk values")
    
    return manipulated_data


def test_dynamic_warning_logic(weather_data_list: List[WeatherData], config: dict) -> Dict[str, Any]:
    """
    Test the dynamic warning logic with manipulated weather data.
    
    Args:
        weather_data_list: List of WeatherData objects with high risk values
        config: Configuration dictionary
        
    Returns:
        Dictionary with test results
    """
    print("Testing dynamic warning logic...")
    
    # Analyze weather data
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
    
    print(f"Risk analysis results:")
    print(f"  Max thunderstorm probability: {weather_analysis.max_thunderstorm_probability:.1f}%")
    print(f"  Max precipitation: {weather_analysis.max_precipitation:.1f}mm")
    print(f"  Max wind speed: {weather_analysis.max_wind_speed:.1f} km/h")
    print(f"  Max temperature: {weather_analysis.max_temperature:.1f}°C")
    print(f"  Computed risk score: {current_risk:.2f}")
    
    # Check if risk exceeds thresholds
    warn_thresholds = config.get("warn_thresholds", {})
    info_threshold = warn_thresholds.get("info", 0.3)
    warning_threshold = warn_thresholds.get("warning", 0.6)
    critical_threshold = warn_thresholds.get("critical", 0.9)
    
    risk_level = "LOW"
    if current_risk >= critical_threshold:
        risk_level = "CRITICAL"
    elif current_risk >= warning_threshold:
        risk_level = "WARNING"
    elif current_risk >= info_threshold:
        risk_level = "INFO"
    
    print(f"  Risk level: {risk_level}")
    
    return {
        "weather_analysis": weather_analysis,
        "current_risk": current_risk,
        "risk_level": risk_level,
        "risk_metrics": risk_metrics,
        "thresholds": {
            "info": info_threshold,
            "warning": warning_threshold,
            "critical": critical_threshold
        }
    }


def test_state_tracker(weather_analysis, config: dict) -> bool:
    """
    Test the state tracker to see if it detects significant changes.
    
    Args:
        weather_analysis: WeatherAnalysis object
        config: Configuration dictionary
        
    Returns:
        True if significant change detected, False otherwise
    """
    print("Testing state tracker for significant changes...")
    
    # Initialize state tracker
    state_file = config.get("state_file", "data/warning_state.json")
    tracker = WarningStateTracker(state_file)
    
    # Check if significant change is detected
    has_change = tracker.has_significant_change(weather_analysis, config)
    
    if has_change:
        print("✅ Significant weather change detected!")
        
        # Generate warning text
        from src.wetter.warntext_generator import generate_warntext
        warning_text = generate_warntext(weather_analysis.risk, config)
        
        if warning_text:
            print(f"✅ Warning text generated: {warning_text[:100]}...")
            
            # Save warning text
            output_file = config.get("warning_output_file", "output/inreach_warnung.txt")
            try:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(warning_text)
                print(f"✅ Warning saved to {output_file}")
            except Exception as e:
                print(f"❌ Failed to save warning: {e}")
        else:
            print("❌ No warning text generated")
    else:
        print("❌ No significant change detected")
    
    # Update state
    tracker.update_state(weather_analysis)
    
    return has_change


def test_email_sending(config: dict, stage_name: str, analysis_result: dict) -> bool:
    """
    Test email sending with high-risk weather data.
    
    Args:
        config: Configuration dictionary
        stage_name: Name of the stage
        analysis_result: Analysis result dictionary
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        print("Testing email sending with high-risk data...")
        
        # Check if email credentials are available
        gmail_pw = get_env_var("GMAIL_APP_PW")
        if not gmail_pw:
            print("Warning: GMAIL_APP_PW not set, skipping email test")
            return False
        
        # Initialize email client
        email_client = EmailClient(config)
        
        # Prepare high-risk report data
        report_data = {
            "location": stage_name,
            "risk_percentage": int(analysis_result["current_risk"] * 100),
            "risk_description": f"High {analysis_result['risk_level']} risk detected",
            "report_time": datetime.now(),
            "report_type": "dynamic",
            "weather_analysis": analysis_result["weather_analysis"]
        }
        
        # Send test email
        success = email_client.send_gr20_report(report_data)
        
        if success:
            print("✅ High-risk email sent successfully")
            return True
        else:
            print("❌ Failed to send high-risk email")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False


def main():
    """Main function for dynamic warning end-to-end test."""
    print("⚡ GR20 Dynamic Warning End-to-End Test")
    print("=" * 50)
    
    setup_logging()
    
    try:
        # Load configuration and etappen
        print("Loading configuration...")
        config = load_config()
        print("✅ Configuration loaded")
        
        print("Loading etappen...")
        etappen = load_etappen()
        print("✅ Etappen loaded")
        
        # Get stage 2 coordinates
        print("Getting stage 2 coordinates...")
        coordinates = get_stage_2_coordinates(etappen)
        stage_name = etappen[1]['name']
        print(f"✅ Using stage: {stage_name}")
        
        # Create manipulated weather data with high risk values
        print("Creating manipulated weather data...")
        manipulated_weather_data = create_manipulated_weather_data(coordinates, [])
        print(f"✅ Created {len(manipulated_weather_data)} manipulated weather datasets")
        
        # Test dynamic warning logic
        print("Testing dynamic warning logic...")
        analysis_result = test_dynamic_warning_logic(manipulated_weather_data, config)
        print("✅ Dynamic warning logic test complete")
        
        # Test state tracker
        print("Testing state tracker...")
        significant_change = test_state_tracker(analysis_result["weather_analysis"], config)
        print("✅ State tracker test complete")
        
        # Test email sending
        print("Testing email sending...")
        email_sent = test_email_sending(config, stage_name, analysis_result)
        print("✅ Email sending test complete")
        
        # Summary
        print("\n🎯 Dynamic Warning Test Results:")
        print(f"✅ Stage 2 ({stage_name}) correctly identified")
        print(f"✅ High-risk weather data created (Thunderstorm: {analysis_result['risk_metrics']['thunderstorm_probability']:.0f}%, Wind: {analysis_result['risk_metrics']['wind_speed']:.0f} km/h)")
        print(f"✅ Risk score: {analysis_result['current_risk']:.2f} (Level: {analysis_result['risk_level']})")
        print(f"✅ Significant change detected: {significant_change}")
        print(f"✅ Warning file generated: {email_sent}")
        print(f"✅ Email sent: {email_sent}")
        
        if significant_change and email_sent:
            print("\n🎉 Dynamic Warning End-to-End Test PASSED!")
            return True
        else:
            print("\n❌ Dynamic Warning End-to-End Test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    import os
    success = main()
    sys.exit(0 if success else 1) 