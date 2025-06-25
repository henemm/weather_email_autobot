#!/usr/bin/env python3
"""
Debug script for Open-Meteo timezone issues.
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast

def test_openmeteo_timezone():
    """Test Open-Meteo API with different timezone approaches."""
    print("🔍 Debug: Open-Meteo Timezone Test")
    print("=" * 50)
    
    # Pouillac coordinates
    lat, lon = 44.857, -0.178
    
    print(f"📍 Location: Pouillac ({lat}, {lon})")
    print()
    
    try:
        print("📡 Testing Open-Meteo API...")
        forecast_data = fetch_openmeteo_forecast(lat, lon)
        
        print("✅ API call successful!")
        print()
        
        # Check timezone info
        location = forecast_data.get("location", {})
        print("🌍 Timezone Information:")
        print(f"   Timezone: {location.get('timezone', 'N/A')}")
        print(f"   Abbreviation: {location.get('timezone_abbreviation', 'N/A')}")
        print(f"   UTC Offset: {location.get('utc_offset_seconds', 'N/A')} seconds")
        print()
        
        # Check current data
        current = forecast_data.get("current", {})
        if current:
            print("🌤️ Current Weather:")
            print(f"   Time: {current.get('time', 'N/A')}")
            print(f"   Temperature: {current.get('temperature_2m', 'N/A')}°C")
            print(f"   Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h")
            print(f"   Precipitation: {current.get('precipitation', 'N/A')} mm")
            print()
        
        # Check hourly data
        hourly = forecast_data.get("hourly", {})
        if hourly and hourly.get("time"):
            times = hourly["time"]
            print(f"📅 Hourly Forecast (showing first 5 entries):")
            for i, time_str in enumerate(times[:5]):
                print(f"   {i+1}. {time_str}")
            print()
            
            # Test time parsing
            print("🔧 Testing time parsing:")
            for i, time_str in enumerate(times[:3]):
                try:
                    # Try different parsing approaches
                    dt1 = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    dt2 = datetime.fromisoformat(time_str)
                    print(f"   Entry {i+1}: {time_str}")
                    print(f"      Parsed (with Z): {dt1}")
                    print(f"      Parsed (without Z): {dt2}")
                except Exception as e:
                    print(f"   Entry {i+1}: {time_str} - ERROR: {e}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_target_timestamp_parsing():
    """Test parsing of target timestamps."""
    print("🕒 Testing Target Timestamp Parsing")
    print("=" * 40)
    
    # Test tomorrow 17:00 CEST
    tomorrow = datetime.now() + timedelta(days=1)
    target_time = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
    utc_time = target_time - timedelta(hours=2)  # Convert to UTC
    target_timestamp = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    print(f"Target time (CEST): {target_time}")
    print(f"Target time (UTC): {utc_time}")
    print(f"Target timestamp: {target_timestamp}")
    print()
    
    try:
        # Test parsing back
        parsed_dt = datetime.fromisoformat(target_timestamp.replace("Z", "+00:00"))
        print(f"Parsed back: {parsed_dt}")
        print("✅ Timestamp parsing works!")
    except Exception as e:
        print(f"❌ Timestamp parsing failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Open-Meteo Debug Session")
    print("=" * 60)
    print()
    
    # Test 1: Basic API functionality
    success = test_openmeteo_timezone()
    
    print()
    print("-" * 60)
    print()
    
    # Test 2: Timestamp parsing
    test_target_timestamp_parsing()
    
    print()
    print("🏁 Debug session completed!") 