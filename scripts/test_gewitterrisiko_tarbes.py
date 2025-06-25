#!/usr/bin/env python3
"""
Test script for thunderstorm risk analysis in Tarbes, France.
Tests multiple weather APIs and calculates thunderstorm risk scores.
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pytz

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome_wcs import fetch_arome_wcs
from wetter.fetch_openmeteo import fetch_openmeteo_forecast
from wetter.warning import fetch_warnings
from utils.env_loader import get_env_var

def calculate_thunderstorm_risk(cape_value, wind_gusts=None, precipitation=None, temperature=None):
    """
    Calculate thunderstorm risk score based on available meteorological parameters.
    
    Args:
        cape_value: CAPE value in J/kg
        wind_gusts: Wind gust speed in m/s
        precipitation: Precipitation rate in mm/h
        temperature: Temperature in °C
        
    Returns:
        Dict with risk score and details
    """
    risk_score = 0
    risk_factors = {}
    
    # CAPE-based risk (primary factor)
    if cape_value is not None:
        if cape_value < 500:
            cape_risk = 1  # Low
        elif cape_value < 1000:
            cape_risk = 2  # Moderate
        elif cape_value < 2000:
            cape_risk = 3  # High
        else:
            cape_risk = 4  # Very high
        risk_score += cape_risk * 3  # CAPE gets highest weight
        risk_factors['CAPE'] = {'value': cape_value, 'risk': cape_risk, 'weight': 3}
    else:
        risk_factors['CAPE'] = {'value': None, 'risk': 0, 'weight': 3}
    
    # Wind gust-based risk (dynamics indicator)
    if wind_gusts is not None:
        if wind_gusts < 10:
            wind_risk = 1
        elif wind_gusts < 20:
            wind_risk = 2
        elif wind_gusts < 30:
            wind_risk = 3
        else:
            wind_risk = 4
        risk_score += wind_risk * 2
        risk_factors['Wind_Gusts'] = {'value': wind_gusts, 'risk': wind_risk, 'weight': 2}
    else:
        risk_factors['Wind_Gusts'] = {'value': None, 'risk': 0, 'weight': 2}
    
    # Precipitation-based risk (moisture indicator)
    if precipitation is not None:
        if precipitation < 1:
            precip_risk = 1
        elif precipitation < 5:
            precip_risk = 2
        elif precipitation < 10:
            precip_risk = 3
        else:
            precip_risk = 4
        risk_score += precip_risk * 1
        risk_factors['Precipitation'] = {'value': precipitation, 'risk': precip_risk, 'weight': 1}
    else:
        risk_factors['Precipitation'] = {'value': None, 'risk': 0, 'weight': 1}
    
    # Temperature-based risk (energy indicator)
    if temperature is not None:
        if temperature < 15:
            temp_risk = 1
        elif temperature < 25:
            temp_risk = 2
        elif temperature < 30:
            temp_risk = 3
        else:
            temp_risk = 4
        risk_score += temp_risk * 1
        risk_factors['Temperature'] = {'value': temperature, 'risk': temp_risk, 'weight': 1}
    else:
        risk_factors['Temperature'] = {'value': None, 'risk': 0, 'weight': 1}
    
    # Normalize risk score (max possible: 4*3 + 4*2 + 4*1 + 4*1 = 20)
    max_possible_score = 20
    normalized_score = risk_score / max_possible_score if max_possible_score > 0 else 0
    
    # Determine risk level
    if normalized_score < 0.25:
        risk_level = "niedrig"
    elif normalized_score < 0.5:
        risk_level = "moderat"
    elif normalized_score < 0.75:
        risk_level = "hoch"
    else:
        risk_level = "sehr hoch"
    
    return {
        'risk_score': normalized_score,
        'risk_level': risk_level,
        'raw_score': risk_score,
        'factors': risk_factors,
        'note': 'SHEAR data not available - using CAPE, wind gusts, precipitation, and temperature'
    }

def get_openmeteo_data_for_timestamp(latitude: float, longitude: float, timestamp_str: str):
    """
    Get Open-Meteo data for a specific timestamp.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        timestamp_str: UTC timestamp string (e.g., "2025-06-24T17:00:00Z")
        
    Returns:
        Dict with weather data for the specified timestamp and metadata
    """
    try:
        # Fetch forecast data
        forecast_data = fetch_openmeteo_forecast(latitude, longitude)
        
        if not forecast_data or "hourly" not in forecast_data:
            return None
        
        hourly = forecast_data["hourly"]
        times = hourly.get("time", [])
        
        if not times:
            return None
        
        # Parse target timestamp
        target_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        
        # Find closest time match
        closest_time = None
        min_diff = float('inf')
        
        for i, time_str in enumerate(times):
            try:
                time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                target_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                diff = abs((time_obj - target_time).total_seconds())
                
                if diff < min_diff:
                    min_diff = diff
                    closest_time = i
            except:
                continue
        
        if closest_time is not None:
            # Extract data for closest time
            result = {
                'temperature_c': hourly.get('temperature_2m', [None])[closest_time],
                'precipitation_mmh': hourly.get('precipitation', [None])[closest_time],
                'wind_speed_ms': hourly.get('wind_speed_10m', [None])[closest_time],
                'wind_gusts_ms': hourly.get('wind_gusts_10m', [None])[closest_time],
                'weather_code': hourly.get('weather_code', [None])[closest_time],
                'time_diff_hours': min_diff / 3600 if min_diff != float('inf') else None
            }
            return result
        
        return None
        
    except Exception as e:
        print(f"Open-Meteo error: {e}")
        return None

def test_tarbes_thunderstorm_risk():
    """Test thunderstorm risk analysis for Tarbes, France."""
    
    # Tarbes coordinates (65000, France)
    latitude = 43.2333
    longitude = 0.0833
    
    # Test time points: today evening to tomorrow noon
    cest_tz = pytz.timezone('Europe/Paris')
    now = datetime.now(cest_tz)
    
    # Define test time points
    test_times = [
        now.replace(hour=17, minute=0, second=0, microsecond=0),  # Today 17:00 CEST
        now.replace(hour=20, minute=0, second=0, microsecond=0),  # Today 20:00 CEST
        (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0),   # Tomorrow 08:00 CEST
        (now + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0),  # Tomorrow 11:00 CEST
        (now + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0),  # Tomorrow 14:00 CEST
        (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0),  # Tomorrow 17:00 CEST
    ]
    
    results = {
        "location": "Tarbes, France",
        "coordinates": [latitude, longitude],
        "test_timestamp": now.isoformat(),
        "time_points": []
    }
    
    print(f"🌩️ Testing thunderstorm risk for Tarbes, France")
    print(f"📍 Coordinates: {latitude}, {longitude}")
    print(f"🕒 Test time points: {len(test_times)}")
    print()
    
    for i, test_time in enumerate(test_times):
        print(f"⏰ Testing time point {i+1}: {test_time.strftime('%Y-%m-%d %H:%M CEST')}")
        
        # Convert to UTC for API calls
        utc_time = test_time.astimezone(pytz.UTC)
        timestamp_str = utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Initialize result structure for this time point
        time_point_result = {
            "timestamp": timestamp_str,
            "apis": {}
        }
        
        print(f"\n🕐 Testing time point: {timestamp_str}")
        
        # Test AROME_HR
        print(f"  🔍 Testing AROME_HR...")
        try:
            # Test CAPE
            cape_result = fetch_arome_wcs(
                latitude, longitude, 
                model="AROME_HR", 
                field="CAPE",
                timestamp=timestamp_str
            )
            cape_value = cape_result.get("value") if cape_result else None
            
            # Test temperature
            temp_result = fetch_arome_wcs(
                latitude, longitude, 
                model="AROME_HR", 
                field="TEMPERATURE",
                timestamp=timestamp_str
            )
            temp_value = temp_result.get("value") if temp_result else None
            
            # Test precipitation
            precip_result = fetch_arome_wcs(
                latitude, longitude, 
                model="AROME_HR", 
                field="PRECIPITATION",
                timestamp=timestamp_str
            )
            precip_value = precip_result.get("value") if precip_result else None
            
            time_point_result["apis"]["AROME_HR"] = {
                "cape_j_kg": cape_value,
                "temperature_c": temp_value,
                "precipitation_mmh": precip_value,
                "time_diff_hours": cape_result.get("time_diff_hours") if cape_result else None
            }
            
            print(f"    ✅ CAPE: {cape_value} J/kg")
            print(f"    ✅ Temperature: {temp_value}°C")
            print(f"    ✅ Precipitation: {precip_value} mm/h")
            if cape_result and cape_result.get("time_diff_hours"):
                print(f"    ⏰ Time diff: {cape_result.get('time_diff_hours'):.2f}h")
                
        except Exception as e:
            print(f"    ❌ AROME_HR error: {e}")
            time_point_result["apis"]["AROME_HR"] = {"error": str(e)}
        
        # Test AROME_HR_NOWCAST
        print(f"  ⚡ Testing AROME_HR_NOWCAST...")
        try:
            # Test CAPE
            cape_result = fetch_arome_wcs(
                latitude, longitude, 
                model="AROME_HR_NOWCAST", 
                field="CAPE",
                timestamp=timestamp_str
            )
            cape_value = cape_result.get("value") if cape_result else None
            
            # Test temperature
            temp_result = fetch_arome_wcs(
                latitude, longitude, 
                model="AROME_HR_NOWCAST", 
                field="TEMPERATURE",
                timestamp=timestamp_str
            )
            temp_value = temp_result.get("value") if temp_result else None
            
            time_point_result["apis"]["AROME_HR_NOWCAST"] = {
                "cape_j_kg": cape_value,
                "temperature_c": temp_value,
                "time_diff_hours": cape_result.get("time_diff_hours") if cape_result else None
            }
            
            print(f"    ✅ CAPE: {cape_value} J/kg")
            print(f"    ✅ Temperature: {temp_value}°C")
            if cape_result and cape_result.get("time_diff_hours"):
                print(f"    ⏰ Time diff: {cape_result.get('time_diff_hours'):.2f}h")
                
        except Exception as e:
            print(f"    ❌ AROME_HR_NOWCAST error: {e}")
            time_point_result["apis"]["AROME_HR_NOWCAST"] = {"error": str(e)}
        
        # Test PIAF_NOWCAST
        print(f"  🌧️ Testing PIAF_NOWCAST...")
        try:
            precip_result = fetch_arome_wcs(
                latitude, longitude, 
                model="PIAF_NOWCAST", 
                field="PRECIPITATION",
                timestamp=timestamp_str
            )
            precip_value = precip_result.get("value") if precip_result else None
            
            time_point_result["apis"]["PIAF_NOWCAST"] = {
                "precipitation_mmh": precip_value,
                "time_diff_hours": precip_result.get("time_diff_hours") if precip_result else None
            }
            
            print(f"    ✅ Precipitation: {precip_value} mm/h")
            if precip_result and precip_result.get("time_diff_hours"):
                print(f"    ⏰ Time diff: {precip_result.get('time_diff_hours'):.2f}h")
                
        except Exception as e:
            print(f"    ❌ PIAF_NOWCAST error: {e}")
            time_point_result["apis"]["PIAF_NOWCAST"] = {"error": str(e)}
        
        # Test Open-Meteo
        print(f"  🌍 Testing OPENMETEO_GLOBAL...")
        try:
            openmeteo_result = get_openmeteo_data_for_timestamp(latitude, longitude, timestamp_str)
            if openmeteo_result:
                time_point_result["apis"]["OPENMETEO_GLOBAL"] = {
                    "temperature_c": openmeteo_result.get("temperature_c"),
                    "precipitation_mmh": openmeteo_result.get("precipitation_mmh"),
                    "wind_speed_ms": openmeteo_result.get("wind_speed_ms"),
                    "wind_gusts_ms": openmeteo_result.get("wind_gusts_ms"),
                    "weather_code": openmeteo_result.get("weather_code"),
                    "time_diff_hours": openmeteo_result.get("time_diff_hours")
                }
                print(f"    ✅ Temperature: {openmeteo_result.get('temperature_c')}°C")
                print(f"    ✅ Precipitation: {openmeteo_result.get('precipitation_mmh')} mm/h")
                print(f"    ✅ Wind Speed: {openmeteo_result.get('wind_speed_ms')} m/s")
                print(f"    ✅ Wind Gusts: {openmeteo_result.get('wind_gusts_ms')} m/s")
                if openmeteo_result.get("time_diff_hours"):
                    print(f"    ⏰ Time diff: {openmeteo_result.get('time_diff_hours'):.2f}h")
            else:
                print(f"    ❌ No data available")
                time_point_result["apis"]["OPENMETEO_GLOBAL"] = {"error": "No data available"}
        except Exception as e:
            print(f"    ❌ Open-Meteo error: {e}")
            time_point_result["apis"]["OPENMETEO_GLOBAL"] = {"error": str(e)}
        
        # Calculate thunderstorm risk
        print(f"  🧮 Calculating thunderstorm risk...")
        
        # Get best available values
        cape_value = None
        wind_gusts = None
        precipitation = None
        temperature = None
        
        # Prioritize AROME_HR for CAPE
        if time_point_result["apis"].get("AROME_HR", {}).get("cape_j_kg") is not None:
            cape_value = time_point_result["apis"]["AROME_HR"]["cape_j_kg"]
        elif time_point_result["apis"].get("AROME_HR_NOWCAST", {}).get("cape_j_kg") is not None:
            cape_value = time_point_result["apis"]["AROME_HR_NOWCAST"]["cape_j_kg"]
        
        # Get wind gusts from any available source
        for api_name in ["AROME_HR", "AROME_HR_NOWCAST", "OPENMETEO_GLOBAL"]:
            if time_point_result["apis"].get(api_name, {}).get("wind_gusts_ms") is not None:
                wind_gusts = time_point_result["apis"][api_name]["wind_gusts_ms"]
                break
        
        # Get precipitation from any available source
        for api_name in ["AROME_HR", "PIAF_NOWCAST", "OPENMETEO_GLOBAL"]:
            if time_point_result["apis"].get(api_name, {}).get("precipitation_mmh") is not None:
                precipitation = time_point_result["apis"][api_name]["precipitation_mmh"]
                break
        
        # Get temperature from any available source
        for api_name in ["AROME_HR", "AROME_HR_NOWCAST", "OPENMETEO_GLOBAL"]:
            if time_point_result["apis"].get(api_name, {}).get("temperature_c") is not None:
                temperature = time_point_result["apis"][api_name]["temperature_c"]
                break
        
        risk_result = calculate_thunderstorm_risk(
            cape_value, wind_gusts, precipitation, temperature
        )
        
        time_point_result["thunderstorm_risk"] = risk_result
        
        print(f"     Risk Score: {risk_result['risk_score']:.2f} ({risk_result['risk_level']})")
        print()
        
        results["time_points"].append(time_point_result)
    
    # Test Vigilance warnings
    print(f"🚨 Testing Vigilance warnings...")
    try:
        vigilance_result = fetch_warnings(latitude, longitude)
        results["vigilance_warnings"] = [v.__dict__ for v in vigilance_result]
        print(f"  ✅ Vigilance warnings: {results['vigilance_warnings']}")
    except Exception as e:
        print(f"  ❌ Vigilance error: {e}")
        results["vigilance_warnings"] = {"error": str(e)}
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/tarbes_risk_analysis_evening_morning_{timestamp}.json"
    
    os.makedirs("output", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {output_file}")
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print(f"📍 Location: Tarbes, France")
    print(f"🕒 Time points tested: {len(test_times)}")
    print(f"🌩️ Risk levels found:")
    
    risk_counts = {"niedrig": 0, "moderat": 0, "hoch": 0, "sehr hoch": 0}
    for tp in results["time_points"]:
        risk_level = tp["thunderstorm_risk"]["risk_level"]
        risk_counts[risk_level] += 1
    
    for level, count in risk_counts.items():
        print(f"   {level.capitalize()}: {count}")
    
    return results

if __name__ == "__main__":
    test_tarbes_thunderstorm_risk() 