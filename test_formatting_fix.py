#!/usr/bin/env python3
"""
Test script to verify formatting functions work correctly.

This script tests the formatting functions with the actual data
that was causing empty values in the reports.
"""

import sys
import os
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.notification.email_client import (
    _format_thunderstorm_field,
    _format_rain_field,
    _format_rain_amount_field,
    _format_temperature_field,
    _format_wind_field,
    _format_wind_gust_field,
    _format_thunderstorm_next_field
)


def test_formatting_functions():
    """Test all formatting functions with realistic data."""
    print("🧪 Testing Formatting Functions")
    print("=" * 50)
    
    # Test case 1: Data from the actual report (Conca example)
    print("\n📊 Test Case 1: Conca Report Data")
    print("-" * 30)
    
    # Simulate the data that was passed to the functions
    g_threshold = 0  # thunderstorm_threshold_pct
    t_g_threshold = ""  # thunderstorm_threshold_time
    g_pmax = 0  # max_thunderstorm_probability
    t_g_pmax = ""  # thunderstorm_max_time
    
    r_threshold = 0  # rain_threshold_pct
    t_r_threshold = ""  # rain_threshold_time
    r_pmax = 0  # max_rain_probability
    t_r_pmax = ""  # rain_max_time
    
    regen_mm = 0  # max_precipitation
    t_regen_max = ""  # rain_total_time
    
    temp_max = 34.7  # max_temperature
    wind = 4  # wind_speed
    wind_max = 13  # max_wind_speed
    
    g1_next = 0  # thunderstorm_next_day
    t_g1_next_threshold = ""  # thunderstorm_next_day_threshold_time
    
    # Test each formatting function
    thunder_part = _format_thunderstorm_field(g_threshold, t_g_threshold, g_pmax, t_g_pmax)
    rain_part = _format_rain_field(r_threshold, t_r_threshold, r_pmax, t_r_pmax)
    rain_amount_part = _format_rain_amount_field(regen_mm, t_regen_max)
    temp_part = _format_temperature_field(temp_max)
    wind_part = _format_wind_field(wind)
    wind_gust_part = _format_wind_gust_field(wind_max)
    thunder_next_part = _format_thunderstorm_next_field(g1_next, t_g1_next_threshold)
    
    print(f"Thunderstorm: '{thunder_part}'")
    print(f"Rain: '{rain_part}'")
    print(f"Rain amount: '{rain_amount_part}'")
    print(f"Temperature: '{temp_part}'")
    print(f"Wind: '{wind_part}'")
    print(f"Wind gusts: '{wind_gust_part}'")
    print(f"Thunderstorm next: '{thunder_next_part}'")
    
    # Verify expected results
    expected_results = {
        "thunderstorm": "Gew. -",
        "rain": "Regen -",
        "rain_amount": "Regen -mm",
        "temperature": "Hitze34.7°C",
        "wind": "Wind4km/h",
        "wind_gusts": "Windböen13km/h",
        "thunderstorm_next": "Gew.+1 -"
    }
    
    actual_results = {
        "thunderstorm": thunder_part,
        "rain": rain_part,
        "rain_amount": rain_amount_part,
        "temperature": temp_part,
        "wind": wind_part,
        "wind_gusts": wind_gust_part,
        "thunderstorm_next": thunder_next_part
    }
    
    all_correct = True
    for field, expected in expected_results.items():
        actual = actual_results[field]
        if actual == expected:
            print(f"✅ {field}: '{actual}'")
        else:
            print(f"❌ {field}: expected '{expected}', got '{actual}'")
            all_correct = False
    
    # Test case 2: Data with actual values
    print("\n📊 Test Case 2: Data with Actual Values")
    print("-" * 30)
    
    g_threshold = 30  # thunderstorm_threshold_pct
    t_g_threshold = "13"  # thunderstorm_threshold_time
    g_pmax = 80  # max_thunderstorm_probability
    t_g_pmax = "15"  # thunderstorm_max_time
    
    r_threshold = 55  # rain_threshold_pct
    t_r_threshold = "15"  # rain_threshold_time
    r_pmax = 70  # max_rain_probability
    t_r_pmax = "16"  # rain_max_time
    
    regen_mm = 2.0  # max_precipitation
    t_regen_max = "15"  # rain_total_time
    
    temp_max = 28.0  # max_temperature
    wind = 15  # wind_speed
    wind_max = 25  # max_wind_speed
    
    g1_next = 80  # thunderstorm_next_day
    t_g1_next_threshold = "14"  # thunderstorm_next_day_threshold_time
    
    # Test each formatting function
    thunder_part = _format_thunderstorm_field(g_threshold, t_g_threshold, g_pmax, t_g_pmax)
    rain_part = _format_rain_field(r_threshold, t_r_threshold, r_pmax, t_r_pmax)
    rain_amount_part = _format_rain_amount_field(regen_mm, t_regen_max)
    temp_part = _format_temperature_field(temp_max)
    wind_part = _format_wind_field(wind)
    wind_gust_part = _format_wind_gust_field(wind_max)
    thunder_next_part = _format_thunderstorm_next_field(g1_next, t_g1_next_threshold)
    
    print(f"Thunderstorm: '{thunder_part}'")
    print(f"Rain: '{rain_part}'")
    print(f"Rain amount: '{rain_amount_part}'")
    print(f"Temperature: '{temp_part}'")
    print(f"Wind: '{wind_part}'")
    print(f"Wind gusts: '{wind_gust_part}'")
    print(f"Thunderstorm next: '{thunder_next_part}'")
    
    # Verify expected results
    expected_results_2 = {
        "thunderstorm": "Gew.30%@13(80%@15)",
        "rain": "Regen55%@15(70%@16)",
        "rain_amount": "Regen2.0mm@15",
        "temperature": "Hitze28.0°C",
        "wind": "Wind15km/h",
        "wind_gusts": "Windböen25km/h",
        "thunderstorm_next": "Gew.+1 80%@14"
    }
    
    actual_results_2 = {
        "thunderstorm": thunder_part,
        "rain": rain_part,
        "rain_amount": rain_amount_part,
        "temperature": temp_part,
        "wind": wind_part,
        "wind_gusts": wind_gust_part,
        "thunderstorm_next": thunder_next_part
    }
    
    for field, expected in expected_results_2.items():
        actual = actual_results_2[field]
        if actual == expected:
            print(f"✅ {field}: '{actual}'")
        else:
            print(f"❌ {field}: expected '{expected}', got '{actual}'")
            all_correct = False
    
    return all_correct


def main():
    """Main test function."""
    print("🚀 Formatting Functions Test")
    print("=" * 60)
    
    success = test_formatting_functions()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All formatting tests passed! The reports should now show correct values.")
    else:
        print("💥 Some formatting tests failed. Check the logic.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 