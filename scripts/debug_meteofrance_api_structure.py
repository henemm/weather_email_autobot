#!/usr/bin/env python3
"""
Debug script to explore MeteoFrance API response structure.
"""

import json
from meteofrance_api.client import MeteoFranceClient


def debug_api_structure():
    """Debug the actual structure of MeteoFrance API responses."""
    
    client = MeteoFranceClient()
    latitude = 43.2333
    longitude = 0.0833
    department = "65"
    
    print("=== MeteoFrance API Structure Debug ===")
    
    # Test forecast
    print("\n1. Testing forecast structure...")
    try:
        forecast = client.get_forecast(latitude, longitude)
        print(f"Forecast type: {type(forecast)}")
        print(f"Forecast dir: {dir(forecast)}")
        
        if hasattr(forecast, 'forecast'):
            print(f"Forecast.forecast type: {type(forecast.forecast)}")
            print(f"Forecast.forecast length: {len(forecast.forecast)}")
            
            if forecast.forecast:
                first_period = forecast.forecast[0]
                print(f"First period type: {type(first_period)}")
                print(f"First period dir: {dir(first_period)}")
                print(f"First period vars: {vars(first_period)}")
                
                # Try to access common attributes
                for attr in ['datetime', 'T', 'weather', 'precipitation_probability']:
                    if hasattr(first_period, attr):
                        value = getattr(first_period, attr)
                        print(f"  {attr}: {value} (type: {type(value)})")
                    else:
                        print(f"  {attr}: Not found")
        else:
            print("No 'forecast' attribute found")
            
    except Exception as e:
        print(f"Forecast error: {e}")
    
    # Test warnings
    print("\n2. Testing warnings structure...")
    try:
        warnings = client.get_warning_current_phenomenons(department)
        print(f"Warnings type: {type(warnings)}")
        print(f"Warnings dir: {dir(warnings)}")
        
        if hasattr(warnings, 'phenomenons_max_colors'):
            print(f"phenomenons_max_colors: {warnings.phenomenons_max_colors}")
        else:
            print("No 'phenomenons_max_colors' attribute found")
            
        # Check for other attributes
        for attr in ['phenomenons', 'domain_id']:
            if hasattr(warnings, attr):
                value = getattr(warnings, attr)
                print(f"  {attr}: {value} (type: {type(value)})")
            else:
                print(f"  {attr}: Not found")
                
    except Exception as e:
        print(f"Warnings error: {e}")
    
    # Test rain
    print("\n3. Testing rain structure...")
    try:
        rain = client.get_rain(latitude, longitude)
        print(f"Rain type: {type(rain)}")
        print(f"Rain dir: {dir(rain)}")
        
        if hasattr(rain, 'forecast'):
            print(f"Rain.forecast type: {type(rain.forecast)}")
            print(f"Rain.forecast length: {len(rain.forecast)}")
            
            if rain.forecast:
                first_period = rain.forecast[0]
                print(f"First rain period type: {type(first_period)}")
                print(f"First rain period dir: {dir(first_period)}")
                print(f"First rain period vars: {vars(first_period)}")
                
                # Try to access common attributes
                for attr in ['datetime', 'intensity']:
                    if hasattr(first_period, attr):
                        value = getattr(first_period, attr)
                        print(f"  {attr}: {value} (type: {type(value)})")
                    else:
                        print(f"  {attr}: Not found")
        else:
            print("No 'forecast' attribute found in rain")
            
    except Exception as e:
        print(f"Rain error: {e}")


if __name__ == "__main__":
    debug_api_structure() 