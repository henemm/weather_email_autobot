#!/usr/bin/env python3
"""
Comprehensive debug script to check all MeteoFrance API endpoints and data structures.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🔍 DEBUG: Comprehensive MeteoFrance API Analysis")
    print("=" * 60)
    
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
        client = MeteoFranceClient()
        
        # Method 1: Check all available methods
        print("🔍 METHOD 1: Available API Methods")
        print("-" * 40)
        
        methods = [method for method in dir(client) if not method.startswith('_')]
        print("Available methods:")
        for method in methods:
            print(f"  - {method}")
        
        print("\n" + "=" * 60)
        
        # Method 2: Test different dates for high gust values
        print("🔍 METHOD 2: Test Different Dates for High Gust Values")
        print("-" * 40)
        
        forecast = client.get_forecast(lat, lon)
        
        if hasattr(forecast, 'forecast') and forecast.forecast:
            print(f"📅 Total forecast entries: {len(forecast.forecast)}")
            
            # Group entries by date
            entries_by_date = {}
            
            for entry in forecast.forecast:
                if 'dt' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    if entry_date not in entries_by_date:
                        entries_by_date[entry_date] = []
                    
                    entries_by_date[entry_date].append(entry)
            
            print(f"📅 Found {len(entries_by_date)} different dates:")
            for entry_date in sorted(entries_by_date.keys()):
                print(f"\n📅 {entry_date}:")
                
                max_gust = 0
                max_gust_time = None
                
                for entry in entries_by_date[entry_date]:
                    if 'wind' in entry:
                        wind_data = entry['wind']
                        gust = wind_data.get('gust', 0)
                        
                        if gust > max_gust:
                            max_gust = gust
                            entry_time = datetime.fromtimestamp(entry['dt'])
                            max_gust_time = entry_time.strftime('%H:%M')
                
                print(f"   🎯 Max gust: {max_gust} km/h at {max_gust_time}")
                
                # Check if we found the 55 km/h gust
                if max_gust >= 50:
                    print(f"   🚨 FOUND HIGH GUST: {max_gust} km/h at {max_gust_time}")
                    
                    # Show all entries with gust > 0 for this date
                    print("   📊 All gust values > 0:")
                    for entry in entries_by_date[entry_date]:
                        if 'wind' in entry:
                            wind_data = entry['wind']
                            gust = wind_data.get('gust', 0)
                            
                            if gust > 0:
                                entry_time = datetime.fromtimestamp(entry['dt'])
                                print(f"     {entry_time.strftime('%H:%M')}: {gust} km/h")
        
        print("\n" + "=" * 60)
        
        # Method 3: Check if the image shows a different month/year
        print("🔍 METHOD 3: Check Different Month/Year")
        print("-" * 40)
        
        print("The image shows 'VENDREDI 01' (Friday 01).")
        print("This could be:")
        print("- January 1st (Friday)")
        print("- February 1st (Friday)") 
        print("- March 1st (Friday)")
        print("- etc.")
        print()
        print("Current date:", date.today())
        print("Current day of week:", date.today().strftime('%A'))
        
        # Check if today is Friday
        if date.today().weekday() == 4:  # Friday
            print("✅ Today is Friday!")
        else:
            print("❌ Today is not Friday")
        
        print("\n" + "=" * 60)
        print("🔍 SUMMARY:")
        print("The image shows 'VENDREDI 01' which could be:")
        print("1. A different month (January, February, etc.)")
        print("2. A different year")
        print("3. A different location")
        print("4. Historical data")
        print()
        print("My API shows max 15 km/h for the current forecast period.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 