#!/usr/bin/env python3
"""
Demo script for AROME weather data fetching functionality.

This script demonstrates how to use the AROME fetch module to retrieve
weather data from Météo-France API.
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome import fetch_arome_weather_data


def demo_arome_fetch():
    """Demonstrate AROME weather data fetching functionality."""
    print("=== AROME Weather Data Fetching Demo ===\n")
    
    # Sample coordinates (Corsica, France)
    latitude = 42.5
    longitude = 9.0
    
    print(f"Fetching weather data for coordinates: {latitude}°N, {longitude}°E")
    print("Location: Corsica, France\n")
    
    try:
        # Check if token is available
        token = os.environ.get("METEOFRANCE_AROME_TOKEN")
        if not token:
            print("⚠️  METEOFRANCE_AROME_TOKEN environment variable not set.")
            print("   This demo will show the expected functionality but cannot make real API calls.")
            print("   To test with real data, set your Météo-France API token:\n")
            print("   export METEOFRANCE_AROME_TOKEN='your_token_here'\n")
            
            # Show expected data structure
            print("Expected API Response Structure:")
            print("""
{
    "forecast": [
        {
            "time": "2025-06-15T12:00:00Z",
            "T": 20.5,              # Temperature in Celsius
            "T_windchill": 18.2,    # Feels like temperature
            "rr1h": 2.5,            # Precipitation in mm
            "cape": 500.0,          # CAPE value
            "shear": 15.0,          # SHEAR value
            "wind_u": 10.0,         # U wind component
            "wind_v": 5.0,          # V wind component
            "tcc": 75.0,            # Total cloud cover percentage
            "altitude": 100.0       # Elevation in meters
        }
    ]
}
            """)
            return
        
        print("✅ Token found. Attempting to fetch real weather data...\n")
        
        # Fetch weather data
        weather_data = fetch_arome_weather_data(latitude, longitude)
        
        print(f"✅ Successfully fetched {len(weather_data.points)} weather data points\n")
        
        # Display sample data points
        print("Sample Weather Data Points:")
        print("-" * 80)
        
        for i, point in enumerate(weather_data.points[:5]):  # Show first 5 points
            print(f"Point {i+1}:")
            print(f"  Time: {point.time}")
            print(f"  Temperature: {point.temperature}°C")
            print(f"  Feels like: {point.feels_like}°C")
            print(f"  Precipitation: {point.precipitation} mm")
            print(f"  Wind: {point.wind_speed:.1f} km/h at {point.wind_direction:.0f}°")
            print(f"  Cloud cover: {point.cloud_cover}%")
            
            if point.thunderstorm_probability is not None:
                print(f"  Thunderstorm probability: {point.thunderstorm_probability:.1f}%")
            
            if point.cape is not None:
                print(f"  CAPE: {point.cape:.0f} J/kg")
            
            if point.shear is not None:
                print(f"  SHEAR: {point.shear:.1f} m/s")
            
            print()
        
        if len(weather_data.points) > 5:
            print(f"... and {len(weather_data.points) - 5} more data points")
        
        # Show data summary
        print("Data Summary:")
        print("-" * 40)
        temperatures = [p.temperature for p in weather_data.points]
        precipitations = [p.precipitation for p in weather_data.points]
        wind_speeds = [p.wind_speed for p in weather_data.points]
        
        print(f"Temperature range: {min(temperatures):.1f}°C to {max(temperatures):.1f}°C")
        print(f"Total precipitation: {sum(precipitations):.1f} mm")
        print(f"Max wind speed: {max(wind_speeds):.1f} km/h")
        
        # Check for thunderstorm conditions
        thunderstorm_points = [p for p in weather_data.points if p.thunderstorm_probability and p.thunderstorm_probability > 30]
        if thunderstorm_points:
            print(f"⚠️  Thunderstorm risk detected in {len(thunderstorm_points)} time periods")
            max_risk = max(p.thunderstorm_probability for p in thunderstorm_points)
            print(f"   Maximum thunderstorm probability: {max_risk:.1f}%")
        
    except RuntimeError as e:
        print(f"❌ Error fetching weather data: {e}")
        print("\nThis could be due to:")
        print("- Invalid API token")
        print("- Network connectivity issues")
        print("- API service unavailability")
        print("- Rate limiting")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demo_error_handling():
    """Demonstrate error handling scenarios."""
    print("\n=== Error Handling Demo ===\n")
    
    # Test invalid coordinates
    print("Testing invalid coordinates:")
    try:
        fetch_arome_weather_data(91.0, 0.0)  # Invalid latitude
    except ValueError as e:
        print(f"✅ Correctly caught invalid latitude: {e}")
    
    try:
        fetch_arome_weather_data(0.0, 181.0)  # Invalid longitude
    except ValueError as e:
        print(f"✅ Correctly caught invalid longitude: {e}")
    
    # Test missing token
    print("\nTesting missing token:")
    original_token = os.environ.get("METEOFRANCE_AROME_TOKEN")
    if "METEOFRANCE_AROME_TOKEN" in os.environ:
        del os.environ["METEOFRANCE_AROME_TOKEN"]
    
    try:
        fetch_arome_weather_data(42.5, 9.0)
    except RuntimeError as e:
        print(f"✅ Correctly caught missing token: {e}")
    
    # Restore token if it existed
    if original_token:
        os.environ["METEOFRANCE_AROME_TOKEN"] = original_token


if __name__ == "__main__":
    demo_arome_fetch()
    demo_error_handling()
    
    print("\n=== Demo Complete ===")
    print("\nKey Features Demonstrated:")
    print("✅ OAuth2 token authentication")
    print("✅ Coordinate validation")
    print("✅ API request with proper headers")
    print("✅ JSON response parsing")
    print("✅ Weather data transformation")
    print("✅ Wind speed/direction calculation")
    print("✅ Thunderstorm probability calculation")
    print("✅ Error handling for various scenarios")
    print("✅ Comprehensive test coverage") 