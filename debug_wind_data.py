#!/usr/bin/env python3
"""
Debug script to check wind data availability in the API response.
"""

import yaml
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
import json

def main():
    print("🔍 DEBUG: Wind Data Availability")
    print("=" * 50)
    
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize API
    api = EnhancedMeteoFranceAPI()
    
    # Test coordinates (first point from etappen.json)
    import json
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
        # Fetch data
        print("📡 Fetching data from API...")
        data = api.get_complete_forecast_data(lat, lon, "test_point")
        
        print("✅ Data fetched successfully!")
        print()
        
        # Check daily data
        daily_data = data.get('daily_data', [])
        print(f"📅 Daily data entries: {len(daily_data)}")
        
        if daily_data:
            print("\n📊 First daily entry structure:")
            first_daily = daily_data[0]
            print(json.dumps(first_daily, indent=2, default=str))
            
            # Check if wind data exists
            wind_data = first_daily.get('wind', {})
            print(f"\n💨 Wind data available: {bool(wind_data)}")
            if wind_data:
                print(f"   Speed: {wind_data.get('speed')}")
                print(f"   Gusts: {wind_data.get('gusts')}")
                print(f"   Direction: {wind_data.get('direction')}")
            else:
                print("   ❌ No wind data found in daily_data")
        
        # Check hourly data for wind
        hourly_data = data.get('hourly_data', [])
        print(f"\n⏰ Hourly data entries: {len(hourly_data)}")
        
        if hourly_data:
            print("\n📊 First hourly entry wind data:")
            first_hourly = hourly_data[0]
            print(f"   Wind Speed: {getattr(first_hourly, 'wind_speed', 'N/A')}")
            print(f"   Wind Gusts: {getattr(first_hourly, 'wind_gusts', 'N/A')}")
            print(f"   Wind Direction: {getattr(first_hourly, 'wind_direction', 'N/A')}")
        
        # Check raw API response
        print("\n🔍 Checking raw API response...")
        from meteofrance_api import MeteoFranceClient
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
            print(f"📅 Raw daily forecast entries: {len(forecast.daily_forecast)}")
            if forecast.daily_forecast:
                first_raw_daily = forecast.daily_forecast[0]
                print("\n📊 Raw first daily entry:")
                print(json.dumps(first_raw_daily, indent=2, default=str))
                
                # Check for wind data in raw response
                wind_raw = first_raw_daily.get('wind', {})
                print(f"\n💨 Raw wind data available: {bool(wind_raw)}")
                if wind_raw:
                    print(f"   Raw wind data: {wind_raw}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 