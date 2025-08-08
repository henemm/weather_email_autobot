#!/usr/bin/env python3
"""
Comprehensive analysis of the Meteo France Python API.
Understanding all endpoints and fields offered.
"""

import yaml
from meteofrance_api import MeteoFranceClient
import json
from datetime import datetime, date, timedelta
import inspect

def main():
    print("🔍 COMPREHENSIVE ANALYSIS: Meteo France Python API")
    print("=" * 60)
    print("Understanding all endpoints and fields offered")
    print()
    
    try:
        client = MeteoFranceClient()
        lat, lon = 47.6386, 6.8631
        
        print(f"📍 Test coordinates: {lat}, {lon}")
        print(f"📅 Test date: {date.today() + timedelta(days=1)}")
        print()
        
        # 1. Analyze the client object
        print("1. CLIENT OBJECT ANALYSIS:")
        print("-" * 40)
        
        print(f"Client type: {type(client)}")
        print(f"Client module: {client.__class__.__module__}")
        print(f"Client class: {client.__class__.__name__}")
        
        # Get all methods
        methods = [method for method in dir(client) if not method.startswith('_')]
        print(f"Available methods: {methods}")
        print()
        
        # 2. Analyze each method systematically
        print("2. METHOD ANALYSIS:")
        print("-" * 40)
        
        for method_name in methods:
            print(f"\n📋 METHOD: {method_name}")
            print("-" * 30)
            
            try:
                method = getattr(client, method_name)
                
                # Get method signature
                sig = inspect.signature(method)
                print(f"Signature: {sig}")
                
                # Get method docstring
                doc = method.__doc__
                if doc:
                    print(f"Docstring: {doc.strip()}")
                
                # Test method with different parameters
                test_params = [
                    (lat, lon),
                    (lat, lon, "france"),
                    (lat, lon, "world"),
                    ("Belfort",),
                    ("Belfort", "france"),
                ]
                
                for params in test_params:
                    try:
                        print(f"\n   Testing {method_name}{params}:")
                        result = method(*params)
                        print(f"   ✅ Result type: {type(result)}")
                        
                        # Analyze result object
                        if hasattr(result, '__dict__'):
                            print(f"   📊 Attributes: {list(result.__dict__.keys())}")
                            
                            # Check for raw_data
                            if hasattr(result, 'raw_data'):
                                print(f"   🔍 Raw data available")
                                raw_data = result.raw_data
                                if isinstance(raw_data, dict):
                                    print(f"   📋 Raw data keys: {list(raw_data.keys())}")
                                    
                                    # Analyze raw_data structure
                                    for key, value in raw_data.items():
                                        if isinstance(value, list) and len(value) > 0:
                                            print(f"   📅 {key}: {len(value)} entries")
                                            if len(value) > 0:
                                                first_item = value[0]
                                                if isinstance(first_item, dict):
                                                    print(f"   🔍 {key} first entry keys: {list(first_item.keys())}")
                                        elif isinstance(value, dict):
                                            print(f"   🔍 {key}: {list(value.keys())}")
                                        else:
                                            print(f"   📋 {key}: {type(value)}")
                        
                        # Check for forecast data
                        if hasattr(result, 'forecast') and result.forecast:
                            print(f"   📅 Forecast entries: {len(result.forecast)}")
                            
                            if len(result.forecast) > 0:
                                first_entry = result.forecast[0]
                                print(f"   🔍 Forecast first entry keys: {list(first_entry.keys())}")
                                
                                # Analyze first entry structure
                                for key, value in first_entry.items():
                                    if isinstance(value, dict):
                                        print(f"   📋 {key}: {list(value.keys())}")
                                        for subkey, subvalue in value.items():
                                            print(f"   📊 {key}.{subkey}: {type(subvalue)} = {subvalue}")
                                    else:
                                        print(f"   📊 {key}: {type(value)} = {value}")
                        
                        # Check for other data structures
                        if hasattr(result, 'properties'):
                            print(f"   📋 Properties available")
                            props = result.properties
                            if isinstance(props, dict):
                                print(f"   🔍 Properties keys: {list(props.keys())}")
                        
                        print()
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        continue
                
            except Exception as e:
                print(f"❌ Error analyzing {method_name}: {e}")
        
        # 3. Test specific data retrieval
        print("3. SPECIFIC DATA RETRIEVAL TEST:")
        print("-" * 40)
        
        # Test get_forecast thoroughly
        print("\n📊 Testing get_forecast thoroughly:")
        try:
            forecast = client.get_forecast(lat, lon)
            
            if hasattr(forecast, 'forecast') and forecast.forecast:
                print(f"Forecast entries: {len(forecast.forecast)}")
                
                # Analyze tomorrow's data
                tomorrow = date.today() + timedelta(days=1)
                tomorrow_entries = []
                
                for entry in forecast.forecast:
                    if 'dt' in entry:
                        entry_time = datetime.fromtimestamp(entry['dt'])
                        entry_date = entry_time.date()
                        if entry_date == tomorrow:
                            tomorrow_entries.append(entry)
                
                print(f"Tomorrow entries: {len(tomorrow_entries)}")
                
                if tomorrow_entries:
                    print("\n📅 Tomorrow's data structure:")
                    first_tomorrow = tomorrow_entries[0]
                    
                    for key, value in first_tomorrow.items():
                        if isinstance(value, dict):
                            print(f"   {key}: {list(value.keys())}")
                            for subkey, subvalue in value.items():
                                print(f"     {subkey}: {type(subvalue)} = {subvalue}")
                        else:
                            print(f"   {key}: {type(value)} = {value}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test get_rain thoroughly
        print("\n🌧️ Testing get_rain thoroughly:")
        try:
            rain_data = client.get_rain(lat, lon)
            
            if hasattr(rain_data, 'forecast') and rain_data.forecast:
                print(f"Rain forecast entries: {len(rain_data.forecast)}")
                
                if len(rain_data.forecast) > 0:
                    first_entry = rain_data.forecast[0]
                    print(f"Rain first entry: {first_entry}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n🎯 SUMMARY:")
        print("This analysis shows all available endpoints and fields in the Meteo France Python API.")
        print("Based on this, we can determine which data is actually available.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 