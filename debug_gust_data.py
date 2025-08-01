#!/usr/bin/env python3
"""
Debug script to check gust data availability and values in the API response.
"""

import yaml
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast
import json
from datetime import datetime, date, timedelta
from meteofrance_api import MeteoFranceClient

def main():
    print("🔍 DEBUG: Gust Data Analysis - Multiple Sources")
    print("=" * 60)
    
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Test coordinates (first point from etappen.json)
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    # Get first stage, first point
    first_stage = etappen_data[0]
    first_point = first_stage['punkte'][0]
    lat, lon = first_point['lat'], first_point['lon']
    
    print(f"📍 Testing coordinates: {lat}, {lon}")
    print(f"🏔️  Stage: {first_stage['name']}")
    print()
    
    try:
        # Method 1: Direct MeteoFrance API
        print("🔍 METHOD 1: Direct MeteoFrance API")
        print("-" * 40)
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print(f"📅 Raw forecast entries: {len(forecast.forecast)}")
            
            # Check next 3 days for high gust values
            for day_offset in range(3):
                check_date = date.today() + timedelta(days=day_offset)
                print(f"\n📅 {check_date}:")
                
                max_gust = 0
                max_gust_time = None
                
                for entry in forecast.forecast:
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        if entry_time.date() == check_date:
                            wind_data = entry.get('wind', {})
                            raw_gust = wind_data.get('gust', 0)
                            
                            if raw_gust > max_gust:
                                max_gust = raw_gust
                                max_gust_time = entry_time.strftime('%H:%M')
                
                print(f"   Max gust: {max_gust} km/h at {max_gust_time}")
                
                # Show all gust values for this day
                print("   Hourly gusts:")
                for entry in forecast.forecast:
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        if entry_time.date() == check_date:
                            wind_data = entry.get('wind', {})
                            raw_gust = wind_data.get('gust', 0)
                            if raw_gust > 0:
                                print(f"     {entry_time.strftime('%H:%M')}: {raw_gust} km/h")
        
        print("\n" + "=" * 60)
        
        # Method 2: Enhanced API (our wrapper)
        print("🔍 METHOD 2: Enhanced API (our wrapper)")
        print("-" * 40)
        api = EnhancedMeteoFranceAPI()
        data = api.get_complete_forecast_data(lat, lon, "test_point")
        
        hourly_data = data.get('hourly_data', [])
        print(f"📅 Enhanced API entries: {len(hourly_data)}")
        
        for day_offset in range(3):
            check_date = date.today() + timedelta(days=day_offset)
            print(f"\n📅 {check_date}:")
            
            max_gust = 0
            max_gust_time = None
            
            for entry in hourly_data:
                if hasattr(entry, 'timestamp'):
                    entry_date = entry.timestamp.date()
                    if entry_date == check_date:
                        wind_gusts = getattr(entry, 'wind_gusts', 0)
                        
                        if wind_gusts > max_gust:
                            max_gust = wind_gusts
                            max_gust_time = entry.timestamp.strftime('%H:%M')
            
            print(f"   Max gust: {max_gust} km/h at {max_gust_time}")
            
            # Show all gust values for this day
            print("   Hourly gusts:")
            for entry in hourly_data:
                if hasattr(entry, 'timestamp'):
                    entry_date = entry.timestamp.date()
                    if entry_date == check_date:
                        wind_gusts = getattr(entry, 'wind_gusts', 0)
                        if wind_gusts > 0:
                            print(f"     {entry.timestamp.strftime('%H:%M')}: {wind_gusts} km/h")
        
        print("\n" + "=" * 60)
        
        # Method 3: Open-Meteo API
        print("🔍 METHOD 3: Open-Meteo API")
        print("-" * 40)
        
        try:
            openmeteo_data = fetch_openmeteo_forecast(lat, lon)
            
            if 'hourly' in openmeteo_data:
                hourly = openmeteo_data['hourly']
                times = hourly.get('time', [])
                wind_gusts = hourly.get('wind_gusts_10m', [])
                wind_speeds = hourly.get('wind_speed_10m', [])
                
                print(f"📅 Open-Meteo entries: {len(times)}")
                
                # Check next 3 days
                for day_offset in range(3):
                    check_date = date.today() + timedelta(days=day_offset)
                    print(f"\n📅 {check_date}:")
                    
                    max_gust = 0
                    max_gust_time = None
                    max_wind = 0
                    max_wind_time = None
                    
                    print("   Hourly data:")
                    for i, time_str in enumerate(times):
                        if i < len(wind_gusts) and i < len(wind_speeds):
                            entry_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                            if entry_time.date() == check_date:
                                gust = wind_gusts[i]
                                wind = wind_speeds[i]
                                
                                print(f"     {entry_time.strftime('%H:%M')}: Wind={wind:.1f} km/h, Gust={gust:.1f} km/h")
                                
                                if gust > max_gust:
                                    max_gust = gust
                                    max_gust_time = entry_time.strftime('%H:%M')
                                
                                if wind > max_wind:
                                    max_wind = wind
                                    max_wind_time = entry_time.strftime('%H:%M')
                    
                    print(f"   Max wind: {max_wind:.1f} km/h at {max_wind_time}")
                    print(f"   Max gust: {max_gust:.1f} km/h at {max_gust_time}")
                    
                    # Check if we found the 55 km/h gust
                    if max_gust >= 50:
                        print(f"🚨 FOUND HIGH GUST: {max_gust:.1f} km/h at {max_gust_time}")
            
        except Exception as e:
            print(f"Open-Meteo API error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("🔍 SUMMARY:")
        print("Comparing all three data sources:")
        print("1. MeteoFrance API: Direct access")
        print("2. Enhanced API: Our wrapper")
        print("3. Open-Meteo API: Alternative source")
        print()
        print("If the image shows 55 km/h, it might be from:")
        print("- Open-Meteo API (different model)")
        print("- A different timezone/date")
        print("- A different location")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 