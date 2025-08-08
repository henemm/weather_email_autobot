"""
Météo-France API integration module.

This module provides weather data fetching using the official meteofrance-api library
with automatic fallback to open-meteo when meteofrance-api is not available.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging

from meteofrance_api.client import MeteoFranceClient
from meteofrance_api.model import Forecast, Place

try:
    from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast
except ImportError:
    try:
        from fetch_openmeteo import fetch_openmeteo_forecast
    except ImportError:
        # If both imports fail, create a dummy function
        def fetch_openmeteo_forecast(lat: float, lon: float):
            raise RuntimeError("OpenMeteo fallback not available")


logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Result of weather forecast data."""
    temperature: float
    weather_condition: Optional[str]
    precipitation_probability: Optional[int]
    timestamp: str
    wind_speed: Optional[float] = None  # Add wind speed
    wind_gusts: Optional[float] = None  # Add wind gusts from MeteoFrance
    precipitation: Optional[float] = None  # Add precipitation amount
    thunderstorm_probability: Optional[float] = None  # Add thunderstorm probability
    data_source: str = "meteofrance-api"
    raw_forecast_data: Optional[List[Dict[str, Any]]] = None  # Raw hourly data for enhanced processing


@dataclass
class Alert:
    """Weather alert information."""
    phenomenon: str
    level: str  # "green", "yellow", "orange", "red"
    description: Optional[str] = None


PHENOMENON_ID_MAP = {
    # Official Météo-France vigilance mapping (see doc)
    # 1: Wind, 2: Rain, 3: Thunderstorm, 4: Snow/Ice, 5: Flood, 6: Forest fire, 7: Heat, 8: Cold, 9: Avalanche
    '1': 'wind',
    '2': 'rain',
    '3': 'thunderstorm',
    '4': 'snow',
    '5': 'flood',
    '6': 'forest_fire',
    '7': 'heat',
    '8': 'cold',
    '9': 'avalanche',
}

# Add level mapping after PHENOMENON_ID_MAP
LEVEL_ID_MAP = {
    # Official Météo-France vigilance level mapping
    # 1: green, 2: yellow, 3: orange, 4: red
    # Using shorter risk-based terms to save characters
    1: 'green',
    2: 'risk',    # 4 chars (was 'yellow' - 6 chars)
    3: 'high',    # 4 chars (was 'orange' - 6 chars)
    4: 'max',     # 3 chars (was 'red' - 3 chars)
}


def _validate_coordinates(lat: float, lon: float) -> None:
    """
    Validate latitude and longitude coordinates.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Raises:
        ValueError: If coordinates are invalid
    """
    if not -90 <= lat <= 90:
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if not -180 <= lon <= 180:
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")


def _get_department_from_coordinates(lat: float, lon: float) -> str:
    """
    Get department code from coordinates.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        Department code as string (e.g., "65" for Tarbes)

    Note:
        This is a simplified implementation. In production, you might want
        to use a more sophisticated geocoding service.
    """
    # Simplified mapping for common French regions
    # In production, consider using a more sophisticated geocoding service
    if 42.5 <= lat <= 44.0 and -1.0 <= lon <= 1.0:
        return "65"  # Hautes-Pyrénées (Tarbes)
    elif 43.0 <= lat <= 44.0 and 4.0 <= lon <= 6.0:
        return "06"  # Alpes-Maritimes
    elif 41.0 <= lat <= 43.0 and 8.0 <= lon <= 10.0:
        return "2A"  # Corse-du-Sud (including Conca: lat=41.79418, lon=9.259567)
    else:
        # Default fallback - in production, implement proper geocoding
        return "75"  # Paris as default


def get_forecast(lat: float, lon: float) -> ForecastResult:
    """
    Get weather forecast from meteofrance-api.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        ForecastResult containing weather data

    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If API request fails
    """
    _validate_coordinates(lat, lon)

    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)

        if not forecast.forecast or len(forecast.forecast) == 0:
            raise RuntimeError("No forecast data received")

        # Extract data from the first forecast entry
        first_forecast = forecast.forecast[0]

        # Extract wind data from the nested structure
        wind_data = first_forecast.get('wind', {})
        wind_speed = wind_data.get('speed', 0.0)
        wind_gusts = wind_data.get('gust', 0.0)

        # Extract precipitation data
        precipitation = None
        if 'rain' in first_forecast:
            rain_data = first_forecast['rain']
            if isinstance(rain_data, dict) and '1h' in rain_data:
                precipitation = rain_data['1h']
            elif isinstance(rain_data, (int, float)):
                precipitation = float(rain_data)

        # Extract thunderstorm probability from weather condition
        thunderstorm_probability = None
        weather_desc = first_forecast.get('weather', {}).get('desc', '')
        if weather_desc in ['thunderstorm', 'Orages', 'Risque d\'orages']:
            # If thunderstorm condition is detected, use precipitation probability as thunderstorm probability
            thunderstorm_probability = first_forecast.get('precipitation_probability', 0)

        return ForecastResult(
            temperature=first_forecast['T']['value'],
            weather_condition=first_forecast.get('weather', {}).get('desc'),
            precipitation_probability=first_forecast.get('precipitation_probability'),
            precipitation=precipitation,
            thunderstorm_probability=thunderstorm_probability,
            timestamp=first_forecast.get('datetime', ''),
            wind_speed=wind_speed,
            wind_gusts=wind_gusts,
            data_source="meteofrance-api"
        )

    except Exception as e:
        logger.error(f"Failed to fetch forecast from meteofrance-api: {e}")
        raise RuntimeError(f"Failed to fetch forecast: {str(e)}")


def get_thunderstorm(lat: float, lon: float) -> str:
    """
    Get thunderstorm information from meteofrance-api.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        String describing thunderstorm conditions

    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If API request fails
    """
    _validate_coordinates(lat, lon)

    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)

        if not forecast.forecast or len(forecast.forecast) == 0:
            return "No thunderstorm data available"

        # Check for thunderstorm conditions in the next few hours
        thunderstorm_entries = []
        for entry in forecast.forecast[:6]:  # Check next 6 hours
            weather_data = entry.get('weather', {})
            if isinstance(weather_data, dict) and weather_data.get('desc') == 'thunderstorm':
                thunderstorm_entries.append(entry)
            elif isinstance(weather_data, str) and weather_data == 'thunderstorm':
                # Fallback for old API format
                thunderstorm_entries.append(entry)

        if thunderstorm_entries:
            # Get the first thunderstorm entry
            first_thunderstorm = thunderstorm_entries[0]
            probability = first_thunderstorm.get('precipitation_probability', 0)
            return f"Thunderstorm detected with {probability}% precipitation probability"
        else:
            return "No thunderstorm conditions detected"

    except Exception as e:
        logger.error(f"Failed to fetch thunderstorm data: {e}")
        raise RuntimeError(f"Failed to fetch thunderstorm data: {str(e)}")


def get_alerts(lat: float, lon: float) -> List[Alert]:
    """
    Get weather alerts from meteofrance-api.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        List of Alert objects

    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If API request fails
    """
    _validate_coordinates(lat, lon)

    try:
        client = MeteoFranceClient()
        department = _get_department_from_coordinates(lat, lon)
        warnings = client.get_warning_current_phenomenons(department)
        alerts = []
        max_colors = getattr(warnings, 'phenomenons_max_colors', None)
        if isinstance(max_colors, dict):
            for phenomenon, level in max_colors.items():
                alerts.append(Alert(
                    phenomenon=phenomenon,
                    level=level,
                    description=f"{phenomenon} warning: {level} level"
                ))
        elif isinstance(max_colors, list):
            for entry in max_colors:
                # Debug logging
                logger.debug(f"Processing entry: {entry}")
                
                # Try to extract phenomenon and level from dict/list entry
                if isinstance(entry, dict):
                    # Map phenomenon id to name if needed
                    phenomenon_id = entry.get('phenomenon_id')
                    phenomenon = (
                        entry.get('phenomenon')
                        or PHENOMENON_ID_MAP.get(str(phenomenon_id), None)
                        or PHENOMENON_ID_MAP.get(str(entry.get('phenomenon')), None)
                        or entry.get('phenomenon_name')
                        or 'unknown'
                    )
                    
                    # Map level id to string
                    level_id = entry.get('phenomenon_max_color_id')
                    level = (
                        LEVEL_ID_MAP.get(level_id, None)
                        or entry.get('level')
                        or entry.get('color')
                        or 'unknown'
                    )
                    
                    # Debug logging
                    logger.debug(f"  phenomenon_id: {phenomenon_id}, level_id: {level_id}")
                    logger.debug(f"  mapped to: phenomenon={phenomenon}, level={level}")
                    
                    alerts.append(Alert(
                        phenomenon=phenomenon,
                        level=level,
                        description=f"{phenomenon} warning: {level} level"
                    ))
                elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                    # If first entry is numeric, map to name
                    phenomenon = entry[0]
                    if isinstance(phenomenon, int) or (isinstance(phenomenon, str) and phenomenon.isdigit()):
                        phenomenon = PHENOMENON_ID_MAP.get(str(phenomenon), phenomenon)
                    level = entry[1]
                    alerts.append(Alert(
                        phenomenon=phenomenon,
                        level=level,
                        description=f"{phenomenon} warning: {level} level"
                    ))
        else:
            logger.warning(f"phenomenons_max_colors is neither dict nor list: {type(max_colors)}")
        return alerts
    except Exception as e:
        logger.error(f"Failed to fetch alerts: {e}")
        raise RuntimeError(f"Failed to fetch alerts: {str(e)}")


def get_forecast_with_fallback(lat: float, lon: float) -> ForecastResult:
    """
    Get weather forecast with fallback to open-meteo.
    
    This function now returns raw hourly MeteoFrance data for better compatibility
    with Evening-Bericht processing, while maintaining fallback to open-meteo.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        ForecastResult containing weather data (raw hourly data for MeteoFrance)

    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If both APIs fail
    """
    _validate_coordinates(lat, lon)

    # Try meteofrance-api first
    try:
        # Get raw hourly data from MeteoFrance API
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)

        if not forecast.forecast or len(forecast.forecast) == 0:
            raise RuntimeError("No forecast data received")

        # Return the first forecast entry for backward compatibility
        # but also include the raw forecast data for enhanced processing
        first_forecast = forecast.forecast[0]

        # Extract wind data from the nested structure
        wind_data = first_forecast.get('wind', {})
        wind_speed = wind_data.get('speed', 0.0)
        wind_gusts = wind_data.get('gust', 0.0)

        # Extract precipitation data
        precipitation = None
        if 'rain' in first_forecast:
            rain_data = first_forecast['rain']
            if isinstance(rain_data, dict) and '1h' in rain_data:
                precipitation = rain_data['1h']
            elif isinstance(rain_data, (int, float)):
                precipitation = float(rain_data)

        # Extract thunderstorm probability from weather condition
        thunderstorm_probability = None
        weather_desc = first_forecast.get('weather', {}).get('desc', '')
        if weather_desc in ['thunderstorm', 'Orages', 'Risque d\'orages']:
            # If thunderstorm condition is detected, use precipitation probability as thunderstorm probability
            thunderstorm_probability = first_forecast.get('precipitation_probability', 0)

        # Create result with raw forecast data for enhanced processing
        result = ForecastResult(
            temperature=first_forecast['T']['value'],
            weather_condition=first_forecast.get('weather', {}).get('desc'),
            precipitation_probability=first_forecast.get('precipitation_probability'),
            precipitation=precipitation,
            thunderstorm_probability=thunderstorm_probability,
            timestamp=first_forecast.get('datetime', ''),
            wind_speed=wind_speed,
            wind_gusts=wind_gusts,
            data_source="meteofrance-api"
        )
        
        # Add raw forecast data for enhanced processing
        result.raw_forecast_data = forecast.forecast
        
        return result
        
    except Exception as e:
        logger.warning(f"MeteoFrance API failed, trying open-meteo: {e}")

        # Fallback to open-meteo
        try:
            openmeteo_data = fetch_openmeteo_forecast(lat, lon)
            current = openmeteo_data.get('current', {})

            return ForecastResult(
                temperature=current.get('temperature_2m'),
                weather_condition=_convert_weather_code_to_condition(current.get('weather_code')),
                precipitation_probability=None,  # OpenMeteo doesn't provide this directly
                timestamp=current.get('time', ''),
                wind_speed=current.get('wind_speed'),
                wind_gusts=None,  # OpenMeteo doesn't provide wind gusts
                data_source="open-meteo"
            )
        except Exception as fallback_error:
            logger.error(f"Both meteofrance-api and open-meteo failed: {fallback_error}")
            raise RuntimeError(f"Both meteofrance-api and open-meteo failed: {str(fallback_error)}")


def get_thunderstorm_with_fallback(lat: float, lon: float) -> str:
    """
    Get thunderstorm information with fallback to open-meteo.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        String describing thunderstorm conditions

    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If both APIs fail
    """
    _validate_coordinates(lat, lon)

    # Try meteofrance-api first
    try:
        result = get_thunderstorm(lat, lon)
        return f"{result} (meteofrance-api)"
    except Exception as e:
        logger.warning(f"MeteoFrance API failed for thunderstorm, trying open-meteo: {e}")

        # Fallback to open-meteo (limited thunderstorm data)
        try:
            openmeteo_data = fetch_openmeteo_forecast(lat, lon)
            current = openmeteo_data.get('current', {})

            # OpenMeteo doesn't provide specific thunderstorm data
            # We can only infer from weather codes
            weather_code = current.get('weather_code')
            if weather_code in [95, 96, 97]:  # Thunderstorm codes in OpenMeteo
                return f"Thunderstorm conditions detected (open-meteo)"
            else:
                return f"No thunderstorm data available (open-meteo)"

        except Exception as fallback_error:
            logger.error(f"Both APIs failed for thunderstorm data: {fallback_error}")
            return f"No thunderstorm data available (both APIs failed)"


def get_alerts_with_fallback(lat: float, lon: float) -> List[Alert]:
    """
    Get weather alerts with fallback handling.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        List of Alert objects (empty list if no fallback available)

    Raises:
        ValueError: If coordinates are invalid
    """
    _validate_coordinates(lat, lon)

    # Try meteofrance-api first
    try:
        return get_alerts(lat, lon)
    except Exception as e:
        logger.warning(f"MeteoFrance API failed for alerts: {e}")
        # No fallback available for alerts - open-meteo doesn't provide weather alerts
        return []


def _convert_weather_code_to_condition(weather_code: Optional[int]) -> Optional[str]:
    """
    Convert OpenMeteo weather code to condition string.

    Args:
        weather_code: OpenMeteo weather code

    Returns:
        Weather condition string or None
    """
    if weather_code is None:
        return None

    # OpenMeteo weather codes mapping
    weather_conditions = {
        0: "clear",
        1: "partly_cloudy",
        2: "partly_cloudy",
        3: "overcast",
        45: "foggy",
        48: "foggy",
        51: "drizzle",
        53: "drizzle",
        55: "drizzle",
        56: "drizzle",
        57: "drizzle",
        61: "rain",
        63: "rain",
        65: "rain",
        66: "rain",
        67: "rain",
        71: "snow",
        73: "snow",
        75: "snow",
        77: "snow",
        80: "rain",
        81: "rain",
        82: "rain",
        85: "snow",
        86: "snow",
        95: "thunderstorm",
        96: "thunderstorm",
        97: "thunderstorm",
        98: "thunderstorm",
        99: "thunderstorm"
    }

    return weather_conditions.get(weather_code, "unknown")


def get_tomorrow_forecast(lat: float, lon: float) -> List[ForecastResult]:
    """
    Get tomorrow's weather forecast from meteofrance-api (05:00-17:00).

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        List of ForecastResult containing tomorrow's weather data

    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If API request fails
    """
    _validate_coordinates(lat, lon)

    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)

        if not forecast.forecast or len(forecast.forecast) == 0:
            raise RuntimeError("No forecast data received")

        # Get tomorrow's date
        from datetime import datetime, timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_date = tomorrow.date()

        tomorrow_forecasts = []

        for entry in forecast.forecast:
            # Parse the datetime from the forecast entry using 'dt' field (Unix timestamp)
            dt_timestamp = entry.get('dt')
            if not dt_timestamp:
                logger.warning(f"Skipping entry with empty dt: {entry}")
                continue

            try:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                entry_date = entry_datetime.date()
                entry_hour = entry_datetime.hour

                # Check if it's tomorrow and between 05:00-17:00
                if entry_date == tomorrow_date and 5 <= entry_hour <= 17:
                    # Extract wind data from the nested structure
                    wind_data = entry.get('wind', {})
                    wind_speed = wind_data.get('speed', 0.0)
                    wind_gusts = wind_data.get('gust', 0.0)

                    tomorrow_forecasts.append(ForecastResult(
                        temperature=entry['T']['value'],
                        weather_condition=entry.get('weather', {}).get('desc'),
                        precipitation_probability=entry.get('precipitation_probability'),
                        timestamp=str(entry_datetime),  # Convert to string for consistency
                        wind_speed=wind_speed,
                        wind_gusts=wind_gusts,
                        data_source="meteofrance-api"
                    ))
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping entry with invalid dt '{dt_timestamp}': {e}")
                continue

        if not tomorrow_forecasts:
            logger.warning(f"No tomorrow forecast data found for {lat}, {lon}")
            return []

        logger.info(f"Found {len(tomorrow_forecasts)} tomorrow forecast entries for {lat}, {lon}")
        return tomorrow_forecasts

    except Exception as e:
        logger.error(f"Failed to fetch tomorrow's forecast from meteofrance-api: {e}")
        raise RuntimeError(f"Failed to fetch tomorrow's forecast: {str(e)}")


def get_french_weather_text(lat: float, lon: float) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get French weather text descriptions for today and tomorrow from MeteoFrance API.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        
    Returns:
        Dictionary with 'today' and 'tomorrow' keys, each containing a list of weather entries
        with French descriptions, timestamps, and other weather data
        
    Raises:
        ValueError: If coordinates are invalid
        RuntimeError: If API request fails
    """
    _validate_coordinates(lat, lon)
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(lat, lon)
        
        if not forecast.forecast or len(forecast.forecast) == 0:
            raise RuntimeError("No forecast data received")
        
        from datetime import datetime, date
        
        today = date.today()
        tomorrow = today.replace(day=today.day + 1)
        
        today_entries = []
        tomorrow_entries = []
        
        for entry in forecast.forecast:
            # Parse the datetime from the forecast entry
            dt_timestamp = entry.get('dt')
            if not dt_timestamp:
                continue
                
            try:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                entry_date = entry_datetime.date()
                
                # Extract weather description in French
                weather_data = entry.get('weather', {})
                if isinstance(weather_data, dict):
                    weather_desc = weather_data.get('desc', '')
                else:
                    weather_desc = str(weather_data) if weather_data else ''
                
                # Extract temperature
                temp_data = entry.get('T', {})
                if isinstance(temp_data, dict):
                    temperature = temp_data.get('value', 0.0)
                else:
                    temperature = float(temp_data) if temp_data else 0.0
                
                # Extract wind data
                wind_data = entry.get('wind', {})
                wind_speed = wind_data.get('speed', 0.0) if isinstance(wind_data, dict) else 0.0
                wind_gusts = wind_data.get('gust', 0.0) if isinstance(wind_data, dict) else 0.0
                
                # Extract precipitation data
                rain_data = entry.get('rain', {})
                precipitation = rain_data.get('1h', 0.0) if isinstance(rain_data, dict) else 0.0
                
                # Create weather entry
                weather_entry = {
                    'datetime': entry_datetime.strftime('%Y-%m-%d %H:%M'),
                    'hour': entry_datetime.hour,
                    'french_description': weather_desc,
                    'temperature': temperature,
                    'wind_speed': wind_speed,
                    'wind_gusts': wind_gusts,
                    'precipitation': precipitation,
                    'precipitation_probability': entry.get('precipitation_probability'),
                    'humidity': entry.get('humidity'),
                    'clouds': entry.get('clouds')
                }
                
                # Categorize by date
                if entry_date == today:
                    today_entries.append(weather_entry)
                elif entry_date == tomorrow:
                    tomorrow_entries.append(weather_entry)
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping entry with invalid dt '{dt_timestamp}': {e}")
                continue
        
        return {
            'today': sorted(today_entries, key=lambda x: x['hour']),
            'tomorrow': sorted(tomorrow_entries, key=lambda x: x['hour'])
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch French weather text: {e}")
        raise RuntimeError(f"Failed to fetch French weather text: {str(e)}") 