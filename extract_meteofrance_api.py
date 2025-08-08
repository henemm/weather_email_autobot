#!/usr/bin/env python3
"""
Extract weather data from Météo-France API for comparison with our system.
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_meteofrance_api_data(lat, lon):
    """
    Get weather data from Météo-France API using coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary with weather data
    """
    try:
        logger.info(f"Fetching Météo-France API data for coordinates: {lat}, {lon}")
        
        # Météo-France API endpoint
        url = f"https://donnees-publiques.meteofrance.com/api/forecast/weather"
        
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json'
        }
        
        headers = {
            'User-Agent': 'WeatherBot/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        result = {
            'coordinates': {'lat': lat, 'lon': lon},
            'extracted_at': datetime.now().isoformat(),
            'api_data': data
        }
        
        logger.info("Successfully fetched Météo-France API data")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching Météo-France API data: {e}")
        return None

def get_meteofrance_forecast_data(lat, lon):
    """
    Get forecast data from Météo-France using the same method as our weather system.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary with forecast data
    """
    try:
        logger.info(f"Fetching Météo-France forecast data for coordinates: {lat}, {lon}")
        
        # Use the same meteofrance-api library that our system uses
        from meteofrance_api import MeteoFranceClient
        
        client = MeteoFranceClient()
        
        # Get forecast data using the same method as our system
        forecast = client.get_forecast(lat, lon)
        
        if forecast:
            # Convert to dictionary format for easier analysis
            result = {
                'coordinates': {'lat': lat, 'lon': lon},
                'extracted_at': datetime.now().isoformat(),
                'forecast_data': {
                    'current': {},
                    'daily': [],
                    'hourly': []
                }
            }
            
            # Extract current forecast data
            if hasattr(forecast, 'current_forecast') and forecast.current_forecast:
                current = forecast.current_forecast
                result['forecast_data']['current'] = {
                    'temperature': getattr(current, 'T', None),
                    'condition': getattr(current, 'weather', None),
                    'wind_speed': getattr(current, 'wind_speed', None),
                    'wind_gust': getattr(current, 'wind_gust', None),
                    'rain_1h': getattr(current, 'rain_1h', None),
                    'rain_3h': getattr(current, 'rain_3h', None)
                }
            
            # Extract daily forecasts
            if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
                for daily in forecast.daily_forecast:
                    daily_data = {
                        'date': getattr(daily, 'dt', None),
                        'temp_min': getattr(daily, 'T_min', None),
                        'temp_max': getattr(daily, 'T_max', None),
                        'condition': getattr(daily, 'weather', None),
                        'rain_24h': getattr(daily, 'rain_24h', None)
                    }
                    result['forecast_data']['daily'].append(daily_data)
            
            # Extract hourly forecasts
            if hasattr(forecast, 'hourly_forecast') and forecast.hourly_forecast:
                for hourly in forecast.hourly_forecast:
                    hourly_data = {
                        'time': getattr(hourly, 'dt', None),
                        'temperature': getattr(hourly, 'T', None),
                        'condition': getattr(hourly, 'weather', None),
                        'wind_speed': getattr(hourly, 'wind_speed', None),
                        'wind_gust': getattr(hourly, 'wind_gust', None),
                        'rain_1h': getattr(hourly, 'rain_1h', None),
                        'rain_3h': getattr(hourly, 'rain_3h', None)
                    }
                    result['forecast_data']['hourly'].append(hourly_data)
            
            # Also try to get raw data for debugging
            result['raw_forecast'] = str(forecast)
            
            logger.info("Successfully fetched Météo-France forecast data")
            return result
        else:
            logger.warning("No forecast data received from Météo-France API")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching Météo-France forecast data: {e}")
        return None

def analyze_weather_conditions(forecast_data):
    """
    Analyze weather conditions from forecast data.
    
    Args:
        forecast_data: Forecast data from Météo-France API
        
    Returns:
        Dictionary with analyzed conditions
    """
    if not forecast_data or 'forecast_data' not in forecast_data:
        return {}
    
    analysis = {
        'rain_detected': False,
        'thunderstorm_detected': False,
        'wind_detected': False,
        'high_temp_detected': False,
        'low_temp_detected': False,
        'temperature_range': None,
        'wind_speed_range': None,
        'rain_amounts': [],
        'thunderstorm_conditions': []
    }
    
    try:
        # Analyze hourly data
        hourly_data = forecast_data['forecast_data']['hourly']
        
        temperatures = []
        wind_speeds = []
        
        for hour in hourly_data:
            # Temperature analysis
            temp = hour.get('temperature')
            if temp is not None:
                temperatures.append(temp)
                if temp > 30:
                    analysis['high_temp_detected'] = True
                if temp < 15:
                    analysis['low_temp_detected'] = True
            
            # Wind analysis
            wind_speed = hour.get('wind_speed')
            if wind_speed is not None:
                wind_speeds.append(wind_speed)
                if wind_speed > 30:  # km/h
                    analysis['wind_detected'] = True
            
            # Rain analysis
            rain_1h = hour.get('rain_1h')
            if rain_1h and rain_1h > 0:
                analysis['rain_detected'] = True
                analysis['rain_amounts'].append(rain_1h)
            
            # Thunderstorm analysis
            condition = hour.get('condition', '').lower()
            if any(word in condition for word in ['orage', 'orageux', 'orageuse', 'orageuse']):
                analysis['thunderstorm_detected'] = True
                analysis['thunderstorm_conditions'].append(condition)
        
        # Calculate ranges
        if temperatures:
            analysis['temperature_range'] = (min(temperatures), max(temperatures))
        
        if wind_speeds:
            analysis['wind_speed_range'] = (min(wind_speeds), max(wind_speeds))
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing weather conditions: {e}")
        return analysis

def main():
    """Main function to extract and analyze Météo-France data."""
    
    # Prunelli-di-Fiumorbo coordinates (Corsica)
    lat = 42.0167
    lon = 9.4000
    
    print("🌤️ MÉTÉO-FRANCE API DATA EXTRACTION")
    print("=" * 50)
    print(f"📍 Location: Prunelli-di-Fiumorbo (Corsica)")
    print(f"🌍 Coordinates: {lat}, {lon}")
    print()
    
    # Get forecast data using meteofrance-api library
    forecast_data = get_meteofrance_forecast_data(lat, lon)
    
    if forecast_data:
        print("✅ Successfully fetched Météo-France forecast data")
        print()
        
        # Analyze weather conditions
        analysis = analyze_weather_conditions(forecast_data)
        
        print("📋 Weather Conditions Analysis:")
        print(f"  {'✅' if analysis['rain_detected'] else '❌'} Rain Detected")
        print(f"  {'✅' if analysis['thunderstorm_detected'] else '❌'} Thunderstorm Detected")
        print(f"  {'✅' if analysis['wind_detected'] else '❌'} High Wind Detected")
        print(f"  {'✅' if analysis['high_temp_detected'] else '❌'} High Temperature Detected")
        print(f"  {'✅' if analysis['low_temp_detected'] else '❌'} Low Temperature Detected")
        
        print()
        print("🌡️ Temperature Range:")
        if analysis['temperature_range']:
            min_temp, max_temp = analysis['temperature_range']
            print(f"  {min_temp}°C to {max_temp}°C")
        else:
            print("  No temperature data available")
        
        print()
        print("💨 Wind Speed Range:")
        if analysis['wind_speed_range']:
            min_wind, max_wind = analysis['wind_speed_range']
            print(f"  {min_wind} to {max_wind} km/h")
        else:
            print("  No wind data available")
        
        print()
        print("🌧️ Rain Amounts:")
        if analysis['rain_amounts']:
            for amount in analysis['rain_amounts'][:5]:  # Show first 5
                print(f"  {amount} mm/h")
        else:
            print("  No rain detected")
        
        print()
        print("⛈️ Thunderstorm Conditions:")
        if analysis['thunderstorm_conditions']:
            for condition in analysis['thunderstorm_conditions'][:3]:  # Show first 3
                print(f"  {condition}")
        else:
            print("  No thunderstorms detected")
        
        print()
        print("💾 Data saved to meteofrance_api_data.json")
        
        # Save to file
        with open('meteofrance_api_data.json', 'w', encoding='utf-8') as f:
            json.dump(forecast_data, f, indent=2, ensure_ascii=False)
            
        # Save analysis separately
        with open('meteofrance_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
            
    else:
        print("❌ Failed to fetch Météo-France API data")

if __name__ == "__main__":
    main() 