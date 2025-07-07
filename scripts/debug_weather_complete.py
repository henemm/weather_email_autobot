#!/usr/bin/env python3
"""
Get comprehensive weather data for GR20 locations including all parameters in TIMESTAMP-DEBUG format (CEST).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from meteofrance_api.client import MeteoFranceClient
from datetime import datetime
import pytz

def get_complete_weather_data():
    """Get complete weather data for GR20 locations in TIMESTAMP-DEBUG format (CEST)."""
    
    locations = [
        (41.79418, 9.259567, 'Conca'),
        (42.533, 8.933, 'Calanzana'),
        (42.119, 9.133, 'Vizzavona'),
        (41.783, 9.217, 'Bavella'),
    ]
    
    print("Complete Weather Data for GR20 Locations (2025-07-07, CEST)")
    print("=" * 120)
    
    client = MeteoFranceClient()
    cest = pytz.timezone('Europe/Paris')
    today_cest = datetime.now(cest).date()
    
    for lat, lon, name in locations:
        print(f"\n{name} ({lat:.3f}, {lon:.3f}):")
        print("-" * 120)
        
        try:
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'forecast') and forecast.forecast:
                entries = forecast.forecast
                today_entries = []
                for entry in entries:
                    dt = entry.get('dt')
                    if dt:
                        utc_dt = datetime.fromtimestamp(dt, pytz.UTC)
                        cest_dt = utc_dt.astimezone(cest)
                        entry_date_cest = cest_dt.date()
                        if entry_date_cest == today_cest:
                            today_entries.append((cest_dt, entry))
                if today_entries:
                    today_entries.sort(key=lambda x: x[0])
                    for cest_dt, entry in today_entries:
                        time_str = cest_dt.strftime('%Y-%m-%d %H:%M:%S')
                        temp = entry.get('T', {}).get('value')
                        rain_prob = entry.get('precipitation_probability')
                        rain_amount = entry.get('rain', {}).get('1h') if isinstance(entry.get('rain'), dict) else None
                        wind_speed = entry.get('wind', {}).get('speed')
                        wind_gusts = entry.get('wind', {}).get('gust')
                        thunder_prob = entry.get('thunderstorm_probability')
                        # Format values
                        temp_str = f"{temp:.1f}°C" if isinstance(temp, (int, float)) else "-"
                        rain_prob_str = f"{rain_prob}%" if isinstance(rain_prob, (int, float)) else "-"
                        rain_amount_str = f"{rain_amount:.1f}mm" if isinstance(rain_amount, (int, float)) else "-"
                        wind_speed_str = f"{int(round(wind_speed))}km/h" if isinstance(wind_speed, (int, float)) else "-"
                        wind_gusts_str = f"{int(round(wind_gusts))}km/h" if isinstance(wind_gusts, (int, float)) else "-"
                        thunder_prob_str = f"{thunder_prob}%" if isinstance(thunder_prob, (int, float)) else "-"
                        print(f"[TIMESTAMP-DEBUG] {name} | {time_str} (CEST) | Temp: {temp_str} | RainW: {rain_prob_str} | Rain: {rain_amount_str} | Wind: {wind_speed_str} | Gusts: {wind_gusts_str} | Thunder: {thunder_prob_str}")
                else:
                    print("No data for today (CEST)")
            else:
                print("No forecast data available")
        except Exception as e:
            print(f"Error: {e}")

def check_timezone_info():
    """Check what timezone the meteofrance-api returns."""
    print("\nTimezone Information Check:")
    print("=" * 50)
    client = MeteoFranceClient()
    forecast = client.get_forecast(41.79418, 9.259567)  # Conca
    if hasattr(forecast, 'forecast') and forecast.forecast:
        first_entry = forecast.forecast[0]
        dt = first_entry.get('dt')
        if dt:
            utc_time = datetime.fromtimestamp(dt, pytz.UTC)
            cest_time = utc_time.astimezone(pytz.timezone('Europe/Paris'))
            print(f"UTC time: {utc_time}")
            print(f"CEST time: {cest_time}")
            print(f"Difference: {cest_time.hour - utc_time.hour} hours")
            print("Note: meteofrance-api returns UTC timestamps")

if __name__ == "__main__":
    check_timezone_info()
    get_complete_weather_data() 