#!/usr/bin/env python3
"""
Test script for the new email format implementation.
Tests all three report types with sample data according to the email_format specification.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.notification.email_client import (
    generate_gr20_report_text, 
    _generate_morning_report,
    _generate_evening_report, 
    _generate_dynamic_report,
    _format_vigilance_warning
)

def test_vigilance_warning_formatting():
    """Test vigilance warning formatting with the German translation table."""
    print("=== Testing Vigilance Warning Formatting ===")
    
    test_cases = [
        ([], ""),
        ([{"phenomenon": "thunderstorm", "level": "green"}], ""),  # Green should be ignored
        ([{"phenomenon": "thunderstorm", "level": "yellow"}], "YELLOW Gewitter"),
        ([{"phenomenon": "forest_fire", "level": "orange"}], "ORANGE Waldbrand"),
        ([{"phenomenon": "wind", "level": "red"}], "RED Wind"),
        ([{"phenomenon": "heat", "level": "red"}], "RED Hitze"),
        ([{"phenomenon": "rain", "level": "yellow"}], "YELLOW Regen"),
        ([{"phenomenon": "snow", "level": "orange"}], "ORANGE Schnee"),
        ([{"phenomenon": "flood", "level": "red"}], "RED Hochwasser"),
        ([{"phenomenon": "cold", "level": "yellow"}], "YELLOW Kälte"),
        ([{"phenomenon": "avalanche", "level": "red"}], "RED Lawine"),
        ([{"phenomenon": "unknown", "level": "orange"}], "ORANGE Warnung"),
        # Multiple alerts - should return highest level
        ([
            {"phenomenon": "rain", "level": "yellow"},
            {"phenomenon": "thunderstorm", "level": "orange"},
            {"phenomenon": "heat", "level": "red"}
        ], "RED Hitze"),
    ]
    
    for alerts, expected in test_cases:
        result = _format_vigilance_warning(alerts)
        status = "✅" if result == expected else "❌"
        print(f"{status} {alerts} → '{result}' (expected: '{expected}')")
    
    print()

def test_morning_report():
    """Test morning report generation with sample data."""
    print("=== Testing Morning Report ===")
    
    # Sample data for morning report
    report_data = {
        "location": "Vizzavona",
        "report_type": "morning",
        "weather_data": {
            "thunderstorm_threshold_pct": 30,
            "thunderstorm_threshold_time": "13",
            "max_thunderstorm_probability": 80,
            "thunderstorm_max_time": "15",
            "rain_threshold_pct": 55,
            "rain_threshold_time": "15",
            "max_rain_probability": 70,
            "rain_max_time": "16",
            "max_precipitation": 2.0,
            "rain_total_time": "15",
            "max_temperature": 28.0,
            "wind_speed": 15,
            "max_wind_speed": 25,
            "thunderstorm_next_day": 80,
            "thunderstorm_next_day_threshold_time": "14",
            "vigilance_alerts": [
                {"phenomenon": "thunderstorm", "level": "orange"}
            ]
        }
    }
    
    config = {"smtp": {"subject": "GR20 Wetter"}}
    
    result = _generate_morning_report(report_data, config)
    print(f"Morning Report: {result}")
    print(f"Length: {len(result)} characters")
    print(f"Within limit: {'✅' if len(result) <= 160 else '❌'}")
    print()

def test_evening_report():
    """Test evening report generation with sample data."""
    print("=== Testing Evening Report ===")
    
    # Sample data for evening report
    report_data = {
        "location": "Conca",
        "report_type": "evening",
        "weather_data": {
            "tomorrow_stage": "Vizzavona",
            "day_after_stage": "Corte",
            "min_temperature": 15.5,
            "tomorrow_thunderstorm_threshold_pct": 40,
            "tomorrow_thunderstorm_threshold_time": "14",
            "tomorrow_thunderstorm_probability": 95,
            "tomorrow_thunderstorm_max_time": "17",
            "tomorrow_rain_threshold_pct": 50,
            "tomorrow_rain_threshold_time": "14",
            "tomorrow_rain_probability": 70,
            "tomorrow_rain_max_time": "17",
            "tomorrow_precipitation": 2.0,
            "tomorrow_rain_total_time": "14",
            "tomorrow_temperature": 33.5,
            "tomorrow_wind_speed": 18,
            "tomorrow_wind_gusts": 38,
            "thunderstorm_day_after": 90,
            "thunderstorm_day_after_threshold_time": "15",
            "vigilance_alerts": [
                {"phenomenon": "forest_fire", "level": "red"}
            ]
        }
    }
    
    config = {"smtp": {"subject": "GR20 Wetter"}}
    
    result = _generate_evening_report(report_data, config)
    print(f"Evening Report: {result}")
    print(f"Length: {len(result)} characters")
    print(f"Within limit: {'✅' if len(result) <= 160 else '❌'}")
    print()

def test_update_report():
    """Test update report generation with sample data."""
    print("=== Testing Update Report ===")
    
    # Sample data for update report
    report_data = {
        "location": "Corte",
        "report_type": "dynamic",
        "weather_data": {
            "thunderstorm_threshold_pct": 35,
            "thunderstorm_threshold_time": "15",
            "max_thunderstorm_probability": 85,
            "thunderstorm_max_time": "16",
            "rain_threshold_pct": 55,
            "rain_threshold_time": "16",
            "max_rain_probability": 75,
            "rain_max_time": "17",
            "max_precipitation": 2.0,
            "rain_total_time": "15",
            "max_temperature": 29.1,
            "wind_speed": 12,
            "max_wind_speed": 31,
            "thunderstorm_next_day": 85,
            "thunderstorm_next_day_threshold_time": "14",
            "vigilance_alerts": [
                {"phenomenon": "thunderstorm", "level": "orange"}
            ]
        }
    }
    
    config = {"smtp": {"subject": "GR20 Wetter"}}
    
    result = _generate_dynamic_report(report_data, config)
    print(f"Update Report: {result}")
    print(f"Length: {len(result)} characters")
    print(f"Within limit: {'✅' if len(result) <= 160 else '❌'}")
    print()

def test_null_values():
    """Test handling of null/zero values."""
    print("=== Testing Null Values ===")
    
    # Sample data with null values
    report_data = {
        "location": "TestLocation",
        "report_type": "morning",
        "weather_data": {
            "thunderstorm_threshold_pct": 0,
            "thunderstorm_threshold_time": "",
            "max_thunderstorm_probability": 0,
            "thunderstorm_max_time": "",
            "rain_threshold_pct": 0,
            "rain_threshold_time": "",
            "max_rain_probability": 0,
            "rain_max_time": "",
            "max_precipitation": 0,
            "rain_total_time": "",
            "max_temperature": 0,
            "wind_speed": 0,
            "max_wind_speed": 0,
            "thunderstorm_next_day": 0,
            "thunderstorm_next_day_threshold_time": "",
            "vigilance_alerts": []
        }
    }
    
    config = {"smtp": {"subject": "GR20 Wetter"}}
    
    result = _generate_morning_report(report_data, config)
    print(f"Null Values Report: {result}")
    print(f"Contains 'Gew. -': {'✅' if 'Gew. -' in result else '❌'}")
    print(f"Contains 'Regen -': {'✅' if 'Regen -' in result else '❌'}")
    print(f"Contains 'Regen -mm': {'✅' if 'Regen -mm' in result else '❌'}")
    print(f"Contains 'Hitze -': {'✅' if 'Hitze -' in result else '❌'}")
    print(f"Contains 'Wind -': {'✅' if 'Wind -' in result else '❌'}")
    print(f"Contains 'Windböen -': {'✅' if 'Windböen -' in result else '❌'}")
    print(f"Contains 'Gew.+1 -': {'✅' if 'Gew.+1 -' in result else '❌'}")
    print()

def test_no_vigilance_warnings():
    """Test reports without vigilance warnings."""
    print("=== Testing No Vigilance Warnings ===")
    
    # Sample data without vigilance warnings
    report_data = {
        "location": "TestLocation",
        "report_type": "morning",
        "weather_data": {
            "thunderstorm_threshold_pct": 25,
            "thunderstorm_threshold_time": "12",
            "max_thunderstorm_probability": 60,
            "thunderstorm_max_time": "14",
            "rain_threshold_pct": 30,
            "rain_threshold_time": "13",
            "max_rain_probability": 45,
            "rain_max_time": "15",
            "max_precipitation": 1.5,
            "rain_total_time": "13",
            "max_temperature": 25.0,
            "wind_speed": 10,
            "max_wind_speed": 20,
            "thunderstorm_next_day": 35,
            "thunderstorm_next_day_threshold_time": "11",
            "vigilance_alerts": []  # No alerts
        }
    }
    
    config = {"smtp": {"subject": "GR20 Wetter"}}
    
    result = _generate_morning_report(report_data, config)
    print(f"No Vigilance Report: {result}")
    print(f"Contains 'ORANGE': {'❌' if 'ORANGE' not in result else '❌'}")
    print(f"Contains 'YELLOW': {'❌' if 'YELLOW' not in result else '❌'}")
    print(f"Contains 'RED': {'❌' if 'RED' not in result else '❌'}")
    print()

def main():
    """Run all tests."""
    print("🧪 Testing New Email Format Implementation")
    print("=" * 50)
    
    test_vigilance_warning_formatting()
    test_morning_report()
    test_evening_report()
    test_update_report()
    test_null_values()
    test_no_vigilance_warnings()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 