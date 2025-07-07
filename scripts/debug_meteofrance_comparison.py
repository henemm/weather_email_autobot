#!/usr/bin/env python3
"""
Compare direct meteofrance-api library calls with custom fetch_meteofrance.py function
to identify where data is being lost.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from meteofrance_api.client import MeteoFranceClient
from src.wetter.fetch_meteofrance import get_forecast
from datetime import datetime

def compare_library_vs_custom():
    """Compare direct library calls with custom function."""
    
    lat, lon = 42.426238, 8.900291  # Ascu
    
    print(f"Comparing meteofrance-api library vs custom function for Ascu (lat={lat}, lon={lon})")
    print("=" * 80)
    
    # Test 1: Direct library call
    print("\n1. DIRECT LIBRARY CALL:")
    print("-" * 40)
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        if hasattr(forecast, 'forecast'):
            entries = forecast.forecast
            print(f"✓ Success: {len(entries)} forecast entries")
            
            if entries:
                print("First 3 entries:")
                for i, entry in enumerate(entries[:3]):
                    dt = entry.get('dt')
                    if dt:
                        dt_str = datetime.fromtimestamp(dt).strftime('%Y-%m-%d %H:%M')
                    else:
                        dt_str = "No timestamp"
                    
                    temp = entry.get('T', {}).get('value', 'N/A') if isinstance(entry.get('T'), dict) else 'N/A'
                    print(f"  {i+1}. {dt_str} | Temp: {temp}°C")
                    
                    # Show full structure of first entry
                    if i == 0:
                        print(f"     Full entry structure: {list(entry.keys())}")
                        print(f"     T field: {entry.get('T')}")
        else:
            print(f"✗ No 'forecast' attribute found")
            print(f"Response type: {type(forecast)}")
            print(f"Response attributes: {dir(forecast)}")
            
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
    
    # Test 2: Custom function call
    print("\n2. CUSTOM FUNCTION CALL:")
    print("-" * 40)
    try:
        result = get_forecast(lat, lon)
        print(f"✓ Success: {result}")
        print(f"  Temperature: {result.temperature}°C")
        print(f"  Data source: {result.data_source}")
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_library_vs_custom() 