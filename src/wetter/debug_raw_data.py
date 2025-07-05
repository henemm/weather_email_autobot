"""
Debug module for Météo-France API raw data output.

This module provides human-readable output of raw weather data to verify
consistency between API data and generated reports.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from meteofrance_api.client import MeteoFranceClient

from .fetch_meteofrance import ForecastResult, Alert

logger = logging.getLogger(__name__)


@dataclass
class RawWeatherPoint:
    """Raw weather data point for debugging."""
    timestamp: datetime
    thunderstorm_probability: Optional[float]
    precipitation_probability: Optional[float]
    precipitation_amount: Optional[float]
    temperature: float
    wind_speed: Optional[float]
    wind_gusts: Optional[float]
    weather_condition: Optional[str]


@dataclass
class DebugWeatherData:
    """Debug weather data structure."""
    etappe: str
    geo_points: List[Tuple[float, float, str]]  # lat, lon, name
    time_points: List[RawWeatherPoint]
    data_source: str


def get_raw_weather_data(
    latitude: float, 
    longitude: float, 
    location_name: str,
    hours_ahead: int = 24
) -> DebugWeatherData:
    """
    Get raw weather data for debugging purposes.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        location_name: Human-readable location name
        hours_ahead: Number of hours to fetch (default: 24)
        
    Returns:
        DebugWeatherData containing raw weather information
        
    Raises:
        RuntimeError: If API request fails
    """
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(latitude, longitude)
        
        if not forecast.forecast or len(forecast.forecast) == 0:
            raise RuntimeError("No forecast data received")
        
        time_points = []
        
        # Process forecast entries
        for entry in forecast.forecast[:hours_ahead]:
            # Parse timestamp
            dt_timestamp = entry.get('dt')
            if not dt_timestamp:
                logger.warning(f"Skipping entry with empty dt: {entry}")
                continue
                
            try:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping entry with invalid dt '{dt_timestamp}': {e}")
                continue
            
            # Extract weather data
            weather_data = entry.get('weather', {})
            weather_condition = None
            if isinstance(weather_data, dict):
                weather_condition = weather_data.get('desc')
            elif isinstance(weather_data, str):
                weather_condition = weather_data
            
            # Extract wind data
            wind_data = entry.get('wind', {})
            wind_speed = wind_data.get('speed') if isinstance(wind_data, dict) else None
            wind_gusts = wind_data.get('gust') if isinstance(wind_data, dict) else None
            
            # Extract precipitation data
            precipitation_data = entry.get('precipitation', {})
            precipitation_amount = None
            if isinstance(precipitation_data, dict):
                # Try different precipitation fields
                precipitation_amount = (
                    precipitation_data.get('1h') or 
                    precipitation_data.get('3h') or 
                    precipitation_data.get('6h') or
                    precipitation_data.get('value')
                )
            
            # Determine thunderstorm probability
            thunderstorm_probability = None
            if weather_condition and 'thunder' in weather_condition.lower():
                # If weather condition indicates thunderstorm, use precipitation probability
                thunderstorm_probability = entry.get('precipitation_probability')
            
            time_point = RawWeatherPoint(
                timestamp=entry_datetime,
                thunderstorm_probability=thunderstorm_probability,
                precipitation_probability=entry.get('precipitation_probability'),
                precipitation_amount=precipitation_amount,
                temperature=entry['T']['value'] if 'T' in entry and 'value' in entry['T'] else None,
                wind_speed=wind_speed,
                wind_gusts=wind_gusts,
                weather_condition=weather_condition
            )
            
            time_points.append(time_point)
        
        return DebugWeatherData(
            etappe=location_name,
            geo_points=[(latitude, longitude, location_name)],
            time_points=time_points,
            data_source="meteofrance-api"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch raw weather data: {e}")
        raise RuntimeError(f"Failed to fetch raw weather data: {str(e)}")


def format_raw_data_output(debug_data: DebugWeatherData) -> str:
    """
    Format raw weather data for human-readable output.
    
    Args:
        debug_data: DebugWeatherData object
        
    Returns:
        Formatted string output
    """
    output_lines = []
    
    # Header
    output_lines.append(f"[{debug_data.etappe}] Raw Weather Data")
    output_lines.append(f"Data Source: {debug_data.data_source}")
    output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("")
    
    # Group by hour for better readability
    current_hour = None
    hour_data = []
    
    for point in debug_data.time_points:
        hour = point.timestamp.hour
        
        if current_hour != hour:
            # Output previous hour's data
            if hour_data:
                output_lines.extend(format_hour_data(current_hour, hour_data))
                output_lines.append("")
            
            current_hour = hour
            hour_data = []
        
        hour_data.append(point)
    
    # Output last hour's data
    if hour_data:
        output_lines.extend(format_hour_data(current_hour, hour_data))
    
    return "\n".join(output_lines)


def format_hour_data(hour: int, points: List[RawWeatherPoint]) -> List[str]:
    """
    Format data for a specific hour.
    
    Args:
        hour: Hour of the day
        points: List of weather points for this hour
        
    Returns:
        List of formatted strings
    """
    lines = []
    
    # Hour header
    time_str = f"{hour:02d}:00"
    lines.append(f"@{time_str}")
    
    # Process each geo point (currently only one per hour)
    for i, point in enumerate(points):
        geo_name = f"Geo {i+1}"
        
        # Format thunderstorm probability
        thunderstorm_str = "N/A"
        if point.thunderstorm_probability is not None:
            thunderstorm_str = f"{point.thunderstorm_probability}%"
        
        # Format precipitation probability
        precip_prob_str = "N/A"
        if point.precipitation_probability is not None:
            precip_prob_str = f"{point.precipitation_probability}%"
        
        # Format precipitation amount
        precip_amount_str = "N/A"
        if point.precipitation_amount is not None:
            precip_amount_str = f"{point.precipitation_amount}mm"
        
        # Format temperature
        temp_str = "N/A"
        if point.temperature is not None:
            temp_str = f"{point.temperature}°C"
        
        # Format wind data
        wind_str = "N/A"
        if point.wind_speed is not None:
            wind_str = f"{point.wind_speed}km/h"
            if point.wind_gusts is not None:
                wind_str += f" (Böen: {point.wind_gusts}km/h)"
        
        # Weather condition
        weather_str = point.weather_condition or "N/A"
        
        # Create the formatted line
        line = (f" - {geo_name}: Blitz {thunderstorm_str}, "
                f"RegenW {precip_prob_str}, RegenM {precip_amount_str}, "
                f"Temp {temp_str}, Wind {wind_str}, Wetter {weather_str}")
        
        lines.append(line)
    
    return lines


def get_raw_data_for_multiple_locations(
    locations: List[Tuple[float, float, str]],
    hours_ahead: int = 24
) -> List[DebugWeatherData]:
    """
    Get raw weather data for multiple locations.
    
    Args:
        locations: List of (lat, lon, name) tuples
        hours_ahead: Number of hours to fetch
        
    Returns:
        List of DebugWeatherData objects
    """
    debug_data_list = []
    
    for latitude, longitude, name in locations:
        try:
            debug_data = get_raw_weather_data(latitude, longitude, name, hours_ahead)
            debug_data_list.append(debug_data)
        except Exception as e:
            logger.error(f"Failed to fetch data for {name}: {e}")
            # Create empty debug data for failed locations
            empty_data = DebugWeatherData(
                etappe=name,
                geo_points=[(latitude, longitude, name)],
                time_points=[],
                data_source="error"
            )
            debug_data_list.append(empty_data)
    
    return debug_data_list


def compare_raw_data_with_report(
    debug_data: DebugWeatherData,
    report_values: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare raw data with generated report values.
    
    Args:
        debug_data: Raw weather data
        report_values: Values from generated report
        config: Configuration with thresholds
        
    Returns:
        Comparison results
    """
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "location": debug_data.etappe,
        "data_source": debug_data.data_source,
        "comparisons": {},
        "threshold_checks": {},
        "issues": []
    }
    
    if not debug_data.time_points:
        comparison["issues"].append("No raw data available")
        return comparison
    
    # Extract maximum values from raw data
    raw_max_values = {
        "thunderstorm_probability": max(
            (p.thunderstorm_probability for p in debug_data.time_points 
             if p.thunderstorm_probability is not None), default=None
        ),
        "precipitation_probability": max(
            (p.precipitation_probability for p in debug_data.time_points 
             if p.precipitation_probability is not None), default=None
        ),
        "precipitation_amount": max(
            (p.precipitation_amount for p in debug_data.time_points 
             if p.precipitation_amount is not None), default=None
        ),
        "temperature": max(
            (p.temperature for p in debug_data.time_points 
             if p.temperature is not None), default=None
        ),
        "wind_speed": max(
            (p.wind_speed for p in debug_data.time_points 
             if p.wind_speed is not None), default=None
        )
    }
    
    # Compare with report values
    thresholds = config.get("thresholds", {})
    
    for key, raw_value in raw_max_values.items():
        report_value = report_values.get(key)
        
        comparison["comparisons"][key] = {
            "raw_value": raw_value,
            "report_value": report_value,
            "match": raw_value == report_value
        }
        
        # Check threshold application
        threshold_key = key.replace("_probability", "_probability").replace("_amount", "_amount")
        threshold_value = thresholds.get(threshold_key)
        
        if threshold_value is not None and raw_value is not None:
            threshold_exceeded = raw_value >= threshold_value
            comparison["threshold_checks"][key] = {
                "threshold": threshold_value,
                "value": raw_value,
                "exceeded": threshold_exceeded
            }
            
            # Check if report correctly reflects threshold crossing
            if threshold_exceeded and report_value is None:
                comparison["issues"].append(
                    f"Threshold exceeded for {key} ({raw_value} >= {threshold_value}) "
                    f"but not reflected in report"
                )
    
    return comparison


def save_debug_output(debug_data: DebugWeatherData, output_file: str) -> None:
    """
    Save debug output to file.
    
    Args:
        debug_data: DebugWeatherData object
        output_file: Output file path
    """
    try:
        formatted_output = format_raw_data_output(debug_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        
        logger.info(f"Debug output saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to save debug output: {e}")
        raise RuntimeError(f"Failed to save debug output: {str(e)}") 