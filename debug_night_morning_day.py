#!/usr/bin/env python3
"""
DEBUG NIGHT AND MORNING DAY DATA PROCESSING
==========================================
Debug why NIGHT data processing fails and MORNING DAY data processing doesn't work.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
import yaml
import json

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def debug_night_morning_day():
    """Debug NIGHT and MORNING DAY data processing"""
    print("🔍 DEBUG NIGHT AND MORNING DAY DATA PROCESSING")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        config = load_config()
        refactor = MorningEveningRefactor(config)
        api = EnhancedMeteoFranceAPI()
        
        # Test data
        target_date = date(2025, 8, 2)
        stage_name = "Test"
        
        print(f"📅 Test Date: {target_date}")
        print(f"📍 Stage: {stage_name}")
        print()
        
        # Debug NIGHT data processing
        print("🌙 DEBUG NIGHT DATA PROCESSING:")
        print("-" * 40)
        
        try:
            # Get stage coordinates
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            # Calculate stage index
            start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (target_date - start_date).days
            stage_idx = days_since_start  # Today's stage for Night
            
            print(f"   Start date: {start_date}")
            print(f"   Days since start: {days_since_start}")
            print(f"   Stage index: {stage_idx}")
            print(f"   Total stages: {len(etappen_data)}")
            
            if stage_idx >= len(etappen_data):
                print(f"   ❌ Stage index {stage_idx} out of range")
                return
            
            stage = etappen_data[stage_idx]
            stage_points = stage.get('punkte', [])
            
            print(f"   Stage name: {stage['name']}")
            print(f"   Stage points: {len(stage_points)}")
            
            if not stage_points:
                print(f"   ❌ No points found for stage {stage['name']}")
                return
            
            # Get the last point's coordinates (T1G3)
            last_point = stage_points[-1]
            last_lat, last_lon = last_point['lat'], last_point['lon']
            
            print(f"   Last point coordinates: ({last_lat}, {last_lon})")
            
            # Fetch weather data for the last point
            last_point_name = f"{stage['name']}_point_{len(stage_points)}"
            print(f"   Fetching data for: {last_point_name}")
            
            last_point_data = api.get_complete_forecast_data(last_lat, last_lon, last_point_name)
            
            if not last_point_data:
                print(f"   ❌ No data returned for {last_point_name}")
                return
            
            print(f"   ✅ Data fetched successfully")
            
            # Extract daily forecast data
            daily_forecast = last_point_data.get('daily_forecast', {})
            if 'daily' not in daily_forecast:
                print(f"   ❌ No daily forecast data for {last_point_name}")
                return
            
            daily_data = daily_forecast['daily']
            print(f"   Daily data entries: {len(daily_data)}")
            
            # Find the entry for the target date
            target_date_str = target_date.strftime('%Y-%m-%d')
            point_value = None
            
            print(f"   Looking for date: {target_date_str}")
            
            for i, day_data in enumerate(daily_data):
                entry_dt = day_data.get('dt')
                if entry_dt:
                    entry_date = datetime.fromtimestamp(entry_dt).date()
                    entry_date_str = entry_date.strftime('%Y-%m-%d')
                    
                    print(f"   Entry {i}: {entry_date_str}")
                    
                    if entry_date_str == target_date_str:
                        # Extract temp_min value
                        temp_data = day_data.get('T', {})
                        point_value = temp_data.get('min')
                        
                        print(f"   ✅ Found matching date!")
                        print(f"   Temperature data: {temp_data}")
                        print(f"   temp_min: {point_value}")
                        break
            
            if point_value is None:
                print(f"   ❌ No temperature data found for {target_date_str}")
                print(f"   Available dates: {[datetime.fromtimestamp(entry.get('dt')).strftime('%Y-%m-%d') for entry in daily_data if entry.get('dt')]}")
                return
            
            print(f"   ✅ Night temperature extracted: {point_value}°C")
            
        except Exception as e:
            print(f"   ❌ Night data processing failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # Debug MORNING DAY data processing
        print("🌅 DEBUG MORNING DAY DATA PROCESSING:")
        print("-" * 40)
        
        try:
            # For Morning report: Day = temp_max of all points of today's stage for today
            stage_idx = days_since_start  # Today's stage
            stage_date = target_date  # Today's date
            
            print(f"   Stage index: {stage_idx}")
            print(f"   Stage date: {stage_date}")
            
            if stage_idx >= len(etappen_data):
                print(f"   ❌ Stage index {stage_idx} out of range")
                return
            
            stage = etappen_data[stage_idx]
            stage_points = stage.get('punkte', [])
            
            print(f"   Stage name: {stage['name']}")
            print(f"   Stage points: {len(stage_points)}")
            
            if not stage_points:
                print(f"   ❌ No points found for stage {stage['name']}")
                return
            
            # Fetch weather data for all points
            geo_points = []
            max_temp = None
            
            for i, point in enumerate(stage_points):
                lat, lon = point['lat'], point['lon']
                point_name = f"{stage['name']}_point_{i+1}"
                
                print(f"   Point {i+1}: ({lat}, {lon}) - {point_name}")
                
                # Fetch weather data for this point
                point_data = api.get_complete_forecast_data(lat, lon, point_name)
                
                if not point_data:
                    print(f"     ❌ No data returned")
                    continue
                
                # Get temp_max from daily forecast
                daily_forecast = point_data.get('daily_forecast', {})
                daily_data = daily_forecast.get('daily', [])
                
                print(f"     Daily data entries: {len(daily_data)}")
                
                temp_max = None
                for entry in daily_data:
                    entry_date = entry.get('date')
                    # Handle datetime.date objects
                    if isinstance(entry_date, date):
                        if entry_date == stage_date:
                            # Get temp_max from temperature object
                            temperature = entry.get('temperature', {})
                            temp_max = temperature.get('max') if temperature else None
                            
                            print(f"     ✅ Found matching date!")
                            print(f"     Temperature data: {temperature}")
                            print(f"     temp_max: {temp_max}")
                            break
                
                if temp_max is not None:
                    # Day uses today's stage for morning
                    tg_ref = f"T1G{i+1}"
                    geo_points.append({tg_ref: temp_max})
                    
                    print(f"     ✅ Added {tg_ref}: {temp_max}°C")
                    
                    # Track the maximum temperature
                    if max_temp is None or temp_max > max_temp:
                        max_temp = temp_max
                else:
                    print(f"     ❌ No temperature data found")
            
            if max_temp is not None:
                print(f"   ✅ Maximum temperature found: {max_temp}°C")
                print(f"   ✅ Geo points: {geo_points}")
            else:
                print(f"   ❌ No maximum temperature found")
            
        except Exception as e:
            print(f"   ❌ Morning day data processing failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # Test the actual methods
        print("🧪 TESTING ACTUAL METHODS:")
        print("-" * 30)
        
        try:
            # Create mock weather data for testing
            mock_weather_data = {
                'daily_forecast': {
                    'daily': [
                        {
                            'date': target_date,
                            'temperature': {'min': 15.2, 'max': 28.7},
                            'T': {'min': 15.2, 'max': 28.7}
                        }
                    ]
                }
            }
            
            # Test Night data processing
            print("Testing Night data processing...")
            night_data = refactor.process_night_data(mock_weather_data, stage_name, target_date, "morning")
            print(f"   Night result: threshold={night_data.threshold_value}, max={night_data.max_value}")
            
            # Test Day data processing
            print("Testing Day data processing...")
            day_data = refactor.process_day_data(mock_weather_data, stage_name, target_date, "morning")
            print(f"   Day result: threshold={day_data.threshold_value}, max={day_data.max_value}")
            
        except Exception as e:
            print(f"   ❌ Method testing failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        print("=" * 60)
        print("🎯 DEBUG SUMMARY:")
        print("=" * 60)
        print("1. NIGHT data processing analyzed")
        print("2. MORNING DAY data processing analyzed")
        print("3. Actual methods tested")
        print("4. Issues identified")
        print()
        print("Next: Fix the identified issues!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_night_morning_day() 