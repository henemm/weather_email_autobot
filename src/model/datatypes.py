from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class CurrentPosition:
    """Current GPS position from Garmin ShareMap"""
    latitude: float
    longitude: float
    timestamp: datetime
    source_url: str


@dataclass
class WeatherAlert:
    """Météo-France Warnmeldung"""
    phenomenon: str              # z. B. "thunderstorm"
    level: str                   # "green", "yellow", "orange", "red"
    valid_from: datetime
    valid_to: datetime
    region: Optional[str] = None
    description: Optional[str] = None


@dataclass
class WeatherPoint:
    """Single weather measurement point (hourly).
    Args:
        latitude: Latitude of the point
        longitude: Longitude of the point
        elevation: Elevation in meters
        time: Timestamp of the measurement
        temperature: Air temperature in °C
        feels_like: Apparent temperature in °C
        precipitation: Precipitation in mm
        wind_speed: Wind speed in km/h
        cloud_cover: Cloud cover in %
        rain_probability: Probability of precipitation in % (NEW)
        thunderstorm_probability: Probability of thunderstorm in %
        wind_direction: Wind direction in degrees
        wind_gusts: Wind gusts in km/h
        cape: Convective Available Potential Energy
        shear: Wind shear
        alerts: List of weather alerts
    """
    latitude: float
    longitude: float
    elevation: float
    time: datetime
    temperature: float
    feels_like: float
    precipitation: float
    wind_speed: float
    cloud_cover: float
    rain_probability: Optional[float] = None  # NEW: Probability of precipitation in %
    thunderstorm_probability: Optional[float] = None
    wind_direction: float = 0.0  # Add default value
    wind_gusts: Optional[float] = None  # Wind gusts (Böen) from OpenMeteo
    cape: Optional[float] = None  # Convective Available Potential Energy
    shear: Optional[float] = None  # Wind shear
    alerts: List[WeatherAlert] = field(default_factory=list)  # NEU


@dataclass
class WeatherData:
    """Wetterdaten für mehrere Punkte einer Etappe"""
    points: List[WeatherPoint]


@dataclass
class WeatherGridData:
    """Grid-based weather data from WCS service"""
    layer: str                   # Layer name (e.g., "TEMPERATURE__GROUND_OR_WATER_SURFACE")
    unit: str                    # Unit of measurement (e.g., "°C", "mm", "%")
    times: List[datetime]        # List of timestamps
    values: List[float]          # List of values corresponding to timestamps
    lat: float                   # Latitude of the grid point
    lon: float                   # Longitude of the grid point


@dataclass
class StageWeather:
    """Wetterdaten nach Tagen gegliedert (heute, morgen, übermorgen)"""
    today: WeatherData
    tomorrow: Optional[WeatherData]
    day_after_tomorrow: Optional[WeatherData]


@dataclass
class WeatherReport:
    """Endgültiger, formatierter Bericht (Analyse + Darstellung)"""
    mode: str  # z. B. "abend", "morgen", "tag"
    stage_name: str
    date: datetime
    night_temperature: Optional[float]
    max_temperature: float
    max_feels_like: float
    max_precipitation: float
    max_thunderstorm_probability: Optional[float]
    max_wind_speed: float
    max_cloud_cover: float
    next_day_thunderstorm: Optional[float]
    text: str  # fertiger Bericht (Lang- oder Kurzform)