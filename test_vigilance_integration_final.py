#!/usr/bin/env python3
"""
Test script to verify vigilance alert integration in report generation.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from wetter.fetch_meteofrance import get_alerts
from notification.email_client import generate_gr20_report_text, _format_vigilance_warning

def test_vigilance_integration():
    """Test vigilance alert integration."""
    print("Testing vigilance alert integration...")
    
    # Test coordinates for Conca (last stage)
    latitude = 41.85538  # Conca coordinates
    longitude = 9.166
    
    # Fetch vigilance alerts
    print(f"Fetching vigilance alerts for coordinates: {latitude}, {longitude}")
    try:
        alerts = get_alerts(latitude, longitude)
        print(f"Retrieved {len(alerts)} vigilance alerts")
        
        for i, alert in enumerate(alerts):
            print(f"  Alert {i+1}: {alert.phenomenon} - {alert.level} - {alert.description}")
        
        # Test formatting
        if alerts:
            formatted_warning = _format_vigilance_warning([
                {
                    "phenomenon": alert.phenomenon,
                    "level": alert.level,
                    "description": alert.description
                }
                for alert in alerts
            ])
            print(f"Formatted warning: '{formatted_warning}'")
            
            # Test report generation
            report_data = {
                "location": "Conca",
                "report_type": "morning",
                "weather_data": {
                    "vigilance_alerts": [
                        {
                            "phenomenon": alert.phenomenon,
                            "level": alert.level,
                            "description": alert.description
                        }
                        for alert in alerts
                    ],
                    "max_temperature": 28.5,
                    "max_precipitation": 2.1,
                    "max_rain_probability": 45.0,
                    "max_thunderstorm_probability": 30.0,
                    "wind_speed": 15.0,
                    "max_wind_speed": 25.0,
                    "thunderstorm_threshold_pct": 0,
                    "thunderstorm_threshold_time": "",
                    "thunderstorm_max_time": "15",
                    "rain_threshold_pct": 45,
                    "rain_threshold_time": "14",
                    "rain_max_time": "15",
                    "rain_total_time": "15",
                    "thunderstorm_next_day": 0,
                    "thunderstorm_next_day_threshold_time": ""
                }
            }
            
            config = {"thresholds": {"rain_probability": 25.0, "thunderstorm_probability": 20.0}}
            
            report_text = generate_gr20_report_text(report_data, config)
            print(f"Generated report text: '{report_text}'")
            print(f"Report length: {len(report_text)} characters")
            
            # Check if vigilance warning is included
            if formatted_warning in report_text:
                print("✅ SUCCESS: Vigilance warning is included in the report!")
            else:
                print("❌ FAILURE: Vigilance warning is NOT included in the report!")
                print(f"Expected to find: '{formatted_warning}'")
                print(f"In report: '{report_text}'")
        else:
            print("No alerts found to test formatting")
            
    except Exception as e:
        print(f"Error testing vigilance integration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vigilance_integration() 