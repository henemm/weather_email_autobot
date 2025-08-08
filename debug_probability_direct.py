#!/usr/bin/env python3
"""
Debug script to test direct HTTP requests to MeteoFrance PROBABILITY_FORECAST endpoint.
"""

import yaml
import requests
import json
from datetime import datetime, date, timedelta

def main():
    print("🌧️ DEBUG: Direct HTTP Request to PROBABILITY_FORECAST")
    print("=" * 60)
    print("Testing direct HTTP requests to MeteoFrance API")
    print()
    
    try:
        # Load config to get API token
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Get API token
        api_token = config.get('meteofrance', {}).get('api_token', '')
        if not api_token:
            print("❌ No MeteoFrance API token found in config.yaml")
            return
        
        print(f"📍 Coordinates: 47.6386, 6.8631")
        print(f"📅 Target date: {date.today() + timedelta(days=1)}")
        print(f"🔑 Using API token: {api_token[:10]}...")
        print()
        
        # Test different API endpoints
        print("🔍 Testing different API endpoints:")
        print("-" * 50)
        
        # Test different endpoints that might be PROBABILITY_FORECAST
        endpoints = [
            f"https://webservice.meteofrance.com/v3/probability_forecast?token={api_token}&lat=47.6386&lon=6.8631",
            f"https://webservice.meteofrance.com/v3/forecast/probability?token={api_token}&lat=47.6386&lon=6.8631",
            f"https://webservice.meteofrance.com/v3/rain/probability?token={api_token}&lat=47.6386&lon=6.8631",
            f"https://webservice.meteofrance.com/v3/forecast?token={api_token}&lat=47.6386&lon=6.8631&type=probability",
            f"https://webservice.meteofrance.com/v3/forecast?token={api_token}&lat=47.6386&lon=6.8631&product=probability",
        ]
        
        for i, endpoint in enumerate(endpoints):
            print(f"Testing endpoint {i+1}: {endpoint}")
            try:
                response = requests.get(endpoint)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Got response data")
                    
                    # Check if there's forecast data
                    if 'forecast' in data:
                        forecast_data = data['forecast']
                        print(f"   📅 Forecast entries: {len(forecast_data)}")
                        
                        # Check first entry for rain_3h or probability data
                        if forecast_data:
                            first_entry = forecast_data[0]
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
                                print(f"   🎯 Endpoint: {endpoint}")
                                return
                    else:
                        print(f"   ❌ No forecast data in response")
                        print(f"   🔍 Response keys: {list(data.keys())}")
                else:
                    print(f"   ❌ Failed: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🎯 CONCLUSION:")
        print("If no endpoint provides rain_3h or probability data:")
        print("1. The PROBABILITY_FORECAST endpoint might not exist")
        print("2. The endpoint might require different parameters")
        print("3. The endpoint might be in a different API version")
        print("4. The endpoint might need different authentication")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 