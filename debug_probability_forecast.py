#!/usr/bin/env python3
"""
Debug script to test PROBABILITY_FORECAST endpoint for rain probability data.
User says: meteo_france / PROBABILITY_FORECAST | rain_3h
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta

def main():
    print("🌧️ DEBUG: PROBABILITY_FORECAST Endpoint")
    print("=" * 50)
    print("Testing meteo_france / PROBABILITY_FORECAST | rain_3h")
    print()
    
    try:
        client = MeteoFranceClient()
        lat, lon = 47.6386, 6.8631
        
        print(f"📍 Coordinates: {lat}, {lon}")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print()
        
        # Test different API methods that might be PROBABILITY_FORECAST
        print("🔍 Testing different API methods:")
        print("-" * 40)
        
        # Get all available methods
        methods = [method for method in dir(client) if not method.startswith('_')]
        print(f"Available methods: {methods}")
        print()
        
        # Test each method systematically
        for method_name in methods:
            print(f"Testing method: {method_name}")
            print("-" * 30)
            
            try:
                method = getattr(client, method_name)
                
                # Test different parameter combinations
                test_params = [
                    (lat, lon),
                    (lat, lon, "france"),
                    (lat, lon, "world"),
                ]
                
                for params in test_params:
                    try:
                        result = method(*params)
                        print(f"   ✅ {method_name}{params} -> {type(result)}")
                        
                        # Check if result has probability data
                        if hasattr(result, '__dict__'):
                            print(f"   📊 Attributes: {list(result.__dict__.keys())}")
                            
                            # Check for forecast data
                            if hasattr(result, 'forecast') and result.forecast:
                                print(f"   📅 Has forecast data: {len(result.forecast)} entries")
                                
                                # Check first entry for rain_3h or probability data
                                first_entry = result.forecast[0]
                                print(f"   🔍 First entry keys: {list(first_entry.keys())}")
                                
                                # Look for rain_3h or probability fields
                                rain_3h = first_entry.get('rain_3h', 'N/A')
                                rain_prob = first_entry.get('rain_probability', 'N/A')
                                probability = first_entry.get('probability', 'N/A')
                                
                                print(f"   💧 rain_3h: {rain_3h}")
                                print(f"   💧 rain_probability: {rain_prob}")
                                print(f"   💧 probability: {probability}")
                                
                                if rain_3h != 'N/A' or rain_prob != 'N/A' or probability != 'N/A':
                                    print(f"   🎉 FOUND PROBABILITY DATA!")
                                    print(f"   🎯 Method: {method_name}")
                                    print(f"   🎯 Params: {params}")
                                    return
                        
                        # Check if result has raw_data
                        if hasattr(result, 'raw_data'):
                            print(f"   🔍 Raw data available")
                            raw_data = result.raw_data
                            if isinstance(raw_data, dict):
                                # Look for probability data in raw_data
                                for key, value in raw_data.items():
                                    if isinstance(value, dict) and ('rain_3h' in value or 'probability' in value):
                                        print(f"   💧 Found {key}: {value}")
                                        
                                        if 'rain_3h' in value or 'probability' in value:
                                            print(f"   🎉 FOUND PROBABILITY DATA IN RAW DATA!")
                                            print(f"   🎯 Method: {method_name}")
                                            print(f"   🎯 Params: {params}")
                                            return
                        
                    except Exception as e:
                        print(f"   ❌ {method_name}{params} -> Error: {e}")
                        continue
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error accessing method {method_name}: {e}")
                print()
        
        print("🎯 CONCLUSION:")
        print("If no method provides rain_3h or probability data:")
        print("1. The PROBABILITY_FORECAST endpoint might not be available in meteofrance-api")
        print("2. The endpoint might require different parameters")
        print("3. The endpoint might be in a different library")
        print("4. The endpoint might need direct HTTP requests")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 