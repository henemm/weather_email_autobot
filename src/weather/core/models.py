"""
Unified data models for weather processing.

This module defines consistent data structures for the centralized weather architecture,
ensuring compatibility across all modules and eliminating data structure inconsistencies.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class ReportType(Enum):
    """Enum for report types."""
    MORNING = "morning"
    EVENING = "evening"
    UPDATE = "update"


class VigilanceLevel(Enum):
    """Enum for vigilance warning levels."""
    NONE = 0
    YELLOW = 2
    ORANGE = 3
    RED = 4


@dataclass
class WeatherPoint:
    """Single weather data point with all available metrics."""
    time: datetime
    temperature: Optional[float] = None
    rain_probability: Optional[float] = None
    precipitation_amount: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_gusts: Optional[float] = None
    thunderstorm_probability: Optional[float] = None
    cloud_cover: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    visibility: Optional[float] = None
    weather_condition: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class WeatherData:
    """Collection of weather points for a location and time period."""
    points: List[WeatherPoint] = field(default_factory=list)
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    data_source: str = "unknown"
    processed_at: Optional[datetime] = None


@dataclass
class AggregatedWeatherData:
    """Aggregated weather data for a specific time period and location."""
    # Location info
    location_name: str
    latitude: float
    longitude: float
    
    # Temperature data
    max_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    max_temperature_time: Optional[str] = None
    min_temperature_time: Optional[str] = None
    
    # Rain data
    max_rain_probability: Optional[float] = None
    max_precipitation: Optional[float] = None
    rain_threshold_pct: Optional[float] = None
    rain_threshold_time: Optional[str] = None
    rain_max_time: Optional[str] = None
    precipitation_max_time: Optional[str] = None
    
    # Wind data
    max_wind_speed: Optional[float] = None
    max_wind_gusts: Optional[float] = None
    wind_threshold_kmh: Optional[float] = None
    wind_threshold_time: Optional[str] = None
    wind_max_time: Optional[str] = None
    wind_gusts_max_time: Optional[str] = None
    
    # Thunderstorm data
    max_thunderstorm_probability: Optional[float] = None
    thunderstorm_threshold_pct: Optional[float] = None
    thunderstorm_threshold_time: Optional[str] = None
    thunderstorm_max_time: Optional[str] = None
    
    # Next day thunderstorm (for +1 reports)
    tomorrow_max_thunderstorm_probability: Optional[float] = None
    tomorrow_thunderstorm_threshold_time: Optional[str] = None
    tomorrow_thunderstorm_max_time: Optional[str] = None
    
    # Day after tomorrow thunderstorm (for evening reports)
    day_after_tomorrow_max_thunderstorm_probability: Optional[float] = None
    day_after_tomorrow_thunderstorm_threshold_time: Optional[str] = None
    day_after_tomorrow_thunderstorm_max_time: Optional[str] = None
    
    # Metadata
    target_date: Optional[date] = None
    time_window: Optional[str] = None
    data_source: str = "unknown"
    processed_at: Optional[datetime] = None
    
    # Additional data
    fire_risk_warning: Optional[str] = None
    raw_temperatures: List[float] = field(default_factory=list)
    raw_rain_probabilities: List[float] = field(default_factory=list)
    raw_precipitations: List[float] = field(default_factory=list)
    raw_wind_speeds: List[float] = field(default_factory=list)
    raw_wind_gusts: List[float] = field(default_factory=list)
    raw_thunderstorm_probabilities: List[float] = field(default_factory=list)


@dataclass
class StageInfo:
    """Information about a hiking stage."""
    name: str
    index: int
    coordinates: List[tuple[float, float]]
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


@dataclass
class VigilanceData:
    """Vigilance warning data."""
    level: VigilanceLevel
    phenomenon: str
    description: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    department: Optional[str] = None


@dataclass
class FireRiskData:
    """Fire risk data from massif warnings."""
    massif_id: Optional[int] = None
    level: Optional[int] = None
    description: Optional[str] = None
    region_name: Optional[str] = None
    warning_text: Optional[str] = None


@dataclass
class WeatherReport:
    """Complete weather report with all components."""
    # Report metadata
    report_type: ReportType
    stage_info: StageInfo
    timestamp: datetime
    success: bool
    weather_data: AggregatedWeatherData
    error_message: Optional[str] = None
    
    # Additional data
    vigilance_data: Optional[VigilanceData] = None
    fire_risk_data: Optional[FireRiskData] = None
    
    # Generated content
    report_text: Optional[str] = None
    email_subject: Optional[str] = None
    sms_text: Optional[str] = None
    
    # Debug information
    debug_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    # Thresholds
    rain_probability_threshold: float = 25.0
    thunderstorm_probability_threshold: float = 20.0
    rain_amount_threshold: float = 2.0
    wind_speed_threshold: float = 20.0
    wind_gust_threshold: float = 20.0
    temperature_threshold: float = 32.0
    
    # Time windows
    day_start_hour: int = 5
    day_end_hour: int = 17
    night_start_hour: int = 22
    night_end_hour: int = 5
    
    # Character limits
    max_report_length: int = 160
    
    # Report settings
    subject_base: str = "GR20 Wetter"
    include_debug: bool = False
    
    # Data sources
    primary_data_source: str = "meteofrance-api"
    fallback_data_source: str = "open-meteo"
    
    # Formatter settings
    use_compact_formatter: bool = False


def create_report_config_from_yaml(config_dict: Dict[str, Any]) -> ReportConfig:
    """
    Create a ReportConfig from a config dictionary loaded from config.yaml.
    
    Args:
        config_dict: Configuration dictionary from config.yaml
        
    Returns:
        ReportConfig with values from config.yaml
    """
    thresholds = config_dict.get('thresholds', {})
    
    return ReportConfig(
        rain_probability_threshold=thresholds.get('rain_probability', 25.0),
        thunderstorm_probability_threshold=thresholds.get('thunderstorm_probability', 20.0),
        rain_amount_threshold=thresholds.get('rain_amount', 2.0),
        wind_speed_threshold=thresholds.get('wind_speed', 20.0),
        wind_gust_threshold=thresholds.get('wind_gust_threshold', thresholds.get('wind_speed', 20.0)),
        temperature_threshold=thresholds.get('temperature', 32.0),
        max_report_length=config_dict.get('max_characters', 160),
        subject_base=config_dict.get('smtp', {}).get('subject', 'GR20 Wetter'),
        use_compact_formatter=config_dict.get('use_compact_formatter', False)
    )


def convert_dict_to_aggregated_weather_data(data: Dict[str, Any], location_name: str, latitude: float, longitude: float) -> AggregatedWeatherData:
    """
    Convert dictionary-based weather data to AggregatedWeatherData.
    
    This function provides backward compatibility with existing dictionary-based data structures.
    """
    return AggregatedWeatherData(
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        max_temperature=data.get('max_temperature'),
        min_temperature=data.get('min_temperature'),
        max_temperature_time=data.get('max_temperature_time'),
        min_temperature_time=data.get('min_temperature_time'),
        max_rain_probability=data.get('max_rain_probability'),
        max_precipitation=data.get('max_precipitation'),
        rain_threshold_pct=data.get('rain_threshold_pct'),
        rain_threshold_time=data.get('rain_threshold_time'),
        rain_max_time=data.get('rain_max_time'),
        precipitation_max_time=data.get('precipitation_max_time'),
        max_wind_speed=data.get('max_wind_speed'),
        max_wind_gusts=data.get('max_wind_gusts'),
        wind_threshold_kmh=data.get('wind_threshold_kmh'),
        wind_threshold_time=data.get('wind_threshold_time'),
        wind_max_time=data.get('wind_max_time'),
        wind_gusts_max_time=data.get('wind_gusts_max_time'),
        max_thunderstorm_probability=data.get('max_thunderstorm_probability'),
        thunderstorm_threshold_pct=data.get('thunderstorm_threshold_pct'),
        thunderstorm_threshold_time=data.get('thunderstorm_threshold_time'),
        thunderstorm_max_time=data.get('thunderstorm_max_time'),
        tomorrow_max_thunderstorm_probability=data.get('tomorrow_max_thunderstorm_probability'),
        tomorrow_thunderstorm_threshold_time=data.get('tomorrow_thunderstorm_threshold_time'),
        tomorrow_thunderstorm_max_time=data.get('tomorrow_thunderstorm_max_time'),
        day_after_tomorrow_max_thunderstorm_probability=data.get('day_after_tomorrow_max_thunderstorm_probability'),
        day_after_tomorrow_thunderstorm_threshold_time=data.get('day_after_tomorrow_thunderstorm_threshold_time'),
        day_after_tomorrow_thunderstorm_max_time=data.get('day_after_tomorrow_thunderstorm_max_time'),
        target_date=data.get('target_date'),
        time_window=data.get('time_window'),
        data_source=data.get('data_source', 'unknown'),
        processed_at=data.get('processed_at'),
        fire_risk_warning=data.get('fire_risk_warning'),
        raw_temperatures=data.get('raw_temperatures', []),
        raw_rain_probabilities=data.get('raw_rain_probabilities', []),
        raw_precipitations=data.get('raw_precipitations', []),
        raw_wind_speeds=data.get('raw_wind_speeds', []),
        raw_wind_gusts=data.get('raw_wind_gusts', []),
        raw_thunderstorm_probabilities=data.get('raw_thunderstorm_probabilities', [])
    )


def convert_aggregated_weather_data_to_dict(data: AggregatedWeatherData) -> Dict[str, Any]:
    """
    Convert AggregatedWeatherData to dictionary for backward compatibility.
    
    This function allows the new data structures to work with existing code.
    """
    return {
        'max_temperature': data.max_temperature,
        'min_temperature': data.min_temperature,
        'max_temperature_time': data.max_temperature_time,
        'min_temperature_time': data.min_temperature_time,
        'max_rain_probability': data.max_rain_probability,
        'max_precipitation': data.max_precipitation,
        'rain_threshold_pct': data.rain_threshold_pct,
        'rain_threshold_time': data.rain_threshold_time,
        'rain_max_time': data.rain_max_time,
        'precipitation_max_time': data.precipitation_max_time,
        'max_wind_speed': data.max_wind_speed,
        'max_wind_gusts': data.max_wind_gusts,
        'wind_threshold_kmh': data.wind_threshold_kmh,
        'wind_threshold_time': data.wind_threshold_time,
        'wind_max_time': data.wind_max_time,
        'wind_gusts_max_time': data.wind_gusts_max_time,
        'max_thunderstorm_probability': data.max_thunderstorm_probability,
        'thunderstorm_threshold_pct': data.thunderstorm_threshold_pct,
        'thunderstorm_threshold_time': data.thunderstorm_threshold_time,
        'thunderstorm_max_time': data.thunderstorm_max_time,
        'tomorrow_max_thunderstorm_probability': data.tomorrow_max_thunderstorm_probability,
        'tomorrow_thunderstorm_threshold_time': data.tomorrow_thunderstorm_threshold_time,
        'tomorrow_thunderstorm_max_time': data.tomorrow_thunderstorm_max_time,
        'day_after_tomorrow_max_thunderstorm_probability': data.day_after_tomorrow_max_thunderstorm_probability,
        'day_after_tomorrow_thunderstorm_threshold_time': data.day_after_tomorrow_thunderstorm_threshold_time,
        'day_after_tomorrow_thunderstorm_max_time': data.day_after_tomorrow_thunderstorm_max_time,
        'target_date': data.target_date,
        'time_window': data.time_window,
        'data_source': data.data_source,
        'processed_at': data.processed_at,
        'fire_risk_warning': data.fire_risk_warning,
        'raw_temperatures': data.raw_temperatures,
        'raw_rain_probabilities': data.raw_rain_probabilities,
        'raw_precipitations': data.raw_precipitations,
        'raw_wind_speeds': data.raw_wind_speeds,
        'raw_wind_gusts': data.raw_wind_gusts,
        'raw_thunderstorm_probabilities': data.raw_thunderstorm_probabilities,
        'location_name': data.location_name,
        'latitude': data.latitude,
        'longitude': data.longitude
    } 