#!/usr/bin/env python3
"""
Test script for enhanced MeteoFrance API implementation.
"""

import sys
import os
sys.path.append('src')

from datetime import datetime, timedelta
from wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI

def test_enhanced_api():
    """Test the enhanced MeteoFrance API implementation."""
    
    print("Testing Enhanced MeteoFrance API Implementation")
    print("=" * 60)
    
    # Test coordinates
    lat = 41.79418
    lon = 9.259567
    location_name = "Conca"
    
    try:
        # Test the enhanced API
        api = EnhancedMeteoFranceAPI()
        
        print(f"Testing location: {location_name}")
        print(f"Coordinates: {lat}, {lon}")
        print()
        
        # Get complete forecast data
        complete_data = api.get_complete_forecast_data(lat, lon, location_name)
        
        print("1. COMPLETE DATA STRUCTURE")
        print("-" * 30)
        print(f"Location: {complete_data['location_name']}")
        print(f"Coordinates: ({complete_data['latitude']}, {complete_data['longitude']})")
        print(f"Hourly entries: {len(complete_data['hourly_data'])}")
        print(f"Daily entries: {len(complete_data['daily_data'])}")
        print(f"Probability entries: {len(complete_data['probability_data'])}")
        print(f"Thunderstorm entries: {len(complete_data['thunderstorm_data'])}")
        print(f"Rain probability entries: {len(complete_data['rain_probability_data'])}")
        print()
        
        # 2. HOURLY DATA ANALYSIS
        print("2. HOURLY DATA ANALYSIS")
        print("-" * 25)
        hourly_data = complete_data['hourly_data']
        if hourly_data:
            print(f"First entry: {hourly_data[0].timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"Last entry: {hourly_data[-1].timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"Sample entry:")
            sample = hourly_data[0]
            print(f"  Time: {sample.timestamp}")
            print(f"  Temperature: {sample.temperature}°C")
            print(f"  Wind: {sample.wind_speed}km/h, Gusts: {sample.wind_gusts}km/h")
            print(f"  Rain: {sample.rain_amount}mm/h")
            print(f"  Weather: {sample.weather_description}")
        print()
        
        # 3. DAILY DATA ANALYSIS
        print("3. DAILY DATA ANALYSIS")
        print("-" * 25)
        daily_data = complete_data['daily_data']
        if daily_data:
            print(f"Daily entries: {len(daily_data)}")
            for i, day in enumerate(daily_data[:3]):  # Show first 3 days
                print(f"Day {i+1}: {day['date']}")
                temp = day['temperature']
                print(f"  Temperature: {temp['min']}°C - {temp['max']}°C")
                precip = day['precipitation']
                print(f"  Precipitation: {precip['24h']}mm")
                if day['sun']:
                    print(f"  Sunrise: {day['sun']['rise'].strftime('%H:%M')}")
                    print(f"  Sunset: {day['sun']['set'].strftime('%H:%M')}")
        print()
        
        # 4. PROBABILITY DATA ANALYSIS
        print("4. PROBABILITY DATA ANALYSIS")
        print("-" * 30)
        probability_data = complete_data['probability_data']
        if probability_data:
            print(f"Probability entries: {len(probability_data)}")
            for i, prob in enumerate(probability_data[:5]):  # Show first 5
                print(f"Entry {i+1}: {prob.timestamp.strftime('%Y-%m-%d %H:%M')}")
                print(f"  Rain 3h: {prob.rain_3h}%")
                print(f"  Rain 6h: {prob.rain_6h}%")
                print(f"  Snow 3h: {prob.snow_3h}%")
                print(f"  Snow 6h: {prob.snow_6h}%")
                print(f"  Freezing: {prob.freezing}%")
        print()
        
        # 5. THUNDERSTORM DATA ANALYSIS
        print("5. THUNDERSTORM DATA ANALYSIS")
        print("-" * 30)
        thunderstorm_data = complete_data['thunderstorm_data']
        if thunderstorm_data:
            print(f"Thunderstorm entries: {len(thunderstorm_data)}")
            for storm in thunderstorm_data:
                print(f"  {storm.timestamp.strftime('%Y-%m-%d %H:%M')}: {storm.description}")
                print(f"    Icon: {storm.icon}, Rain: {storm.rain_amount}mm/h, Wind: {storm.wind_speed}km/h")
        else:
            print("No thunderstorm data found")
        print()
        
        # 6. RAIN PROBABILITY DATA ANALYSIS
        print("6. RAIN PROBABILITY DATA ANALYSIS")
        print("-" * 35)
        rain_prob_data = complete_data['rain_probability_data']
        if rain_prob_data:
            print(f"Rain probability entries: {len(rain_prob_data)}")
            entries_with_prob = [entry for entry in rain_prob_data if entry['has_rain_probability']]
            print(f"Entries with probability data: {len(entries_with_prob)}")
            
            for i, prob in enumerate(rain_prob_data[:5]):  # Show first 5
                print(f"Entry {i+1}: {prob['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                print(f"  Rain 3h: {prob['rain_3h']}%")
                print(f"  Rain 6h: {prob['rain_6h']}%")
                print(f"  Has probability: {prob['has_rain_probability']}")
        print()
        
        # 7. POSITION DATA ANALYSIS
        print("7. POSITION DATA ANALYSIS")
        print("-" * 25)
        position_data = complete_data['position_data']
        if position_data:
            print(f"Location: {position_data['name']}")
            print(f"Country: {position_data['country']}")
            print(f"Department: {position_data['department']}")
            print(f"Altitude: {position_data['altitude']}m")
            print(f"Timezone: {position_data['timezone']}")
        print()
        
        # 8. CURRENT DATA ANALYSIS
        print("8. CURRENT DATA ANALYSIS")
        print("-" * 25)
        current_data = complete_data['current_data']
        if current_data:
            print(f"Current time: {current_data['timestamp']}")
            print(f"Temperature: {current_data['temperature']}°C")
            print(f"Wind: {current_data['wind']['speed']}km/h, Gusts: {current_data['wind']['gust']}km/h")
            print(f"Rain: {current_data['rain']}mm/h")
            print(f"Weather: {current_data['weather']['desc']}")
        print()
        
        print("=" * 60)
        print("Enhanced API test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error testing enhanced API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_api()
    sys.exit(0 if success else 1) 