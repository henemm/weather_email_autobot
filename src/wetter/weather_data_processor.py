"""
Weather data processor for Météo-France API.

This module processes raw weather data from Météo-France API and converts it
into the format expected by the report generator.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from meteofrance_api.client import MeteoFranceClient

logger = logging.getLogger(__name__)


@dataclass
class WeatherDataProcessor:
    """Processes weather data for report generation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = config.get("thresholds", {})
        
    def process_weather_data(
        self, 
        latitude: float, 
        longitude: float, 
        location_name: str,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """Process weather data for a location and return report-ready format."""
        try:
            client = MeteoFranceClient()
            forecast = client.get_forecast(latitude, longitude)
            
            if not forecast.forecast:
                logger.error(f"No forecast data for {location_name}")
                return self._create_empty_result()
            
            processed_data = self._process_forecast_data(
                forecast.forecast[:hours_ahead], 
                location_name
            )
            
            logger.info(f"Processed weather data for {location_name}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process weather data for {location_name}: {e}")
            return self._create_empty_result()
    
    def _process_forecast_data(
        self, 
        forecast_entries: List[Dict], 
        location_name: str
    ) -> Dict[str, Any]:
        """Process forecast entries into report-ready format."""
        time_points = []
        
        # Find entries for the stage time (14-17 Uhr)
        stage_entries = []
        for entry in forecast_entries:
            try:
                dt_timestamp = entry.get('dt')
                if not dt_timestamp:
                    continue
                    
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                hour = entry_datetime.hour
                
                # Check if this is for the stage time (14-17 Uhr)
                if 14 <= hour <= 17:
                    stage_entries.append(entry)
                    
            except Exception as e:
                logger.warning(f"Failed to process forecast entry timestamp: {e}")
                continue
        
        # If no stage-specific entries found, use all entries as fallback
        if not stage_entries:
            logger.warning(f"No stage time entries (14-17 Uhr) found for {location_name}, using all entries")
            stage_entries = forecast_entries
        
        logger.info(f"Processing {len(stage_entries)} entries for {location_name} (stage time: 14-17 Uhr)")
        
        for entry in stage_entries:
            try:
                dt_timestamp = entry.get('dt')
                if not dt_timestamp:
                    continue
                    
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                
                # Extract data
                weather_condition = self._extract_weather_condition(entry)
                temperature = self._extract_temperature(entry)
                wind_speed = self._extract_wind_speed(entry)
                wind_gusts = self._extract_wind_gusts(entry)
                precipitation_probability = entry.get('precipitation_probability')
                precipitation_amount = self._extract_precipitation_amount(entry)
                
                # Determine thunderstorm probability
                thunderstorm_probability = self._determine_thunderstorm_probability(
                    weather_condition, precipitation_probability
                )
                
                # Determine rain probability
                rain_probability = self._determine_rain_probability(
                    weather_condition, precipitation_probability, precipitation_amount
                )
                
                time_point = {
                    'datetime': entry_datetime,
                    'temperature': temperature,
                    'wind_speed': wind_speed,
                    'wind_gusts': wind_gusts,
                    'precipitation_probability': precipitation_probability,
                    'precipitation_amount': precipitation_amount,
                    'thunderstorm_probability': thunderstorm_probability,
                    'rain_probability': rain_probability,
                    'weather_condition': weather_condition
                }
                
                time_points.append(time_point)
                
            except Exception as e:
                logger.warning(f"Failed to process forecast entry: {e}")
                continue
        
        if not time_points:
            return self._create_empty_result()
        
        return self._calculate_report_values(time_points, location_name)
    
    def _extract_weather_condition(self, entry: Dict) -> Optional[str]:
        """Extract weather condition from forecast entry."""
        weather_data = entry.get('weather', {})
        if isinstance(weather_data, dict):
            return weather_data.get('desc')
        elif isinstance(weather_data, str):
            return weather_data
        return None
    
    def _extract_temperature(self, entry: Dict) -> Optional[float]:
        """Extract temperature from forecast entry."""
        temp_data = entry.get('T', {})
        if isinstance(temp_data, dict):
            return temp_data.get('value')
        return None
    
    def _extract_wind_speed(self, entry: Dict) -> Optional[float]:
        """Extract wind speed from forecast entry."""
        wind_data = entry.get('wind', {})
        if isinstance(wind_data, dict):
            return wind_data.get('speed')
        return None
    
    def _extract_wind_gusts(self, entry: Dict) -> Optional[float]:
        """Extract wind gusts from forecast entry."""
        wind_data = entry.get('wind', {})
        if isinstance(wind_data, dict):
            return wind_data.get('gust')
        return None
    
    def _extract_precipitation_amount(self, entry: Dict) -> Optional[float]:
        """Extract precipitation amount from forecast entry."""
        # Try rain field first (Météo-France API format)
        rain_data = entry.get('rain', {})
        if isinstance(rain_data, dict):
            rain_1h = rain_data.get('1h')
            if rain_1h is not None and rain_1h > 0:
                return rain_1h
        
        # Fallback to precipitation field
        precipitation_data = entry.get('precipitation', {})
        if isinstance(precipitation_data, dict):
            return (
                precipitation_data.get('1h') or 
                precipitation_data.get('3h') or 
                precipitation_data.get('6h') or
                precipitation_data.get('value')
            )
        
        return None
    
    def _determine_thunderstorm_probability(
        self, 
        weather_condition: Optional[str], 
        precipitation_probability: Optional[int]
    ) -> Optional[float]:
        """Determine thunderstorm probability based on weather condition."""
        if not weather_condition:
            return None
        
        weather_lower = weather_condition.lower()
        
        # Check for thunderstorm indicators
        thunderstorm_indicators = [
            'orage', 'orages', 'thunderstorm', 'thunder', 'storm',
            'risque d\'orage', 'risque d\'orages', 'averse orageuse', 'averses orageuses'
        ]
        
        is_thunderstorm = any(indicator in weather_lower for indicator in thunderstorm_indicators)
        
        if is_thunderstorm:
            # For thunderstorm conditions, use precipitation probability if available
            if precipitation_probability is not None:
                return float(precipitation_probability)
            else:
                # Estimate based on weather description
                if 'averse orageuse' in weather_lower or 'averses orageuses' in weather_lower:
                    return 60.0  # Thunderstorm showers
                elif 'orage' in weather_lower:
                    return 80.0  # Direct thunderstorm
                elif 'risque' in weather_lower:
                    return 40.0  # Risk of thunderstorm
                else:
                    return 70.0  # Default thunderstorm probability
        
        return None

    def _determine_rain_probability(
        self, 
        weather_condition: Optional[str], 
        precipitation_probability: Optional[int],
        precipitation_amount: Optional[float]
    ) -> Optional[float]:
        """Determine rain probability based on weather condition and precipitation amount."""
        if not weather_condition:
            return None
        
        weather_lower = weather_condition.lower()
        
        # Check for rain indicators
        rain_indicators = [
            'averse', 'averses', 'pluie', 'pluies', 'rain', 'rains',
            'averse orageuse', 'averses orageuses', 'orage', 'orages'
        ]
        
        is_rain = any(indicator in weather_lower for indicator in rain_indicators)
        
        if is_rain:
            # Use precipitation probability if available
            if precipitation_probability is not None:
                return float(precipitation_probability)
            else:
                # Estimate based on weather description and precipitation amount
                if precipitation_amount and precipitation_amount > 0:
                    # If there's actual precipitation, estimate probability based on amount
                    if precipitation_amount >= 2.0:
                        return 80.0  # Heavy rain
                    elif precipitation_amount >= 1.0:
                        return 60.0  # Moderate rain
                    elif precipitation_amount >= 0.5:
                        return 40.0  # Light rain
                    else:
                        return 30.0  # Very light rain
                else:
                    # Estimate based on weather description only
                    if 'averse orageuse' in weather_lower or 'averses orageuses' in weather_lower:
                        return 70.0  # Thunderstorm showers
                    elif 'orage' in weather_lower:
                        return 80.0  # Thunderstorm
                    elif 'averse' in weather_lower or 'averses' in weather_lower:
                        return 60.0  # Showers
                    elif 'pluie' in weather_lower:
                        return 50.0  # Rain
                    else:
                        return 30.0  # Default rain probability
        
        return None
    
    def _calculate_report_values(
        self, 
        time_points: List[Dict], 
        location_name: str
    ) -> Dict[str, Any]:
        """Calculate report values from processed time points."""
        # Use all time points (already filtered for stage time 14-17 Uhr)
        if not time_points:
            return self._create_empty_result()
        
        # Calculate maximum values
        max_values = self._calculate_max_values(time_points)
        
        # Calculate threshold crossings
        threshold_crossings = self._calculate_threshold_crossings(time_points)
        
        # Build report data
        report_data = {
            'max_temperature': max_values['temperature'],
            'max_precipitation': max_values['precipitation_amount'],
            'max_rain_probability': max_values['precipitation_probability'],
            'max_thunderstorm_probability': max_values['thunderstorm_probability'],
            'max_wind_speed': max_values['wind_gusts'] or max_values['wind_speed'],
            'wind_speed': max_values['wind_speed'],
            
            'thunderstorm_threshold_pct': threshold_crossings['thunderstorm']['value'],
            'thunderstorm_threshold_time': threshold_crossings['thunderstorm']['time'],
            'thunderstorm_max_time': max_values['thunderstorm_time'],
            
            'rain_threshold_pct': threshold_crossings['rain']['value'],
            'rain_threshold_time': threshold_crossings['rain']['time'],
            'rain_max_time': max_values['rain_time'],
            'rain_total_time': max_values['precipitation_time'],
            
            'location': location_name,
            'data_source': 'meteofrance-api',
            'processed_at': datetime.now().isoformat()
        }
        
        return report_data
    
    def _calculate_max_values(self, time_points: List[Dict]) -> Dict[str, Any]:
        """Calculate maximum values from time points."""
        max_values = {
            'temperature': 0.0,
            'precipitation_amount': 0.0,
            'precipitation_probability': 0.0,
            'rain_probability': 0.0,
            'thunderstorm_probability': 0.0,
            'wind_speed': 0.0,
            'wind_gusts': 0.0,
            'temperature_time': '',
            'precipitation_time': '',
            'rain_time': '',
            'thunderstorm_time': ''
        }
        
        for point in time_points:
            time_str = point['datetime'].strftime('%H')
            
            if point['temperature'] and point['temperature'] > max_values['temperature']:
                max_values['temperature'] = point['temperature']
                max_values['temperature_time'] = time_str
            
            if point['precipitation_amount'] and point['precipitation_amount'] > max_values['precipitation_amount']:
                max_values['precipitation_amount'] = point['precipitation_amount']
                max_values['precipitation_time'] = time_str
            
            # Use rain_probability if available, otherwise fallback to precipitation_probability
            rain_prob = point.get('rain_probability') or point.get('precipitation_probability')
            if rain_prob and rain_prob > max_values['rain_probability']:
                max_values['rain_probability'] = rain_prob
                max_values['precipitation_probability'] = rain_prob  # Keep for backward compatibility
                max_values['rain_time'] = time_str
            
            if point['thunderstorm_probability'] and point['thunderstorm_probability'] > max_values['thunderstorm_probability']:
                max_values['thunderstorm_probability'] = point['thunderstorm_probability']
                max_values['thunderstorm_time'] = time_str
            
            if point['wind_speed'] and point['wind_speed'] > max_values['wind_speed']:
                max_values['wind_speed'] = point['wind_speed']
            
            if point['wind_gusts'] and point['wind_gusts'] > max_values['wind_gusts']:
                max_values['wind_gusts'] = point['wind_gusts']
        
        return max_values
    
    def _calculate_threshold_crossings(self, time_points: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Calculate first threshold crossings for each parameter."""
        thunderstorm_threshold = self.thresholds.get('thunderstorm_probability', 20.0)
        rain_threshold = self.thresholds.get('rain_probability', 25.0)
        
        crossings = {
            'thunderstorm': {'value': 0, 'time': ''},
            'rain': {'value': 0, 'time': ''}
        }
        
        for point in time_points:
            time_str = point['datetime'].strftime('%H')
            
            if (point['thunderstorm_probability'] and 
                point['thunderstorm_probability'] >= thunderstorm_threshold and
                crossings['thunderstorm']['value'] == 0):
                crossings['thunderstorm'] = {
                    'value': point['thunderstorm_probability'],
                    'time': time_str
                }
            
            # Use rain_probability if available, otherwise fallback to precipitation_probability
            rain_prob = point.get('rain_probability') or point.get('precipitation_probability')
            if (rain_prob and 
                rain_prob >= rain_threshold and
                crossings['rain']['value'] == 0):
                crossings['rain'] = {
                    'value': rain_prob,
                    'time': time_str
                }
        
        return crossings
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result when no data is available."""
        return {
            'max_temperature': 0.0,
            'max_precipitation': 0.0,
            'max_rain_probability': 0.0,
            'max_thunderstorm_probability': 0.0,
            'max_wind_speed': 0.0,
            'wind_speed': 0.0,
            'thunderstorm_threshold_pct': 0,
            'thunderstorm_threshold_time': '',
            'thunderstorm_max_time': '',
            'rain_threshold_pct': 0,
            'rain_threshold_time': '',
            'rain_max_time': '',
            'rain_total_time': '',
            'location': 'Unknown',
            'data_source': 'meteofrance-api',
            'processed_at': datetime.now().isoformat()
        }


def process_weather_data_for_report(
    latitude: float,
    longitude: float,
    location_name: str,
    config: Dict[str, Any],
    hours_ahead: int = 24
) -> Dict[str, Any]:
    """Process weather data for report generation."""
    processor = WeatherDataProcessor(config)
    return processor.process_weather_data(latitude, longitude, location_name, hours_ahead) 