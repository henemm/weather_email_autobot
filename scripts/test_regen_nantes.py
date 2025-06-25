#!/usr/bin/env python3
"""
Simple test script for rain forecast in Nantes (44000) for tomorrow 9-11 AM.
Compares multiple weather APIs to identify discrepancies.
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pytz

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome_wcs import fetch_arome_wcs, get_available_arome_layers
from wetter.fetch_openmeteo import fetch_openmeteo_forecast
from utils.env_loader import get_env_var

def get_openmeteo_rain_for_timestamp(latitude: float, longitude: float, timestamp_str: str):
    """
    Get Open-Meteo rain data for a specific timestamp.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        timestamp_str: UTC timestamp string (e.g., "2025-06-24T15:00:00Z")
        
    Returns:
        Dict with rain data for the specified timestamp
    """
    try:
        # Fetch forecast data
        forecast_data = fetch_openmeteo_forecast(latitude, longitude)
        
        if not forecast_data or "hourly" not in forecast_data:
            return None
        
        hourly = forecast_data["hourly"]
        times = hourly.get("time", [])
        precipitation = hourly.get("precipitation", [])
        
        if not times or not precipitation:
            return None
        
        # Find closest time match
        closest_time = None
        min_diff = float('inf')
        
        for i, time_str in enumerate(times):
            try:
                # Open-Meteo returns ISO format like "2025-06-24T15:00:00"
                time_obj = datetime.fromisoformat(time_str)
                target_time = datetime.fromisoformat(timestamp_str.replace('Z', ''))
                diff = abs((time_obj - target_time).total_seconds())
                
                if diff < min_diff:
                    min_diff = diff
                    closest_time = i
            except Exception as e:
                print(f"  ⚠️ Time parsing error: {e}")
                continue
        
        if closest_time is not None:
            # Extract data for closest time
            result = {
                'precipitation_mmh': precipitation[closest_time] if precipitation[closest_time] is not None else 0.0,
                'time_diff_hours': min_diff / 3600.0
            }
            return result
        else:
            return None
            
    except Exception as e:
        print(f"  ❌ Open-Meteo error: {e}")
        return None

def get_available_timestamps_for_model(model: str, field: str = "PRECIPITATION"):
    """
    Get available timestamps for a specific model and field.
    
    Args:
        model: Model name (e.g., "AROME_HR", "PIAF_NOWCAST")
        field: Field name (e.g., "PRECIPITATION", "CAPE")
        
    Returns:
        List of available timestamps as datetime objects
    """
    try:
        layers = get_available_arome_layers(model)
        field_layers = [l for l in layers if field.upper() in l.upper()]
        
        timestamps = []
        for layer in field_layers:
            if '___' in layer:
                time_part = layer.split('___')[-1]
                if 'T' in time_part and 'Z' in time_part:
                    # Extract just the timestamp part before any duration
                    timestamp_part = time_part.split('_PT')[0] if '_PT' in time_part else time_part
                    try:
                        # Parse timestamp (e.g., "2025-06-24T15.00.00Z")
                        timestamp_str = timestamp_part.replace('.', ':')
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        timestamps.append(dt)
                    except:
                        continue
        
        return sorted(list(set(timestamps)))  # Remove duplicates and sort
    except Exception as e:
        print(f"Error getting timestamps for {model}: {e}")
        return []

def main():
    """Main test function for Nantes rain forecast."""
    # Nantes coordinates (44000)
    latitude = 47.2184
    longitude = -1.5536
    
    print(f"🌧️ Testing rain forecast for Nantes (44000) - TODAY EVENING")
    print(f"📍 Coordinates: {latitude}°N, {longitude}°E")
    print(f"🎯 Testing for TODAY (25th June) EVENING when Météo-France forecasts rain")
    
    # Test times for today evening (25th June) when rain is forecasted
    test_times = [
        "2025-06-25T18:00:00Z",  # Today 20:00 CEST
        "2025-06-25T19:00:00Z",  # Today 21:00 CEST
        "2025-06-25T20:00:00Z",  # Today 22:00 CEST
    ]
    
    print(f"✅ Using {len(test_times)} test timestamps for today evening: {test_times}")
    print()
    
    results = {
        "location": "Nantes (44000)",
        "coordinates": [latitude, longitude],
        "test_times": test_times,
        "data": []
    }
    
    for timestamp_str in test_times:
        time_data = {
            "timestamp": timestamp_str,
            "apis": {}
        }
        
        print(f"🕐 Testing time: {timestamp_str}")
        
        # Test AROME_HR precipitation
        print(f"  🔍 Testing AROME_HR precipitation...")
        try:
            precip_result = fetch_arome_wcs(
                latitude, longitude, 
                model="AROME_HR", 
                field="PRECIPITATION",
                timestamp=timestamp_str
            )
            precip_value = precip_result.get("value") if precip_result else None
            time_data["apis"]["AROME_HR"] = {
                "precipitation_mmh": precip_value,
                "layer_name": precip_result.get("layer_name") if precip_result else None,
                "time_diff_hours": precip_result.get("time_diff_hours") if precip_result else None
            }
            print(f"    ✅ Precipitation: {precip_value} mm/h")
        except Exception as e:
            print(f"    ❌ AROME_HR error: {e}")
            time_data["apis"]["AROME_HR"] = {"error": str(e)}
        
        # Test PIAF_NOWCAST precipitation
        print(f"  ⚡ Testing PIAF_NOWCAST precipitation...")
        try:
            precip_result = fetch_arome_wcs(
                latitude, longitude, 
                model="PIAF_NOWCAST", 
                field="PRECIPITATION",
                timestamp=timestamp_str
            )
            precip_value = precip_result.get("value") if precip_result else None
            time_data["apis"]["PIAF_NOWCAST"] = {
                "precipitation_mmh": precip_value,
                "layer_name": precip_result.get("layer_name") if precip_result else None,
                "time_diff_hours": precip_result.get("time_diff_hours") if precip_result else None
            }
            print(f"    ✅ Precipitation: {precip_value} mm/h")
        except Exception as e:
            print(f"    ❌ PIAF_NOWCAST error: {e}")
            time_data["apis"]["PIAF_NOWCAST"] = {"error": str(e)}
        
        # Test Open-Meteo precipitation
        print(f"  🌍 Testing OPENMETEO_GLOBAL precipitation...")
        try:
            openmeteo_result = get_openmeteo_rain_for_timestamp(latitude, longitude, timestamp_str)
            if openmeteo_result:
                time_data["apis"]["OPENMETEO_GLOBAL"] = {
                    "precipitation_mmh": openmeteo_result.get("precipitation_mmh"),
                    "time_diff_hours": openmeteo_result.get("time_diff_hours")
                }
                print(f"    ✅ Precipitation: {openmeteo_result.get('precipitation_mmh')} mm/h")
            else:
                print(f"    ❌ No Open-Meteo data")
                time_data["apis"]["OPENMETEO_GLOBAL"] = {"error": "No data"}
        except Exception as e:
            print(f"    ❌ Open-Meteo error: {e}")
            time_data["apis"]["OPENMETEO_GLOBAL"] = {"error": str(e)}
        
        results["data"].append(time_data)
        print()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/nantes_rain_forecast_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Results saved to: {output_file}")
    
    # Print summary
    print(f"\n📋 Summary:")
    for time_data in results["data"]:
        print(f"  {time_data['timestamp']}:")
        for api, data in time_data["apis"].items():
            if "error" in data:
                print(f"    {api}: ERROR - {data['error']}")
            else:
                print(f"    {api}: {data.get('precipitation_mmh', 'None')} mm/h")

if __name__ == "__main__":
    main() 