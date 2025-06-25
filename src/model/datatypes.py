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
    """Einzelner Wettermesspunkt (stündlich)"""
    latitude: float
    longitude: float
    elevation: float
    time: datetime
    temperature: float
    feels_like: float
    precipitation: float
    thunderstorm_probability: Optional[float]
    wind_speed: float
    wind_direction: float
    cloud_cover: float
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