#!/usr/bin/env python3
"""
Script to compare Météo-France API data with official website visualization.

This script fetches raw API data and provides instructions for manual comparison
with the official Météo-France website for the same location and time.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.wetter.debug_raw_data import get_raw_weather_data, format_raw_data_output
from src.wetter.fetch_meteofrance import get_forecast, get_thunderstorm


def get_meteofrance_website_url(latitude: float, longitude: float, location_name: str) -> str:
    """
    Generate Météo-France website URL for manual comparison.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        location_name: Human-readable location name
        
    Returns:
        URL for Météo-France website
    """
    # Météo-France uses a different coordinate system or location names
    # This is a simplified mapping for common locations
    
    location_mapping = {
        "Corte": "corte-2B",
        "Asco": "asco-2B", 
        "Calenzana": "calenzana-2B",
        "Tarbes": "tarbes-65",
        "Nantes": "nantes-44"
    }
    
    if location_name in location_mapping:
        location_code = location_mapping[location_name]
        return f"https://meteofrance.com/previsions-meteo-france/{location_code}"
    else:
        # Fallback to generic URL with coordinates
        return f"https://meteofrance.com/previsions-meteo-france/recherche?lat={latitude}&lon={longitude}"


def compare_with_website(latitude: float, longitude: float, location_name: str):
    """
    Compare API data with Météo-France website.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        location_name: Human-readable location name
    """
    print(f"🌐 Comparing API data with Météo-France website for {location_name}")
    print("=" * 60)
    
    try:
        # Get current time
        now = datetime.now()
        target_date = now.date()
        
        print(f"📅 Target date: {target_date.strftime('%d.%m.%Y')}")
        print(f"🕐 Current time: {now.strftime('%H:%M')}")
        
        # Get raw API data
        print(f"\n📡 Fetching API data...")
        raw_data = get_raw_weather_data(latitude, longitude, location_name, hours_ahead=24)
        
        # Get current forecast
        forecast = get_forecast(latitude, longitude)
        thunderstorm = get_thunderstorm(latitude, longitude)
        
        # Display API data
        print(f"\n📊 API Data Summary:")
        print(f"  Temperature: {forecast.temperature}°C")
        print(f"  Weather: {forecast.weather_condition}")
        print(f"  Precipitation probability: {forecast.precipitation_probability}%")
        print(f"  Wind speed: {forecast.wind_speed} km/h")
        print(f"  Wind gusts: {forecast.wind_gusts} km/h")
        print(f"  Thunderstorm: {thunderstorm}")
        
        # Generate website URL
        website_url = get_meteofrance_website_url(latitude, longitude, location_name)
        
        print(f"\n🌐 Météo-France Website:")
        print(f"  URL: {website_url}")
        print(f"  Location: {location_name}")
        print(f"  Date: {target_date.strftime('%d.%m.%Y')}")
        
        # Display raw data for comparison
        print(f"\n📋 Raw API Data for Manual Comparison:")
        print("-" * 40)
        formatted_output = format_raw_data_output(raw_data)
        print(formatted_output)
        
        # Instructions for manual comparison
        print(f"\n📝 Manual Comparison Instructions:")
        print("1. Open the Météo-France website URL above")
        print("2. Navigate to the hourly forecast for today")
        print("3. Compare the following values:")
        print("   - Temperature (°C)")
        print("   - Precipitation probability (%)")
        print("   - Weather conditions (sunny, rain, thunderstorm, etc.)")
        print("   - Wind speed (km/h)")
        print("4. Note any discrepancies between API and website")
        
        # Save comparison data
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        output_file = f"output/{location_name.lower()}_website_comparison_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Météo-France API vs Website Comparison\n")
            f.write(f"Location: {location_name}\n")
            f.write(f"Date: {target_date.strftime('%d.%m.%Y')}\n")
            f.write(f"Time: {now.strftime('%H:%M')}\n")
            f.write(f"Website URL: {website_url}\n\n")
            f.write("API Data:\n")
            f.write(f"Temperature: {forecast.temperature}°C\n")
            f.write(f"Weather: {forecast.weather_condition}\n")
            f.write(f"Precipitation probability: {forecast.precipitation_probability}%\n")
            f.write(f"Wind speed: {forecast.wind_speed} km/h\n")
            f.write(f"Wind gusts: {forecast.wind_gusts} km/h\n")
            f.write(f"Thunderstorm: {thunderstorm}\n\n")
            f.write("Raw API Data:\n")
            f.write(formatted_output)
        
        print(f"\n💾 Comparison data saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during website comparison: {e}")
        return False


def analyze_specific_time(latitude: float, longitude: float, location_name: str, target_time: str):
    """
    Analyze API data for a specific time and compare with website.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        location_name: Human-readable location name
        target_time: Target time in HH:MM format (e.g., "14:00")
    """
    print(f"🕐 Analyzing specific time: {target_time} for {location_name}")
    print("=" * 60)
    
    try:
        # Parse target time
        hour, minute = map(int, target_time.split(':'))
        now = datetime.now()
        target_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Get raw data
        raw_data = get_raw_weather_data(latitude, longitude, location_name, hours_ahead=24)
        
        # Find data for target time
        target_data = None
        for point in raw_data.time_points:
            if point.timestamp.hour == hour:
                target_data = point
                break
        
        if target_data:
            print(f"📊 API Data for {target_time}:")
            print(f"  Temperature: {target_data.temperature}°C")
            print(f"  Weather: {target_data.weather_condition}")
            print(f"  Precipitation probability: {target_data.precipitation_probability}%")
            print(f"  Precipitation amount: {target_data.precipitation_amount}mm")
            print(f"  Thunderstorm probability: {target_data.thunderstorm_probability}%")
            print(f"  Wind speed: {target_data.wind_speed} km/h")
            print(f"  Wind gusts: {target_data.wind_gusts} km/h")
            
            # Generate website URL
            website_url = get_meteofrance_website_url(latitude, longitude, location_name)
            
            print(f"\n🌐 Compare with Météo-France website:")
            print(f"  URL: {website_url}")
            print(f"  Time: {target_time}")
            print(f"  Date: {target_datetime.strftime('%d.%m.%Y')}")
            
        else:
            print(f"❌ No data found for {target_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during specific time analysis: {e}")
        return False


def main():
    """Main function."""
    print("🌤️ Météo-France API vs Website Comparison")
    print("=" * 50)
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Test locations
    test_locations = [
        (42.15, 9.15, "Corte"),  # Example from request
        (42.23, 9.15, "Asco"),
        (42.45, 9.03, "Calenzana")
    ]
    
    # Test current time comparison
    print("Testing current time comparison...")
    for latitude, longitude, name in test_locations:
        success = compare_with_website(latitude, longitude, name)
        if not success:
            print(f"⚠️ Failed to compare {name}")
    
    # Test specific time (14:00 as mentioned in request)
    print(f"\nTesting specific time comparison (14:00)...")
    latitude, longitude, name = test_locations[0]  # Use Corte
    success = analyze_specific_time(latitude, longitude, name, "14:00")
    
    if success:
        print("✅ Website comparison completed successfully")
        print("\n📋 Next steps:")
        print("1. Open the provided Météo-France website URLs")
        print("2. Compare the displayed values with the API data")
        print("3. Note any discrepancies in the output files")
        print("4. Use the raw data output for detailed verification")
    else:
        print("❌ Website comparison failed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 