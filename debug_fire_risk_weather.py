#!/usr/bin/env python3
"""
Standalone debug script to print fire risk and weather aggregation for GR20 stages.
Run from project root: python3 debug_fire_risk_weather.py
"""

import sys
import os
import yaml
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wetter.fire_risk_massif import FireRiskMassif
from wetter.weather_data_processor import WeatherDataProcessor

def main():
    # GR20 stage coordinates
    GR20_POINTS = [
        (41.5912, 9.2806, "Conca"),
        (41.7358, 9.2042, "Col de Bavella"), 
        (41.9181, 8.9247, "Vizzavona"),
        (42.3061, 9.1500, "Corte"),
        (42.4181, 8.9247, "Haut Asco"),
        (42.4900, 8.9000, "Calenzana"),
        (41.9000, 8.7000, "Porto-Vecchio"),  # Add Porto-Vecchio for testing
    ]

    # Load config
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    fire_risk = FireRiskMassif()
    processor = WeatherDataProcessor(config)

    print(f"GR20 Weather & Fire Risk Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 140)
    print("Stage | Lat | Lon | Massif | FireWarn | MaxTemp | MaxRain | MaxRainProb | MaxThunderProb | MaxWind | MaxWindGusts | API:ID:Level")
    print("-" * 140)
    
    # Debug: Show raw API data for first location
    print("\nDEBUG: Raw API data for Conca:")
    try:
        from meteofrance_api.client import MeteoFranceClient
        client = MeteoFranceClient()
        forecast = client.get_forecast(41.5912, 9.2806)
        
        if forecast.forecast:
            print("All forecast entries (showing time filtering):")
            for i, entry in enumerate(forecast.forecast):
                dt = datetime.fromtimestamp(entry.get('dt', 0))
                hour = dt.hour
                weather = entry.get('weather', {})
                weather_desc = weather.get('desc', 'N/A') if isinstance(weather, dict) else str(weather)
                temp = entry.get('T', {}).get('value', 'N/A') if isinstance(entry.get('T'), dict) else 'N/A'
                rain = entry.get('rain', {})
                rain_1h = rain.get('1h', 0) if isinstance(rain, dict) else 0
                precip_prob = entry.get('precipitation_probability', 'N/A')
                
                # Mark if this entry would be included in 05-17 Uhr filter
                included = "✓" if 5 <= hour <= 17 else "✗"
                
                print(f"  {dt.strftime('%H:%M')} [{included}]: {weather_desc}, {temp}°C, Rain: {rain_1h}mm, Prob: {precip_prob}")
                
                if i >= 10:  # Limit output
                    print(f"  ... and {len(forecast.forecast) - 10} more entries")
                    break
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nDEBUG: Weather processing details for Conca:")
    try:
        # Get the raw forecast data
        from meteofrance_api.client import MeteoFranceClient
        client = MeteoFranceClient()
        forecast = client.get_forecast(41.5912, 9.2806)
        
        if forecast.forecast:
            # Process like the weather processor does - WITH TOMORROW DATE FILTERING
            tomorrow_date = datetime.now().date() + timedelta(days=1)
            stage_entries = []
            
            print(f"DEBUG: Filtering for tomorrow's date: {tomorrow_date}")
            print(f"DEBUG: Looking for entries with date={tomorrow_date} AND hour between 05-17")
            
            for entry in forecast.forecast:
                dt_timestamp = entry.get('dt')
                if dt_timestamp:
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    entry_date = entry_datetime.date()
                    hour = entry_datetime.hour
                    
                    # Check if this is for tomorrow and stage time (05-17 Uhr) - EXACT WeatherDataProcessor logic
                    if entry_date == tomorrow_date and 5 <= hour <= 17:
                        stage_entries.append(entry)
            
            print(f"Found {len(stage_entries)} entries for tomorrow 05-17 Uhr")
            
            # If no tomorrow-specific entries found, use all entries as fallback (like WeatherDataProcessor)
            if not stage_entries:
                print("No tomorrow's stage time entries (05-17 Uhr) found, using all entries as fallback")
                stage_entries = forecast.forecast
            
            # Show processing for first few entries
            for i, entry in enumerate(stage_entries[:3]):
                dt = datetime.fromtimestamp(entry.get('dt', 0))
                weather = entry.get('weather', {})
                weather_desc = weather.get('desc', 'N/A') if isinstance(weather, dict) else str(weather)
                temp = entry.get('T', {}).get('value', 'N/A') if isinstance(entry.get('T'), dict) else 'N/A'
                rain = entry.get('rain', {})
                rain_1h = rain.get('1h', 0) if isinstance(rain, dict) else 0
                precip_prob = entry.get('precipitation_probability', 'N/A')
                
                print(f"  Entry {i} ({dt.strftime('%Y-%m-%d %H:%M')}):")
                print(f"    Weather: '{weather_desc}'")
                print(f"    Temperature: {temp}°C")
                print(f"    Rain 1h: {rain_1h}mm")
                print(f"    Precipitation probability: {precip_prob}")
                
                # Simulate the processing logic
                if rain_1h > 0:
                    if 'averse' in weather_desc.lower() or 'pluie' in weather_desc.lower():
                        if rain_1h >= 2.0:
                            estimated_prob = 80.0
                        elif rain_1h >= 1.0:
                            estimated_prob = 60.0
                        elif rain_1h >= 0.5:
                            estimated_prob = 40.0
                        else:
                            estimated_prob = 30.0
                        print(f"    → Estimated rain probability: {estimated_prob}% (based on {rain_1h}mm)")
                    else:
                        print(f"    → No rain indicators in weather description")
                else:
                    print(f"    → No precipitation, no probability estimated")
                print()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nDEBUG: WeatherDataProcessor internal processing for Conca:")
    try:
        # Get the raw forecast data
        from meteofrance_api.client import MeteoFranceClient
        client = MeteoFranceClient()
        forecast = client.get_forecast(41.5912, 9.2806)
        
        if forecast.forecast:
            # Simulate the exact WeatherDataProcessor logic
            time_points = []
            stage_entries = []
            
            # Get tomorrow's date for filtering - EXACT WeatherDataProcessor logic
            tomorrow_date = datetime.now().date() + timedelta(days=1)
            
            # Step 1: Time filtering (05-17 Uhr) WITH TOMORROW DATE FILTERING
            print("DEBUG: All API timestamps:")
            for i, entry in enumerate(forecast.forecast[:20]):  # Show first 20 entries
                dt_timestamp = entry.get('dt')
                if dt_timestamp:
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    entry_date = entry_datetime.date()
                    hour = entry_datetime.hour
                    temp = entry.get('T', {}).get('value', 'N/A') if isinstance(entry.get('T'), dict) else 'N/A'
                    
                    # Check if this is for tomorrow and stage time (05-17 Uhr) - EXACT WeatherDataProcessor logic
                    included = "✓" if (entry_date == tomorrow_date and 5 <= hour <= 17) else "✗"
                    print(f"  Entry {i}: {entry_datetime.strftime('%Y-%m-%d %H:%M')} [{included}] - {temp}°C")
            
            # Find entries for tomorrow's stage time (05-17 Uhr) - EXACT WeatherDataProcessor logic
            for entry in forecast.forecast:
                try:
                    dt_timestamp = entry.get('dt')
                    if not dt_timestamp:
                        continue
                        
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    entry_date = entry_datetime.date()
                    hour = entry_datetime.hour
                    
                    # Check if this is for tomorrow and stage time (05-17 Uhr) - EXACT WeatherDataProcessor logic
                    if entry_date == tomorrow_date and 5 <= hour <= 17:
                        stage_entries.append(entry)
                        
                except Exception as e:
                    continue
            
            # If no tomorrow-specific entries found, use all entries as fallback - EXACT WeatherDataProcessor logic
            if not stage_entries:
                print("No tomorrow's stage time entries (05-17 Uhr) found, using all entries as fallback")
                stage_entries = forecast.forecast
            
            print(f"WeatherDataProcessor found {len(stage_entries)} entries for processing")
            
            # Step 2: Process each entry
            for i, entry in enumerate(stage_entries):
                dt_timestamp = entry.get('dt')
                if dt_timestamp:
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    
                    # Extract data like WeatherDataProcessor does
                    weather_condition = None
                    weather_data = entry.get('weather', {})
                    if isinstance(weather_data, dict):
                        weather_condition = weather_data.get('desc')
                    
                    temperature = None
                    temp_data = entry.get('T', {})
                    if isinstance(temp_data, dict):
                        temperature = temp_data.get('value')
                    
                    precipitation_amount = None
                    rain_data = entry.get('rain', {})
                    if isinstance(rain_data, dict):
                        precipitation_amount = rain_data.get('1h')
                    
                    precipitation_probability = entry.get('precipitation_probability')
                    
                    # Determine rain probability
                    rain_probability = None
                    if precipitation_probability is not None:
                        rain_probability = float(precipitation_probability)
                    elif precipitation_amount and precipitation_amount > 0:
                        if weather_condition:
                            weather_lower = weather_condition.lower()
                            rain_indicators = ['averse', 'averses', 'pluie', 'pluies', 'rain', 'rains']
                            is_rain = any(indicator in weather_lower for indicator in rain_indicators)
                            
                            if is_rain:
                                if precipitation_amount >= 2.0:
                                    rain_probability = 80.0
                                elif precipitation_amount >= 1.0:
                                    rain_probability = 60.0
                                elif precipitation_amount >= 0.5:
                                    rain_probability = 40.0
                                else:
                                    rain_probability = 30.0
                    
                    time_point = {
                        'datetime': entry_datetime,
                        'temperature': temperature,
                        'precipitation_amount': precipitation_amount,
                        'rain_probability': rain_probability,
                        'precipitation_probability': precipitation_probability
                    }
                    time_points.append(time_point)
                    
                    # Show first few processed entries
                    if i < 3:
                        print(f"  Processed Entry {i} ({entry_datetime.strftime('%Y-%m-%d %H:%M')}):")
                        print(f"    Temperature: {temperature}°C")
                        print(f"    Precipitation: {precipitation_amount}mm")
                        print(f"    Rain Probability: {rain_probability}%")
                        print()
            
            # Step 3: Calculate max values
            max_temp = 0.0
            max_rain_prob = 0.0
            max_temp_time = ""
            max_rain_time = ""
            
            for point in time_points:
                time_str = point['datetime'].strftime('%H')
                
                if point['temperature'] and point['temperature'] > max_temp:
                    max_temp = point['temperature']
                    max_temp_time = time_str
                
                rain_prob = point.get('rain_probability') or point.get('precipitation_probability')
                if rain_prob and rain_prob > max_rain_prob:
                    max_rain_prob = rain_prob
                    max_rain_time = time_str
            
            print(f"WeatherDataProcessor calculated max values:")
            print(f"  Max Temperature: {max_temp}°C @ {max_temp_time}")
            print(f"  Max Rain Probability: {max_rain_prob}% @ {max_rain_time}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nDEBUG: Weather processing for each location:")
    
    for lat, lon, name in GR20_POINTS:
        try:
            # Get massif assignment
            massif_id = fire_risk._get_massif_for_coordinates(lat, lon)
            massif_name = fire_risk._get_massif_name(massif_id) if massif_id else "-"
            
            # Get fire risk warning
            fire_warn = fire_risk.format_fire_warnings(lat, lon)
            
            # Debug: Show actual API data
            api_data = fire_risk.fetch_fire_risk_data()
            massifs_data = api_data.get('massifs', {})
            massif_level = "N/A"
            if isinstance(massifs_data, dict) and str(massif_id) in massifs_data:
                massif_data = massifs_data[str(massif_id)]
                if isinstance(massif_data, list) and len(massif_data) > 0:
                    massif_level = str(massif_data[0])
                elif isinstance(massif_data, dict):
                    massif_level = str(massif_data.get('niveau', 'N/A'))
            
            # Get weather data
            report = processor.process_weather_data(lat, lon, name)
            
            # Extract values
            max_temp = report.get("max_temperature", "-")
            max_rain = report.get("max_precipitation", "-")
            max_rain_prob = report.get("max_rain_probability", "-")
            max_thunder_prob = report.get("max_thunderstorm_probability", "-")
            max_wind = report.get("wind_speed", "-")
            max_wind_gusts = report.get("max_wind_speed", "-")
            
            print(f"{name:12} | {lat:.4f} | {lon:.4f} | {massif_name:15} | {fire_warn:10} | {max_temp:7} | {max_rain:7} | {max_rain_prob:11} | {max_thunder_prob:14} | {max_wind:7} | {max_wind_gusts:12} | API:{massif_id}:{massif_level}")
            
            # Debug: Show processing details for suspicious values
            if max_rain_prob in [30.0, 60.0] or max_thunder_prob == 0.0:
                print(f"  ⚠️  {name}: Suspicious values - Rain prob: {max_rain_prob}%, Thunder: {max_thunder_prob}%")
            
        except Exception as e:
            print(f"{name:12} | {lat:.4f} | {lon:.4f} | ERROR: {str(e)}")

if __name__ == "__main__":
    main() 