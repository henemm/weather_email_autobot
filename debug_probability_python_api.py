#!/usr/bin/env python3
"""
Debug script to find the correct method in meteofrance-api Python library for rain probability.
I must stay with the Python API as instructed.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌧️ DEBUG: Finding Rain Probability in Python API")
    print("=" * 50)
    print("Staying with meteofrance-api Python library")
    print()
    
    try:
        client = MeteoFranceClient()
        lat, lon = 47.6386, 6.8631
        
        print(f"📍 Coordinates: {lat}, {lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Test get_forecast with different parameters
        print("🔍 Testing get_forecast with different parameters:")
        print("-" * 40)
        
        # Test different parameter combinations
        test_params = [
            (lat, lon),
            (lat, lon, "france"),
            (lat, lon, "world"),
        ]
        
        for params in test_params:
            print(f"Testing get_forecast{params}:")
            try:
                forecast = client.get_forecast(*params)
                
                if hasattr(forecast, 'forecast') and forecast.forecast:
                    # Check first entry for any probability-related fields
                    first_entry = forecast.forecast[0]
                    
                    print(f"   First entry keys: {list(first_entry.keys())}")
                    
                    # Look for any fields that might contain probability
                    for key, value in first_entry.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'prob' in subkey.lower() or 'rain_3h' in subkey.lower():
                                    print(f"   Found {key}.{subkey}: {subvalue}")
                    
                    # Check if there are any other fields that might contain probability
                    for key, value in first_entry.items():
                        if isinstance(value, dict):
                            print(f"   {key}: {value}")
                
            except Exception as e:
                print(f"   Error: {e}")
        
        # Test get_rain with different parameters
        print("\n🔍 Testing get_rain with different parameters:")
        print("-" * 40)
        
        for params in test_params:
            print(f"Testing get_rain{params}:")
            try:
                rain_data = client.get_rain(*params)
                
                if hasattr(rain_data, 'forecast') and rain_data.forecast:
                    # Check first entry for any probability-related fields
                    first_entry = rain_data.forecast[0]
                    
                    print(f"   First entry keys: {list(first_entry.keys())}")
                    
                    # Look for any fields that might contain probability
                    for key, value in first_entry.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'prob' in subkey.lower() or 'rain_3h' in subkey.lower():
                                    print(f"   Found {key}.{subkey}: {subvalue}")
                    
                    # Check if there are any other fields that might contain probability
                    for key, value in first_entry.items():
                        if isinstance(value, dict):
                            print(f"   {key}: {value}")
                
            except Exception as e:
                print(f"   Error: {e}")
        
        # Test if there are other methods I haven't tried
        print("\n🔍 Testing other methods:")
        print("-" * 40)
        
        methods = [method for method in dir(client) if not method.startswith('_')]
        print(f"Available methods: {methods}")
        
        # Test methods that might have probability data
        for method_name in methods:
            if 'prob' in method_name.lower() or 'forecast' in method_name.lower():
                print(f"\nTesting {method_name}:")
                try:
                    method = getattr(client, method_name)
                    
                    # Try different parameter combinations
                    for params in test_params:
                        try:
                            result = method(*params)
                            print(f"   ✅ {method_name}{params} -> {type(result)}")
                            
                            if hasattr(result, '__dict__'):
                                print(f"   📊 Attributes: {list(result.__dict__.keys())}")
                                
                                if hasattr(result, 'forecast') and result.forecast:
                                    first_entry = result.forecast[0]
                                    print(f"   🔍 First entry keys: {list(first_entry.keys())}")
                                    
                                    # Look for probability fields
                                    for key, value in first_entry.items():
                                        if isinstance(value, dict):
                                            for subkey, subvalue in value.items():
                                                if 'prob' in subkey.lower() or 'rain_3h' in subkey.lower():
                                                    print(f"   🎉 Found {key}.{subkey}: {subvalue}")
                                                    return
                        
                        except Exception as e:
                            print(f"   ❌ {method_name}{params} -> Error: {e}")
                
                except Exception as e:
                    print(f"   ❌ Error accessing {method_name}: {e}")
        
        print("\n🎯 CONCLUSION:")
        print("If the Python API doesn't provide rain probability data:")
        print("1. I might be using the wrong method")
        print("2. I might be using the wrong parameters")
        print("3. I might be looking in the wrong field")
        print("4. The API might not provide this data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 