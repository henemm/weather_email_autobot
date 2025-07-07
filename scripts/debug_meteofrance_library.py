#!/usr/bin/env python3
"""
Direct test of the meteofrance-api library without any custom code.
This will help determine if the problem is with the library itself or with our custom code.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from meteofrance_api.client import MeteoFranceClient
from datetime import datetime

def test_meteofrance_library():
    """Test the meteofrance-api library directly."""
    
    # Test coordinates (same as in debug_meteofrance_raw.py)
    test_locations = [
        (42.426238, 8.900291, 'Ascu (original)'),
        (42.307, 9.150, 'Corte'),
        (48.8566, 2.3522, 'Paris'),
    ]
    
    print("Testing meteofrance-api library directly...")
    print("=" * 60)
    
    client = MeteoFranceClient()
    
    for lat, lon, name in test_locations:
        print(f"\n{name} (lat={lat}, lon={lon}):")
        print("-" * 40)
        
        try:
            # Test 1: Basic forecast
            print("1. Testing client.get_forecast()...")
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'forecast'):
                entries = forecast.forecast
                print(f"   ✓ Success: {len(entries)} forecast entries")
                
                if entries:
                    # Show first few entries
                    print("   First 3 entries:")
                    for i, entry in enumerate(entries[:3]):
                        dt = entry.get('dt')
                        if dt:
                            dt_str = datetime.fromtimestamp(dt).strftime('%Y-%m-%d %H:%M')
                        else:
                            dt_str = "No timestamp"
                        
                        temp = entry.get('T', {}).get('value', 'N/A') if isinstance(entry.get('T'), dict) else 'N/A'
                        print(f"     {i+1}. {dt_str} | Temp: {temp}°C")
                else:
                    print("   ⚠ No forecast entries in response")
            else:
                print(f"   ⚠ No 'forecast' attribute found in response")
                print(f"   Response type: {type(forecast)}")
                print(f"   Response attributes: {dir(forecast)}")
                
        except Exception as e:
            print(f"   ✗ Error: {type(e).__name__}: {e}")
        
        try:
            # Test 2: Place information
            print("2. Testing client.get_place()...")
            place = client.get_place(lat, lon)
            print(f"   ✓ Success: {place.name if hasattr(place, 'name') else 'Place found'}")
            
        except Exception as e:
            print(f"   ✗ Error: {type(e).__name__}: {e}")
        
        try:
            # Test 3: Current weather
            print("3. Testing client.get_current_weather()...")
            current = client.get_current_weather(lat, lon)
            print(f"   ✓ Success: Current weather retrieved")
            
        except Exception as e:
            print(f"   ✗ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_meteofrance_library() 