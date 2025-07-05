#!/usr/bin/env python3
"""
Debug script to show the actual raw Météo-France API response.
This will help us understand what fields are actually available and how to map them correctly.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meteofrance_api.client import MeteoFranceClient


def debug_raw_api_response():
    """Show the actual raw API response from Météo-France."""
    
    print("🔍 DEBUGGING MÉTÉO-FRANCE API RAW RESPONSE")
    print("=" * 60)
    
    # Test coordinates (Asco)
    latitude = 42.4542
    longitude = 8.7389
    
    print(f"Testing coordinates: {latitude}, {longitude}")
    print()
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(latitude, longitude)
        
        print("✅ API call successful!")
        print(f"Number of forecast entries: {len(forecast.forecast)}")
        print()
        
        # Show the first few entries in detail
        for i, entry in enumerate(forecast.forecast[:6]):  # First 6 hours
            print(f"🕐 ENTRY {i+1} (Hour {i}):")
            print("-" * 40)
            
            # Show all available fields
            print("📋 ALL FIELDS:")
            for key, value in entry.items():
                print(f"  {key}: {value}")
            
            print()
            
            # Show specific weather-related fields
            print("🌤️ WEATHER FIELDS:")
            if 'weather' in entry:
                weather = entry['weather']
                print(f"  weather: {weather}")
                if isinstance(weather, dict):
                    for w_key, w_value in weather.items():
                        print(f"    {w_key}: {w_value}")
            
            if 'T' in entry:
                temp = entry['T']
                print(f"  temperature: {temp}")
                if isinstance(temp, dict):
                    for t_key, t_value in temp.items():
                        print(f"    {t_key}: {t_value}")
            
            if 'wind' in entry:
                wind = entry['wind']
                print(f"  wind: {wind}")
                if isinstance(wind, dict):
                    for w_key, w_value in wind.items():
                        print(f"    {w_key}: {w_value}")
            
            if 'rain' in entry:
                rain = entry['rain']
                print(f"  rain: {rain}")
                if isinstance(rain, dict):
                    for r_key, r_value in rain.items():
                        print(f"    {r_key}: {r_value}")
            
            if 'precipitation_probability' in entry:
                print(f"  precipitation_probability: {entry['precipitation_probability']}")
            
            if 'precipitation' in entry:
                precip = entry['precipitation']
                print(f"  precipitation: {precip}")
                if isinstance(precip, dict):
                    for p_key, p_value in precip.items():
                        print(f"    {p_key}: {p_value}")
            
            print()
            print("=" * 60)
            print()
        
        # Save full response to file for detailed analysis
        output_file = "output/debug/meteofrance_raw_response.json"
        Path("output/debug").mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(forecast.forecast, f, indent=2, default=str)
        
        print(f"💾 Full raw response saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_raw_api_response() 