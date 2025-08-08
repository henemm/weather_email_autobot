#!/usr/bin/env python3
"""
Debug script to check why thunderstorm processing is not working.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def main():
    print("🌩️ DEBUG: Thunderstorm Processing Issue")
    print("=" * 50)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test with Belfort coordinates
        belfort_lat, belfort_lon = 47.6386, 6.8631
        
        print(f"📍 Testing Belfort: {belfort_lat}, {belfort_lon}")
        print()
        
        # Get raw API data
        client = MeteoFranceClient()
        forecast = client.get_forecast(belfort_lat, belfort_lon)
        
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print(f"📅 Total forecast entries: {len(forecast.forecast)}")
            
            # Focus on tomorrow (2025-08-02)
            tomorrow = date.today() + timedelta(days=1)
            print(f"📅 Analyzing data for: {tomorrow}")
            print()
            
            print("📊 Raw API data for tomorrow:")
            print("Time | Weather Condition | Raw Data")
            print("-" * 60)
            
            thunderstorm_entries = []
            
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    if entry_date == tomorrow:
                        time_str = entry_time.strftime('%H:%M')
                        weather_data = entry.get('weather', {})
                        condition = weather_data.get('desc', 'Unknown')
                        
                        print(f"{time_str} | {condition} | {weather_data}")
                        
                        # Check for thunderstorm conditions
                        thunderstorm_keywords = ['orage', 'orageuse', 'orageux', 'thunderstorm']
                        if any(keyword in condition.lower() for keyword in thunderstorm_keywords):
                            thunderstorm_entries.append({
                                'time': time_str,
                                'condition': condition,
                                'raw_data': weather_data
                            })
            
            print("-" * 60)
            print(f"⚡ Found {len(thunderstorm_entries)} thunderstorm entries")
            
            if thunderstorm_entries:
                print("\n🔍 Thunderstorm entries:")
                for entry in thunderstorm_entries:
                    print(f"  {entry['time']}: {entry['condition']}")
            
            # Now test the processing function
            print("\n🔍 Testing process_thunderstorm_data function...")
            
            # Structure data as expected by the function
            weather_data = {
                'hourly_data': [
                    {
                        'data': forecast.forecast
                    }
                ]
            }
            
            print(f"📊 Weather data structure:")
            print(f"  hourly_data length: {len(weather_data['hourly_data'])}")
            print(f"  First geo point data length: {len(weather_data['hourly_data'][0]['data'])}")
            
            # Check first few entries
            print(f"\n📊 First few entries in data:")
            for i, entry in enumerate(weather_data['hourly_data'][0]['data'][:3]):
                print(f"  Entry {i}: {entry}")
                if 'weather' in entry:
                    print(f"    Weather: {entry['weather']}")
            
            # Process thunderstorm data
            print(f"\n🔍 Processing thunderstorm data for date: {tomorrow}")
            
            # Debug the processing function step by step
            result = refactor.process_thunderstorm_data(
                weather_data, 'Belfort', tomorrow, 'evening'
            )
            
            # Let's also debug the function manually
            print(f"\n🔍 Manual debugging of process_thunderstorm_data...")
            
            # Get the threshold
            threshold = refactor.thresholds.get('thunderstorm', 'med')
            print(f"  Threshold: {threshold}")
            
            # Check thunderstorm levels mapping
            thunderstorm_levels = {
                'Risque d\'orages': 'low',
                'Averses orageuses': 'med', 
                'Orages': 'high'
            }
            print(f"  Thunderstorm levels: {thunderstorm_levels}")
            
            # Check level hierarchy
            level_hierarchy = {'low': 1, 'med': 2, 'high': 3}
            threshold_level = level_hierarchy.get(threshold, 2)
            print(f"  Threshold level: {threshold_level}")
            
            # Check a few entries manually
            print(f"\n🔍 Checking entries manually...")
            for i, entry in enumerate(weather_data['hourly_data'][0]['data']):
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    if entry_date == tomorrow:
                        time_str = entry_time.strftime('%H:%M')
                        weather_data_entry = entry.get('weather', {})
                        condition = weather_data_entry.get('desc', '')
                        
                        if condition in thunderstorm_levels:
                            level = thunderstorm_levels[condition]
                            print(f"  {time_str}: {condition} -> {level}")
                            break
            
            print(f"\n📊 Processing result:")
            print(f"  Threshold value: {result.threshold_value}")
            print(f"  Threshold time: {result.threshold_time}")
            print(f"  Max value: {result.max_value}")
            print(f"  Max time: {result.max_time}")
            print(f"  Geo points: {len(result.geo_points)}")
            
            if result.geo_points:
                print(f"\n📍 Geo point data:")
                for point in result.geo_points:
                    print(f"  {point}")
            
        else:
            print("❌ No forecast data available")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 