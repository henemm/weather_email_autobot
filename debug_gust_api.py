#!/usr/bin/env python3
"""
Debug script to check what gust data is actually available from MeteoFrance API.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌪️ DEBUG: Gust Data from MeteoFrance API")
    print("=" * 50)
    
    try:
        # Test with Test stage coordinates
        test_coordinates = [
            (47.6386, 6.8631),  # G1
            (47.6386, 6.8631),  # G2 (same for now)
            (47.6386, 6.8631)   # G3 (same for now)
        ]
        
        client = MeteoFranceClient()
        
        for i, (lat, lon) in enumerate(test_coordinates):
            print(f"\n📍 Testing G{i+1}: {lat}, {lon}")
            print("-" * 40)
            
            # Get forecast
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'forecast') and forecast.forecast:
                print(f"📅 Total forecast entries: {len(forecast.forecast)}")
                
                # Focus on tomorrow (2025-08-02)
                tomorrow = date.today() + timedelta(days=1)
                print(f"📅 Analyzing data for: {tomorrow}")
                print()
                
                print("📊 Raw API data for tomorrow (first 5 entries):")
                print("Time | Wind Speed | Gust | Wind Data Structure")
                print("-" * 60)
                
                gust_found = False
                
                for j, entry in enumerate(forecast.forecast):
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        entry_date = entry_time.date()
                        
                        if entry_date == tomorrow and j < 5:  # First 5 entries
                            time_str = entry_time.strftime('%H:%M')
                            wind_speed = entry.get('wind', {}).get('speed', 'N/A')
                            gust = entry.get('wind', {}).get('gust', 'N/A')
                            
                            print(f"{time_str} | {wind_speed} | {gust} | {entry.get('wind', {})}")
                            
                            if gust != 'N/A' and gust != 0:
                                gust_found = True
                
                print("-" * 60)
                if gust_found:
                    print(f"✅ Gust data found for G{i+1}!")
                else:
                    print(f"❌ No gust data found for G{i+1}")
                
                # Check all available fields in first entry
                if forecast.forecast:
                    first_entry = forecast.forecast[0]
                    print(f"\n🔍 All available fields in first entry:")
                    print(f"Keys: {list(first_entry.keys())}")
                    
                    if 'wind' in first_entry:
                        wind_data = first_entry['wind']
                        print(f"Wind data: {wind_data}")
                        print(f"Wind keys: {list(wind_data.keys())}")
                    
                    # Check for alternative gust field names
                    gust_alternatives = ['gust', 'gusts', 'wind_gust', 'wind_gusts', 'gust_speed']
                    for alt in gust_alternatives:
                        if alt in first_entry:
                            print(f"Found {alt}: {first_entry[alt]}")
                        elif 'wind' in first_entry and alt in first_entry['wind']:
                            print(f"Found wind.{alt}: {first_entry['wind'][alt]}")
                
            else:
                print("❌ No forecast data available")
        
        print("\n🎯 SUMMARY:")
        print("If gust data is always 0, the issue might be:")
        print("1. Wrong field name (not 'gust' but something else)")
        print("2. API doesn't provide gust data for this location")
        print("3. Gust data is in a different API endpoint")
        print("4. Gust data is calculated differently")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 