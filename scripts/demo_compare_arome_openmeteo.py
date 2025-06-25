#!/usr/bin/env python3
"""
Demo script for AROME vs Open-Meteo weather comparison.

This script demonstrates how to compare weather data from two different sources:
- Météo-France AROME WCS: For CAPE, SHEAR, and specialized parameters
- Open-Meteo API: For temperature, wind, and precipitation

The comparison is performed for Conca, Corsica (lat=41.7481, lon=9.2972).
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.compare_models import (
    compare_arome_openmeteo_conca,
    save_comparison_to_file,
    get_comparison_summary
)
from wetter.fetch_openmeteo import fetch_openmeteo_forecast


def demo_openmeteo_only():
    """Demonstrate Open-Meteo functionality (no token required)."""
    print("🌤️  Open-Meteo Weather Data Demo")
    print("=" * 50)
    print("📍 Location: Conca, Corsica (41.7481°N, 9.2972°E)")
    print("🔗 API: https://api.open-meteo.com/v1/forecast")
    print("🔓 Authentication: None required")
    print()
    
    try:
        # Fetch Open-Meteo data
        print("📡 Fetching Open-Meteo weather data...")
        forecast_data = fetch_openmeteo_forecast(41.7481, 9.2972)
        
        print("✅ Successfully fetched Open-Meteo data!")
        print()
        
        # Display current weather
        current = forecast_data.get("current", {})
        if current:
            print("🌡️  Current Weather Conditions:")
            print(f"   Temperature: {current.get('temperature_2m')}°C")
            print(f"   Feels like: {current.get('apparent_temperature')}°C")
            print(f"   Humidity: {current.get('relative_humidity_2m')}%")
            print(f"   Wind: {current.get('wind_speed_10m')} km/h at {current.get('wind_direction_10m')}°")
            print(f"   Precipitation: {current.get('precipitation')} mm")
            print(f"   Cloud cover: {current.get('cloud_cover')}%")
            print(f"   Pressure: {current.get('pressure_msl')} hPa")
            print(f"   Weather code: {current.get('weather_code')}")
            print()
        
        # Display forecast info
        hourly = forecast_data.get("hourly", {})
        if hourly and hourly.get("time"):
            print("📅 Forecast Information:")
            print(f"   Time steps: {len(hourly['time'])}")
            print(f"   Time range: {hourly['time'][0]} to {hourly['time'][-1]}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Open-Meteo demo failed: {e}")
        return False


def demo_full_comparison():
    """Demonstrate full AROME vs Open-Meteo comparison."""
    print("🔄 Full Weather Model Comparison Demo")
    print("=" * 50)
    print("📍 Location: Conca, Corsica")
    print("📊 Comparing: AROME WCS vs Open-Meteo API")
    print()
    
    try:
        # Perform comparison
        print("🔄 Performing weather model comparison...")
        comparison_data = compare_arome_openmeteo_conca()
        
        print("✅ Comparison completed!")
        print()
        
        # Generate and display summary
        summary = get_comparison_summary(comparison_data)
        
        print("📋 Comparison Summary:")
        print(f"   Timestamp: {summary['timestamp']}")
        print(f"   Location: {summary['location']['name']}")
        print()
        
        # Data source status
        print("📡 Data Source Status:")
        for source, status in summary['data_sources'].items():
            status_icon = "✅" if status == "available" else "❌"
            print(f"   {status_icon} {source.upper()}: {status}")
        print()
        
        # Errors
        if summary['errors']:
            print("⚠️  Errors encountered:")
            for error in summary['errors']:
                print(f"   - {error}")
            print()
        
        # AROME summary
        arome_summary = summary['summary'].get('arome', {})
        if 'error' not in arome_summary:
            print("🌩️  AROME Data (CAPE/SHEAR layers):")
            print(f"   Layers fetched: {arome_summary['layers_fetched']}/{arome_summary['total_layers']}")
            if arome_summary['available_layers']:
                print(f"   Available layers: {', '.join(arome_summary['available_layers'])}")
        else:
            print(f"❌ AROME Data: {arome_summary['error']}")
        print()
        
        # Open-Meteo summary
        openmeteo_summary = summary['summary'].get('open_meteo', {})
        if 'error' not in openmeteo_summary:
            print("🌤️  Open-Meteo Data (Temperature/Wind/Precipitation):")
            print(f"   Temperature: {openmeteo_summary['temperature']}°C")
            print(f"   Wind speed: {openmeteo_summary['wind_speed']} km/h")
            print(f"   Precipitation: {openmeteo_summary['precipitation']} mm")
        else:
            print(f"❌ Open-Meteo Data: {openmeteo_summary['error']}")
        print()
        
        # Save to file
        try:
            filepath = save_comparison_to_file(comparison_data)
            print(f"💾 Comparison data saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Failed to save comparison data: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full comparison demo failed: {e}")
        return False


def main():
    """Main demo function."""
    print("🌍 AROME vs Open-Meteo Weather Comparison Demo")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().isoformat()}")
    print()
    
    # Check if AROME token is available
    try:
        from src.auth.api_token_provider import get_api_token
        token = get_api_token("arome")
        has_arome_token = bool(token)
    except Exception:
        has_arome_token = False
    
    print("🔑 Token Status:")
    print(f"   Open-Meteo: ✅ No token required")
    print(f"   AROME WCS: {'✅ Token available' if has_arome_token else '❌ No token available'}")
    print()
    
    # Demo Open-Meteo (always works)
    print("=" * 60)
    openmeteo_success = demo_openmeteo_only()
    
    # Demo full comparison (if AROME token available)
    if has_arome_token:
        print("=" * 60)
        comparison_success = demo_full_comparison()
    else:
        print("=" * 60)
        print("⏭️  Skipping full comparison demo - AROME token not available")
        print("   To enable AROME comparison:")
        print("   1. Get AROME WCS token from Météo-France")
        print("   2. Set METEOFRANCE_WCS_TOKEN environment variable")
        print("   3. Run this demo again")
        comparison_success = False
    
    print("=" * 60)
    print("📊 Demo Summary:")
    print(f"   Open-Meteo demo: {'✅ Success' if openmeteo_success else '❌ Failed'}")
    print(f"   Full comparison: {'✅ Success' if comparison_success else '❌ Skipped/Failed'}")
    print()
    print("🎉 Demo completed!")


if __name__ == "__main__":
    main() 