#!/usr/bin/env python3
"""
Debug script to test alternative API methods for gust data.
The meteofrance-api library seems incomplete, so I need to find the right method.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌪️ DEBUG: Alternative API Methods for Gust Data")
    print("=" * 60)
    
    try:
        client = MeteoFranceClient()
        belfort_lat, belfort_lon = 47.6386, 6.8631
        
        print(f"📍 Belfort coordinates: {belfort_lat}, {belfort_lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Test get_forecast_for_place method
        print("1. Testing get_forecast_for_place:")
        print("-" * 40)
        try:
            place_forecast = client.get_forecast_for_place("Belfort")
            print(f"   ✅ Place forecast type: {type(place_forecast)}")
            
            if hasattr(place_forecast, 'forecast') and place_forecast.forecast:
                print(f"   📅 Place forecast entries: {len(place_forecast.forecast)}")
                
                # Check tomorrow's data
                tomorrow = date.today() + timedelta(days=1)
                tomorrow_entries = []
                
                for entry in place_forecast.forecast:
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        entry_date = entry_time.date()
                        if entry_date == tomorrow:
                            tomorrow_entries.append(entry)
                
                print(f"   📅 Tomorrow entries: {len(tomorrow_entries)}")
                
                if tomorrow_entries:
                    first_tomorrow = tomorrow_entries[0]
                    if 'wind' in first_tomorrow:
                        wind_data = first_tomorrow['wind']
                        print(f"   🌪️ Wind data: {wind_data}")
                        
                        # Check for non-zero gusts
                        gust_values = []
                        for entry in tomorrow_entries:
                            wind = entry.get('wind', {})
                            gust = wind.get('gust', 0)
                            if gust > 0:
                                time = datetime.fromtimestamp(entry['dt'])
                                gust_values.append(f"{time.strftime('%H:%M')}: {gust} km/h")
                        
                        if gust_values:
                            print(f"   ✅ Found non-zero gusts: {gust_values}")
                        else:
                            print(f"   ❌ All gusts are still 0")
            else:
                print(f"   ❌ No forecast data in place forecast")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test get_observation method
        print("\n2. Testing get_observation:")
        print("-" * 40)
        try:
            observation = client.get_observation(belfort_lat, belfort_lon)
            print(f"   ✅ Observation type: {type(observation)}")
            
            if hasattr(observation, '__dict__'):
                print(f"   📊 Observation attributes: {list(observation.__dict__.keys())}")
                
                # Check if observation has wind data
                if hasattr(observation, 'raw_data'):
                    print(f"   🔍 Raw observation data: {observation.raw_data}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test get_observation_for_place method
        print("\n3. Testing get_observation_for_place:")
        print("-" * 40)
        try:
            place_observation = client.get_observation_for_place("Belfort")
            print(f"   ✅ Place observation type: {type(place_observation)}")
            
            if hasattr(place_observation, '__dict__'):
                print(f"   📊 Place observation attributes: {list(place_observation.__dict__.keys())}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test search_places to find correct place name
        print("\n4. Testing search_places:")
        print("-" * 40)
        try:
            places = client.search_places("Belfort")
            print(f"   ✅ Found places: {len(places)}")
            
            for i, place in enumerate(places[:3]):  # Show first 3
                print(f"   📍 Place {i+1}: {place}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Check if the issue is with the coordinates
        print("\n5. Testing different coordinates:")
        print("-" * 40)
        
        # Try coordinates from the website
        test_coordinates = [
            (47.6386, 6.8631),  # Current
            (47.6386, 6.8631),  # Same but different precision
            (47.64, 6.86),      # Rounded
        ]
        
        for i, (lat, lon) in enumerate(test_coordinates):
            print(f"   Testing coordinates {i+1}: {lat}, {lon}")
            try:
                test_forecast = client.get_forecast(lat, lon)
                if hasattr(test_forecast, 'forecast') and test_forecast.forecast:
                    # Check first entry for gust
                    first_entry = test_forecast.forecast[0]
                    wind_data = first_entry.get('wind', {})
                    gust = wind_data.get('gust', 0)
                    print(f"      Gust value: {gust}")
                    
                    if gust > 0:
                        print(f"      ✅ Found non-zero gust!")
                        break
                else:
                    print(f"      ❌ No forecast data")
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        print("\n🎯 CONCLUSION:")
        print("The meteofrance-api library seems to have incomplete gust data.")
        print("Possible solutions:")
        print("1. Use a different API endpoint")
        print("2. Use direct HTTP requests to MeteoFrance API")
        print("3. Use a different weather API library")
        print("4. Calculate gust from wind speed using a formula")
        print("5. The gust data might be in a different field or format")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 