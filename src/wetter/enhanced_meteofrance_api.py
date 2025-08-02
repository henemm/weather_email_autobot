"""
Enhanced MeteoFrance API implementation with comprehensive data handling.

This module provides a complete interface to the MeteoFrance API with support for:
- Hourly forecast data
- Daily forecast data  
- Probability forecast data
- Thunderstorm detection with timing
- Rain probability calculations
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from meteofrance_api.client import MeteoFranceClient

from .unified_weather_data import (
    WeatherEntry, 
    WeatherDataPoint, 
    UnifiedWeatherData
)

logger = logging.getLogger(__name__)


@dataclass
class ProbabilityData:
    """Probability forecast data structure."""
    timestamp: datetime
    rain_3h: Optional[int]  # Rain probability for next 3 hours (0-100%)
    rain_6h: Optional[int]  # Rain probability for next 6 hours (0-100%)
    snow_3h: Optional[int]  # Snow probability for next 3 hours (0-100%)
    snow_6h: Optional[int]  # Snow probability for next 6 hours (0-100%)
    freezing: int  # Freezing probability (0-100%)


@dataclass
class ThunderstormData:
    """Thunderstorm detection data structure."""
    timestamp: datetime
    description: str
    icon: str
    rain_amount: float  # mm/h
    wind_speed: float   # km/h
    probability: Optional[int] = None  # Calculated probability


class EnhancedMeteoFranceAPI:
    """
    Enhanced MeteoFrance API client with comprehensive data handling.
    
    This class provides a complete interface to fetch and process all available
    weather data from MeteoFrance using the official Python library.
    """
    
    def __init__(self):
        """Initialize the enhanced MeteoFrance API client."""
        self.client = MeteoFranceClient()
        logger.info("EnhancedMeteoFranceAPI initialized")
    
    def get_complete_forecast_data(self, latitude: float, longitude: float, location_name: str) -> Dict[str, Any]:
        """
        Get complete forecast data including hourly, daily, and probability data.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            location_name: Name of the location
            
        Returns:
            Dictionary containing all available forecast data
            
        Raises:
            RuntimeError: If API request fails
        """
        try:
            logger.info(f"Fetching complete forecast data for {location_name} ({latitude}, {longitude})")
            
            # Fetch data from MeteoFrance API
            forecast = self.client.get_forecast(latitude, longitude)
            
            if not forecast.forecast or len(forecast.forecast) == 0:
                raise RuntimeError(f"No forecast data received for {location_name}")
            
            logger.info(f"Received {len(forecast.forecast)} hourly entries for {location_name}")
            
            # Extract all data types
            result = {
                'location_name': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'hourly_data': self._extract_hourly_data(forecast.forecast),
                'daily_forecast': {'daily': self._extract_daily_data(forecast.daily_forecast)} if hasattr(forecast, 'daily_forecast') else {'daily': []},
                'probability_data': self._extract_probability_data(forecast.probability_forecast) if hasattr(forecast, 'probability_forecast') else [],
                'current_data': self._extract_current_data(forecast.current_forecast) if hasattr(forecast, 'current_forecast') else None,
                'position_data': self._extract_position_data(forecast.position) if hasattr(forecast, 'position') else None,
                'thunderstorm_data': self._extract_thunderstorm_data(forecast.forecast),
                'rain_probability_data': self._extract_rain_probability_data(forecast.probability_forecast) if hasattr(forecast, 'probability_forecast') else []
            }
            
            logger.info(f"Successfully extracted complete data for {location_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch complete forecast data for {location_name}: {e}")
            raise RuntimeError(f"Failed to fetch complete forecast data for {location_name}: {str(e)}")
    
    def _extract_hourly_data(self, forecast_entries: List[Dict[str, Any]]) -> List[WeatherEntry]:
        """Extract hourly weather data from forecast entries."""
        hourly_data = []
        
        for entry in forecast_entries:
            try:
                weather_entry = WeatherEntry.from_meteofrance_entry(entry)
                hourly_data.append(weather_entry)
            except Exception as e:
                logger.warning(f"Failed to extract hourly entry: {e}")
                continue
        
        logger.info(f"Extracted {len(hourly_data)} hourly entries")
        return hourly_data
    
    def _extract_daily_data(self, daily_forecast: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract daily forecast data."""
        if not daily_forecast:
            return []
        
        daily_data = []
        for entry in daily_forecast:
            try:
                daily_entry = {
                    'dt': entry['dt'],  # Keep original dt for Night function
                    'date': datetime.fromtimestamp(entry['dt']).date(),
                    'timestamp': datetime.fromtimestamp(entry['dt']),
                    'T': {  # Keep original T structure for Night function
                        'min': entry.get('T', {}).get('min'),
                        'max': entry.get('T', {}).get('max'),
                        'sea': entry.get('T', {}).get('sea')
                    },
                    'temperature': {
                        'min': entry.get('T', {}).get('min'),
                        'max': entry.get('T', {}).get('max'),
                        'sea': entry.get('T', {}).get('sea')
                    },
                    'humidity': {
                        'min': entry.get('humidity', {}).get('min'),
                        'max': entry.get('humidity', {}).get('max')
                    },
                    'precipitation': {
                        '24h': entry.get('precipitation', {}).get('24h')
                    },
                    'wind': {
                        'speed': entry.get('wind', {}).get('speed'),
                        'gusts': entry.get('wind', {}).get('gust'),
                        'direction': entry.get('wind', {}).get('direction')
                    },
                    'uv_index': entry.get('uv'),
                    'weather_12h': {
                        'icon': entry.get('weather12H', {}).get('icon'),
                        'desc': entry.get('weather12H', {}).get('desc')
                    },
                    'sun': {
                        'rise': datetime.fromtimestamp(entry.get('sun', {}).get('rise', 0)),
                        'set': datetime.fromtimestamp(entry.get('sun', {}).get('set', 0))
                    } if entry.get('sun') else None
                }
                daily_data.append(daily_entry)
            except Exception as e:
                logger.warning(f"Failed to extract daily entry: {e}")
                continue
        
        logger.info(f"Extracted {len(daily_data)} daily entries")
        return daily_data
    
    def _extract_probability_data(self, probability_forecast: List[Dict[str, Any]]) -> List[ProbabilityData]:
        """Extract probability forecast data."""
        if not probability_forecast:
            return []
        
        probability_data = []
        for entry in probability_forecast:
            try:
                prob_entry = ProbabilityData(
                    timestamp=datetime.fromtimestamp(entry['dt']),
                    rain_3h=entry.get('rain', {}).get('3h'),
                    rain_6h=entry.get('rain', {}).get('6h'),
                    snow_3h=entry.get('snow', {}).get('3h'),
                    snow_6h=entry.get('snow', {}).get('6h'),
                    freezing=entry.get('freezing', 0)
                )
                probability_data.append(prob_entry)
            except Exception as e:
                logger.warning(f"Failed to extract probability entry: {e}")
                continue
        
        logger.info(f"Extracted {len(probability_data)} probability entries")
        return probability_data
    
    def _extract_current_data(self, current_forecast: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract current weather data."""
        if not current_forecast:
            return None
        
        try:
            current_data = {
                'timestamp': datetime.fromtimestamp(current_forecast['dt']),
                'temperature': current_forecast.get('T', {}).get('value'),
                'windchill': current_forecast.get('T', {}).get('windchill'),
                'humidity': current_forecast.get('humidity'),
                'pressure': current_forecast.get('sea_level'),
                'wind': {
                    'speed': current_forecast.get('wind', {}).get('speed'),
                    'gust': current_forecast.get('wind', {}).get('gust'),
                    'direction': current_forecast.get('wind', {}).get('direction'),
                    'icon': current_forecast.get('wind', {}).get('icon')
                },
                'rain': current_forecast.get('rain', {}).get('1h'),
                'snow': current_forecast.get('snow', {}).get('1h'),
                'weather': {
                    'icon': current_forecast.get('weather', {}).get('icon'),
                    'desc': current_forecast.get('weather', {}).get('desc')
                }
            }
            logger.info("Extracted current weather data")
            return current_data
        except Exception as e:
            logger.warning(f"Failed to extract current data: {e}")
            return None
    
    def _extract_position_data(self, position: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract position data."""
        if not position:
            return None
        
        try:
            position_data = {
                'latitude': position.get('lat'),
                'longitude': position.get('lon'),
                'altitude': position.get('alti'),
                'name': position.get('name'),
                'country': position.get('country'),
                'department': position.get('dept'),
                'timezone': position.get('timezone'),
                'insee_code': position.get('insee')
            }
            logger.info("Extracted position data")
            return position_data
        except Exception as e:
            logger.warning(f"Failed to extract position data: {e}")
            return None
    
    def _extract_thunderstorm_data(self, forecast_entries: List[Dict[str, Any]]) -> List[ThunderstormData]:
        """Extract thunderstorm detection data."""
        thunderstorm_data = []
        thunderstorm_keywords = ['orage', 'thunderstorm', 'éclair', 'orages', 'averses orageuses']
        
        for entry in forecast_entries:
            try:
                weather = entry.get('weather', {})
                desc = weather.get('desc', '').lower()
                
                if any(keyword in desc for keyword in thunderstorm_keywords):
                    thunderstorm_entry = ThunderstormData(
                        timestamp=datetime.fromtimestamp(entry['dt']),
                        description=weather.get('desc', ''),
                        icon=weather.get('icon', ''),
                        rain_amount=entry.get('rain', {}).get('1h', 0.0),
                        wind_speed=entry.get('wind', {}).get('speed', 0.0)
                    )
                    thunderstorm_data.append(thunderstorm_entry)
            except Exception as e:
                logger.warning(f"Failed to extract thunderstorm entry: {e}")
                continue
        
        logger.info(f"Extracted {len(thunderstorm_data)} thunderstorm entries")
        return thunderstorm_data
    
    def _extract_rain_probability_data(self, probability_forecast: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract rain probability data for analysis."""
        if not probability_forecast:
            return []
        
        rain_probability_data = []
        for entry in probability_forecast:
            try:
                rain_prob_entry = {
                    'timestamp': datetime.fromtimestamp(entry['dt']),
                    'rain_3h': entry.get('rain', {}).get('3h'),
                    'rain_6h': entry.get('rain', {}).get('6h'),
                    'has_rain_probability': entry.get('rain', {}).get('3h') is not None or entry.get('rain', {}).get('6h') is not None
                }
                rain_probability_data.append(rain_prob_entry)
            except Exception as e:
                logger.warning(f"Failed to extract rain probability entry: {e}")
                continue
        
        logger.info(f"Extracted {len(rain_probability_data)} rain probability entries")
        return rain_probability_data
    
    def get_weather_summary_with_probabilities(self, unified_data: UnifiedWeatherData, 
                                             start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Get comprehensive weather summary including probability data.
        
        Args:
            unified_data: UnifiedWeatherData object
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            Dictionary containing comprehensive weather summary
        """
        try:
            # Get basic aggregated stats
            aggregated_stats = unified_data.get_aggregated_stats(start_time, end_time)
            
            # Get tomorrow's thunderstorm forecast
            tomorrow_thunderstorm = self.get_thunderstorm_forecast_tomorrow(unified_data)
            
            # Create comprehensive summary
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
                'debug_info': self._generate_enhanced_debug_info(unified_data, start_time, end_time)
            }
            
            logger.info(f"Generated comprehensive weather summary for {unified_data.stage_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive weather summary: {e}")
            raise RuntimeError(f"Failed to generate comprehensive weather summary: {str(e)}")
    
    def _generate_enhanced_debug_info(self, unified_data: UnifiedWeatherData, 
                                    start_time: datetime, end_time: datetime) -> str:
        """Generate enhanced debug information including probability data."""
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
    
    def get_thunderstorm_forecast_tomorrow(self, unified_data: UnifiedWeatherData) -> Dict[str, Any]:
        """Get thunderstorm forecast for tomorrow (+1 day)."""
        try:
            # Find tomorrow's date by looking at the actual data timestamps
            all_timestamps = []
            for point in unified_data.data_points:
                for entry in point.entries:
                    all_timestamps.append(entry.timestamp.date())
            
            if not all_timestamps:
                logger.error("No timestamps found in unified data")
                return {
                    'has_thunderstorm': False,
                    'thunderstorm_count': 0,
                    'first_thunderstorm_time': None,
                    'max_thunderstorm_probability': 0,
                    'thunderstorm_details': []
                }
            
            # Find the second unique date (tomorrow)
            unique_dates = sorted(list(set(all_timestamps)))
            if len(unique_dates) < 2:
                logger.info(f"Only one date available: {unique_dates[0]}, no tomorrow data")
                return {
                    'has_thunderstorm': False,
                    'thunderstorm_count': 0,
                    'first_thunderstorm_time': None,
                    'max_thunderstorm_probability': 0,
                    'thunderstorm_details': []
                }
            
            tomorrow_date = unique_dates[1]  # Second date is tomorrow
            logger.info(f"Found tomorrow's date: {tomorrow_date}")
            
            # Define time range for tomorrow (04:00-22:00)
            tomorrow_start = datetime.combine(tomorrow_date, datetime.min.time().replace(hour=4))
            tomorrow_end = datetime.combine(tomorrow_date, datetime.min.time().replace(hour=22))
            
            logger.info(f"Analyzing thunderstorm forecast for tomorrow ({tomorrow_date})")
            
            all_thunderstorm_entries = []
            
            # Check all data points for tomorrow's thunderstorm data
            for point in unified_data.data_points:
                tomorrow_entries = point.get_entries_for_time_range(tomorrow_start, tomorrow_end)
                
                for entry in tomorrow_entries:
                    # Check for thunderstorm in weather description
                    desc_lower = entry.weather_description.lower()
                    if any(keyword in desc_lower for keyword in ['orage', 'thunderstorm', 'éclair', 'orages', 'averses orageuses']):
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


# Convenience functions for backward compatibility
def get_enhanced_forecast_data(latitude: float, longitude: float, location_name: str) -> Dict[str, Any]:
    """Get enhanced forecast data for a single location."""
    api = EnhancedMeteoFranceAPI()
    return api.get_complete_forecast_data(latitude, longitude, location_name) 