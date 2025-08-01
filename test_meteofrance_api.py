#!/usr/bin/env python3
"""
Test script to explore meteofrance-api get_forecast() function.
This will help us understand the data structure and available fields.
"""

import sys
import json
from datetime import datetime
from meteofrance_api.client import MeteoFranceClient

def test_get_forecast():
    """Test get_forecast() with a known coordinate (Conca, Corsica)."""
    
    # Test coordinate: Conca, Corsica (from etappen.json)
    lat = 41.79418
    lon = 9.259567
    
    print(f"Testing meteofrance-api get_forecast() for coordinates: {lat}, {lon}")
    print("=" * 60)
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        print(f"Forecast object type: {type(forecast)}")
        print(f"Forecast has forecast attribute: {hasattr(forecast, 'forecast')}")
        print(f"Forecast entries count: {len(forecast.forecast) if hasattr(forecast, 'forecast') else 'N/A'}")
        
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print("\nFirst forecast entry structure:")
            first_entry = forecast.forecast[0]
            print(f"Entry type: {type(first_entry)}")
            print(f"Entry keys: {list(first_entry.keys()) if isinstance(first_entry, dict) else 'Not a dict'}")
            
            if isinstance(first_entry, dict):
                print("\nDetailed first entry:")
                for key, value in first_entry.items():
                    print(f"  {key}: {type(value)} = {value}")
                
                # Check for specific fields we need
                print("\nChecking for specific fields:")
                
                # Temperature
                if 'T' in first_entry:
                    temp_data = first_entry['T']
                    print(f"  Temperature data: {temp_data}")
                    if isinstance(temp_data, dict) and 'value' in temp_data:
                        print(f"  Temperature value: {temp_data['value']}°C")
                
                # Wind
                if 'wind' in first_entry:
                    wind_data = first_entry['wind']
                    print(f"  Wind data: {wind_data}")
                
                # Rain
                if 'rain' in first_entry:
                    rain_data = first_entry['rain']
                    print(f"  Rain data: {rain_data}")
                
                # Weather
                if 'weather' in first_entry:
                    weather_data = first_entry['weather']
                    print(f"  Weather data: {weather_data}")
                
                # Precipitation probability
                if 'precipitation_probability' in first_entry:
                    print(f"  Precipitation probability: {first_entry['precipitation_probability']}%")
                
                # Datetime
                if 'dt' in first_entry:
                    dt_timestamp = first_entry['dt']
                    dt_datetime = datetime.fromtimestamp(dt_timestamp)
                    print(f"  Datetime: {dt_timestamp} -> {dt_datetime}")
                
                # CAPE (for thunderstorm analysis)
                if 'cape' in first_entry:
                    print(f"  CAPE: {first_entry['cape']}")
            
            # Analyze multiple entries to understand time range and data patterns
            print("\n" + "=" * 60)
            print("Analyzing multiple entries:")
            
            # Show first 5 entries with datetime
            print("\nFirst 5 entries:")
            for i, entry in enumerate(forecast.forecast[:5]):
                if 'dt' in entry:
                    dt_timestamp = entry['dt']
                    dt_datetime = datetime.fromtimestamp(dt_timestamp)
                    temp_value = entry.get('T', {}).get('value', 'N/A')
                    weather_desc = entry.get('weather', {}).get('desc', 'N/A')
                    rain_1h = entry.get('rain', {}).get('1h', 'N/A')
                    wind_speed = entry.get('wind', {}).get('speed', 'N/A')
                    
                    print(f"  Entry {i+1}: {dt_datetime} - Temp: {temp_value}°C, Weather: {weather_desc}, Rain: {rain_1h}mm, Wind: {wind_speed}km/h")
            
            # Check for daily max/min patterns
            print("\nChecking for daily temperature patterns:")
            today = datetime.now().date()
            today_temps = []
            
            for entry in forecast.forecast:
                if 'dt' in entry and 'T' in entry:
                    dt_timestamp = entry['dt']
                    dt_datetime = datetime.fromtimestamp(dt_timestamp)
                    entry_date = dt_datetime.date()
                    
                    if entry_date == today:
                        temp_value = entry.get('T', {}).get('value')
                        if temp_value is not None:
                            today_temps.append((dt_datetime, temp_value))
            
            if today_temps:
                print(f"  Found {len(today_temps)} temperature readings for today ({today})")
                min_temp = min(today_temps, key=lambda x: x[1])
                max_temp = max(today_temps, key=lambda x: x[1])
                print(f"  Today's min: {min_temp[1]}°C at {min_temp[0].strftime('%H:%M')}")
                print(f"  Today's max: {max_temp[1]}°C at {max_temp[0].strftime('%H:%M')}")
            
            # Check for precipitation probability
            print("\nChecking for precipitation probability:")
            prob_entries = [entry for entry in forecast.forecast if 'precipitation_probability' in entry]
            if prob_entries:
                print(f"  Found {len(prob_entries)} entries with precipitation probability")
                for i, entry in enumerate(prob_entries[:3]):
                    dt_timestamp = entry['dt']
                    dt_datetime = datetime.fromtimestamp(dt_timestamp)
                    prob = entry['precipitation_probability']
                    print(f"    Entry {i+1}: {dt_datetime} - Probability: {prob}%")
            else:
                print("  No precipitation probability data found")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error testing get_forecast(): {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_forecast() 