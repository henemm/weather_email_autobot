#!/usr/bin/env python3
"""
Get raw maximum temperatures for specific GR20 locations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from meteofrance_api.client import MeteoFranceClient
from datetime import datetime

def get_temperatures_for_locations():
    """Get temperatures for specific GR20 locations."""
    
    # GR20 locations with coordinates
    locations = [
        (41.79418, 9.259567, 'Conca'),
        (42.533, 8.933, 'Calanzana'),
        (42.119, 9.133, 'Vizzavona'),
        (41.783, 9.217, 'Bavella'),
    ]
    
    print("Raw Maximum Temperatures for GR20 Locations")
    print("=" * 60)
    print(f"{'Location':<12} | {'Max Temp (°C)':<12} | {'Time':<10} | {'Coordinates':<20}")
    print("-" * 60)
    
    client = MeteoFranceClient()
    
    for lat, lon, name in locations:
        try:
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'forecast') and forecast.forecast:
                entries = forecast.forecast
                
                # Find maximum temperature for today (2025-07-07)
                max_temp = -999
                max_temp_time = ""
                today = datetime.now().date()
                
                for entry in entries:
                    dt = entry.get('dt')
                    if dt:
                        entry_datetime = datetime.fromtimestamp(dt)
                        entry_date = entry_datetime.date()
                        
                        # Only process today's data
                        if entry_date == today:
                            temp = entry.get('T', {}).get('value')
                            if temp is not None and temp > max_temp:
                                max_temp = temp
                                max_temp_time = entry_datetime.strftime('%H:%M')
                
                if max_temp > -999:
                    print(f"{name:<12} | {max_temp:<12.1f} | {max_temp_time:<10} | {lat:.3f}, {lon:.3f}")
                else:
                    print(f"{name:<12} | {'No data':<12} | {'':<10} | {lat:.3f}, {lon:.3f}")
            else:
                print(f"{name:<12} | {'No forecast':<12} | {'':<10} | {lat:.3f}, {lon:.3f}")
                
        except Exception as e:
            print(f"{name:<12} | {'Error':<12} | {'':<10} | {lat:.3f}, {lon:.3f} ({e})")

if __name__ == "__main__":
    get_temperatures_for_locations() 