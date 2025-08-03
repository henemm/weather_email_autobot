#!/usr/bin/env python3
"""
Test Rain(mm) with real coordinates that are likely to have rain data
"""

import json
from datetime import date, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.config.config_loader import load_config

def test_rain_mm_with_real_coordinates():
    """Test Rain(mm) with real coordinates that are likely to have rain data"""
    
    print("=" * 80)
    print("TESTING RAIN(MM) WITH REAL COORDINATES")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test with real coordinates that are likely to have rain
    # Using coordinates from different regions in France
    test_coordinates = [
        {"name": "Brest (Brittany)", "lat": 48.3904, "lon": -4.4861},
        {"name": "Nantes (Loire)", "lat": 47.2184, "lon": -1.5536},
        {"name": "Bordeaux (Aquitaine)", "lat": 44.8378, "lon": -0.5792},
        {"name": "Toulouse (Occitanie)", "lat": 43.6047, "lon": 1.4442},
        {"name": "Lyon (Auvergne-Rhône-Alpes)", "lat": 45.7578, "lon": 4.8320},
        {"name": "Strasbourg (Grand Est)", "lat": 48.5734, "lon": 7.7521},
        {"name": "Paris (Île-de-France)", "lat": 48.8566, "lon": 2.3522},
        {"name": "Nice (Provence-Alpes-Côte d'Azur)", "lat": 43.7102, "lon": 7.2620},
    ]
    
    test_date = date(2025, 8, 3)  # Use tomorrow
    
    for coord in test_coordinates:
        print(f"\n{'='*60}")
        print(f"TESTING: {coord['name']}")
        print(f"Coordinates: lat={coord['lat']}, lon={coord['lon']}")
        print(f"Date: {test_date}")
        print(f"{'='*60}")
        
        # Create a temporary stage with this coordinate
        temp_stage_name = f"Temp_{coord['name'].replace(' ', '_').replace('(', '').replace(')', '')}"
        
        # Create weather data structure manually
        weather_data = {
            'hourly_data': [
                {
                    'point_name': f"{temp_stage_name}_point_1",
                    'coordinates': {'lat': coord['lat'], 'lon': coord['lon']},
                    'data': []
                }
            ]
        }
        
        # Fetch data for this coordinate
        try:
            # Use the enhanced API directly
            from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
            
            api = EnhancedMeteoFranceAPI()
            forecast_data = api.get_forecast(coord['lat'], coord['lon'])
            
            if forecast_data and 'hourly' in forecast_data:
                # Extract hourly data
                hourly_entries = forecast_data['hourly']
                
                # Convert to our format
                for entry in hourly_entries:
                    if 'dt' in entry:
                        weather_data['hourly_data'][0]['data'].append(entry)
                
                print(f"✅ Fetched {len(weather_data['hourly_data'][0]['data'])} hourly entries")
                
                # Check for rain data
                has_rain = False
                max_rain = 0
                rain_entries = []
                
                for entry in weather_data['hourly_data'][0]['data']:
                    if 'dt' in entry:
                        from datetime import datetime
                        hour_time = datetime.fromtimestamp(entry['dt'])
                        hour_date = hour_time.date()
                        if hour_date == test_date:
                            rain_value = entry.get('rain', {}).get('1h', 0)
                            if rain_value > 0:
                                has_rain = True
                                max_rain = max(max_rain, rain_value)
                                rain_entries.append({
                                    'hour': hour_time.hour,
                                    'rain': rain_value
                                })
                
                print(f"Has rain data: {has_rain}")
                print(f"Max rain value: {max_rain}")
                
                if has_rain:
                    print("🎉 FOUND COORDINATES WITH RAIN DATA!")
                    print(f"Location: {coord['name']}")
                    print(f"Max rain: {max_rain} mm")
                    print("\nRain entries:")
                    for entry in rain_entries:
                        print(f"  {entry['hour']:02d}:00 - {entry['rain']} mm")
                    
                    # Test the Rain(mm) processing
                    print("\nTesting Rain(mm) processing...")
                    rain_mm_data = refactor.process_rain_mm_data(weather_data, temp_stage_name, test_date, "morning")
                    
                    print(f"Threshold value: {rain_mm_data.threshold_value}")
                    print(f"Threshold time: {rain_mm_data.threshold_time}")
                    print(f"Max value: {rain_mm_data.max_value}")
                    print(f"Max time: {rain_mm_data.max_time}")
                    
                    return coord, test_date
                
                print("❌ No rain data found for this location")
                
            else:
                print("❌ No hourly data in forecast")
                
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
    
    print("\n" + "="*80)
    print("NO COORDINATES WITH RAIN DATA FOUND!")
    print("="*80)
    print("All tested coordinates have 0mm rain. This suggests:")
    print("1. A dry period in the forecast")
    print("2. An issue with the API data")
    print("3. The forecast period is too far in the future")
    
    return None, None

if __name__ == "__main__":
    test_rain_mm_with_real_coordinates() 