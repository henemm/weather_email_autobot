#!/usr/bin/env python3
"""
Detailed debug script for evening report aggregation.

This script demonstrates the detailed aggregation process for evening reports:
1. Night values for last point of Capanelle with temp minimum
2. Day values for all three points of SanPetru with intermediate sums and global max
3. Verification that temp-min combines with night values for overall night minimum
4. Max values for Usciolu (next day) for thunderstorm probability only
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_loader import load_config
from src.wetter.weather_data_processor import WeatherDataProcessor
from src.position.etappenlogik import get_current_stage, get_stage_coordinates

def main():
    """Main function to test detailed evening report debug output."""
    print("🌙 EVENING REPORT DETAILED DEBUG TEST")
    print("=" * 80)
    
    # Load configuration
    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Initialize weather data processor
    processor = WeatherDataProcessor(config)
    print("✅ Weather data processor initialized")
    
    # Test with Capanelle coordinates (last point)
    # From etappen.json: Capanelle last point is (42.077314, 9.150127)
    test_lat = 42.077314
    test_lon = 9.150127
    test_location = "Capanelle_LastPoint"
    
    print(f"\n📍 Testing with coordinates: ({test_lat}, {test_lon})")
    print(f"📍 Location: {test_location}")
    
    # Process weather data for evening report
    # This will trigger the detailed debug output
    try:
        result = processor.process_weather_data(
            latitude=test_lat,
            longitude=test_lon,
            location_name=test_location,
            report_type='evening',
            hours_ahead=48  # Need more hours for evening report
        )
        
        print(f"\n✅ Weather data processing completed")
        print(f"📊 Result summary:")
        print(f"   - Max temperature: {result.get('max_temperature', 'N/A')}°C")
        print(f"   - Min temperature: {result.get('min_temperature', 'N/A')}°C")
        print(f"   - Max rain probability: {result.get('max_rain_probability', 'N/A')}%")
        print(f"   - Max thunderstorm probability: {result.get('max_thunderstorm_probability', 'N/A')}%")
        print(f"   - Thunderstorm next day: {result.get('thunderstorm_next_day', 'N/A')}%")
        
    except Exception as e:
        print(f"❌ Error processing weather data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 