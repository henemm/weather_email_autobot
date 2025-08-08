"""
Stable MeteoFrance API implementation using meteofrance-api library.

This module provides a stable and reliable interface to the MeteoFrance API
using the official meteofrance-api Python library with unified data structures.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from meteofrance_api.client import MeteoFranceClient

from .unified_weather_data import (
    WeatherEntry, 
    WeatherDataPoint, 
    UnifiedWeatherData
)

logger = logging.getLogger(__name__)


class StableMeteoFranceAPI:
    """
    Stable MeteoFrance API client using meteofrance-api library.
    
    This class provides a reliable interface to fetch weather data
    from MeteoFrance using the official Python library.
    """
    
    def __init__(self):
        """Initialize the MeteoFrance API client."""
        self.client = MeteoFranceClient()
        logger.info("StableMeteoFranceAPI initialized")
    
    def get_forecast_data(self, latitude: float, longitude: float, location_name: str) -> WeatherDataPoint:
        """
        Get forecast data for a specific location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            location_name: Name of the location
            
        Returns:
            WeatherDataPoint containing all forecast entries
            
        Raises:
            RuntimeError: If API request fails
        """
        try:
            logger.info(f"Fetching forecast data for {location_name} ({latitude}, {longitude})")
            
            # Fetch data from MeteoFrance API
            forecast = self.client.get_forecast(latitude, longitude)
            
            if not forecast.forecast or len(forecast.forecast) == 0:
                raise RuntimeError(f"No forecast data received for {location_name}")
            
            logger.info(f"Received {len(forecast.forecast)} forecast entries for {location_name}")
            
            # Create data point
            data_point = WeatherDataPoint(
                latitude=latitude,
                longitude=longitude,
                location_name=location_name
            )
            
            # Convert entries to unified format
            for entry in forecast.forecast:
                weather_entry = WeatherEntry.from_meteofrance_entry(entry)
                data_point.add_entry(weather_entry)
            
            logger.info(f"Successfully converted {len(data_point.entries)} entries for {location_name}")
            return data_point
            
        except Exception as e:
            logger.error(f"Failed to fetch forecast data for {location_name}: {e}")
            raise RuntimeError(f"Failed to fetch forecast data for {location_name}: {str(e)}")
    
    def get_multiple_locations_data(self, locations: List[Dict[str, Any]]) -> UnifiedWeatherData:
        """
        Get forecast data for multiple locations.
        
        Args:
            locations: List of location dictionaries with 'lat', 'lon', 'name' keys
            
        Returns:
            UnifiedWeatherData containing data for all locations
        """
        unified_data = UnifiedWeatherData()
        unified_data.stage_date = datetime.now().strftime('%Y-%m-%d')
        
        for location in locations:
            try:
                lat = location['lat']
                lon = location['lon']
                name = location['name']
                
                data_point = self.get_forecast_data(lat, lon, name)
                unified_data.add_data_point(data_point)
                
                logger.info(f"Successfully added data for {name}")
                
            except Exception as e:
                logger.error(f"Failed to get data for location {location}: {e}")
                # Continue with other locations instead of failing completely
                continue
        
        if not unified_data.data_points:
            raise RuntimeError("No weather data could be fetched for any location")
        
        logger.info(f"Successfully fetched data for {len(unified_data.data_points)} locations")
        return unified_data
    
    def get_stage_weather_data(self, stage_coordinates: List[List[float]], stage_name: str) -> UnifiedWeatherData:
        """
        Get weather data for all points of a stage.
        
        Args:
            stage_coordinates: List of [lat, lon] coordinate pairs
            stage_name: Name of the stage
            
        Returns:
            UnifiedWeatherData containing data for all stage points
        """
        locations = []
        
        for i, coord in enumerate(stage_coordinates):
            if len(coord) >= 2:
                lat, lon = coord[0], coord[1]
                location_name = f"{stage_name}_point_{i+1}"
                locations.append({
                    'lat': lat,
                    'lon': lon,
                    'name': location_name
                })
        
        unified_data = self.get_multiple_locations_data(locations)
        unified_data.stage_name = stage_name
        
        logger.info(f"Successfully fetched weather data for stage {stage_name} with {len(unified_data.data_points)} points")
        return unified_data
    
    def get_thunderstorm_forecast_tomorrow(self, unified_data: UnifiedWeatherData) -> Dict[str, Any]:
        """
        Get thunderstorm forecast for tomorrow (+1 day).
        
        Args:
            unified_data: UnifiedWeatherData object
            
        Returns:
            Dictionary containing tomorrow's thunderstorm forecast
        """
        try:
            # Calculate tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_date = tomorrow.date()
            
            # Define time range for tomorrow (04:00-22:00)
            tomorrow_start = tomorrow.replace(hour=4, minute=0, second=0, microsecond=0)
            tomorrow_end = tomorrow.replace(hour=22, minute=0, second=0, microsecond=0)
            
            logger.info(f"Analyzing thunderstorm forecast for tomorrow ({tomorrow_date})")
            
            all_thunderstorm_entries = []
            
            # Check all data points for tomorrow's thunderstorm data
            for point in unified_data.data_points:
                tomorrow_entries = point.get_entries_for_time_range(tomorrow_start, tomorrow_end)
                
                for entry in tomorrow_entries:
                    # Check for thunderstorm in weather description
                    desc_lower = entry.weather_description.lower()
                    if any(keyword in desc_lower for keyword in ['orage', 'thunderstorm', 'éclair', 'orages']):
                        all_thunderstorm_entries.append({
                            'timestamp': entry.timestamp,
                            'location': point.location_name,
                            'description': entry.weather_description,
                            'rain_amount': entry.rain_amount,
                            'wind_speed': entry.wind_speed
                        })
            
            if not all_thunderstorm_entries:
                return {
                    'has_thunderstorm': False,
                    'thunderstorm_count': 0,
                    'first_thunderstorm_time': None,
                    'max_thunderstorm_probability': 0,
                    'thunderstorm_details': []
                }
            
            # Sort by timestamp to find first occurrence
            all_thunderstorm_entries.sort(key=lambda x: x['timestamp'])
            first_thunderstorm_time = all_thunderstorm_entries[0]['timestamp']
            
            # Calculate thunderstorm probability based on number of thunderstorm hours
            total_hours = 18  # 04:00-22:00 = 18 hours
            thunderstorm_hours = len(all_thunderstorm_entries)
            thunderstorm_probability = min(100, int((thunderstorm_hours / total_hours) * 100))
            
            return {
                'has_thunderstorm': True,
                'thunderstorm_count': len(all_thunderstorm_entries),
                'first_thunderstorm_time': first_thunderstorm_time,
                'max_thunderstorm_probability': thunderstorm_probability,
                'thunderstorm_details': all_thunderstorm_entries
            }
            
        except Exception as e:
            logger.error(f"Failed to get tomorrow's thunderstorm forecast: {e}")
            return {
                'has_thunderstorm': False,
                'thunderstorm_count': 0,
                'first_thunderstorm_time': None,
                'max_thunderstorm_probability': 0,
                'thunderstorm_details': [],
                'error': str(e)
            }
    
    def get_weather_summary(self, unified_data: UnifiedWeatherData, 
                          start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Get a weather summary for the specified time range.
        
        Args:
            unified_data: UnifiedWeatherData object
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            Dictionary containing weather summary
        """
        try:
            aggregated_stats = unified_data.get_aggregated_stats(start_time, end_time)
            
            # Get tomorrow's thunderstorm forecast
            tomorrow_thunderstorm = self.get_thunderstorm_forecast_tomorrow(unified_data)
            
            # Create a human-readable summary
            summary = {
                'stage_name': unified_data.stage_name,
                'stage_date': unified_data.stage_date,
                'time_range': {
                    'start': start_time.strftime('%H:%M'),
                    'end': end_time.strftime('%H:%M')
                },
                'data_points': len(unified_data.data_points),
                'temperature': aggregated_stats.get('temperature', {}),
                'rain': aggregated_stats.get('rain', {}),
                'wind': aggregated_stats.get('wind', {}),
                'thunderstorm': aggregated_stats.get('thunderstorm', {}),
                'thunderstorm_tomorrow': tomorrow_thunderstorm,
                'debug_info': self._generate_debug_info(unified_data, start_time, end_time)
            }
            
            logger.info(f"Generated weather summary for {unified_data.stage_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate weather summary: {e}")
            raise RuntimeError(f"Failed to generate weather summary: {str(e)}")
    
    def _generate_debug_info(self, unified_data: UnifiedWeatherData, 
                           start_time: datetime, end_time: datetime) -> str:
        """
        Generate debug information for the weather data.
        
        Args:
            unified_data: UnifiedWeatherData object
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            Formatted debug information string
        """
        debug_lines = []
        debug_lines.append(f"Stage: {unified_data.stage_name}")
        debug_lines.append(f"Date: {unified_data.stage_date}")
        debug_lines.append(f"Data points: {len(unified_data.data_points)}")
        debug_lines.append(f"Time range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        for i, point in enumerate(unified_data.data_points):
            debug_lines.append(f"\nPoint {i+1}: {point.location_name}")
            debug_lines.append(f"  Coordinates: ({point.latitude:.6f}, {point.longitude:.6f})")
            debug_lines.append(f"  Total entries: {len(point.entries)}")
            
            # Get stats for this point
            temp_stats = point.get_temperature_stats(start_time, end_time)
            rain_stats = point.get_rain_stats(start_time, end_time)
            wind_stats = point.get_wind_stats(start_time, end_time)
            
            if temp_stats['max_temp'] is not None:
                debug_lines.append(f"  Temperature: {temp_stats['min_temp']:.1f}°C - {temp_stats['max_temp']:.1f}°C")
            
            if rain_stats['max_rain_rate'] > 0:
                debug_lines.append(f"  Rain: {rain_stats['total_rain']:.1f}mm total, max {rain_stats['max_rain_rate']:.1f}mm/h")
            
            if wind_stats['max_wind_gusts'] > 0:
                debug_lines.append(f"  Wind: avg {wind_stats['avg_wind_speed']:.1f}km/h, gusts up to {wind_stats['max_wind_gusts']:.1f}km/h")
        
        # Add tomorrow's thunderstorm forecast
        tomorrow_thunderstorm = self.get_thunderstorm_forecast_tomorrow(unified_data)
        debug_lines.append(f"\nTomorrow's Thunderstorm Forecast:")
        if tomorrow_thunderstorm['has_thunderstorm']:
            debug_lines.append(f"  Has thunderstorm: Yes")
            debug_lines.append(f"  Probability: {tomorrow_thunderstorm['max_thunderstorm_probability']}%")
            debug_lines.append(f"  First occurrence: {tomorrow_thunderstorm['first_thunderstorm_time'].strftime('%H:%M')}")
            debug_lines.append(f"  Total occurrences: {tomorrow_thunderstorm['thunderstorm_count']}")
        else:
            debug_lines.append(f"  Has thunderstorm: No")
        
        return "\n".join(debug_lines)


# Convenience functions for backward compatibility
def get_stable_forecast_data(latitude: float, longitude: float, location_name: str) -> WeatherDataPoint:
    """
    Get stable forecast data for a single location.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        location_name: Name of the location
        
    Returns:
        WeatherDataPoint containing forecast data
    """
    api = StableMeteoFranceAPI()
    return api.get_forecast_data(latitude, longitude, location_name)


def get_stable_stage_data(stage_coordinates: List[List[float]], stage_name: str) -> UnifiedWeatherData:
    """
    Get stable weather data for a stage.
    
    Args:
        stage_coordinates: List of [lat, lon] coordinate pairs
        stage_name: Name of the stage
        
    Returns:
        UnifiedWeatherData containing stage weather data
    """
    api = StableMeteoFranceAPI()
    return api.get_stage_weather_data(stage_coordinates, stage_name) 