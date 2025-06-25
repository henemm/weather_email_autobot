"""
Open-Meteo weather data fetching module.

This module provides functionality to fetch weather data from the Open-Meteo API,
which offers free weather forecasts without requiring authentication.
"""

import requests
from datetime import datetime
from typing import Dict, Any, Optional


def fetch_openmeteo_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch current weather forecast from Open-Meteo API.
    
    Args:
        lat: Latitude in decimal degrees (-90 to 90)
        lon: Longitude in decimal degrees (-180 to 180)
        
    Returns:
        Dict containing weather forecast data with current conditions and hourly forecast
        
    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If API request fails
    """
    # Validate coordinates
    if not -90 <= lat <= 90:
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if not -180 <= lon <= 180:
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
    
    # Build API URL
    url = "https://api.open-meteo.com/v1/forecast"
    
    # Define parameters for comprehensive weather data
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover",
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover",
        "timezone": "auto",
        "forecast_days": 3  # Get 3 days of forecast
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return _parse_openmeteo_response(data, lat, lon)
        
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")
    except ValueError as e:
        raise RuntimeError(f"Invalid JSON response: {str(e)}")


def _parse_openmeteo_response(data: Dict[str, Any], lat: float, lon: float) -> Dict[str, Any]:
    """
    Parse Open-Meteo API response into structured format.
    
    Args:
        data: Raw API response data
        lat: Latitude of the location
        lon: Longitude of the location
        
    Returns:
        Dict containing parsed weather data
    """
    result = {
        "location": {
            "latitude": lat,
            "longitude": lon,
            "timezone": data.get("timezone", "auto"),
            "timezone_abbreviation": data.get("timezone_abbreviation", ""),
            "utc_offset_seconds": data.get("utc_offset_seconds", 0)
        },
        "current": {},
        "hourly": {},
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "data_source": "Open-Meteo API",
            "api_version": "v1"
        }
    }
    
    # Parse current weather data
    current = data.get("current", {})
    if current:
        result["current"] = {
            "time": current.get("time"),
            "temperature_2m": current.get("temperature_2m"),
            "relative_humidity_2m": current.get("relative_humidity_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "precipitation": current.get("precipitation"),
            "weather_code": current.get("weather_code"),
            "wind_speed_10m": current.get("wind_speed_10m"),
            "wind_direction_10m": current.get("wind_direction_10m"),
            "pressure_msl": current.get("pressure_msl"),
            "cloud_cover": current.get("cloud_cover")
        }
    
    # Parse hourly forecast data
    hourly = data.get("hourly", {})
    if hourly:
        result["hourly"] = {
            "time": hourly.get("time", []),
            "temperature_2m": hourly.get("temperature_2m", []),
            "relative_humidity_2m": hourly.get("relative_humidity_2m", []),
            "apparent_temperature": hourly.get("apparent_temperature", []),
            "precipitation_probability": hourly.get("precipitation_probability", []),
            "precipitation": hourly.get("precipitation", []),
            "weather_code": hourly.get("weather_code", []),
            "wind_speed_10m": hourly.get("wind_speed_10m", []),
            "wind_direction_10m": hourly.get("wind_direction_10m", []),
            "pressure_msl": hourly.get("pressure_msl", []),
            "cloud_cover": hourly.get("cloud_cover", [])
        }
    
    return result


def get_weather_summary(forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract a summary of current weather conditions from forecast data.
    
    Args:
        forecast_data: Parsed Open-Meteo forecast data
        
    Returns:
        Dict containing weather summary
    """
    current = forecast_data.get("current", {})
    
    if not current:
        return {"error": "No current weather data available"}
    
    return {
        "temperature": {
            "current": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "unit": "°C"
        },
        "wind": {
            "speed": current.get("wind_speed_10m"),
            "direction": current.get("wind_direction_10m"),
            "speed_unit": "km/h",
            "direction_unit": "degrees"
        },
        "precipitation": {
            "current": current.get("precipitation"),
            "unit": "mm"
        },
        "conditions": {
            "weather_code": current.get("weather_code"),
            "cloud_cover": current.get("cloud_cover"),
            "relative_humidity": current.get("relative_humidity_2m"),
            "pressure": current.get("pressure_msl")
        },
        "timestamp": current.get("time")
    } 