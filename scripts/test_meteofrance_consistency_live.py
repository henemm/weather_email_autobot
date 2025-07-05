#!/usr/bin/env python3
"""
Live test script for Météo-France API consistency verification.

This script demonstrates the debug functionality for verifying consistency
between raw weather data and generated reports.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.wetter.debug_raw_data import (
    get_raw_weather_data,
    format_raw_data_output,
    compare_raw_data_with_report,
    save_debug_output
)
from src.wetter.fetch_meteofrance import get_forecast, get_thunderstorm
from src.logic.analyse_weather import analyze_weather_data
from src.model.datatypes import WeatherData, WeatherPoint
from src.config.config_loader import load_config


def test_corte_consistency():
    """Test consistency for Corte, Corsica (example from request)."""
    print("=== Testing Météo-France Consistency for Corte ===")
    
    # Test coordinates for Corte, Corsica
    latitude = 42.15
    longitude = 9.15
    location_name = "Corte"
    
    try:
        # Load configuration
        config = load_config()
        print(f"✅ Configuration loaded")
        
        # Get raw weather data
        print(f"📡 Fetching raw weather data for {location_name}...")
        raw_data = get_raw_weather_data(latitude, longitude, location_name, hours_ahead=24)
        print(f"✅ Raw data fetched: {len(raw_data.time_points)} time points")
        
        # Format and display raw data
        print("\n" + "="*60)
        print("RAW WEATHER DATA OUTPUT")
        print("="*60)
        formatted_output = format_raw_data_output(raw_data)
        print(formatted_output)
        
        # Save raw data to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/corte_raw_data_{timestamp}.txt"
        save_debug_output(raw_data, output_file)
        print(f"\n💾 Raw data saved to: {output_file}")
        
        # Get current forecast for comparison
        print(f"\n📊 Fetching current forecast for comparison...")
        forecast = get_forecast(latitude, longitude)
        thunderstorm = get_thunderstorm(latitude, longitude)
        
        # Create mock report values for comparison
        report_values = {
            "temperature": forecast.temperature,
            "precipitation_probability": forecast.precipitation_probability,
            "wind_speed": forecast.wind_speed,
            "wind_gusts": forecast.wind_gusts,
            "weather_condition": forecast.weather_condition
        }
        
        print(f"✅ Current forecast: {forecast.temperature}°C, "
              f"Precipitation: {forecast.precipitation_probability}%, "
              f"Wind: {forecast.wind_speed}km/h")
        print(f"✅ Thunderstorm: {thunderstorm}")
        
        # Compare raw data with report values
        print(f"\n🔍 Comparing raw data with report values...")
        comparison = compare_raw_data_with_report(raw_data, report_values, config)
        
        # Display comparison results
        print("\n" + "="*60)
        print("COMPARISON RESULTS")
        print("="*60)
        
        print(f"Location: {comparison['location']}")
        print(f"Data Source: {comparison['data_source']}")
        print(f"Timestamp: {comparison['timestamp']}")
        
        print("\nValue Comparisons:")
        for key, comp in comparison['comparisons'].items():
            status = "✅" if comp['match'] else "❌"
            print(f"  {status} {key}: Raw={comp['raw_value']}, Report={comp['report_value']}")
        
        print("\nThreshold Checks:")
        for key, check in comparison['threshold_checks'].items():
            status = "⚠️" if check['exceeded'] else "✅"
            print(f"  {status} {key}: {check['value']} (threshold: {check['threshold']})")
        
        if comparison['issues']:
            print("\nIssues Found:")
            for issue in comparison['issues']:
                print(f"  ❌ {issue}")
        else:
            print("\n✅ No issues found")
        
        # Save comparison results
        comparison_file = f"output/corte_comparison_{timestamp}.json"
        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, default=str)
        print(f"\n💾 Comparison results saved to: {comparison_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during consistency test: {e}")
        return False


def test_multiple_locations():
    """Test consistency for multiple locations."""
    print("\n=== Testing Multiple Locations ===")
    
    # Test locations from etappen.json
    locations = [
        (42.15, 9.15, "Corte"),
        (42.23, 9.15, "Asco"),
        (42.45, 9.03, "Calenzana")
    ]
    
    try:
        config = load_config()
        
        for latitude, longitude, name in locations:
            print(f"\n📍 Testing {name} ({latitude}, {longitude})...")
            
            try:
                # Get raw data
                raw_data = get_raw_weather_data(latitude, longitude, name, hours_ahead=12)
                
                # Get current forecast
                forecast = get_forecast(latitude, longitude)
                
                # Create report values
                report_values = {
                    "temperature": forecast.temperature,
                    "precipitation_probability": forecast.precipitation_probability,
                    "wind_speed": forecast.wind_speed,
                    "wind_gusts": forecast.wind_gusts
                }
                
                # Compare
                comparison = compare_raw_data_with_report(raw_data, report_values, config)
                
                # Display summary
                matches = sum(1 for comp in comparison['comparisons'].values() if comp['match'])
                total = len(comparison['comparisons'])
                issues = len(comparison['issues'])
                
                print(f"  📊 Data points: {len(raw_data.time_points)}")
                print(f"  ✅ Matches: {matches}/{total}")
                print(f"  ⚠️ Issues: {issues}")
                
                if issues > 0:
                    print(f"  ❌ Issues: {', '.join(comparison['issues'])}")
                
            except Exception as e:
                print(f"  ❌ Error for {name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during multi-location test: {e}")
        return False


def test_threshold_validation():
    """Test threshold validation with known data."""
    print("\n=== Testing Threshold Validation ===")
    
    try:
        config = load_config()
        thresholds = config.get("thresholds", {})
        
        print(f"📋 Current thresholds:")
        for key, value in thresholds.items():
            print(f"  {key}: {value}")
        
        # Test with Corte data
        latitude = 42.15
        longitude = 9.15
        location_name = "Corte"
        
        raw_data = get_raw_weather_data(latitude, longitude, location_name, hours_ahead=24)
        
        # Analyze threshold crossings
        print(f"\n🔍 Analyzing threshold crossings for {location_name}:")
        
        for point in raw_data.time_points:
            time_str = point.timestamp.strftime("%H:%M")
            
            # Check precipitation probability threshold
            if point.precipitation_probability is not None:
                threshold = thresholds.get("rain_probability", 25.0)
                if point.precipitation_probability >= threshold:
                    print(f"  ⚠️ {time_str}: Rain probability {point.precipitation_probability}% >= {threshold}%")
            
            # Check thunderstorm probability threshold
            if point.thunderstorm_probability is not None:
                threshold = thresholds.get("thunderstorm_probability", 20.0)
                if point.thunderstorm_probability >= threshold:
                    print(f"  ⚡ {time_str}: Thunderstorm probability {point.thunderstorm_probability}% >= {threshold}%")
            
            # Check precipitation amount threshold
            if point.precipitation_amount is not None:
                threshold = thresholds.get("rain_amount", 2.0)
                if point.precipitation_amount >= threshold:
                    print(f"  🌧️ {time_str}: Precipitation amount {point.precipitation_amount}mm >= {threshold}mm")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during threshold validation: {e}")
        return False


def main():
    """Main test function."""
    print("🌤️ Météo-France API Consistency Verification")
    print("=" * 50)
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Run tests
    tests = [
        ("Corte Consistency", test_corte_consistency),
        ("Multiple Locations", test_multiple_locations),
        ("Threshold Validation", test_threshold_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 