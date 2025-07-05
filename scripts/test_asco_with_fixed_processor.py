#!/usr/bin/env python3
"""
Test script specifically for Asco with meteofrance-api to verify the fix.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wetter.weather_data_processor import process_weather_data_for_report
from notification.email_client import _generate_morning_report


def test_asco_with_meteofrance():
    """Test Asco specifically with meteofrance-api."""
    
    print("🧪 TESTING ASCO WITH MÉTÉO-FRANCE API")
    print("=" * 60)
    
    # Test coordinates (Asco)
    latitude = 42.426238
    longitude = 8.900291
    location_name = "Asco"
    
    print(f"Testing coordinates: {latitude}, {longitude}")
    print(f"Location: {location_name}")
    print()
    
    # Load config
    config = {
        "thresholds": {
            "thunderstorm_probability": 20.0,
            "rain_probability": 25.0,
            "rain_amount": 2.0,
            "wind_speed": 20.0,
            "temperature": 32.0
        },
        "subject": "GR20 Wetter"
    }
    
    try:
        # Process weather data with meteofrance-api
        weather_data = process_weather_data_for_report(
            latitude, longitude, location_name, config
        )
        
        print("✅ Weather data processing successful!")
        print()
        
        print("📊 PROCESSED WEATHER DATA:")
        print("-" * 40)
        print(f"Location: {weather_data['location']}")
        print(f"Data source: {weather_data['data_source']}")
        print()
        
        print("🌤️ WEATHER VALUES:")
        print(f"Max temperature: {weather_data['max_temperature']}°C")
        print(f"Max precipitation: {weather_data['max_precipitation']}mm")
        print(f"Max rain probability: {weather_data['max_rain_probability']}%")
        print(f"Max thunderstorm probability: {weather_data['max_thunderstorm_probability']}%")
        print(f"Max wind speed: {weather_data['max_wind_speed']}km/h")
        print()
        
        print("⏰ THRESHOLD CROSSINGS:")
        print(f"Thunderstorm: {weather_data['thunderstorm_threshold_pct']}% @ {weather_data['thunderstorm_threshold_time']}")
        print(f"Thunderstorm max: {weather_data['thunderstorm_max_time']}")
        print(f"Rain: {weather_data['rain_threshold_pct']}% @ {weather_data['rain_threshold_time']}")
        print(f"Rain max: {weather_data['rain_max_time']}")
        print()
        
        # Generate morning report
        print("📋 GENERATING MORNING REPORT:")
        print("-" * 40)
        
        # Add required fields for report generation
        weather_data['vigilance_alerts'] = []
        weather_data['min_temperature'] = 0.0
        weather_data['thunderstorm_next_day'] = 0.0
        
        # Prepare report_data in the expected format
        report_data = {
            'location': location_name,
            'weather_data': weather_data
        }
        report_text = _generate_morning_report(report_data, config)
        
        print(f"Report text: {report_text}")
        print(f"Length: {len(report_text)} characters")
        print()
        
        # Check if thunderstorm data is in the report
        if "Gew." in report_text and "Gew. -" not in report_text:
            print("✅ SUCCESS: Thunderstorm data in report!")
            print(f"   Report shows: {report_text}")
        else:
            print("❌ FAILURE: No thunderstorm data in report")
            print(f"   Report shows: {report_text}")
        
        if "Regen" in report_text and "Regen -" not in report_text:
            print("✅ SUCCESS: Rain data in report!")
        else:
            print("❌ FAILURE: No rain data in report")
        
        # Save results
        output_file = "output/debug/asco_meteofrance_test.json"
        Path("output/debug").mkdir(parents=True, exist_ok=True)
        
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'location': location_name,
            'coordinates': {'lat': latitude, 'lon': longitude},
            'weather_data': weather_data,
            'report_text': report_text,
            'report_length': len(report_text)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, indent=2, default=str)
        
        print(f"\n💾 Test result saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error testing Asco: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_asco_with_meteofrance() 