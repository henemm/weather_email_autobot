#!/usr/bin/env python3
"""
Debug script to find the correct API method for gust data.
The user expects 55 km/h gusts for Belfort, so I must be using the wrong API method.
"""

import yaml
import requests
import json
from datetime import datetime, date, timedelta

def main():
    print("🌪️ DEBUG: Finding Correct API Method for Gust Data")
    print("=" * 60)
    
    try:
        # Load config to get API token
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Get API token
        api_token = config.get('meteofrance', {}).get('api_token', '')
        if not api_token:
            print("❌ No MeteoFrance API token found in config.yaml")
            return
        
        print(f"📍 Belfort coordinates: 47.6386, 6.8631")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print(f"🔑 Using API token: {api_token[:10]}...")
        print()
        
        # Test direct API calls to MeteoFrance
        print("🔍 Testing direct MeteoFrance API calls:")
        print("-" * 50)
        
        # 1. Test the forecast API endpoint directly
        print("1. Testing direct forecast API:")
        print("-" * 30)
        
        forecast_url = f"https://webservice.meteofrance.com/v3/forecast?token={api_token}&lat=47.6386&lon=6.8631"
        
        try:
            response = requests.get(forecast_url)
            print(f"   Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Got response data")
                
                # Check if there's forecast data
                if 'forecast' in data:
                    forecast_data = data['forecast']
                    print(f"   📅 Forecast entries: {len(forecast_data)}")
                    
                    # Check first entry for wind data
                    if forecast_data:
                        first_entry = forecast_data[0]
                        print(f"   🔍 First entry keys: {list(first_entry.keys())}")
                        
                        if 'wind' in first_entry:
                            wind_data = first_entry['wind']
                            print(f"   🌪️ Wind data: {wind_data}")
                            
                            # Check for gust data
                            if 'gust' in wind_data:
                                gust = wind_data['gust']
                                print(f"   💨 Gust value: {gust}")
                                
                                if gust > 0:
                                    print(f"   ✅ Found non-zero gust!")
                                else:
                                    print(f"   ❌ Gust is still 0")
                        else:
                            print(f"   ❌ No wind data in first entry")
                else:
                    print(f"   ❌ No forecast data in response")
            else:
                print(f"   ❌ API request failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 2. Test different API endpoints
        print("\n2. Testing different API endpoints:")
        print("-" * 30)
        
        # Test different endpoints that might have gust data
        endpoints = [
            f"https://webservice.meteofrance.com/v3/forecast?token={api_token}&lat=47.6386&lon=6.8631",
            f"https://webservice.meteofrance.com/v3/forecast?token={api_token}&lat=47.6386&lon=6.8631&domain=france",
            f"https://webservice.meteofrance.com/v3/forecast?token={api_token}&lat=47.6386&lon=6.8631&domain=world",
        ]
        
        for i, endpoint in enumerate(endpoints):
            print(f"   Testing endpoint {i+1}:")
            try:
                response = requests.get(endpoint)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'forecast' in data and data['forecast']:
                        first_entry = data['forecast'][0]
                        if 'wind' in first_entry:
                            wind_data = first_entry['wind']
                            gust = wind_data.get('gust', 0)
                            print(f"      Gust: {gust}")
                            
                            if gust > 0:
                                print(f"      ✅ Found non-zero gust!")
                                break
                else:
                    print(f"      ❌ Failed: {response.text[:100]}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        # 3. Test if gust data is in a different field
        print("\n3. Checking for gust data in different fields:")
        print("-" * 30)
        
        try:
            response = requests.get(forecast_url)
            if response.status_code == 200:
                data = response.json()
                
                if 'forecast' in data and data['forecast']:
                    first_entry = data['forecast'][0]
                    
                    # Check all fields for wind-related data
                    for key, value in first_entry.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'gust' in subkey.lower() or 'wind' in subkey.lower():
                                    print(f"   Found {key}.{subkey}: {subvalue}")
                        
                        # Check if the field itself contains wind data
                        if 'gust' in key.lower() or 'wind' in key.lower():
                            print(f"   Found {key}: {value}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n🎯 CONCLUSION:")
        print("If all API calls return 0 for gust data:")
        print("1. The MeteoFrance API might not provide gust data for this location")
        print("2. Gust data might require a different API endpoint")
        print("3. Gust data might be calculated from other parameters")
        print("4. The API token might not have access to gust data")
        print("5. The user might be referring to a different data source")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 