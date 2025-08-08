"""
Unified weather data structure for meteofrance-api integration.

This module provides a unified data structure for weather data that can handle
the meteofrance-api data format and provide a clean interface for processing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class WeatherEntry:
    """Single weather data entry with unified structure."""
    
    # Time information
    timestamp: datetime
    unix_timestamp: int
    
    # Temperature
    temperature: float  # °C
    
    # Wind
    wind_speed: float  # km/h
    wind_gusts: float  # km/h
    wind_direction: int  # degrees
    
    # Precipitation
    rain_amount: float  # mm/h
    snow_amount: float  # mm/h
    
    # Weather conditions
    weather_description: str
    weather_icon: str
    
    # Additional data
    humidity: int  # %
    clouds: int  # %
    sea_level_pressure: float  # hPa
    
    # Source information
    data_source: str = "meteofrance-api"
    
    @classmethod
    def from_meteofrance_entry(cls, entry: Dict[str, Any]) -> 'WeatherEntry':
        """Create WeatherEntry from meteofrance-api forecast entry."""
        
        # Extract timestamp
        dt_timestamp = entry.get('dt', 0)
        dt_datetime = datetime.fromtimestamp(dt_timestamp)
        
        # Extract temperature
        temp_data = entry.get('T', {})
        temperature = temp_data.get('value', 0.0) if isinstance(temp_data, dict) else 0.0
        
        # Extract wind data
        wind_data = entry.get('wind', {})
        wind_speed = wind_data.get('speed', 0.0) if isinstance(wind_data, dict) else 0.0
        wind_gusts = wind_data.get('gust', 0.0) if isinstance(wind_data, dict) else 0.0
        wind_direction = wind_data.get('direction', 0) if isinstance(wind_data, dict) else 0
        
        # Extract precipitation data
        rain_data = entry.get('rain', {})
        rain_amount = rain_data.get('1h', 0.0) if isinstance(rain_data, dict) else 0.0
        
        snow_data = entry.get('snow', {})
        snow_amount = snow_data.get('1h', 0.0) if isinstance(snow_data, dict) else 0.0
        
        # Extract weather data
        weather_data = entry.get('weather', {})
        weather_description = weather_data.get('desc', 'Unknown') if isinstance(weather_data, dict) else 'Unknown'
        weather_icon = weather_data.get('icon', '') if isinstance(weather_data, dict) else ''
        
        # Extract additional data
        humidity = entry.get('humidity', 0)
        clouds = entry.get('clouds', 0)
        sea_level_pressure = entry.get('sea_level', 0.0)
        
        return cls(
            timestamp=dt_datetime,
            unix_timestamp=dt_timestamp,
            temperature=temperature,
            wind_speed=wind_speed,
            wind_gusts=wind_gusts,
            wind_direction=wind_direction,
            rain_amount=rain_amount,
            snow_amount=snow_amount,
            weather_description=weather_description,
            weather_icon=weather_icon,
            humidity=humidity,
            clouds=clouds,
            sea_level_pressure=sea_level_pressure
        )


@dataclass
class WeatherDataPoint:
    """Weather data for a specific geographic point."""
    
    latitude: float
    longitude: float
    location_name: str
    entries: List[WeatherEntry] = field(default_factory=list)
    
    def add_entry(self, entry: WeatherEntry) -> None:
        """Add a weather entry to this data point."""
        self.entries.append(entry)
    
    def get_entries_for_time_range(self, start_time: datetime, end_time: datetime) -> List[WeatherEntry]:
        """Get entries within a specific time range."""
        return [
            entry for entry in self.entries
            if start_time <= entry.timestamp <= end_time
        ]
    
    def get_temperature_stats(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get temperature statistics for a time range."""
        relevant_entries = self.get_entries_for_time_range(start_time, end_time)
        
        if not relevant_entries:
            return {
                'min_temp': None,
                'max_temp': None,
                'avg_temp': None,
                'min_time': None,
                'max_time': None
            }
        
        temps = [(entry.temperature, entry.timestamp) for entry in relevant_entries]
        min_temp, min_time = min(temps, key=lambda x: x[0])
        max_temp, max_time = max(temps, key=lambda x: x[0])
        avg_temp = sum(temp for temp, _ in temps) / len(temps)
        
        return {
            'min_temp': min_temp,
            'max_temp': max_temp,
            'avg_temp': avg_temp,
            'min_time': min_time,
            'max_time': max_time
        }
    
    def get_rain_stats(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get rain statistics for a time range."""
        relevant_entries = self.get_entries_for_time_range(start_time, end_time)
        
        if not relevant_entries:
            return {
                'total_rain': 0.0,
                'max_rain_rate': 0.0,
                'max_rain_time': None,
                'rain_hours': 0
            }
        
        rain_entries = [(entry.rain_amount, entry.timestamp) for entry in relevant_entries]
        total_rain = sum(rain for rain, _ in rain_entries)
        max_rain_rate, max_rain_time = max(rain_entries, key=lambda x: x[0])
        rain_hours = sum(1 for rain, _ in rain_entries if rain > 0)
        
        return {
            'total_rain': total_rain,
            'max_rain_rate': max_rain_rate,
            'max_rain_time': max_rain_time,
            'rain_hours': rain_hours
        }
    
    def get_wind_stats(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get wind statistics for a time range."""
        relevant_entries = self.get_entries_for_time_range(start_time, end_time)
        
        if not relevant_entries:
            return {
                'avg_wind_speed': 0.0,
                'max_wind_gusts': 0.0,
                'max_gusts_time': None
            }
        
        wind_entries = [(entry.wind_speed, entry.wind_gusts, entry.timestamp) for entry in relevant_entries]
        avg_wind_speed = sum(wind for wind, _, _ in wind_entries) / len(wind_entries)
        max_gusts = max(wind_entries, key=lambda x: x[1])
        max_wind_gusts, _, max_gusts_time = max_gusts
        
        return {
            'avg_wind_speed': avg_wind_speed,
            'max_wind_gusts': max_wind_gusts,
            'max_gusts_time': max_gusts_time
        }
    
    def get_thunderstorm_info(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get thunderstorm information for a time range."""
        relevant_entries = self.get_entries_for_time_range(start_time, end_time)
        
        thunderstorm_entries = []
        for entry in relevant_entries:
            # Check for thunderstorm in weather description
            desc_lower = entry.weather_description.lower()
            if any(keyword in desc_lower for keyword in ['orage', 'thunderstorm', 'éclair']):
                thunderstorm_entries.append(entry)
        
        if not thunderstorm_entries:
            return {
                'has_thunderstorm': False,
                'thunderstorm_count': 0,
                'first_thunderstorm_time': None
            }
        
        return {
            'has_thunderstorm': True,
            'thunderstorm_count': len(thunderstorm_entries),
            'first_thunderstorm_time': min(entry.timestamp for entry in thunderstorm_entries)
        }


@dataclass
class UnifiedWeatherData:
    """Unified weather data container for multiple geographic points."""
    
    data_points: List[WeatherDataPoint] = field(default_factory=list)
    stage_name: str = ""
    stage_date: str = ""
    
    def add_data_point(self, data_point: WeatherDataPoint) -> None:
        """Add a weather data point."""
        self.data_points.append(data_point)
    
    def get_data_point(self, latitude: float, longitude: float) -> Optional[WeatherDataPoint]:
        """Get weather data point for specific coordinates."""
        for point in self.data_points:
            if abs(point.latitude - latitude) < 0.001 and abs(point.longitude - longitude) < 0.001:
                return point
        return None
    
    def get_aggregated_stats(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get aggregated statistics across all data points."""
        if not self.data_points:
            return {}
        
        all_temp_stats = []
        all_rain_stats = []
        all_wind_stats = []
        all_thunderstorm_stats = []
        
        for point in self.data_points:
            temp_stats = point.get_temperature_stats(start_time, end_time)
            rain_stats = point.get_rain_stats(start_time, end_time)
            wind_stats = point.get_wind_stats(start_time, end_time)
            thunderstorm_stats = point.get_thunderstorm_info(start_time, end_time)
            
            if temp_stats['max_temp'] is not None:
                all_temp_stats.append(temp_stats)
            if rain_stats['max_rain_rate'] > 0:
                all_rain_stats.append(rain_stats)
            if wind_stats['max_wind_gusts'] > 0:
                all_wind_stats.append(wind_stats)
            if thunderstorm_stats['has_thunderstorm']:
                all_thunderstorm_stats.append(thunderstorm_stats)
        
        # Aggregate temperature data
        if all_temp_stats:
            max_temp = max(stats['max_temp'] for stats in all_temp_stats)
            min_temp = min(stats['min_temp'] for stats in all_temp_stats)
            avg_temp = sum(stats['avg_temp'] for stats in all_temp_stats) / len(all_temp_stats)
        else:
            max_temp = min_temp = avg_temp = None
        
        # Aggregate rain data
        if all_rain_stats:
            total_rain = sum(stats['total_rain'] for stats in all_rain_stats)
            max_rain_rate = max(stats['max_rain_rate'] for stats in all_rain_stats)
        else:
            total_rain = 0.0
            max_rain_rate = 0.0
        
        # Aggregate wind data
        if all_wind_stats:
            max_wind_gusts = max(stats['max_wind_gusts'] for stats in all_wind_stats)
            avg_wind_speed = sum(stats['avg_wind_speed'] for stats in all_wind_stats) / len(all_wind_stats)
        else:
            max_wind_gusts = 0.0
            avg_wind_speed = 0.0
        
        # Thunderstorm data
        has_thunderstorm = any(stats['has_thunderstorm'] for stats in all_thunderstorm_stats)
        thunderstorm_count = sum(stats['thunderstorm_count'] for stats in all_thunderstorm_stats)
        
        return {
            'temperature': {
                'max': max_temp,
                'min': min_temp,
                'average': avg_temp
            },
            'rain': {
                'total': total_rain,
                'max_rate': max_rain_rate
            },
            'wind': {
                'average_speed': avg_wind_speed,
                'max_gusts': max_wind_gusts
            },
            'thunderstorm': {
                'has_thunderstorm': has_thunderstorm,
                'count': thunderstorm_count
            }
        } 