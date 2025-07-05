#!/usr/bin/env python3
"""
Debug script to test if vigilance warnings are included in the report for the last stage.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up environment
os.environ['PYTHONPATH'] = project_root

from src.position.etappenlogik import get_current_stage_info
from src.wetter.fetch_meteofrance import get_alerts_with_fallback
from src.wetter.weather_data_processor import process_weather_data
from src.notification.email_client import generate_gr20_report_text, _format_vigilance_warning


def test_vigilance_in_report():
    """Test if vigilance warnings are included in the report for the last stage."""
    print("=== Testing Vigilance Warnings in Report ===")
    print(f"Test time: {datetime.now()}")
    print()
    
    # Get current stage info
    try:
        stage_info = get_current_stage_info()
        print(f"Current stage: {stage_info['name']}")
        print(f"Stage coordinates: {stage_info['coordinates']}")
        print()
    except Exception as e:
        print(f"Error getting stage info: {e}")
        return
    
    # Fetch vigilance alerts for the stage
    try:
        lat, lon = stage_info['coordinates']
        print(f"Fetching vigilance alerts for coordinates: {lat}, {lon}")
        
        alerts = get_alerts_with_fallback(lat, lon)
        print(f"Found {len(alerts)} vigilance alerts:")
        
        for i, alert in enumerate(alerts, 1):
            print(f"  {i}. {alert.phenomenon} - Level: {alert.level}")
            print(f"     Description: {alert.description}")
        
        print()
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        alerts = []
    
    # Test vigilance warning formatting
    print("=== Testing Vigilance Warning Formatting ===")
    
    # Convert alerts to the format expected by the report generator
    vigilance_alerts = []
    for alert in alerts:
        vigilance_alerts.append({
            "phenomenon": alert.phenomenon,
            "level": alert.level,
            "description": alert.description
        })
    
    # Test the formatting function
    formatted_warning = _format_vigilance_warning(vigilance_alerts)
    print(f"Formatted vigilance warning: '{formatted_warning}'")
    print()
    
    # Test with sample weather data
    print("=== Testing Report Generation with Vigilance ===")
    
    # Sample weather data (similar to what we've seen in previous tests)
    weather_data = {
        "max_thunderstorm_probability": 45.0,
        "thunderstorm_threshold_time": "14:00",
        "thunderstorm_threshold_pct": 30.0,
        "thunderstorm_next_day": 25.0,
        "max_precipitation_probability": 60.0,
        "rain_threshold_time": "15:30",
        "rain_threshold_pct": 50.0,
        "max_precipitation": 12.5,
        "max_temperature": 28.5,
        "max_wind_speed": 35.0,
        "vigilance_alerts": vigilance_alerts  # Include the real alerts
    }
    
    # Test morning report
    report_data = {
        "location": stage_info['name'],
        "report_type": "morning",
        "weather_data": weather_data
    }
    
    config = {"max_characters": 160}
    
    try:
        morning_report = generate_gr20_report_text(report_data, config)
        print(f"Morning report: {morning_report}")
        print(f"Length: {len(morning_report)} characters")
        print(f"Contains vigilance: {'ORANGE' in morning_report or 'YELLOW' in morning_report or 'RED' in morning_report}")
        print()
    except Exception as e:
        print(f"Error generating morning report: {e}")
    
    # Test evening report
    report_data["report_type"] = "evening"
    weather_data["tomorrow_stage"] = "NextStage"
    weather_data["day_after_stage"] = "AfterNextStage"
    weather_data["min_temperature"] = 15.2
    
    try:
        evening_report = generate_gr20_report_text(report_data, config)
        print(f"Evening report: {evening_report}")
        print(f"Length: {len(evening_report)} characters")
        print(f"Contains vigilance: {'ORANGE' in evening_report or 'YELLOW' in evening_report or 'RED' in evening_report}")
        print()
    except Exception as e:
        print(f"Error generating evening report: {e}")
    
    # Test with no vigilance alerts
    print("=== Testing Report Generation without Vigilance ===")
    
    weather_data_no_alerts = weather_data.copy()
    weather_data_no_alerts["vigilance_alerts"] = []
    
    report_data_no_alerts = {
        "location": stage_info['name'],
        "report_type": "morning",
        "weather_data": weather_data_no_alerts
    }
    
    try:
        no_alerts_report = generate_gr20_report_text(report_data_no_alerts, config)
        print(f"Report without alerts: {no_alerts_report}")
        print(f"Length: {len(no_alerts_report)} characters")
        print(f"Contains vigilance: {'ORANGE' in no_alerts_report or 'YELLOW' in no_alerts_report or 'RED' in no_alerts_report}")
        print()
    except Exception as e:
        print(f"Error generating report without alerts: {e}")


if __name__ == "__main__":
    test_vigilance_in_report() 