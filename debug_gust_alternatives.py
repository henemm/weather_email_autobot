#!/usr/bin/env python3
"""
Debug script to check alternative API methods and field names for gust data.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌪️ DEBUG: Alternative Gust Data Sources")
    print("=" * 50)
    
    try:
        client = MeteoFranceClient()
        lat, lon = 47.6386, 6.8631
        
        print(f"📍 Testing coordinates: {lat}, {lon}")
        print()
        
        # Test different API methods
        print("🔍 Testing different API methods:")
        print("-" * 40)
        
        # 1. get_forecast
        print("1. get_forecast:")
        forecast = client.get_forecast(lat, lon)
        if hasattr(forecast, 'forecast') and forecast.forecast:
            first_entry = forecast.forecast[0]
            print(f"   Wind data: {first_entry.get('wind', {})}")
        
        # 2. get_daily_forecast
        print("\n2. get_daily_forecast:")
        try:
            daily_forecast = client.get_daily_forecast(lat, lon)
            if hasattr(daily_forecast, 'forecast') and daily_forecast.forecast:
                first_daily = daily_forecast.forecast[0]
                print(f"   Daily data: {first_daily}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 3. get_hourly_forecast
        print("\n3. get_hourly_forecast:")
        try:
            hourly_forecast = client.get_hourly_forecast(lat, lon)
            if hasattr(hourly_forecast, 'forecast') and hourly_forecast.forecast:
                first_hourly = hourly_forecast.forecast[0]
                print(f"   Hourly data: {first_hourly}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 4. Check for alternative field names in forecast
        print("\n4. Checking alternative field names:")
        if hasattr(forecast, 'forecast') and forecast.forecast:
            first_entry = forecast.forecast[0]
            print(f"   All keys: {list(first_entry.keys())}")
            
            # Check for wind-related fields
            wind_related = [key for key in first_entry.keys() if 'wind' in key.lower() or 'gust' in key.lower()]
            print(f"   Wind-related keys: {wind_related}")
            
            # Check nested wind data
            if 'wind' in first_entry:
                wind_data = first_entry['wind']
                print(f"   Wind data keys: {list(wind_data.keys())}")
                
                # Check for any non-zero values
                for key, value in wind_data.items():
                    if value != 0:
                        print(f"   Non-zero wind.{key}: {value}")
        
        # 5. Check if gust data is in a different format
        print("\n5. Checking for gust data in different format:")
        if hasattr(forecast, 'forecast') and forecast.forecast:
            # Check all entries for non-zero gust values
            tomorrow = date.today() + timedelta(days=1)
            gust_found = False
            
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    if entry_date == tomorrow:
                        wind_data = entry.get('wind', {})
                        gust_value = wind_data.get('gust', 0)
                        
                        if gust_value != 0:
                            gust_found = True
                            print(f"   Found non-zero gust: {gust_value} at {entry_time.strftime('%H:%M')}")
            
            if not gust_found:
                print("   No non-zero gust values found in any entry")
        
        print("\n🎯 CONCLUSION:")
        print("If the API consistently returns 0 for gust data:")
        print("1. This might be normal for this location/time")
        print("2. Gust data might require a different API endpoint")
        print("3. Gust data might be calculated from other wind parameters")
        print("4. The API might not provide gust data for this region")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 