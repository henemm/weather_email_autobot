#!/usr/bin/env python3
"""
Detailed debug script to examine all possible fields in the meteofrance API response.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from meteofrance_api.client import MeteoFranceClient
from src.wetter.weather_data_processor import WeatherDataProcessor

def debug_api_detailed():
    """Debug meteofrance-api data structure in detail."""
    
    # Test coordinates (Conca, GR20)
    lat, lon = 41.7, 9.3
    
    print(f"🔍 DEBUGGING METEOFRANCE API FOR {lat}, {lon}")
    print("=" * 60)
    
    try:
        # Get raw forecast data
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        if not forecast or not forecast.forecast:
            print("❌ No forecast data received")
            return
        
        print(f"✅ Received {len(forecast.forecast)} forecast entries")
        print()
        
        # Get today's date
        today = date.today()
        
        # Filter entries for today, 05:00-17:00
        today_entries = []
        for i, entry in enumerate(forecast.forecast):
            dt_timestamp = entry.get('dt')
            if dt_timestamp:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                if (entry_datetime.date() == today and 
                    5 <= entry_datetime.hour <= 17):
                    today_entries.append({
                        'index': i,
                        'datetime': entry_datetime,
                        'entry': entry
                    })
        
        print(f"📅 Found {len(today_entries)} entries for today 05:00-17:00")
        print()
        
        # Process first 3 entries in detail
        for entry_info in today_entries[:3]:
            i = entry_info['index']
            dt = entry_info['datetime']
            entry = entry_info['entry']
            
            print(f"🕐 ENTRY {i+1} - {dt.strftime('%Y-%m-%d %H:%M')} (Hour {dt.hour}):")
            print("-" * 50)
            
            # Show all fields in detail
            print("📋 ALL FIELDS:")
            for key, value in entry.items():
                print(f"  {key}: {value}")
            
            print()
            
            # Look specifically for probability-related fields
            print("🔍 PROBABILITY ANALYSIS:")
            
            # Check for precipitation_probability
            precip_prob = entry.get('precipitation_probability')
            print(f"  precipitation_probability: {precip_prob}")
            
            # Check for any field containing 'prob'
            prob_fields = {k: v for k, v in entry.items() if 'prob' in k.lower()}
            if prob_fields:
                print(f"  Fields containing 'prob': {prob_fields}")
            else:
                print("  No fields containing 'prob' found")
            
            # Check for any field containing 'rain'
            rain_fields = {k: v for k, v in entry.items() if 'rain' in k.lower()}
            if rain_fields:
                print(f"  Fields containing 'rain': {rain_fields}")
            else:
                print("  No fields containing 'rain' found")
            
            # Check for any field containing 'precip'
            precip_fields = {k: v for k, v in entry.items() if 'precip' in k.lower()}
            if precip_fields:
                print(f"  Fields containing 'precip': {precip_fields}")
            else:
                print("  No fields containing 'precip' found")
            
            # Check weather description
            weather = entry.get('weather', {})
            weather_desc = weather.get('desc', 'N/A') if isinstance(weather, dict) else str(weather)
            print(f"  Weather description: '{weather_desc}'")
            
            # Check temperature
            temp_data = entry.get('T', {})
            temp = temp_data.get('value', 'N/A') if isinstance(temp_data, dict) else 'N/A'
            print(f"  Temperature: {temp}°C")
            
            # Check precipitation amount
            rain_data = entry.get('rain', {})
            rain_1h = rain_data.get('1h', 0) if isinstance(rain_data, dict) else 0
            print(f"  Rain 1h: {rain_1h}mm")
            
            print()
            
            # Simulate WeatherDataProcessor extraction
            print("🔧 WEATHERDATAPROCESSOR SIMULATION:")
            processor = WeatherDataProcessor({})
            
            # Extract weather condition
            weather_condition = processor._extract_weather_condition(entry)
            print(f"  Extracted weather condition: '{weather_condition}'")
            
            # Extract precipitation amount
            precipitation_amount = processor._extract_precipitation_amount(entry)
            print(f"  Extracted precipitation amount: {precipitation_amount}mm")
            
            # Determine rain probability
            rain_probability = processor._determine_rain_probability(
                weather_condition, precip_prob, precipitation_amount
            )
            print(f"  Determined rain probability: {rain_probability}%")
            
            # Determine thunderstorm probability
            thunderstorm_probability = processor._determine_thunderstorm_probability(
                weather_condition, precip_prob
            )
            print(f"  Determined thunderstorm probability: {thunderstorm_probability}%")
            
            print()
            print("=" * 60)
            print()
        
        # Summary
        print("📊 SUMMARY:")
        print(f"Total entries: {len(forecast.forecast)}")
        print(f"Today 05:00-17:00 entries: {len(today_entries)}")
        
        # Check if precipitation_probability exists in any entry
        has_precip_prob = any('precipitation_probability' in entry for entry in forecast.forecast)
        print(f"Has precipitation_probability field: {has_precip_prob}")
        
        # Check if any entry has non-None precipitation_probability
        has_precip_prob_values = any(
            entry.get('precipitation_probability') is not None 
            for entry in forecast.forecast
        )
        print(f"Has non-None precipitation_probability values: {has_precip_prob_values}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_detailed() 