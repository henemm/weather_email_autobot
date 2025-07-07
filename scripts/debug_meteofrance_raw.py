#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from meteofrance_api.client import MeteoFranceClient
from datetime import datetime

locations = [
    (42.426238, 8.900291, 'Ascu (original)'),
    (42.426238, 8.901, 'Ascu (lon+0.001)'),
    (42.427, 8.900291, 'Ascu (lat+0.001)'),
    (42.426238, 8.905, 'Ascu (lon+0.005)'),
    (42.430, 8.900291, 'Ascu (lat+0.004)'),
    (42.307, 9.150, 'Corte'),
    (48.8566, 2.3522, 'Paris'),
]

for lat, lon, name in locations:
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        entries = getattr(forecast, 'forecast', [])
        print(f"\n{name} (lat={lat}, lon={lon}): {len(entries)} forecast entries")
        if entries:
            print(f"{'UTC':<20} | {'Local':<20} | {'Temp (°C)':<10}")
            print("-"*60)
            for entry in entries[:6]:
                dt = entry.get('dt')
                if dt:
                    dt_utc = datetime.utcfromtimestamp(dt)
                    dt_local = datetime.fromtimestamp(dt)
                    temp = entry.get('T', {}).get('value')
                    print(f"{dt_utc.strftime('%Y-%m-%d %H:%M'):<20} | {dt_local.strftime('%Y-%m-%d %H:%M'):<20} | {str(temp):<10}")
        else:
            print("No forecast data returned.")
    except Exception as e:
        print(f"{name} (lat={lat}, lon={lon}): Exception: {e}") 