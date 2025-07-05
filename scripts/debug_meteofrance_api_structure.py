#!/usr/bin/env python3
"""
Debug script to examine the actual structure of Météo-France API responses.
This helps understand why precipitation amounts are not available.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meteofrance_api.client import MeteoFranceClient


def debug_api_structure():
    """Debug the actual API response structure."""
    
    # Test coordinates (Asco)
    latitude = 42.4542
    longitude = 8.7389
    
    print(f"Debugging Météo-France API structure for Asco ({latitude}, {longitude})")
    print("=" * 60)
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(latitude, longitude)
        
        if not forecast.forecast:
            print("❌ No forecast data received")
            return
        
        print(f"✅ Received {len(forecast.forecast)} forecast entries")
        print()
        
        # Examine first few entries in detail
        for i, entry in enumerate(forecast.forecast[:3]):
            print(f"Entry {i+1}:")
            print(f"  Timestamp: {entry.get('dt')} -> {datetime.fromtimestamp(entry['dt'])}")
            print(f"  Raw entry: {json.dumps(entry, indent=2, default=str)}")
            print()
            
            # Check precipitation structure
            precipitation = entry.get('precipitation')
            print(f"  Precipitation field: {precipitation}")
            if isinstance(precipitation, dict):
                print(f"  Precipitation keys: {list(precipitation.keys())}")
                for key, value in precipitation.items():
                    print(f"    {key}: {value}")
            print()
            
            # Check weather structure
            weather = entry.get('weather')
            print(f"  Weather field: {weather}")
            if isinstance(weather, dict):
                print(f"  Weather keys: {list(weather.keys())}")
                for key, value in weather.items():
                    print(f"    {key}: {value}")
            print()
            
            # Check temperature structure
            temp = entry.get('T')
            print(f"  Temperature field: {temp}")
            if isinstance(temp, dict):
                print(f"  Temperature keys: {list(temp.keys())}")
                for key, value in temp.items():
                    print(f"    {key}: {value}")
            print()
            
            # Check wind structure
            wind = entry.get('wind')
            print(f"  Wind field: {wind}")
            if isinstance(wind, dict):
                print(f"  Wind keys: {list(wind.keys())}")
                for key, value in wind.items():
                    print(f"    {key}: {value}")
            print("-" * 40)
        
        # Check if there are any entries with precipitation data
        entries_with_precip = []
        for i, entry in enumerate(forecast.forecast):
            precipitation = entry.get('precipitation')
            if precipitation and isinstance(precipitation, dict):
                for key, value in precipitation.items():
                    if value is not None and value != 0:
                        entries_with_precip.append((i, key, value))
        
        print(f"Entries with precipitation data: {len(entries_with_precip)}")
        for idx, key, value in entries_with_precip[:5]:  # Show first 5
            timestamp = datetime.fromtimestamp(forecast.forecast[idx]['dt'])
            print(f"  Entry {idx} @ {timestamp}: {key} = {value}")
        
        if not entries_with_precip:
            print("  ❌ No precipitation data found in any entries")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_api_structure() 