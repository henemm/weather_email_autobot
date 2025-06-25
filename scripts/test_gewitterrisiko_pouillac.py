#!/usr/bin/env python3
"""
Live-Test: Gewitterrisiko-Berechnung für Pouillac (Frankreich)

This script tests the risk analysis for thunderstorms at a specific point outside GR20
to validate the model integration logic.

Location: Pouillac, France (44.8570 N, -0.1780 E)
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.env_loader import get_env_var
from src.wetter.fetch_arome_wcs import fetch_arome_wcs, fetch_arome_temperature, fetch_arome_precipitation
from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast, get_weather_summary
from src.logic.analyse_weather import compute_risk


# Test coordinates for Pauillac (Gironde)
POUILLAC_LATITUDE = 45.1996
POUILLAC_LONGITUDE = -0.7462

# Risk thresholds from config.yaml
RISK_THRESHOLDS = {
    "CAPE": 1000.0,  # J/kg
    "SHEAR": 20.0,   # m/s
    "RAINRATE": 2.0, # mm/h
    "TEMPERATURE": 25.0,  # °C
    "WIND": 40.0     # km/h
}

# Risk levels
RISK_LEVELS = {
    "niedrig": "low",
    "mittel": "medium", 
    "hoch": "high"
}


def get_target_timestamp() -> str:
    """Get target timestamp for tomorrow 17:00 CEST."""
    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    # Set time to 17:00 CEST (UTC+2)
    target_time = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
    # Convert to UTC (subtract 2 hours for CEST)
    utc_time = target_time - timedelta(hours=2)
    return utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_arome_hr_data(target_timestamp: str = None) -> Dict[str, Any]:
    """Fetch AROME_HR data for CAPE and SHEAR."""
    print("🌩️ Fetching AROME_HR data (CAPE, SHEAR)...")
    
    result = {
        "CAPE": None,
        "SHEAR": None,
        "TEMPERATURE": None,
        "status": "not_available"
    }
    
    try:
        # Fetch CAPE data
        cape_result = fetch_arome_wcs(
            latitude=POUILLAC_LATITUDE,
            longitude=POUILLAC_LONGITUDE,
            model="AROME_HR",
            field="CAPE",
            timestamp=target_timestamp
        )
        
        if cape_result and cape_result.get("value") is not None:
            result["CAPE"] = cape_result["value"]
            print(f"   ✅ CAPE: {cape_result['value']} {cape_result.get('unit', 'J/kg')}")
        else:
            print("   ❌ CAPE: No data available")
        
        # Fetch SHEAR data
        shear_result = fetch_arome_wcs(
            latitude=POUILLAC_LATITUDE,
            longitude=POUILLAC_LONGITUDE,
            model="AROME_HR",
            field="SHEAR",
            timestamp=target_timestamp
        )
        
        if shear_result and shear_result.get("value") is not None:
            result["SHEAR"] = shear_result["value"]
            print(f"   ✅ SHEAR: {shear_result['value']} {shear_result.get('unit', 'm/s')}")
        else:
            print("   ❌ SHEAR: No data available")
        
        # Fetch temperature data
        temp_result = fetch_arome_temperature(
            latitude=POUILLAC_LATITUDE,
            longitude=POUILLAC_LONGITUDE,
            model="AROME_HR",
            timestamp=target_timestamp
        )
        
        if temp_result is not None:
            result["TEMPERATURE"] = temp_result
            print(f"   ✅ Temperature: {temp_result}°C")
        else:
            print("   ❌ Temperature: No data available")
        
        # Determine status
        if result["CAPE"] is not None or result["SHEAR"] is not None:
            result["status"] = "available"
        
    except Exception as e:
        print(f"   ❌ AROME_HR Error: {e}")
        result["error"] = str(e)
    
    return result


def fetch_arome_nowcast_data(target_timestamp: str = None) -> Dict[str, Any]:
    """Fetch AROME_HR_NOWCAST data for short-term wind and convection data."""
    print("🌤️ Fetching AROME_HR_NOWCAST data...")
    
    result = {
        "WIND_SPEED": None,
        "WIND_DIRECTION": None,
        "TEMPERATURE": None,
        "status": "not_available"
    }
    
    try:
        # Fetch wind data (U and V components)
        u_wind_result = fetch_arome_wcs(
            latitude=POUILLAC_LATITUDE,
            longitude=POUILLAC_LONGITUDE,
            model="AROME_HR_NOWCAST",
            field="WIND",
            timestamp=target_timestamp
        )
        
        if u_wind_result and u_wind_result.get("value") is not None:
            result["WIND_SPEED"] = u_wind_result["value"]
            print(f"   ✅ Wind Speed: {u_wind_result['value']} {u_wind_result.get('unit', 'm/s')}")
        else:
            print("   ❌ Wind Speed: No data available")
        
        # Fetch temperature data
        temp_result = fetch_arome_temperature(
            latitude=POUILLAC_LATITUDE,
            longitude=POUILLAC_LONGITUDE,
            model="AROME_HR_NOWCAST",
            timestamp=target_timestamp
        )
        
        if temp_result is not None:
            result["TEMPERATURE"] = temp_result
            print(f"   ✅ Temperature: {temp_result}°C")
        else:
            print("   ❌ Temperature: No data available")
        
        # Determine status
        if result["WIND_SPEED"] is not None or result["TEMPERATURE"] is not None:
            result["status"] = "available"
        
    except Exception as e:
        print(f"   ❌ AROME_HR_NOWCAST Error: {e}")
        result["error"] = str(e)
    
    return result


def fetch_piaf_nowcast_data(target_timestamp: str = None) -> Dict[str, Any]:
    """Fetch PIAF_NOWCAST data for rain rate nowcasting."""
    print("🌧️ Fetching PIAF_NOWCAST data (rain rate)...")
    
    result = {
        "RAINRATE": None,
        "status": "not_available"
    }
    
    try:
        # Fetch precipitation data
        precip_result = fetch_arome_precipitation(
            latitude=POUILLAC_LATITUDE,
            longitude=POUILLAC_LONGITUDE,
            model="PIAF_NOWCAST",
            timestamp=target_timestamp
        )
        
        if precip_result is not None:
            result["RAINRATE"] = precip_result
            print(f"   ✅ Rain Rate: {precip_result} mm/h")
        else:
            print("   ❌ Rain Rate: No data available")
        
        # Determine status
        if result["RAINRATE"] is not None:
            result["status"] = "available"
        
    except Exception as e:
        print(f"   ❌ PIAF_NOWCAST Error: {e}")
        result["error"] = str(e)
    
    return result


def fetch_openmeteo_data(target_timestamp: str = None) -> Dict[str, Any]:
    """Fetch OPENMETEO_GLOBAL data for temperature, wind, and precipitation."""
    print("🌍 Fetching OPENMETEO_GLOBAL data...")
    
    result = {
        "TEMPERATURE": None,
        "WIND_SPEED": None,
        "WIND_DIRECTION": None,
        "PRECIPITATION": None,
        "HUMIDITY": None,
        "status": "not_available"
    }
    
    try:
        # Fetch Open-Meteo forecast data
        forecast_data = fetch_openmeteo_forecast(POUILLAC_LATITUDE, POUILLAC_LONGITUDE)
        
        if forecast_data and "hourly" in forecast_data:
            hourly = forecast_data["hourly"]
            
            # Find the closest time to target_timestamp
            if target_timestamp and hourly.get("time"):
                target_dt = datetime.fromisoformat(target_timestamp.replace("Z", "+00:00"))
                
                # Find the closest hourly forecast
                closest_time = None
                closest_index = 0
                min_diff = float('inf')
                
                for i, time_str in enumerate(hourly["time"]):
                    # Open-Meteo times are in local timezone (Europe/Paris for Pouillac)
                    # Parse as local time and convert to UTC for comparison
                    try:
                        # Parse the time string (format: "2025-06-24T18:00")
                        forecast_dt_local = datetime.fromisoformat(time_str)
                        # Convert to UTC (subtract 2 hours for CEST) and make timezone-aware
                        forecast_dt = forecast_dt_local - timedelta(hours=2)
                        forecast_dt = forecast_dt.replace(tzinfo=None)  # Make naive for comparison
                        
                        diff = abs((forecast_dt - target_dt).total_seconds())
                        if diff < min_diff:
                            min_diff = diff
                            closest_time = time_str
                            closest_index = i
                    except Exception as e:
                        print(f"   ⚠️ Warning: Could not parse time '{time_str}': {e}")
                        continue
                
                if closest_time:
                    print(f"   📅 Using forecast for: {closest_time}")
                    result["TEMPERATURE"] = hourly.get("temperature_2m", [None])[closest_index]
                    result["WIND_SPEED"] = hourly.get("wind_speed_10m", [None])[closest_index]
                    result["WIND_DIRECTION"] = hourly.get("wind_direction_10m", [None])[closest_index]
                    result["PRECIPITATION"] = hourly.get("precipitation", [None])[closest_index]
                    result["HUMIDITY"] = hourly.get("relative_humidity_2m", [None])[closest_index]
                else:
                    # Fallback to current data
                    current = forecast_data.get("current", {})
                    result["TEMPERATURE"] = current.get("temperature_2m")
                    result["WIND_SPEED"] = current.get("wind_speed_10m")
                    result["WIND_DIRECTION"] = current.get("wind_direction_10m")
                    result["PRECIPITATION"] = current.get("precipitation")
                    result["HUMIDITY"] = current.get("relative_humidity_2m")
            else:
                # Fallback to current data
                current = forecast_data.get("current", {})
                result["TEMPERATURE"] = current.get("temperature_2m")
                result["WIND_SPEED"] = current.get("wind_speed_10m")
                result["WIND_DIRECTION"] = current.get("wind_direction_10m")
                result["PRECIPITATION"] = current.get("precipitation")
                result["HUMIDITY"] = current.get("relative_humidity_2m")
            
            print(f"   ✅ Temperature: {result['TEMPERATURE']}°C")
            print(f"   ✅ Wind Speed: {result['WIND_SPEED']} km/h")
            print(f"   ✅ Wind Direction: {result['WIND_DIRECTION']}°")
            print(f"   ✅ Precipitation: {result['PRECIPITATION']} mm")
            print(f"   ✅ Humidity: {result['HUMIDITY']}%")
            
            result["status"] = "available"
        else:
            print("   ❌ No forecast data available")
        
    except Exception as e:
        print(f"   ❌ OPENMETEO_GLOBAL Error: {e}")
        result["error"] = str(e)
    
    return result


def calculate_risk_level(value: float, threshold: float, risk_levels: list) -> str:
    """Calculate risk level based on value and threshold."""
    if value is None:
        return "niedrig"
    
    if value <= threshold:
        return "niedrig"
    elif value <= threshold * 1.5:
        return "mittel"
    else:
        return "hoch"


def calculate_arome_hr_risk(arome_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate risk for AROME_HR based on CAPE and SHEAR."""
    cape_value = arome_data.get("CAPE")
    shear_value = arome_data.get("SHEAR")
    
    cape_risk = calculate_risk_level(cape_value, RISK_THRESHOLDS["CAPE"], [1000, 1500, 2000])
    shear_risk = calculate_risk_level(shear_value, RISK_THRESHOLDS["SHEAR"], [20, 30, 40])
    
    # Combine CAPE and SHEAR for overall risk
    if cape_risk == "hoch" or shear_risk == "hoch":
        overall_risk = "hoch"
    elif cape_risk == "mittel" or shear_risk == "mittel":
        overall_risk = "mittel"
    else:
        overall_risk = "niedrig"
    
    return {
        "CAPE": cape_value,
        "CAPE_risk": cape_risk,
        "SHEAR": shear_value,
        "SHEAR_risk": shear_risk,
        "risk": overall_risk
    }


def calculate_piaf_risk(piaf_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate risk for PIAF_NOWCAST based on rain rate."""
    rainrate_value = piaf_data.get("RAINRATE")
    rain_risk = calculate_risk_level(rainrate_value, RISK_THRESHOLDS["RAINRATE"], [2, 5, 10])
    
    return {
        "rainrate": rainrate_value,
        "risk": rain_risk
    }


def calculate_openmeteo_risk(openmeteo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate risk for OPENMETEO_GLOBAL based on temperature, wind, and precipitation."""
    temp_value = openmeteo_data.get("TEMPERATURE")
    wind_value = openmeteo_data.get("WIND_SPEED")
    precip_value = openmeteo_data.get("PRECIPITATION")
    
    temp_risk = calculate_risk_level(temp_value, RISK_THRESHOLDS["TEMPERATURE"], [25, 30, 35])
    wind_risk = calculate_risk_level(wind_value, RISK_THRESHOLDS["WIND"], [40, 60, 80])
    precip_risk = calculate_risk_level(precip_value, RISK_THRESHOLDS["RAINRATE"], [2, 5, 10])
    
    # Determine overall risk (highest of the three)
    risks = [temp_risk, wind_risk, precip_risk]
    if "hoch" in risks:
        overall_risk = "hoch"
    elif "mittel" in risks:
        overall_risk = "mittel"
    else:
        overall_risk = "niedrig"
    
    return {
        "temp": temp_value,
        "wind_speed": wind_value,
        "wind_direction": openmeteo_data.get("WIND_DIRECTION"),
        "rain": precip_value,
        "humidity": openmeteo_data.get("HUMIDITY"),
        "risk": overall_risk
    }


def calculate_overall_risk(risks: Dict[str, Any]) -> str:
    """Calculate overall risk from all sources."""
    risk_values = []
    
    # Extract risk levels from each source
    for source, data in risks.items():
        if isinstance(data, dict) and "risk" in data:
            risk_level = data["risk"]
            if risk_level == "hoch":
                risk_values.append(3)
            elif risk_level == "mittel":
                risk_values.append(2)
            else:
                risk_values.append(1)
    
    if not risk_values:
        return "niedrig"
    
    # Calculate average risk
    avg_risk = sum(risk_values) / len(risk_values)
    
    if avg_risk >= 2.5:
        return "hoch"
    elif avg_risk >= 1.5:
        return "mittel"
    else:
        return "niedrig"


def get_time_range_timestamps() -> list:
    """Get target timestamps for tomorrow 11:00, 14:00, and 17:00 CEST (hourly intervals)."""
    timestamps = []
    tomorrow = datetime.now() + timedelta(days=1)
    # Generate timestamps for 11:00, 14:00, and 17:00 CEST
    for hour in [11, 14, 17]:
        target_time = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
        # Convert to UTC (subtract 2 hours for CEST)
        utc_time = target_time - timedelta(hours=2)
        timestamps.append(utc_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return timestamps


def analyze_time_range() -> Dict[str, Any]:
    """Analyze thunderstorm risk for a time range (11:00, 14:00, 17:00 CEST)."""
    print("🌩️ Live-Test: Gewitterrisiko-Berechnung für Pauillac (11:00, 14:00, 17:00 CEST)")
    print("=" * 70)
    print(f"📍 Location: Pauillac, France (Gironde)")
    print(f"📍 Coordinates: {POUILLAC_LATITUDE}°N, {POUILLAC_LONGITUDE}°E")
    # Get target timestamps for 11:00, 14:00, 17:00 CEST
    timestamps = get_time_range_timestamps()
    print(f"🕒 Time Points: 11:00, 14:00, 17:00 CEST (tomorrow)")
    print(f"🕒 Timestamps: {timestamps}")
    print()
    # Define 'tomorrow' for use in label formatting
    tomorrow = datetime.now() + timedelta(days=1)
    # Analyze each time point
    time_point_results = {}
    for idx, ts in enumerate(timestamps):
        label = ["11:00 CEST", "14:00 CEST", "17:00 CEST"][idx]
        print(f"--- {label} ---")
        arome_hr = fetch_arome_hr_data(ts)
        piaf = fetch_piaf_nowcast_data(ts)
        openmeteo = fetch_openmeteo_data(ts)
        risks = {
            "AROME_HR": calculate_arome_hr_risk(arome_hr),
            "PIAF_NOWCAST": calculate_piaf_risk(piaf),
            "OPENMETEO_GLOBAL": calculate_openmeteo_risk(openmeteo)
        }
        overall_risk = calculate_overall_risk(risks)
        time_point_results[label] = {
            "timestamp": ts,
            "target_time_cest": label.replace("CEST", f"{tomorrow.strftime('%Y-%m-%d')} CEST"),
            "risks": risks,
            "overall_risk": overall_risk,
            "api_status": {
                "AROME_HR": arome_hr.get("status"),
                "AROME_HR_NOWCAST": arome_hr.get("nowcast_status", "not_tested"),
                "PIAF_NOWCAST": piaf.get("status"),
                "OPENMETEO_GLOBAL": openmeteo.get("status")
            }
        }
    # Output and save results as before
    # ... existing code ...


def main():
    """Main test function for Pouillac thunderstorm risk analysis."""
    print("🌩️ Live-Test: Gewitterrisiko-Berechnung für Pouillac (Frankreich)")
    print("=" * 70)
    print("Choose analysis type:")
    print("1. Single time point (tomorrow 17:00 CEST)")
    print("2. Time range (tomorrow 11:00, 14:00, 17:00 CEST)")
    print()
    
    # For now, run the time range analysis
    analyze_time_range()


if __name__ == "__main__":
    main() 