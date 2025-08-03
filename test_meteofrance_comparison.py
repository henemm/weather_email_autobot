#!/usr/bin/env python3
"""
Test Météo-France data comparison using our existing weather system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import yaml
from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def test_meteofrance_comparison():
    """Test Météo-France data extraction using our system."""
    
    print("🌤️ MÉTÉO-FRANCE COMPARISON TEST")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create weather processor
    weather_processor = MorningEveningRefactor(config)
    
    # Prunelli-di-Fiumorbo coordinates (Corsica)
    lat = 42.0167
    lon = 9.4000
    
    print(f"📍 Location: Prunelli-di-Fiumorbo (Corsica)")
    print(f"🌍 Coordinates: {lat}, {lon}")
    print(f"📅 Test Date: {date.today()}")
    print()
    
    try:
        # Use the existing "Test" stage but fetch data directly for Corsica coordinates
        print("🔍 Fetching weather data using our system...")
        
        # Create a temporary stage with Corsica coordinates
        test_coordinates = [(lat, lon), (lat + 0.01, lon + 0.01), (lat + 0.02, lon + 0.02)]
        
        # Fetch weather data for each coordinate
        all_weather_data = []
        
        for i, (test_lat, test_lon) in enumerate(test_coordinates):
            print(f"  📍 Fetching data for coordinate {i+1}: {test_lat}, {test_lon}")
            
            # Use the meteofrance-api directly
            from meteofrance_api import MeteoFranceClient
            client = MeteoFranceClient()
            
            try:
                forecast = client.get_forecast(test_lat, test_lon)
                
                if forecast:
                    # Convert to our format
                    weather_data = {
                        'coordinates': (test_lat, test_lon),
                        'forecast': forecast,
                        'raw_data': str(forecast)
                    }
                    all_weather_data.append(weather_data)
                    print(f"    ✅ Successfully fetched data")
                else:
                    print(f"    ❌ No data received")
                    
            except Exception as e:
                print(f"    ❌ Error fetching data: {e}")
        
        if all_weather_data:
            print()
            print("✅ Successfully fetched weather data for Corsica")
            print()
            
            # Analyze the first dataset
            first_data = all_weather_data[0]
            forecast = first_data['forecast']
            
            print("📊 Weather Data Analysis:")
            
            # Check current forecast
            if hasattr(forecast, 'current_forecast') and forecast.current_forecast:
                current = forecast.current_forecast
                print("  🌤️ Current Forecast:")
                
                # Temperature
                if hasattr(current, 'T'):
                    print(f"    🌡️ Temperature: {current.T}°C")
                
                # Weather condition
                if hasattr(current, 'weather'):
                    print(f"    🌤️ Condition: {current.weather}")
                
                # Wind
                if hasattr(current, 'wind_speed'):
                    print(f"    💨 Wind Speed: {current.wind_speed} m/s ({current.wind_speed * 3.6:.1f} km/h)")
                
                # Rain
                if hasattr(current, 'rain_1h'):
                    print(f"    🌧️ Rain 1h: {current.rain_1h} mm")
            
            # Check daily forecast
            if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
                print(f"  📅 Daily Forecast: {len(forecast.daily_forecast)} entries")
                
                for i, daily in enumerate(forecast.daily_forecast[:3]):  # First 3 days
                    print(f"    Day {i+1}:")
                    
                    if hasattr(daily, 'T_min'):
                        print(f"      🌡️ Min: {daily.T_min}°C")
                    if hasattr(daily, 'T_max'):
                        print(f"      🌡️ Max: {daily.T_max}°C")
                    if hasattr(daily, 'weather'):
                        print(f"      🌤️ Condition: {daily.weather}")
            
            # Check hourly forecast
            if hasattr(forecast, 'hourly_forecast') and forecast.hourly_forecast:
                print(f"  ⏰ Hourly Forecast: {len(forecast.hourly_forecast)} entries")
                
                # Check for specific weather conditions
                thunderstorm_found = False
                rain_found = False
                high_wind_found = False
                
                for hourly in forecast.hourly_forecast[:10]:  # First 10 hours
                    # Check for thunderstorms
                    if hasattr(hourly, 'weather'):
                        condition = str(hourly.weather).lower()
                        if any(word in condition for word in ['orage', 'orageux', 'orageuse']):
                            thunderstorm_found = True
                    
                    # Check for rain
                    if hasattr(hourly, 'rain_1h') and hourly.rain_1h > 0:
                        rain_found = True
                    
                    # Check for high wind
                    if hasattr(hourly, 'wind_speed') and hourly.wind_speed > 8:  # > 30 km/h
                        high_wind_found = True
                
                print(f"    ⛈️ Thunderstorms: {'✅' if thunderstorm_found else '❌'}")
                print(f"    🌧️ Rain: {'✅' if rain_found else '❌'}")
                print(f"    💨 High Wind: {'✅' if high_wind_found else '❌'}")
            
            print()
            print("💾 Raw weather data saved to meteofrance_comparison_data.json")
            
            # Save raw data for analysis
            import json
            with open('meteofrance_comparison_data.json', 'w', encoding='utf-8') as f:
                json.dump(all_weather_data, f, indent=2, ensure_ascii=False, default=str)
                
        else:
            print("❌ Failed to fetch weather data")
            
    except Exception as e:
        print(f"❌ Error during weather data extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_meteofrance_comparison() 