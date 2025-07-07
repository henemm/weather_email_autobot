#!/usr/bin/env python3
"""
Comprehensive debug script for all report types.

This script demonstrates the detailed aggregation process for all report types:
1. Morning Report: Current day data for all points of current stage
2. Evening Report: Night values + tomorrow data + day after tomorrow thunderstorm
3. Update Report: Changed values for current day + tomorrow thunderstorm
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_loader import load_config
from src.wetter.weather_data_processor import WeatherDataProcessor

def main():
    """Main function to test detailed debug output for all report types."""
    print("📊 COMPREHENSIVE REPORT DEBUG TEST")
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
    test_lat = 42.077314
    test_lon = 9.150127
    test_location = "Capanelle_LastPoint"
    
    print(f"\n📍 Testing with coordinates: ({test_lat}, {test_lon})")
    print(f"📍 Location: {test_location}")
    
    # Test all three report types
    report_types = ['morning', 'evening', 'update']
    
    for report_type in report_types:
        print(f"\n{'='*80}")
        print(f"🧪 TESTING {report_type.upper()} REPORT")
        print(f"{'='*80}")
        
        try:
            result = processor.process_weather_data(
                latitude=test_lat,
                longitude=test_lon,
                location_name=f"{test_location}_{report_type}",
                report_type=report_type,
                hours_ahead=48  # Need more hours for evening report
            )
            
            print(f"\n✅ {report_type.capitalize()} report processing completed")
            print(f"📊 Result summary:")
            print(f"   - Max temperature: {result.get('max_temperature', 'N/A')}°C")
            print(f"   - Min temperature: {result.get('min_temperature', 'N/A')}°C")
            print(f"   - Max rain probability: {result.get('max_rain_probability', 'N/A')}%")
            print(f"   - Max thunderstorm probability: {result.get('max_thunderstorm_probability', 'N/A')}%")
            print(f"   - Thunderstorm next day: {result.get('thunderstorm_next_day', 'N/A')}%")
            
        except Exception as e:
            print(f"❌ Error processing {report_type} report: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("🎯 ALL REPORT TYPES TESTED")
    print(f"{'='*80}")
    print("✅ Morning Report: Current day data aggregation")
    print("✅ Evening Report: Night + tomorrow + day after tomorrow data")
    print("✅ Update Report: Changed values detection")
    print("\n📋 Each report type shows:")
    print("   - Detailed point-by-point data collection")
    print("   - Global maxima calculation")
    print("   - Threshold crossings and timing")
    print("   - Thunderstorm +1 for next day")
    print("   - Complete aggregation transparency")

if __name__ == "__main__":
    main() 