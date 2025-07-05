#!/usr/bin/env python3
"""
Test alternative Météo-France API calls to get thunderstorm data.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meteofrance_api.client import MeteoFranceClient


def test_alternative_api_calls():
    """Test alternative API calls to get thunderstorm data."""
    
    print("🔍 TESTING ALTERNATIVE MÉTÉO-FRANCE API CALLS")
    print("=" * 60)
    
    # Test coordinates (Asco)
    latitude = 42.426238
    longitude = 8.900291
    
    print(f"Testing coordinates: {latitude}, {longitude}")
    print()
    
    try:
        client = MeteoFranceClient()
        
        # Test 1: Get current weather
        print("📊 TEST 1: Current Weather")
        print("-" * 30)
        try:
            current_weather = client.get_current_weather(latitude, longitude)
            print(f"Current weather: {current_weather}")
        except Exception as e:
            print(f"❌ Current weather failed: {e}")
        print()
        
        # Test 2: Get rain forecast
        print("📊 TEST 2: Rain Forecast")
        print("-" * 30)
        try:
            rain_forecast = client.get_rain(latitude, longitude)
            print(f"Rain forecast: {rain_forecast}")
        except Exception as e:
            print(f"❌ Rain forecast failed: {e}")
        print()
        
        # Test 3: Get weather alerts
        print("📊 TEST 3: Weather Alerts")
        print("-" * 30)
        try:
            # Try different department codes
            departments = ["2A", "2B", "20"]  # Corse-du-Sud, Haute-Corse, Corse
            for dept in departments:
                try:
                    alerts = client.get_warning_current_phenomenons(dept)
                    print(f"Alerts for department {dept}: {alerts}")
                except Exception as e:
                    print(f"❌ Alerts for {dept} failed: {e}")
        except Exception as e:
            print(f"❌ Weather alerts failed: {e}")
        print()
        
        # Test 4: Get detailed forecast with different parameters
        print("📊 TEST 4: Detailed Forecast")
        print("-" * 30)
        try:
            forecast = client.get_forecast(latitude, longitude)
            
            # Look for thunderstorm indicators in all entries
            thunderstorm_entries = []
            for i, entry in enumerate(forecast.forecast):
                weather = entry.get('weather', {})
                if isinstance(weather, dict):
                    desc = weather.get('desc', '').lower()
                    if any(keyword in desc for keyword in ['orage', 'thunder', 'storm']):
                        thunderstorm_entries.append({
                            'index': i,
                            'entry': entry
                        })
            
            print(f"Found {len(thunderstorm_entries)} entries with thunderstorm indicators:")
            for entry in thunderstorm_entries:
                print(f"  Entry {entry['index']}: {entry['entry'].get('weather', {})}")
                
        except Exception as e:
            print(f"❌ Detailed forecast failed: {e}")
        print()
        
        # Test 5: Check if there are other API methods
        print("📊 TEST 5: Available API Methods")
        print("-" * 30)
        try:
            # List all available methods
            methods = [method for method in dir(client) if not method.startswith('_')]
            print("Available client methods:")
            for method in methods:
                print(f"  - {method}")
        except Exception as e:
            print(f"❌ Method listing failed: {e}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_alternative_api_calls() 