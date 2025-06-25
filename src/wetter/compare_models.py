"""
Weather model comparison module.

This module provides functionality to compare weather data from different sources:
- Météo-France API: Primary source for French weather data
- Open-Meteo API: Fallback for temperature, wind, and precipitation
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Fix import paths for both direct and src-root execution
try:
    from wetter.fetch_openmeteo import fetch_openmeteo_forecast, get_weather_summary
    from wetter.fetch_meteofrance import get_forecast_with_fallback, get_thunderstorm_with_fallback, get_alerts_with_fallback
except ImportError:
    from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast, get_weather_summary
    from src.wetter.fetch_meteofrance import get_forecast_with_fallback, get_thunderstorm_with_fallback, get_alerts_with_fallback


# Conca, Corsica coordinates
CONCA_LATITUDE = 41.7481
CONCA_LONGITUDE = 9.2972


def compare_meteofrance_openmeteo_conca() -> Dict[str, Any]:
    """
    Compare Météo-France and Open-Meteo weather data for Conca, Corsica.
    
    Returns:
        Dict containing comparison data with both Météo-France and Open-Meteo information
        
    Raises:
        RuntimeError: If data cannot be fetched from either source
    """
    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": {
            "name": "Conca, Corsica",
            "latitude": CONCA_LATITUDE,
            "longitude": CONCA_LONGITUDE
        },
        "meteofrance": {},
        "open_meteo": {},
        "errors": []
    }
    
    # Fetch Météo-France data
    try:
        result["meteofrance"] = _fetch_meteofrance_data()
    except Exception as e:
        error_msg = f"Météo-France data fetch failed: {str(e)}"
        result["errors"].append(error_msg)
        result["meteofrance"] = {"error": error_msg}
    
    # Fetch Open-Meteo data
    try:
        result["open_meteo"] = _fetch_openmeteo_data()
    except Exception as e:
        error_msg = f"Open-Meteo data fetch failed: {str(e)}"
        result["errors"].append(error_msg)
        result["open_meteo"] = {"error": error_msg}
    
    return result


def _fetch_meteofrance_data() -> Dict[str, Any]:
    """
    Fetch Météo-France API data.
    
    Returns:
        Dict containing Météo-France weather data
        
    Raises:
        RuntimeError: If Météo-France data cannot be fetched
    """
    meteofrance_data = {
        "forecast": {},
        "thunderstorm": {},
        "alerts": {},
        "metadata": {
            "data_source": "Météo-France API",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    try:
        # Get forecast data
        forecast = get_forecast_with_fallback(CONCA_LATITUDE, CONCA_LONGITUDE)
        meteofrance_data["forecast"] = {
            "temperature": forecast.temperature,
            "weather_condition": forecast.weather_condition,
            "precipitation_probability": forecast.precipitation_probability,
            "timestamp": forecast.timestamp,
            "data_source": forecast.data_source
        }
        
        # Get thunderstorm information
        thunderstorm = get_thunderstorm_with_fallback(CONCA_LATITUDE, CONCA_LONGITUDE)
        meteofrance_data["thunderstorm"] = {
            "status": thunderstorm,
            "data_source": "meteofrance-api" if "meteofrance-api" in thunderstorm else "open-meteo"
        }
        
        # Get weather alerts
        alerts = get_alerts_with_fallback(CONCA_LATITUDE, CONCA_LONGITUDE)
        meteofrance_data["alerts"] = {
            "count": len(alerts),
            "alerts": [
                {
                    "phenomenon": alert.phenomenon,
                    "level": alert.level,
                    "description": alert.description
                }
                for alert in alerts
            ]
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Météo-France data: {str(e)}")
    
    return meteofrance_data


def _fetch_openmeteo_data() -> Dict[str, Any]:
    """
    Fetch Open-Meteo weather data.
    
    Returns:
        Dict containing Open-Meteo weather data
        
    Raises:
        RuntimeError: If Open-Meteo data cannot be fetched
    """
    # Fetch full forecast data
    forecast_data = fetch_openmeteo_forecast(CONCA_LATITUDE, CONCA_LONGITUDE)
    
    # Get weather summary
    summary = get_weather_summary(forecast_data)
    
    return {
        "current": summary,
        "forecast": forecast_data.get("hourly", {}),
        "metadata": {
            "data_source": "Open-Meteo API",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }


def save_comparison_to_file(comparison_data: Dict[str, Any], filename: str = None) -> str:
    """
    Save weather comparison data to JSON file.
    
    Args:
        comparison_data: Weather comparison data
        filename: Optional custom filename (defaults to timestamped name)
        
    Returns:
        str: Path to the saved file
        
    Raises:
        RuntimeError: If file cannot be saved
    """
    # Create data directory if it doesn't exist
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conca_weather_comparison_{timestamp}.json"
    
    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    filepath = os.path.join(data_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, indent=2, ensure_ascii=False)
        
        return filepath
        
    except Exception as e:
        raise RuntimeError(f"Failed to save comparison data to {filepath}: {str(e)}")


def get_comparison_summary(comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary of the weather comparison.
    
    Args:
        comparison_data: Weather comparison data
        
    Returns:
        Dict containing comparison summary
    """
    summary = {
        "timestamp": comparison_data.get("timestamp"),
        "location": comparison_data.get("location"),
        "data_sources": {
            "meteofrance": "available" if not comparison_data.get("meteofrance", {}).get("error") else "error",
            "open_meteo": "available" if not comparison_data.get("open_meteo", {}).get("error") else "error"
        },
        "errors": comparison_data.get("errors", []),
        "summary": {}
    }
    
    # Météo-France summary
    meteofrance_data = comparison_data.get("meteofrance", {})
    if not meteofrance_data.get("error"):
        forecast = meteofrance_data.get("forecast", {})
        thunderstorm = meteofrance_data.get("thunderstorm", {})
        alerts = meteofrance_data.get("alerts", {})
        
        summary["summary"]["meteofrance"] = {
            "temperature": forecast.get("temperature"),
            "weather_condition": forecast.get("weather_condition"),
            "precipitation_probability": forecast.get("precipitation_probability"),
            "thunderstorm_status": thunderstorm.get("status"),
            "alerts_count": alerts.get("count", 0),
            "data_source": forecast.get("data_source"),
            "data_available": True
        }
    else:
        summary["summary"]["meteofrance"] = {"error": meteofrance_data.get("error")}
    
    # Open-Meteo summary
    openmeteo_data = comparison_data.get("open_meteo", {})
    if not openmeteo_data.get("error"):
        current = openmeteo_data.get("current", {})
        if not current.get("error"):
            summary["summary"]["open_meteo"] = {
                "temperature": current.get("temperature", {}).get("current"),
                "wind_speed": current.get("wind", {}).get("speed"),
                "precipitation": current.get("precipitation", {}).get("current"),
                "data_available": True
            }
        else:
            summary["summary"]["open_meteo"] = {"error": current.get("error")}
    else:
        summary["summary"]["open_meteo"] = {"error": openmeteo_data.get("error")}
    
    return summary


# Backward compatibility function
def compare_arome_openmeteo_conca() -> Dict[str, Any]:
    """
    Backward compatibility function for AROME/Open-Meteo comparison.
    
    Returns:
        Dict containing comparison data (now using Météo-France API)
    """
    return compare_meteofrance_openmeteo_conca() 