#!/usr/bin/env python3
"""
Debug script to understand the structure of probability_forecast data.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌧️ DEBUG: Probability Forecast Structure")
    print("=" * 50)
    
    try:
        client = MeteoFranceClient()
        lat, lon = 47.6386, 6.8631
        
        print(f"📍 Coordinates: {lat}, {lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Get forecast data
        forecast = client.get_forecast(lat, lon)
        
        if hasattr(forecast, 'probability_forecast') and forecast.probability_forecast:
            print(f"📅 Probability forecast entries: {len(forecast.probability_forecast)}")
            
            # Analyze first few entries
            print("\n📊 First 5 probability forecast entries:")
            print("-" * 50)
            
            for i, entry in enumerate(forecast.probability_forecast[:5]):
                print(f"Entry {i+1}: {entry}")
                
                if isinstance(entry, dict):
                    for key, value in entry.items():
                        print(f"  {key}: {type(value)} = {value}")
                print()
            
            # Check tomorrow's entries
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_entries = []
            
            for entry in forecast.probability_forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    if entry_date == tomorrow:
                        tomorrow_entries.append(entry)
            
            print(f"📅 Tomorrow probability entries: {len(tomorrow_entries)}")
            
            if tomorrow_entries:
                print("\n📊 Tomorrow's probability forecast entries:")
                print("-" * 50)
                
                for i, entry in enumerate(tomorrow_entries[:10]):
                    time = datetime.fromtimestamp(entry['dt'])
                    time_str = time.strftime('%H:%M')
                    print(f"{time_str}: {entry}")
                    
                    if isinstance(entry, dict):
                        for key, value in entry.items():
                            print(f"  {key}: {type(value)} = {value}")
                    print()
        
        else:
            print("❌ No probability forecast data available")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 