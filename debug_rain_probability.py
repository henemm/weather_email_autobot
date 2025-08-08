#!/usr/bin/env python3
"""
Debug script to investigate rain probability data structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI

def debug_rain_probability_structure():
    """Debug the rain probability data structure."""
    
    print("DEBUGGING RAIN PROBABILITY STRUCTURE")
    print("=" * 50)
    
    # Initialize API
    api = EnhancedMeteoFranceAPI()
    
    # Fetch data for a test point
    lat, lon = 42.219882, 8.980494  # Petra point 1
    point_name = "Petra_point_1"
    
    print(f"Fetching data for {point_name} ({lat}, {lon})...")
    
    try:
        point_data = api.get_complete_forecast_data(lat, lon, point_name)
        
        # Get hourly data
        hourly_data = point_data.get('hourly_data', [])
        print(f"Found {len(hourly_data)} hourly entries")
        
        # Get rain probability data
        rain_prob_data = point_data.get('rain_probability_data', [])
        print(f"Found {len(rain_prob_data)} rain probability entries")
        
        # Check how many entries have has_rain_probability: True
        true_count = 0
        false_count = 0
        
        for entry in rain_prob_data:
            has_rain_prob = entry.get('has_rain_probability', False)
            if has_rain_prob:
                true_count += 1
            else:
                false_count += 1
        
        print(f"Entries with has_rain_probability: True: {true_count}")
        print(f"Entries with has_rain_probability: False: {false_count}")
        
        # Check rain_3h and rain_6h values
        print(f"\nChecking rain_3h and rain_6h values:")
        none_count = 0
        value_count = 0
        
        for i, entry in enumerate(rain_prob_data[:5]):  # Check first 5 entries
            rain_3h = entry.get('rain_3h')
            rain_6h = entry.get('rain_6h')
            has_rain_prob = entry.get('has_rain_probability', False)
            timestamp = entry.get('timestamp')
            
            print(f"Entry {i+1}: timestamp={timestamp}, has_rain_prob={has_rain_prob}, rain_3h={rain_3h}, rain_6h={rain_6h}")
            
            if rain_3h is None and rain_6h is None:
                none_count += 1
            else:
                value_count += 1
        
        print(f"Entries with rain_3h=None and rain_6h=None: {none_count}")
        print(f"Entries with actual values: {value_count}")
        
        if rain_prob_data:
            # Examine first rain probability entry
            first_prob_entry = rain_prob_data[0]
            print(f"\nFirst rain probability entry type: {type(first_prob_entry)}")
            print(f"First rain probability entry: {first_prob_entry}")
            
            # List all attributes
            if hasattr(first_prob_entry, '__dict__'):
                print(f"\nAll attributes:")
                for attr_name, attr_value in first_prob_entry.__dict__.items():
                    print(f"  {attr_name}: {attr_value}")
            
            # Check for probability-related attributes
            print(f"\nProbability-related attributes:")
            for attr_name in dir(first_prob_entry):
                if 'prob' in attr_name.lower() or 'chance' in attr_name.lower():
                    try:
                        attr_value = getattr(first_prob_entry, attr_name)
                        print(f"  {attr_name}: {attr_value}")
                    except Exception as e:
                        print(f"  {attr_name}: ERROR - {e}")
            
            # Check for precipitation-related attributes
            print(f"\nPrecipitation-related attributes:")
            for attr_name in dir(first_prob_entry):
                if 'precip' in attr_name.lower() or 'rain' in attr_name.lower():
                    try:
                        attr_value = getattr(first_prob_entry, attr_name)
                        print(f"  {attr_name}: {attr_value}")
                    except Exception as e:
                        print(f"  {attr_name}: ERROR - {e}")
            
            # Check for timestamp-related attributes
            print(f"\nTimestamp-related attributes:")
            for attr_name in dir(first_prob_entry):
                if 'time' in attr_name.lower() or 'date' in attr_name.lower():
                    try:
                        attr_value = getattr(first_prob_entry, attr_name)
                        print(f"  {attr_name}: {attr_value}")
                    except Exception as e:
                        print(f"  {attr_name}: ERROR - {e}")
            
            # Check if there's a separate probability data structure
            print(f"\nChecking for probability data in point_data:")
            for key, value in point_data.items():
                if 'prob' in key.lower() or 'chance' in key.lower():
                    print(f"  {key}: {type(value)} - {len(value) if hasattr(value, '__len__') else 'N/A'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_rain_probability_structure() 