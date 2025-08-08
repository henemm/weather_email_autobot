#!/usr/bin/env python3
"""
Test script for stable MeteoFrance API implementation.
"""

import sys
import os
sys.path.append('src')

from datetime import datetime, timedelta
from wetter.stable_meteofrance_api import StableMeteoFranceAPI, get_stable_stage_data

def test_stable_api():
    """Test the stable MeteoFrance API implementation."""
    
    print("Testing stable MeteoFrance API implementation")
    print("=" * 60)
    
    # Test coordinates for Conca stage (simplified)
    stage_coordinates = [
        [41.79418, 9.259567],  # Conca
        [41.80000, 9.260000],  # Nearby point
        [41.79000, 9.250000]   # Another nearby point
    ]
    stage_name = "Conca"
    
    try:
        # Test the API
        api = StableMeteoFranceAPI()
        
        print(f"Testing stage: {stage_name}")
        print(f"Coordinates: {len(stage_coordinates)} points")
        
        # Get stage weather data
        unified_data = api.get_stage_weather_data(stage_coordinates, stage_name)
        
        print(f"Successfully fetched data for {len(unified_data.data_points)} points")
        
        # Define time range (04:00-22:00 as per email_format.mdc)
        now = datetime.now()
        start_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        print(f"\nTime range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Get weather summary
        summary = api.get_weather_summary(unified_data, start_time, end_time)
        
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
            
            # Show details of first few thunderstorm entries
            if tomorrow_thunderstorm['thunderstorm_details']:
                print(f"  Details:")
                for i, detail in enumerate(tomorrow_thunderstorm['thunderstorm_details'][:3]):
                    print(f"    {i+1}. {detail['timestamp'].strftime('%H:%M')} - {detail['location']} - {detail['description']}")
        else:
            print(f"  Has thunderstorm: No")
            if 'error' in tomorrow_thunderstorm:
                print(f"  Error: {tomorrow_thunderstorm['error']}")
        
        # Debug info
        print("\n" + "=" * 60)
        print("DEBUG INFORMATION:")
        print(summary['debug_info'])
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error testing stable API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stable_api()
    sys.exit(0 if success else 1) 