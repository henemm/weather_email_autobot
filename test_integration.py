#!/usr/bin/env python3
"""
Test script for integration of enhanced MeteoFrance API into weather data processor.
"""

import sys
import os
sys.path.append('src')

from datetime import datetime, timedelta
from wetter.weather_data_processor import WeatherDataProcessor

def test_integration():
    """Test the integration of enhanced API into weather data processor."""
    
    print("Testing Integration of Enhanced MeteoFrance API")
    print("=" * 60)
    
    # Test coordinates for Conca stage
    stage_coordinates = [
        [41.79418, 9.259567],  # Conca
        [41.80000, 9.260000],  # Nearby point
        [41.79000, 9.250000]   # Another nearby point
    ]
    stage_name = "Conca"
    
    try:
        # Test the integrated processor
        processor = WeatherDataProcessor()
        
        print(f"Testing stage: {stage_name}")
        print(f"Coordinates: {len(stage_coordinates)} points")
        print()
        
        # Get stage weather data
        unified_data = processor.get_stage_weather_data(stage_coordinates, stage_name)
        
        print(f"Successfully fetched data for {len(unified_data.data_points)} points")
        
        # Define time range (04:00-22:00 as per email_format.mdc)
        now = datetime.now()
        start_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        print(f"\nTime range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Get weather summary
        summary = processor.get_weather_summary(unified_data, start_time, end_time)
        
        print("\nWeather Summary:")
        print(f"  Stage: {summary['stage_name']}")
        print(f"  Date: {summary['stage_date']}")
        print(f"  Data points: {summary['data_points']}")
        
        # Temperature
        temp = summary['temperature']
        if temp['max'] is not None:
            print(f"  Temperature: {temp['min']:.1f}°C - {temp['max']:.1f}°C (avg: {temp['average']:.1f}°C)")
        
        # Rain
        rain = summary['rain']
        if rain['max_rate'] > 0:
            print(f"  Rain: {rain['total']:.1f}mm total, max {rain['max_rate']:.1f}mm/h")
        else:
            print(f"  Rain: No significant precipitation")
        
        # Wind
        wind = summary['wind']
        print(f"  Wind: avg {wind['average_speed']:.1f}km/h, gusts up to {wind['max_gusts']:.1f}km/h")
        
        # Thunderstorm (today)
        thunderstorm = summary['thunderstorm']
        if thunderstorm['has_thunderstorm']:
            print(f"  Thunderstorm: {thunderstorm['count']} occurrences detected")
        else:
            print(f"  Thunderstorm: None detected")
        
        # Thunderstorm tomorrow (+1)
        tomorrow_thunderstorm = summary['thunderstorm_tomorrow']
        print(f"\nTomorrow's Thunderstorm Forecast (+1):")
        if tomorrow_thunderstorm['has_thunderstorm']:
            print(f"  Has thunderstorm: Yes")
            print(f"  Probability: {tomorrow_thunderstorm['max_thunderstorm_probability']}%")
            print(f"  First occurrence: {tomorrow_thunderstorm['first_thunderstorm_time'].strftime('%H:%M')}")
            print(f"  Total occurrences: {tomorrow_thunderstorm['thunderstorm_count']}")
        else:
            print(f"  Has thunderstorm: No")
        
        # Get rain probability data
        rain_prob_data = processor.get_rain_probability_data(unified_data, start_time, end_time)
        print(f"\nRain Probability Data:")
        print(f"  Entries: {len(rain_prob_data)}")
        if rain_prob_data:
            entries_with_prob = [entry for entry in rain_prob_data if entry['has_rain_probability']]
            print(f"  With probability data: {len(entries_with_prob)}")
            
            # Show first few entries with probability
            for i, prob in enumerate(entries_with_prob[:3]):
                print(f"    Entry {i+1}: {prob['timestamp'].strftime('%H:%M')} - 3h: {prob['rain_3h']}%, 6h: {prob['rain_6h']}%")
        
        # Get debug info
        debug_info = processor.get_debug_info(unified_data, start_time, end_time)
        print(f"\nDebug Info Length: {len(debug_info)} characters")
        
        # Show first part of debug info
        debug_lines = debug_info.split('\n')
        print("Debug Info Preview:")
        for i, line in enumerate(debug_lines[:10]):
            print(f"  {line}")
        if len(debug_lines) > 10:
            print(f"  ... ({len(debug_lines) - 10} more lines)")
        
        print("\n" + "=" * 60)
        print("Integration test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error testing integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1) 