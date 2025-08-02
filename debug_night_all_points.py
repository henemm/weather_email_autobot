#!/usr/bin/env python3
"""
Debug Night Temperature - Check ALL geo points
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml
from datetime import datetime

def main():
    print("🔍 DEBUG NIGHT TEMPERATURE - ALL POINTS")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "Vergio"
    date_str = "2025-08-02"
    report_type = "morning"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {date_str}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    try:
        # Get weather data
        print("🔍 Fetching weather data...")
        from datetime import date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        print("📊 CHECKING ALL GEO POINTS:")
        print("=" * 40)
        
        # Get stage coordinates
        import json
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
        
        # Find current stage
        start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
        days_since_start = (target_date - start_date).days
        
        if report_type == 'morning':
            stage_idx = days_since_start  # Today's stage
        else:  # evening
            stage_idx = days_since_start  # Today's stage for Night
        
        if stage_idx >= len(etappen_data):
            print(f"❌ Stage index {stage_idx} out of range")
            return
        
        stage = etappen_data[stage_idx]
        stage_points = stage.get('punkte', [])
        
        print(f"📍 Stage: {stage['name']} (index {stage_idx})")
        print(f"📍 Points: {len(stage_points)}")
        print()
        
        # Check each point
        from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
        api = EnhancedMeteoFranceAPI()
        
        for i, point in enumerate(stage_points):
            lat, lon = point['lat'], point['lon']
            point_name = f"{stage['name']}_point_{i+1}"
            
            print(f"🔍 Point {i+1} ({point_name}):")
            print(f"  Coordinates: {lat}, {lon}")
            
            # Fetch weather data for this point
            point_data = api.get_complete_forecast_data(lat, lon, point_name)
            
            # Check daily forecast
            daily_forecast = point_data.get('daily_forecast', {})
            if 'daily' in daily_forecast:
                daily_data = daily_forecast['daily']
                
                # Find target date entry
                target_date_str = target_date.strftime('%Y-%m-%d')
                found_entry = None
                
                for day_data in daily_data:
                    dt = day_data.get('dt')
                    if dt:
                        entry_date = datetime.fromtimestamp(dt).date()
                        entry_date_str = entry_date.strftime('%Y-%m-%d')
                        
                        if entry_date_str == target_date_str:
                            found_entry = day_data
                            break
                
                if found_entry:
                    temp_min = found_entry.get('T', {}).get('min')
                    temp_max = found_entry.get('T', {}).get('max')
                    print(f"  T.min: {temp_min}°C")
                    print(f"  T.max: {temp_max}°C")
                    
                    # Check if this is the 13°C point
                    if temp_min == 13 or temp_min == 13.0:
                        print(f"  🎯 FOUND 13°C POINT!")
                else:
                    print(f"  ❌ No data for target date")
            else:
                print(f"  ❌ No daily forecast data")
            
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 