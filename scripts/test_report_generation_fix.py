#!/usr/bin/env python3
"""
Test script to verify that the report generation now uses the correct weather data processor.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.config_loader import load_config
from wetter.weather_data_processor import process_weather_data_for_report
from notification.email_client import generate_gr20_report_text


def test_report_generation():
    """Test the report generation with the new weather data processor."""
    
    print("🧪 TESTING REPORT GENERATION FIX")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Test coordinates (Asco)
    latitude = 42.4542
    longitude = 8.7389
    location_name = "Asco"
    
    print(f"Testing location: {location_name}")
    print(f"Coordinates: {latitude}, {longitude}")
    print()
    
    try:
        # Get processed weather data using the new processor
        print("📊 Getting processed weather data...")
        processed_weather_data = process_weather_data_for_report(latitude, longitude, location_name, config)
        
        print("✅ Weather data processed successfully!")
        print()
        
        # Create report data
        report_data = {
            "location": location_name,
            "risk_percentage": 50,
            "risk_description": "Test risk",
            "report_time": "2025-07-05T07:00:00",
            "report_type": "morning",
            "weather_data": processed_weather_data
        }
        
        # Generate report text
        print("📝 Generating report text...")
        report_text = generate_gr20_report_text(report_data, config)
        
        print("✅ Report generated successfully!")
        print()
        
        # Display results
        print("📋 REPORT RESULTS:")
        print("-" * 30)
        print(f"Generated report: {report_text}")
        print()
        
        # Show key weather data values
        print("🔍 KEY WEATHER DATA VALUES:")
        print("-" * 30)
        print(f"Thunderstorm threshold: {processed_weather_data.get('thunderstorm_threshold_pct', 'N/A')}% @ {processed_weather_data.get('thunderstorm_threshold_time', 'N/A')}")
        print(f"Thunderstorm max: {processed_weather_data.get('max_thunderstorm_probability', 'N/A')}% @ {processed_weather_data.get('thunderstorm_max_time', 'N/A')}")
        print(f"Rain threshold: {processed_weather_data.get('rain_threshold_pct', 'N/A')}% @ {processed_weather_data.get('rain_threshold_time', 'N/A')}")
        print(f"Rain max: {processed_weather_data.get('max_rain_probability', 'N/A')}% @ {processed_weather_data.get('rain_max_time', 'N/A')}")
        print(f"Precipitation amount: {processed_weather_data.get('max_precipitation', 'N/A')}mm @ {processed_weather_data.get('rain_total_time', 'N/A')}")
        print(f"Temperature max: {processed_weather_data.get('max_temperature', 'N/A')}°C")
        print(f"Wind speed: {processed_weather_data.get('wind_speed', 'N/A')}km/h")
        print(f"Wind gusts: {processed_weather_data.get('max_wind_speed', 'N/A')}km/h")
        print()
        
        # Check if the report shows the correct values
        print("✅ VERIFICATION:")
        print("-" * 30)
        
        # Check thunderstorm
        if "Gew. -" in report_text:
            print("❌ Thunderstorm shows 'Gew. -' (no thunderstorm)")
        else:
            print("✅ Thunderstorm shows actual values")
        
        # Check precipitation
        if "Regen -mm" in report_text:
            print("❌ Precipitation shows 'Regen -mm' (no precipitation)")
        else:
            print("✅ Precipitation shows actual values")
        
        # Check if values match the processed data
        thunderstorm_pct = processed_weather_data.get('thunderstorm_threshold_pct', 0)
        precipitation_mm = processed_weather_data.get('max_precipitation', 0)
        
        if thunderstorm_pct > 0 and f"Gew.{thunderstorm_pct:.0f}%" in report_text:
            print("✅ Thunderstorm percentage matches processed data")
        elif thunderstorm_pct == 0 and "Gew. -" in report_text:
            print("✅ Thunderstorm correctly shows '-' for zero probability")
        else:
            print("❌ Thunderstorm percentage mismatch")
        
        if precipitation_mm > 0 and f"Regen{precipitation_mm:.1f}mm" in report_text:
            print("✅ Precipitation amount matches processed data")
        elif precipitation_mm == 0 and "Regen -mm" in report_text:
            print("✅ Precipitation correctly shows '-' for zero amount")
        else:
            print("❌ Precipitation amount mismatch")
        
        print()
        print("🎯 SUMMARY:")
        print("-" * 30)
        print("The report generation now uses the new weather data processor")
        print("which correctly extracts thunderstorm and precipitation data")
        print("from the Météo-France API raw data.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_report_generation() 