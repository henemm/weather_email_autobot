#!/usr/bin/env python3
"""
Debug script to test Belfort coordinates and find the 55 km/h gust data.
"""

import yaml
from meteofrance_api import MeteoFranceClient
from src.wetter.fetch_meteofrance import get_thunderstorm, get_forecast
from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast
import json
from datetime import datetime, date, timedelta

def main():
    print("🔍 DEBUG: Belfort Coordinates Analysis - TOMORROW")
    print("=" * 60)
    
    # Belfort coordinates (approximate)
    # Belfort is located in eastern France, near the Swiss border
    belfort_lat, belfort_lon = 47.6386, 6.8631  # Approximate coordinates for Belfort
    
    print(f"📍 Testing Belfort coordinates: {belfort_lat}, {belfort_lon}")
    print("🎯 FOCUSING ON TOMORROW (2025-08-02) - THUNDERSTORMS FORECASTED")
    print()
    
    try:
        client = MeteoFranceClient()
        
        # Method 1: Get forecast for Belfort
        print("🔍 METHOD 1: Belfort Forecast - TOMORROW DETAILED")
        print("-" * 40)
        
        forecast = client.get_forecast(belfort_lat, belfort_lon)
        
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print(f"📅 Total forecast entries: {len(forecast.forecast)}")
            
            # Focus on tomorrow (2025-08-02)
            tomorrow = date.today() + timedelta(days=1)
            print(f"📅 Analyzing data for: {tomorrow}")
            print()
            
            max_gust = 0
            max_gust_time = None
            max_wind = 0
            max_wind_time = None
            
            print("📊 Hourly data for tomorrow:")
            print("Time | Wind Speed | Wind Gusts | Weather | Description")
            print("-" * 60)
            
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    if entry_date == tomorrow:
                        time_str = entry_time.strftime('%H:%M')
                        wind_data = entry.get('wind', {})
                        wind_speed = wind_data.get('speed', 0)
                        wind_gust = wind_data.get('gust', 0)
                        weather_data = entry.get('weather', {})
                        weather_desc = weather_data.get('desc', 'Unknown')
                        
                        print(f"{time_str} | {wind_speed:8.1f} | {wind_gust:10.1f} | {weather_desc}")
                        
                        if wind_gust > max_gust:
                            max_gust = wind_gust
                            max_gust_time = time_str
                        
                        if wind_speed > max_wind:
                            max_wind = wind_speed
                            max_wind_time = time_str
            
            print("-" * 60)
            print(f"🎯 Max wind: {max_wind} km/h at {max_wind_time}")
            print(f"🎯 Max gust: {max_gust} km/h at {max_gust_time}")
            
            # Check if we found the 55 km/h gust
            if max_gust >= 50:
                print(f"🚨 FOUND HIGH GUST: {max_gust} km/h at {max_gust_time}")
            else:
                print(f"❌ No high gusts found (max: {max_gust} km/h)")
        
        print("\n" + "=" * 60)
        
        # Method 2: Test Open-Meteo API for Belfort
        print("🔍 METHOD 2: Open-Meteo API for Belfort")
        print("-" * 40)
        
        try:
            openmeteo_data = fetch_openmeteo_forecast(belfort_lat, belfort_lon)
            
            if 'hourly' in openmeteo_data:
                hourly = openmeteo_data['hourly']
                times = hourly.get('time', [])
                wind_gusts = hourly.get('wind_gusts_10m', [])
                wind_speeds = hourly.get('wind_speed_10m', [])
                
                print(f"📅 Open-Meteo entries: {len(times)}")
                
                # Focus on tomorrow
                tomorrow = date.today() + timedelta(days=1)
                print(f"📅 Analyzing Open-Meteo data for: {tomorrow}")
                print()
                
                max_gust = 0
                max_gust_time = None
                max_wind = 0
                max_wind_time = None
                
                print("📊 Open-Meteo hourly data for tomorrow:")
                print("Time | Wind Speed | Wind Gusts")
                print("-" * 40)
                
                for i, time_str in enumerate(times):
                    if i < len(wind_gusts) and i < len(wind_speeds):
                        entry_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        if entry_time.date() == tomorrow:
                            gust = wind_gusts[i]
                            wind = wind_speeds[i]
                            
                            print(f"{entry_time.strftime('%H:%M')} | {wind:8.1f} | {gust:10.1f}")
                            
                            if gust > max_gust:
                                max_gust = gust
                                max_gust_time = entry_time.strftime('%H:%M')
                            
                            if wind > max_wind:
                                max_wind = wind
                                max_wind_time = entry_time.strftime('%H:%M')
                
                print("-" * 40)
                print(f"🎯 Max wind: {max_wind:.1f} km/h at {max_wind_time}")
                print(f"🎯 Max gust: {max_gust:.1f} km/h at {max_gust_time}")
                
                # Check if we found the 55 km/h gust
                if max_gust >= 50:
                    print(f"🚨 FOUND HIGH GUST: {max_gust:.1f} km/h at {max_gust_time}")
                else:
                    print(f"❌ No high gusts found (max: {max_gust:.1f} km/h)")
            
        except Exception as e:
            print(f"Open-Meteo API error: {e}")
        
        print("\n" + "=" * 60)
        
        # Method 3: Test thunderstorm-specific functions
        print("🔍 METHOD 3: Test Thunderstorm Functions")
        print("-" * 40)
        
        try:
            print("Testing get_thunderstorm function...")
            thunderstorm_result = get_thunderstorm(belfort_lat, belfort_lon)
            print(f"Thunderstorm result: {thunderstorm_result}")
        except Exception as e:
            print(f"Thunderstorm function error: {e}")
        
        try:
            print("\nTesting get_forecast function...")
            forecast_result = get_forecast(belfort_lat, belfort_lon)
            print(f"Forecast result: {forecast_result}")
        except Exception as e:
            print(f"Forecast function error: {e}")
        
        print("\n" + "=" * 60)
        print("🔍 SUMMARY:")
        print("The image shows Belfort (90000) with 55 km/h gusts.")
        print("Tomorrow has thunderstorms forecasted, which should cause higher gusts.")
        print()
        print("Comparing data sources:")
        print("1. MeteoFrance API: Direct access")
        print("2. Open-Meteo API: Alternative source")
        print("3. Thunderstorm functions: Specialized functions")
        print()
        print("If we don't find 55 km/h gusts:")
        print("1. The image might show a different time of day")
        print("2. The image might use a different forecast model")
        print("3. The image might show historical data")
        print("4. The image might show simulated/example data")
        print("5. The image might use a different API endpoint")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 