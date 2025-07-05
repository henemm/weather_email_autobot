#!/usr/bin/env python3
"""
Test script to verify the fixed weather data processor.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wetter.weather_data_processor import process_weather_data_for_report


def test_fixed_processor():
    """Test the fixed weather data processor."""
    
    print("🧪 TESTING FIXED WEATHER DATA PROCESSOR")
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
        }
    }
    
    try:
        # Process weather data
        result = process_weather_data_for_report(
            latitude, longitude, location_name, config
        )
        
        print("✅ Weather data processing successful!")
        print()
        
        print("📊 PROCESSED WEATHER DATA:")
        print("-" * 40)
        print(f"Location: {result['location']}")
        print(f"Data source: {result['data_source']}")
        print(f"Processed at: {result['processed_at']}")
        print()
        
        print("🌤️ WEATHER VALUES:")
        print(f"Max temperature: {result['max_temperature']}°C")
        print(f"Max precipitation: {result['max_precipitation']}mm")
        print(f"Max rain probability: {result['max_rain_probability']}%")
        print(f"Max thunderstorm probability: {result['max_thunderstorm_probability']}%")
        print(f"Max wind speed: {result['max_wind_speed']}km/h")
        print(f"Wind speed: {result['wind_speed']}km/h")
        print()
        
        print("⏰ THRESHOLD CROSSINGS:")
        print(f"Thunderstorm: {result['thunderstorm_threshold_pct']}% @ {result['thunderstorm_threshold_time']}")
        print(f"Thunderstorm max: {result['thunderstorm_max_time']}")
        print(f"Rain: {result['rain_threshold_pct']}% @ {result['rain_threshold_time']}")
        print(f"Rain max: {result['rain_max_time']}")
        print(f"Rain total: {result['rain_total_time']}")
        print()
        
        # Check if thunderstorm data is now present
        if result['max_thunderstorm_probability'] > 0:
            print("✅ SUCCESS: Thunderstorm data detected!")
            print(f"   Max thunderstorm probability: {result['max_thunderstorm_probability']}%")
        else:
            print("❌ FAILURE: No thunderstorm data detected")
        
        if result['max_precipitation'] > 0:
            print("✅ SUCCESS: Precipitation data detected!")
            print(f"   Max precipitation: {result['max_precipitation']}mm")
        else:
            print("❌ FAILURE: No precipitation data detected")
        
        # Save result to file
        output_file = "output/debug/fixed_processor_test.json"
        Path("output/debug").mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Test result saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error testing fixed processor: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fixed_processor() 