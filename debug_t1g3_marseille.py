#!/usr/bin/env python3
"""
Debug T1G3 Marseille Temperature - Check MeteoFrance data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
from datetime import datetime

def main():
    print("🔍 DEBUG T1G3 MARSEILLE TEMPERATURE")
    print("=" * 50)
    
    # T1G3 coordinates (Marseille)
    lat = 43.283255
    lon = 5.370061
    point_name = "Marseille_T1G3"
    
    print(f"📍 Location: Marseille (T1G3)")
    print(f"📍 Coordinates: {lat}, {lon}")
    print(f"📍 Point Name: {point_name}")
    print()
    
    try:
        # Initialize API
        api = EnhancedMeteoFranceAPI()
        
        # Fetch weather data
        print("🔍 Fetching MeteoFrance data...")
        weather_data = api.get_complete_forecast_data(lat, lon, point_name)
        
        # Check daily forecast
        daily_forecast = weather_data.get('daily_forecast', {})
        print(f"daily_forecast keys: {list(daily_forecast.keys())}")
        
        if 'daily' in daily_forecast:
            daily_data = daily_forecast['daily']
            print(f"daily_data length: {len(daily_data)}")
            
            # Find today's entry (2025-08-02)
            target_date_str = "2025-08-02"
            found_entry = None
            
            print(f"\n🎯 LOOKING FOR DATE: {target_date_str}")
            print("-" * 30)
            
            for i, entry in enumerate(daily_data[:5]):  # Show first 5 entries
                dt = entry.get('dt')
                if dt:
                    entry_date = datetime.fromtimestamp(dt).date()
                    entry_date_str = entry_date.strftime('%Y-%m-%d')
                    
                    print(f"Entry {i}: {entry_date_str}")
                    print(f"  dt: {dt}")
                    print(f"  T: {entry.get('T')}")
                    
                    if entry_date_str == target_date_str:
                        found_entry = entry
                        print(f"  ✅ FOUND TARGET DATE!")
            
            if found_entry:
                temp_min = found_entry.get('T', {}).get('min')
                temp_max = found_entry.get('T', {}).get('max')
                
                print(f"\n📊 MARSEILLE TEMPERATURES (2025-08-02):")
                print(f"  T.min: {temp_min}°C")
                print(f"  T.max: {temp_max}°C")
                
                # Check if this matches what we expect
                if temp_min == 13 or temp_min == 13.0:
                    print(f"  🎯 FOUND 13°C!")
                elif temp_min == 7 or temp_min == 7.0:
                    print(f"  🎯 FOUND 7°C!")
                else:
                    print(f"  ❓ Unexpected temperature: {temp_min}°C")
            else:
                print(f"❌ No data found for {target_date_str}")
        else:
            print("❌ No daily forecast data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 