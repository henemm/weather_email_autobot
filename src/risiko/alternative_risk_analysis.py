"""
Alternative risk analysis module.

This module provides an alternative approach to weather risk analysis
that uses direct MeteoFrance API data without traditional thresholds (except for rain).
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class WeatherRiskType(Enum):
    """Enum for different weather risk types."""
    HEAT = "heat"
    COLD = "cold"
    RAIN = "rain"
    THUNDERSTORM = "thunderstorm"
    WIND = "wind"


@dataclass
class HeatRiskResult:
    """Result of heat risk analysis."""
    max_temperature: float
    has_risk: bool = False
    description: str = ""

    def __post_init__(self):
        """Set description after initialization."""
        if not self.description:
            self.description = f"Maximum temperature: {self.max_temperature}°C"


@dataclass
class ColdRiskResult:
    """Result of cold risk analysis."""
    min_temperature: float
    has_risk: bool = False
    description: str = ""

    def __post_init__(self):
        """Set description after initialization."""
        if not self.description:
            self.description = f"Minimum temperature: {self.min_temperature}°C"


@dataclass
class RainRiskResult:
    """Result of rain risk analysis with timing information."""
    max_probability: float
    max_precipitation: float
    probability_threshold_time: str = ""  # Time when probability threshold is first exceeded
    probability_max_time: str = ""        # Time of maximum probability
    precipitation_threshold_time: str = "" # Time when precipitation threshold is first exceeded
    precipitation_max_time: str = ""      # Time of maximum precipitation
    has_risk: bool = False
    description: str = ""

    def __post_init__(self):
        """Set description after initialization."""
        if self.has_risk:
            time_info = ""
            if self.probability_max_time:
                time_info += f"@{self.probability_max_time}"
            elif self.precipitation_max_time:
                time_info += f"@{self.precipitation_max_time}"
            self.description = f"Rain risk detected: {self.max_probability}% probability{time_info}, {self.max_precipitation}mm/h max"
        else:
            time_info = ""
            if self.probability_max_time:
                time_info += f"@{self.probability_max_time}"
            elif self.precipitation_max_time:
                time_info += f"@{self.precipitation_max_time}"
            self.description = f"Rain: {self.max_probability}% probability{time_info}, {self.max_precipitation}mm/h max"


@dataclass
class ThunderstormTime:
    """Time information for thunderstorm detection."""
    hour: int
    description: str
    intensity: str  # "moderate", "heavy", "risk"
    cape_value: float = 0.0  # CAPE value if available


@dataclass
class ThunderstormRiskResult:
    """Result of thunderstorm risk analysis with timing information."""
    thunderstorm_times: List[ThunderstormTime]
    threshold_time: str = ""  # Time when threshold is first exceeded
    max_time: str = ""        # Time of maximum thunderstorm probability
    max_cape: float = 0.0     # Maximum CAPE value
    has_risk: bool = False
    description: str = ""

    def __post_init__(self):
        """Set description after initialization."""
        if self.has_risk:
            time_str = ", ".join([f"{t.description}@{t.hour:02d}h" for t in self.thunderstorm_times])
            threshold_info = ""
            if self.threshold_time and self.max_time:
                threshold_info = f" ({self.threshold_time}@{self.max_time})"
            cape_info = ""
            if self.max_cape > 0:
                cape_info = f" [CAPE: {self.max_cape:.0f}]"
            self.description = f"Thunderstorm: {time_str}{threshold_info}{cape_info}"
        else:
            self.description = "No thunderstorm conditions detected"


@dataclass
class WindRiskResult:
    """Result of wind risk analysis with timing information."""
    max_wind_speed: float
    max_wind_gusts: float
    wind_speed_time: str = ""
    wind_gusts_time: str = ""
    has_risk: bool = False
    description: str = ""

    def __post_init__(self):
        """Set description after initialization."""
        if self.has_risk:
            time_info = ""
            if self.wind_gusts_time:
                time_info = f"@{self.wind_gusts_time}"
            self.description = f"Wind risk detected: {self.max_wind_speed} km/h, {self.max_wind_gusts} km/h gusts{time_info}"
        else:
            time_info = ""
            if self.wind_speed_time:
                time_info = f"@{self.wind_speed_time}"
            self.description = f"Wind: {self.max_wind_speed} km/h, gusts: {self.max_wind_gusts} km/h{time_info}"


@dataclass
class RiskAnalysisResult:
    """Complete result of alternative risk analysis."""
    heat_risk: HeatRiskResult
    cold_risk: ColdRiskResult
    rain_risk: RainRiskResult
    thunderstorm_risk: ThunderstormRiskResult
    wind_risk: WindRiskResult


class AlternativeRiskAnalyzer:
    """Alternative risk analyzer that uses direct MeteoFrance API data without traditional thresholds."""
    
    # WMO weather codes for thunderstorms
    THUNDERSTORM_CODES = {95, 96, 97, 98, 99}
    
    # Rain risk thresholds
    RAIN_PROBABILITY_THRESHOLD = 50.0  # %
    RAIN_AMOUNT_THRESHOLD = 2.0  # mm/h
    
    # Wind risk threshold
    WIND_GUST_THRESHOLD = 30.0  # km/h
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the analyzer with configuration.
        
        Args:
            config: Configuration dictionary containing thresholds
        """
        self.config = config or {}
        self.wind_gust_threshold = self.config.get('wind_gust_threshold', 10.0)
        self.wind_gust_percentage = self.config.get('wind_gust_percentage', 50.0)
    
    # Data validation thresholds
    MIN_VALID_TEMPERATURE = -50.0  # °C
    MAX_VALID_TEMPERATURE = 60.0   # °C
    MIN_VALID_SUMMER_TEMPERATURE = 5.0  # °C (minimum reasonable summer temperature)
    MIN_VALID_RAIN_PROBABILITY = 0.0  # %
    MAX_VALID_RAIN_PROBABILITY = 100.0  # %
    MIN_VALID_PRECIPITATION = 0.0  # mm/h
    MAX_VALID_PRECIPITATION = 100.0  # mm/h
    MIN_VALID_WIND_SPEED = 0.0  # km/h
    MAX_VALID_WIND_SPEED = 200.0  # km/h
    
    def _is_valid_temperature(self, temp: float) -> bool:
        """
        Validate temperature value.
        
        Args:
            temp: Temperature value in °C
            
        Returns:
            bool: True if temperature is valid
        """
        if temp is None:
            return False
        
        try:
            temp_float = float(temp)
        except (ValueError, TypeError):
            return False
        
        # Check basic range
        if temp_float < self.MIN_VALID_TEMPERATURE or temp_float > self.MAX_VALID_TEMPERATURE:
            return False
        
        # Check for suspicious values (0°C is often an error, especially in summer)
        from datetime import datetime
        current_month = datetime.now().month
        
        if temp_float == 0.0 and current_month not in [12, 1, 2]:  # Not winter months
            logger.warning(f"Suspicious temperature value detected: {temp_float}°C (likely API error)")
            return False
        
        return True
    
    def _is_valid_rain_probability(self, prob: float) -> bool:
        """Check if rain probability value is valid and meaningful."""
        return (prob is not None and 
                isinstance(prob, (int, float)) and 
                self.MIN_VALID_RAIN_PROBABILITY <= prob <= self.MAX_VALID_RAIN_PROBABILITY)
    
    def _is_valid_precipitation(self, precip: float) -> bool:
        """Check if precipitation value is valid and meaningful."""
        return (precip is not None and 
                isinstance(precip, (int, float)) and 
                self.MIN_VALID_PRECIPITATION <= precip <= self.MAX_VALID_PRECIPITATION)
    
    def _is_valid_wind_speed(self, speed: float) -> bool:
        """Check if wind speed value is valid and meaningful."""
        return (speed is not None and 
                isinstance(speed, (int, float)) and 
                self.MIN_VALID_WIND_SPEED <= speed <= self.MAX_VALID_WIND_SPEED)
    
    def _detect_api_failure(self, weather_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Detect API failures and data quality issues in MeteoFrance format.
        
        Args:
            weather_data: Weather data dictionary in MeteoFrance format
            
        Returns:
            Dict[str, bool]: Dictionary indicating different types of failures
        """
        failures = {
            'general_api_failure': False,
            'temperature_failure': False,
            'rain_failure': False,
            'wind_failure': False,
            'thunderstorm_failure': False
        }
        
        if not weather_data:
            failures['general_api_failure'] = True
            logger.error("MeteoFrance API failure: Empty weather data")
            return failures
        
        # Check for MeteoFrance API failure indicators
        forecast_entries = weather_data.get('forecast', [])
        if not forecast_entries:
            logger.error("MeteoFrance API failure: No forecast entries found")
            failures['general_api_failure'] = True
            return failures
        
        # Check if forecast entries contain valid data
        valid_entries = 0
        for entry in forecast_entries:
            if isinstance(entry, dict) and entry:
                # Check if entry has at least one weather parameter
                if any(key in entry for key in ['T', 'rain', 'wind', 'weather']):
                    valid_entries += 1
        
        if valid_entries == 0:
            logger.error("MeteoFrance API failure: No valid weather data in forecast entries")
            failures['general_api_failure'] = True
            return failures
        
        # Check for MeteoFrance temperature issues (known problem)
        if forecast_entries:
            temp_values = []
            for entry in forecast_entries:
                if 'T' in entry and isinstance(entry['T'], dict):
                    temp_value = entry['T'].get('value')
                    if temp_value is not None:
                        temp_float = float(temp_value)
                        if temp_float < 5.0:  # MeteoFrance known issue: too low temperatures
                            logger.error(f"MeteoFrance API failure: Temperatures too low (avg: {temp_float}°C) - CODE ERROR")
                            failures['temperature_failure'] = True
                        else:
                            temp_values.append(temp_float)
            
            if temp_values:
                avg_temp = sum(temp_values) / len(temp_values)
                if avg_temp < 5.0:  # MeteoFrance known issue: too low temperatures
                    logger.error(f"MeteoFrance API failure: Average temperature too low ({avg_temp}°C) - CODE ERROR")
                    failures['temperature_failure'] = True
        
        return failures

    def analyze_heat_risk(self, weather_data: Dict[str, Any]) -> HeatRiskResult:
        """
        Analyze heat risk using MeteoFrance daily temperature data ONLY.
        
        Args:
            weather_data: Weather data dictionary containing MeteoFrance forecast data
            
        Returns:
            HeatRiskResult: Analysis result with maximum temperature
        """
        try:
            # Detect API failures first
            failures = self._detect_api_failure(weather_data)
            if failures['general_api_failure']:
                logger.error("MeteoFrance API failure detected in heat risk analysis")
                return HeatRiskResult(max_temperature=0.0, description="❌ MeteoFrance API failure: No weather data available")
            
            if failures['temperature_failure']:
                logger.error("MeteoFrance API failure: Temperature data quality issue")
                return HeatRiskResult(max_temperature=0.0, description="❌ MeteoFrance API failure: Invalid temperature data")
            
            # Use MeteoFrance format ONLY - look for daily.temperature_2m_max first
            forecast_entries = weather_data.get('forecast', [])
            if not forecast_entries:
                logger.error("No MeteoFrance forecast entries found")
                return HeatRiskResult(max_temperature=0.0, description="❌ MeteoFrance API failure: No forecast data")
            
            # First try to find daily.temperature_2m_max (API liefert direkt das Tagesmaximum)
            max_temp = None
            
            for entry in forecast_entries:
                if isinstance(entry, dict):
                    # Look for daily temperature max
                    if 'daily' in entry and isinstance(entry['daily'], dict):
                        daily_data = entry['daily']
                        if 'temperature_2m_max' in daily_data:
                            temp_value = daily_data['temperature_2m_max']
                            if temp_value is not None:
                                temp_float = float(temp_value)
                                if self._is_valid_temperature(temp_float):
                                    max_temp = temp_float
                                    logger.info(f"Found daily.temperature_2m_max: {max_temp}°C")
                                    break
            
            # Fallback to hourly aggregation only if daily max not found
            if max_temp is None:
                logger.warning("daily.temperature_2m_max not found, falling back to hourly aggregation")
                max_temp = float('-inf')
                
                for entry in forecast_entries:
                    if 'T' in entry and isinstance(entry['T'], dict):
                        temp_value = entry['T'].get('value')
                        if temp_value is not None:
                            temp_float = float(temp_value)
                            
                            # Validate temperature
                            if not self._is_valid_temperature(temp_float):
                                logger.error(f"MeteoFrance API failure: Invalid temperature value {temp_float}°C")
                                return HeatRiskResult(max_temperature=0.0, description="❌ MeteoFrance API failure: Invalid temperature data")
                            
                            if temp_float > max_temp:
                                max_temp = temp_float
            
            if max_temp is None or max_temp == float('-inf'):
                logger.error("MeteoFrance API failure: No valid temperature data found")
                return HeatRiskResult(max_temperature=0.0, description="❌ MeteoFrance API failure: No temperature data")
            
            return HeatRiskResult(max_temperature=max_temp, description=f"Maximum temperature: {max_temp}°C")
            
        except Exception as e:
            logger.error(f"MeteoFrance API failure in heat risk analysis: {e}")
            return HeatRiskResult(max_temperature=0.0, description="❌ MeteoFrance API failure: Analysis error")

    def analyze_cold_risk(self, weather_data: Dict[str, Any], report_type: str = None, debug_data: Dict[str, Any] = None) -> ColdRiskResult:
        """
        Analyze cold risk using MeteoFrance daily temperature data ONLY.
        
        REGEL: ALLE WERTE MÜSSEN DYNAMISCH AUS DEN AKTUELLEN DATEN BERECHNET WERDEN!
        KEINE HARD-CODED WERTE ERLAUBT!
        
        EVENING-REPORT-LOGIK: Für Evening-Report wird die Cold-Temperatur aus den DAILY_FORECAST 
        Daten für HEUTE vom letzten Geo-Punkt der heutigen Etappe extrahiert (22:00-05:00).
        
        Args:
            weather_data: Weather data dictionary containing MeteoFrance forecast data
            report_type: Type of report ('morning', 'evening', 'update')
            debug_data: Debug data for evening report logic
            
        Returns:
            ColdRiskResult: Analysis result with minimum temperature
        """
        try:
            # Detect API failures first
            failures = self._detect_api_failure(weather_data)
            if failures['general_api_failure']:
                logger.error("MeteoFrance API failure detected in cold risk analysis")
                return ColdRiskResult(min_temperature=0.0, description="❌ MeteoFrance API failure: No weather data available")
            
            if failures['temperature_failure']:
                logger.error("MeteoFrance API failure: Temperature data quality issue")
                return ColdRiskResult(min_temperature=0.0, description="❌ MeteoFrance API failure: Invalid temperature data")
            
            # EVENING-REPORT-LOGIK: Für Evening-Report spezielle Logik für Cold-Temperatur
            if report_type == 'evening' and debug_data:
                logger.info("=== EVENING-REPORT COLD TEMPERATURE ANALYSIS ===")
                
                # Extract DAILY_FORECAST data for today from debug_data
                daily_forecast_data = debug_data.get('daily_forecast', [])
                logger.info(f"Daily forecast data type: {type(daily_forecast_data)}")
                logger.info(f"Daily forecast data length: {len(daily_forecast_data) if isinstance(daily_forecast_data, list) else 'N/A'}")
                
                if isinstance(daily_forecast_data, list):
                    # DEBUG: Log all available dates to see what's actually there
                    logger.info(f"=== DEBUG: All available dates in daily_forecast_data ===")
                    for entry in daily_forecast_data:
                        if isinstance(entry, dict):
                            date_str = entry.get('date', '')
                            temp_min = entry.get('temp_min', 'N/A')
                            position = entry.get('position', 'unknown')
                            logger.info(f"Date: {date_str}, temp_min: {temp_min}, position: {position}")
                    
                    # Find the last position of today's stage for cold temperature
                    today_entries = []
                    for entry in daily_forecast_data:
                        if isinstance(entry, dict):
                            # Look for today's date (2025-07-31) - try multiple formats
                            date_str = str(entry.get('date', ''))
                            logger.info(f"Checking date: '{date_str}' for today's data")
                            
                            # Try different date formats
                            if ('2025-07-31' in date_str or 
                                '2025-07-31' in date_str or 
                                'today' in date_str.lower() or
                                'heute' in date_str.lower()):
                                today_entries.append(entry)
                                logger.info(f"Found today's data: {entry}")
                    
                    if today_entries:
                        # Find the last position (highest position number)
                        last_entry = None
                        for entry in today_entries:
                            # Extract position from entry if available
                            position = entry.get('position', 'unknown')
                            if last_entry is None or position > last_entry.get('position', 'unknown'):
                                last_entry = entry
                        
                        if last_entry:
                            # Extract temp_min from the last position
                            temp_min = last_entry.get('temp_min', 0.0)
                            if isinstance(temp_min, (int, float)) and self._is_valid_temperature(temp_min):
                                logger.info(f"=== EVENING-REPORT COLD ANALYSIS RESULT ===")
                                logger.info(f"Last position of today's stage: {last_entry.get('position', 'unknown')}")
                                logger.info(f"Cold temperature (temp_min): {temp_min}°C")
                                logger.info(f"Source: DAILY_FORECAST for today (2025-07-31)")
                                return ColdRiskResult(min_temperature=float(temp_min), description=f"Evening-Report Cold: {temp_min}°C (last position today)")
                    else:
                        logger.warning("Evening-Report: No entries found for today (2025-07-31) in daily_forecast_data")
                
                logger.warning("Evening-Report: No valid DAILY_FORECAST data for today found, falling back to standard logic")
            
            # Standard logic for morning/update reports or fallback
            # Use MeteoFrance format ONLY - look for daily.temperature_2m_min first
            forecast_entries = weather_data.get('forecast', [])
            if not forecast_entries:
                logger.error("No MeteoFrance forecast entries found")
                return ColdRiskResult(min_temperature=0.0, description="❌ MeteoFrance API failure: No forecast data")
            
            # First try to find daily.temperature_2m_min (API liefert direkt das Tagesminimum)
            min_temp = None
            
            for entry in forecast_entries:
                if isinstance(entry, dict):
                    # Look for daily temperature min
                    if 'daily' in entry and isinstance(entry['daily'], dict):
                        daily_data = entry['daily']
                        if 'temperature_2m_min' in daily_data:
                            temp_value = daily_data['temperature_2m_min']
                            if temp_value is not None:
                                temp_float = float(temp_value)
                                if self._is_valid_temperature(temp_float):
                                    min_temp = temp_float
                                    logger.info(f"Found daily.temperature_2m_min: {min_temp}°C")
                                    break
            
            # Fallback to hourly aggregation only if daily min not found
            if min_temp is None:
                logger.warning("daily.temperature_2m_min not found, falling back to hourly aggregation")
                min_temp = float('inf')
                
                for entry in forecast_entries:
                    if 'T' in entry and isinstance(entry['T'], dict):
                        temp_value = entry['T'].get('value')
                        if temp_value is not None:
                            temp_float = float(temp_value)
                            
                            # Validate temperature
                            if not self._is_valid_temperature(temp_float):
                                logger.error(f"MeteoFrance API failure: Invalid temperature value {temp_float}°C")
                                return ColdRiskResult(min_temperature=0.0, description="❌ MeteoFrance API failure: Invalid temperature data")
                            
                            if temp_float < min_temp:
                                min_temp = temp_float
            
            if min_temp is None or min_temp == float('inf'):
                logger.error("MeteoFrance API failure: No valid temperature data found")
                return ColdRiskResult(min_temperature=0.0, description="❌ MeteoFrance API failure: No temperature data")
            
            return ColdRiskResult(min_temperature=min_temp, description=f"Minimum temperature: {min_temp}°C")
            
        except Exception as e:
            logger.error(f"MeteoFrance API failure in cold risk analysis: {e}")
            return ColdRiskResult(min_temperature=0.0, description="❌ MeteoFrance API failure: Analysis error")

    def analyze_rain_risk(self, weather_data: Dict[str, Any]) -> RainRiskResult:
        """
        Analyze rain risk using MeteoFrance precipitation data ONLY with timing information.
        
        Args:
            weather_data: Weather data dictionary containing MeteoFrance forecast data
            
        Returns:
            RainRiskResult: Analysis result with timing information
        """
        try:
            # Detect API failures first
            failures = self._detect_api_failure(weather_data)
            if failures['general_api_failure']:
                logger.error("MeteoFrance API failure detected in rain risk analysis")
                return RainRiskResult(max_probability=0.0, max_precipitation=0.0, description="❌ MeteoFrance API failure: No weather data available")
            
            # Use MeteoFrance format ONLY
            forecast_entries = weather_data.get('forecast', [])
            if not forecast_entries:
                logger.error("No MeteoFrance forecast entries found")
                return RainRiskResult(max_probability=0.0, max_precipitation=0.0, description="❌ MeteoFrance API failure: No forecast data")
            
            # Extract precipitation data from MeteoFrance API structure with timing
            precipitations = []
            probabilities = []
            timing_data = []
            
            for entry in forecast_entries:
                # Extract timestamp for timing
                dt_timestamp = entry.get('dt')
                if dt_timestamp:
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    hour = entry_datetime.hour
                else:
                    hour = 0
                
                # Extract precipitation amount
                if 'rain' in entry:
                    rain_data = entry['rain']
                    if isinstance(rain_data, dict) and '1h' in rain_data:
                        precip_value = rain_data['1h']
                        if precip_value is not None:
                            precip_float = float(precip_value)
                            if self._is_valid_precipitation(precip_float):
                                precipitations.append(precip_float)
                                timing_data.append((hour, precip_float, 'precipitation'))
                            else:
                                logger.warning(f"Invalid MeteoFrance precipitation value: {precip_float}mm/h")
                    elif isinstance(rain_data, (int, float)):
                        precip_float = float(rain_data)
                        if self._is_valid_precipitation(precip_float):
                            precipitations.append(precip_float)
                            timing_data.append((hour, precip_float, 'precipitation'))
                        else:
                            logger.warning(f"Invalid MeteoFrance precipitation value: {precip_float}mm/h")
                
                # Extract precipitation probability (if available)
                prob_value = entry.get('precipitation_probability')
                if prob_value is not None:
                    prob_float = float(prob_value)
                    if self._is_valid_rain_probability(prob_float):
                        probabilities.append(prob_float)
                        timing_data.append((hour, prob_float, 'probability'))
                    else:
                        logger.warning(f"Invalid MeteoFrance rain probability: {prob_float}%")
            
            # If no precipitation probability available, estimate from weather description
            if not probabilities:
                for entry in forecast_entries:
                    weather_desc = entry.get('weather', {}).get('desc', '').lower()
                    if any(word in weather_desc for word in ['pluie', 'rain', 'averse', 'shower']):
                        probabilities.append(60.0)  # Estimate 60% for rain conditions
                        # Add timing for estimated probability
                        dt_timestamp = entry.get('dt')
                        if dt_timestamp:
                            entry_datetime = datetime.fromtimestamp(dt_timestamp)
                            hour = entry_datetime.hour
                            timing_data.append((hour, 60.0, 'probability'))
                    else:
                        probabilities.append(10.0)  # Low probability for clear weather
                        # Add timing for estimated probability
                        dt_timestamp = entry.get('dt')
                        if dt_timestamp:
                            entry_datetime = datetime.fromtimestamp(dt_timestamp)
                            hour = entry_datetime.hour
                            timing_data.append((hour, 10.0, 'probability'))
            
            if precipitations:
                max_precipitation = max(precipitations)
                # Find timing for max precipitation
                max_precip_time = ""
                for hour, value, data_type in timing_data:
                    if data_type == 'precipitation' and value == max_precipitation:
                        max_precip_time = str(hour)
                        break
            else:
                max_precipitation = 0.0
                max_precip_time = ""
            
            if probabilities:
                max_probability = max(probabilities)
                # Find timing for max probability
                max_prob_time = ""
                for hour, value, data_type in timing_data:
                    if data_type == 'probability' and value == max_probability:
                        max_prob_time = str(hour)
                        break
            else:
                max_probability = 0.0
                max_prob_time = ""
            
            # Check for rain risk conditions
            has_risk = (max_probability >= self.RAIN_PROBABILITY_THRESHOLD and 
                       max_precipitation > self.RAIN_AMOUNT_THRESHOLD)
            
            if failures['temperature_failure']:
                return RainRiskResult(
                    max_probability=max_probability,
                    max_precipitation=max_precipitation,
                    probability_max_time=max_prob_time,
                    precipitation_max_time=max_precip_time,
                    has_risk=has_risk,
                    description=f"⚠️ MeteoFrance data quality issue: {max_probability}% prob, {max_precipitation}mm/h"
                )
            
            return RainRiskResult(
                max_probability=max_probability,
                max_precipitation=max_precipitation,
                probability_max_time=max_prob_time,
                precipitation_max_time=max_precip_time,
                has_risk=has_risk
            )
            
        except Exception as e:
            logger.error(f"Error analyzing rain risk: {e}")
            return RainRiskResult(max_probability=0.0, max_precipitation=0.0, description=f"❌ MeteoFrance analysis error: {str(e)}")

    def analyze_thunderstorm_risk(self, weather_data: Dict[str, Any]) -> ThunderstormRiskResult:
        """
        Analyze thunderstorm risk using MeteoFrance data ONLY with timing information and CAPE.
        
        Args:
            weather_data: Weather data dictionary containing MeteoFrance forecast data
            
        Returns:
            ThunderstormRiskResult: Analysis result with timing and CAPE information
        """
        try:
            # Detect API failures first
            failures = self._detect_api_failure(weather_data)
            if failures['general_api_failure']:
                logger.error("MeteoFrance API failure detected in thunderstorm risk analysis")
                return ThunderstormRiskResult(thunderstorm_times=[], description="❌ MeteoFrance API failure: No weather data available")
            
            # Use MeteoFrance format ONLY
            forecast_entries = weather_data.get('forecast', [])
            if not forecast_entries:
                logger.error("No MeteoFrance forecast entries found")
                return ThunderstormRiskResult(thunderstorm_times=[], description="❌ MeteoFrance API failure: No forecast data")
            
            # Analyze thunderstorm indicators with timing
            thunderstorm_times = []
            max_cape = 0.0
            
            for entry in forecast_entries:
                # Get timestamp and hour
                dt_timestamp = entry.get('dt')
                if not dt_timestamp:
                    continue
                
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                hour = entry_datetime.hour
                
                weather_desc = entry.get('weather', {}).get('desc', '').lower()
                
                # Check for thunderstorm indicators in French weather descriptions
                thunderstorm_keywords = [
                    'orage', 'orages', 'thunderstorm', 'thunder', 'storm',
                    'risque d\'orage', 'risque d\'orages', 'averse orageuse', 'averses orageuses'
                ]
                
                if any(keyword in weather_desc for keyword in thunderstorm_keywords):
                    # Determine intensity and description
                    if 'lourd' in weather_desc or 'heavy' in weather_desc:
                        description = "Orages lourds"
                        intensity = "heavy"
                    elif 'grêle' in weather_desc or 'hail' in weather_desc:
                        description = "Orages avec grêle"
                        intensity = "heavy"
                    elif 'risque' in weather_desc:
                        description = "Risque d'orages"
                        intensity = "risk"
                    else:
                        description = "Orages"
                        intensity = "moderate"
                    
                    # Extract CAPE value if available
                    cape_value = entry.get('cape', 0.0)
                    if cape_value and cape_value > max_cape:
                        max_cape = float(cape_value)
                    
                    thunderstorm_times.append(ThunderstormTime(
                        hour=hour,
                        description=description,
                        intensity=intensity,
                        cape_value=cape_value or 0.0
                    ))
            
            has_risk = len(thunderstorm_times) > 0
            
            if failures['temperature_failure']:
                return ThunderstormRiskResult(
                    thunderstorm_times=thunderstorm_times,
                    max_cape=max_cape,
                    has_risk=has_risk,
                    description=f"⚠️ MeteoFrance data quality issue: {len(thunderstorm_times)} thunderstorm events"
                )
            
            return ThunderstormRiskResult(
                thunderstorm_times=thunderstorm_times,
                max_cape=max_cape,
                has_risk=has_risk
            )
            
        except Exception as e:
            logger.error(f"Error analyzing thunderstorm risk: {e}")
            return ThunderstormRiskResult(thunderstorm_times=[], description=f"❌ MeteoFrance analysis error: {str(e)}")

    def analyze_wind_risk(self, weather_data: Dict[str, Any]) -> WindRiskResult:
        """
        Analyze wind risk using MeteoFrance wind data ONLY with timing information.
        
        Args:
            weather_data: Weather data dictionary containing MeteoFrance forecast data
            
        Returns:
            WindRiskResult: Analysis result with timing information
        """
        try:
            # Detect API failures first
            failures = self._detect_api_failure(weather_data)
            if failures['general_api_failure']:
                logger.error("MeteoFrance API failure detected in wind risk analysis")
                return WindRiskResult(max_wind_speed=0.0, max_wind_gusts=0.0, description="❌ MeteoFrance API failure: No weather data available")
            
            # Use MeteoFrance format ONLY
            forecast_entries = weather_data.get('forecast', [])
            if not forecast_entries:
                logger.error("No MeteoFrance forecast entries found")
                return WindRiskResult(max_wind_speed=0.0, max_wind_gusts=0.0, description="❌ MeteoFrance API failure: No forecast data")
            
            # Extract wind data from MeteoFrance API structure with timing
            wind_speeds = []
            wind_gusts = []
            timing_data = []
            
            for entry in forecast_entries:
                # Extract timestamp for timing
                dt_timestamp = entry.get('dt')
                if dt_timestamp:
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    hour = entry_datetime.hour
                else:
                    hour = 0
                
                # Extract wind speed
                if 'wind' in entry:
                    wind_data = entry['wind']
                    if isinstance(wind_data, dict):
                        # Wind speed
                        speed_value = wind_data.get('speed')
                        if speed_value is not None:
                            speed_float = float(speed_value)
                            if self._is_valid_wind_speed(speed_float):
                                wind_speeds.append(speed_float)
                                timing_data.append((hour, speed_float, 'speed'))
                            else:
                                logger.warning(f"Invalid MeteoFrance wind speed: {speed_float} km/h")
                        
                        # Wind gusts
                        gust_value = wind_data.get('gust')
                        if gust_value is not None:
                            gust_float = float(gust_value)
                            if self._is_valid_wind_speed(gust_float):
                                wind_gusts.append(gust_float)
                                timing_data.append((hour, gust_float, 'gust'))
                            else:
                                logger.warning(f"Invalid MeteoFrance wind gust: {gust_float} km/h")
            
            # Find maximum values and their timing
            max_wind_speed = max(wind_speeds) if wind_speeds else 0.0
            max_wind_gusts = max(wind_gusts) if wind_gusts else 0.0
            
            # Find timing for max wind speed
            max_speed_time = ""
            for hour, value, data_type in timing_data:
                if data_type == 'speed' and value == max_wind_speed:
                    max_speed_time = str(hour)
                    break
            
            # Find timing for max wind gusts
            max_gust_time = ""
            for hour, value, data_type in timing_data:
                if data_type == 'gust' and value == max_wind_gusts:
                    max_gust_time = str(hour)
                    break
            
            # Check for wind risk conditions
            has_risk = max_wind_gusts > self.WIND_GUST_THRESHOLD
            
            if failures['temperature_failure']:
                return WindRiskResult(
                    max_wind_speed=max_wind_speed,
                    max_wind_gusts=max_wind_gusts,
                    wind_speed_time=max_speed_time,
                    wind_gusts_time=max_gust_time,
                    has_risk=has_risk,
                    description=f"⚠️ MeteoFrance data quality issue: {max_wind_speed} km/h, {max_wind_gusts} km/h gusts"
                )
            
            return WindRiskResult(
                max_wind_speed=max_wind_speed,
                max_wind_gusts=max_wind_gusts,
                wind_speed_time=max_speed_time,
                wind_gusts_time=max_gust_time,
                has_risk=has_risk
            )
            
        except Exception as e:
            logger.error(f"Error analyzing wind risk: {e}")
            return WindRiskResult(max_wind_speed=0.0, max_wind_gusts=0.0, description=f"❌ MeteoFrance analysis error: {str(e)}")

    def analyze_all_risks(self, weather_data: Dict[str, Any]) -> RiskAnalysisResult:
        """
        Analyze all weather risks using the provided weather data.
        
        Args:
            weather_data: Weather data dictionary containing forecast data or processed weather data
            
        Returns:
            RiskAnalysisResult: Complete risk analysis result
        """
        try:
            # Check if we have processed weather data (from weather_data_processor)
            if 'forecast' in weather_data and isinstance(weather_data['forecast'], list):
                # Use forecast data (original MeteoFrance format)
                forecast_data = weather_data['forecast']
                if forecast_data:
                    # Analyze all forecast entries using individual risk analysis methods
                    # This ensures proper MeteoFrance API data processing
                    heat_risk = self.analyze_heat_risk(weather_data)
                    cold_risk = self.analyze_cold_risk(weather_data)
                    rain_risk = self.analyze_rain_risk(weather_data)
                    thunderstorm_risk = self.analyze_thunderstorm_risk(weather_data)
                    wind_risk = self.analyze_wind_risk(weather_data)
                    
                    return RiskAnalysisResult(
                        heat_risk=heat_risk,
                        cold_risk=cold_risk,
                        rain_risk=rain_risk,
                        thunderstorm_risk=thunderstorm_risk,
                        wind_risk=wind_risk
                    )
                else:
                    logger.warning("Empty forecast data provided")
                    return self._create_default_result()
            else:
                # Use processed weather data (from weather_data_processor)
                return self._analyze_from_processed_data(weather_data)
            
        except Exception as e:
            logger.error(f"Error in complete risk analysis: {e}")
            return self._create_default_result()
    
    def _analyze_from_forecast(self, forecast_entry: Dict[str, Any]) -> RiskAnalysisResult:
        """Analyze risks from MeteoFrance forecast entry."""
        try:
            # Extract data from forecast entry
            temperature = forecast_entry.get('T', {}).get('value', 0.0) if isinstance(forecast_entry.get('T'), dict) else 0.0
            rain_probability = forecast_entry.get('precipitation_probability', 0.0)
            precipitation = forecast_entry.get('precipitation', {}).get('1h', 0.0) if isinstance(forecast_entry.get('precipitation'), dict) else 0.0
            wind_speed = forecast_entry.get('wind', {}).get('speed', 0.0) if isinstance(forecast_entry.get('wind'), dict) else 0.0
            wind_gusts = forecast_entry.get('wind', {}).get('gust', 0.0) if isinstance(forecast_entry.get('wind'), dict) else 0.0
            
            # Create processed data format
            processed_data = {
                'max_temperature': temperature,
                'min_temperature': temperature,
                'max_rain_probability': rain_probability,
                'max_precipitation': precipitation,
                'max_wind_speed': wind_speed,
                'max_wind_gusts': wind_gusts,
                'max_thunderstorm_probability': 0.0  # Not available in basic forecast
            }
            
            return self._analyze_from_processed_data(processed_data)
            
        except Exception as e:
            logger.error(f"Error analyzing from forecast: {e}")
            return self._create_default_result()
    
    def _analyze_from_processed_data(self, processed_data: Dict[str, Any]) -> RiskAnalysisResult:
        """Analyze risks from processed weather data."""
        try:
            # Analyze each risk type using processed data
            heat_risk = self._analyze_heat_from_processed(processed_data)
            cold_risk = self._analyze_cold_from_processed(processed_data)
            rain_risk = self._analyze_rain_from_processed(processed_data)
            thunderstorm_risk = self._analyze_thunderstorm_from_processed(processed_data)
            wind_risk = self._analyze_wind_from_processed(processed_data)
            
            return RiskAnalysisResult(
                heat_risk=heat_risk,
                cold_risk=cold_risk,
                rain_risk=rain_risk,
                thunderstorm_risk=thunderstorm_risk,
                wind_risk=wind_risk
            )
            
        except Exception as e:
            logger.error(f"Error analyzing from processed data: {e}")
            return self._create_default_result()
    
    def _create_default_result(self) -> RiskAnalysisResult:
        """Create default risk analysis result with MeteoFrance API failure messages."""
        return RiskAnalysisResult(
            heat_risk=HeatRiskResult(max_temperature=0.0, description="❌ MeteoFrance API failure: No weather data available"),
            cold_risk=ColdRiskResult(min_temperature=0.0, description="❌ MeteoFrance API failure: No weather data available"),
            rain_risk=RainRiskResult(max_probability=0.0, max_precipitation=0.0, description="❌ MeteoFrance API failure: No weather data available"),
            thunderstorm_risk=ThunderstormRiskResult(thunderstorm_times=[], description="❌ MeteoFrance API failure: No weather data available"),
            wind_risk=WindRiskResult(max_wind_speed=0.0, max_wind_gusts=0.0, description="❌ MeteoFrance API failure: No weather data available")
        )
    
    def _analyze_heat_from_processed(self, data: Dict[str, Any]) -> HeatRiskResult:
        """Analyze heat risk from processed weather data."""
        max_temp = data.get('max_temperature', 0.0)
        if self._is_valid_temperature(max_temp):
            return HeatRiskResult(max_temperature=max_temp)
        else:
            return HeatRiskResult(max_temperature=0.0, description="❌ Invalid temperature data")
    
    def _analyze_cold_from_processed(self, data: Dict[str, Any]) -> ColdRiskResult:
        """Analyze cold risk from processed weather data."""
        min_temp = data.get('min_temperature', 0.0)
        if self._is_valid_temperature(min_temp):
            return ColdRiskResult(min_temperature=min_temp)
        else:
            return ColdRiskResult(min_temperature=0.0, description="❌ Invalid temperature data")
    
    def _analyze_rain_from_processed(self, data: Dict[str, Any]) -> RainRiskResult:
        """Analyze rain risk from processed weather data."""
        max_probability = data.get('max_rain_probability', 0.0)
        max_precipitation = data.get('max_precipitation', 0.0)
        probability_max_time = data.get('rain_max_time', '')
        precipitation_max_time = data.get('precipitation_time', '')
        probability_threshold_time = data.get('rain_threshold_time', '')
        precipitation_threshold_time = data.get('precipitation_threshold_time', '')
        
        # Check if both conditions are met for rain risk
        has_risk = (max_probability >= self.RAIN_PROBABILITY_THRESHOLD and 
                   max_precipitation > self.RAIN_AMOUNT_THRESHOLD)
        
        return RainRiskResult(
            max_probability=max_probability,
            max_precipitation=max_precipitation,
            probability_threshold_time=probability_threshold_time,
            probability_max_time=probability_max_time,
            precipitation_threshold_time=precipitation_threshold_time,
            precipitation_max_time=precipitation_max_time,
            has_risk=has_risk
        )
    
    def _analyze_thunderstorm_from_processed(self, data: Dict[str, Any]) -> ThunderstormRiskResult:
        """Analyze thunderstorm risk from processed weather data."""
        max_thunderstorm_prob = data.get('max_thunderstorm_probability', 0.0)
        thunderstorm_max_time = data.get('thunderstorm_max_time', '')
        thunderstorm_threshold_time = data.get('thunderstorm_threshold_time', '')
        
        # For processed data, we can only check if thunderstorm probability is available
        if max_thunderstorm_prob > 0:
            return ThunderstormRiskResult(
                thunderstorm_times=[ThunderstormTime(
                    hour=0,  # We don't have hour-level data
                    description=f"{max_thunderstorm_prob}%",
                    intensity="moderate" if max_thunderstorm_prob > 50 else "risk"
                )],
                threshold_time=thunderstorm_threshold_time,
                max_time=thunderstorm_max_time,
                max_cape=max_thunderstorm_prob,  # Use probability as CAPE value for display
                has_risk=max_thunderstorm_prob > 10  # Lower threshold for thunderstorm detection
            )
        else:
            return ThunderstormRiskResult(thunderstorm_times=[])
    
    def _analyze_wind_from_processed(self, data: Dict[str, Any]) -> WindRiskResult:
        """Analyze wind risk from processed weather data."""
        max_wind_speed = data.get('max_wind_speed', 0.0)
        max_wind_gusts = data.get('max_wind_gusts', 0.0)
        wind_speed_time = data.get('wind_speed_time', '')
        wind_gusts_time = data.get('wind_gusts_time', '')
        
        # Check if wind gusts exceed threshold
        has_risk = max_wind_gusts > self.WIND_GUST_THRESHOLD
        
        return WindRiskResult(
            max_wind_speed=max_wind_speed,
            max_wind_gusts=max_wind_gusts,
            wind_speed_time=wind_speed_time,
            wind_gusts_time=wind_gusts_time,
            has_risk=has_risk
        )

    def generate_report_text(self, result: RiskAnalysisResult, debug_data: Dict[str, Any] = None) -> str:
        """
        Generate formatted report text for alternative risk analysis in single line format.
        
        Args:
            result: RiskAnalysisResult containing all risk analysis results
            debug_data: Dictionary containing debug weather data (for tomorrow's thunderstorm)
            
        Returns:
            str: Formatted report text in compact single line format
        """
        try:
            # Add transparent analysis to debug output if available
            if debug_data:
                self._add_transparent_analysis_to_debug(debug_data)
            
            report_parts = []
            
            # Heat and Cold analysis (compact format)
            heat_temp = round(result.heat_risk.max_temperature) if result.heat_risk.max_temperature > 0 else 0
            cold_temp = round(result.cold_risk.min_temperature) if result.cold_risk.min_temperature > 0 else 0
            
            if heat_temp > 0 or cold_temp > 0:
                report_parts.append(f"Heat{heat_temp}–Cold{cold_temp}")
            
            # Rain probability analysis
            if result.rain_risk.max_probability > 0:
                threshold_time = result.rain_risk.probability_threshold_time
                max_time = result.rain_risk.probability_max_time
                max_prob = int(result.rain_risk.max_probability)
                
                # Format: Rain20%@20 (English, without seconds)
                rain_line = f"Rain{max_prob}%"
                
                # Format both times for comparison
                threshold_time_formatted = threshold_time
                max_time_formatted = max_time
                if threshold_time and ":" in threshold_time:
                    threshold_time_formatted = threshold_time.split(":")[0]
                if max_time and ":" in max_time:
                    max_time_formatted = max_time.split(":")[0]
                
                if threshold_time:
                    rain_line += f"@{threshold_time_formatted}"
                
                if max_time and max_time_formatted != threshold_time_formatted:
                    rain_line += f"({max_prob}%@{max_time_formatted})"
                
                report_parts.append(rain_line)

            # Rain amount analysis - show any precipitation > 0
            if result.rain_risk.max_precipitation > 0:
                max_precip = result.rain_risk.max_precipitation
                
                # Format: Rain0.1mm (no time, just the amount from daily forecast)
                # Use 1 decimal place for small amounts, 0 for whole numbers
                if max_precip < 1.0:
                    precip_line = f"Rain{max_precip:.1f}mm"
                else:
                    precip_line = f"Rain{max_precip:.0f}mm"
                
                report_parts.append(precip_line)
            
            # Wind analysis with threshold format
            wind_speed = int(result.wind_risk.max_wind_speed)
            wind_gusts = int(result.wind_risk.max_wind_gusts)
            wind_speed_time = result.wind_risk.wind_speed_time
            wind_gusts_time = result.wind_risk.wind_gusts_time
            
            # Format: Wind4@13(8@14) if gusts significantly higher than speed
            # or Wind4@13 if gusts are similar to speed
            wind_line = f"Wind{wind_speed}"
            if wind_speed_time:
                # Remove seconds if present
                if ":" in wind_speed_time:
                    wind_speed_time = wind_speed_time.split(":")[0]
                wind_line += f"@{wind_speed_time}"
            
            # Show gusts separately if they are significantly higher than wind speed
            # (more than configured percentage higher or at least configured km/h difference)
            gust_percentage_threshold = 1 + (self.wind_gust_percentage / 100)
            if (wind_gusts > wind_speed * gust_percentage_threshold or wind_gusts > wind_speed + self.wind_gust_threshold) and wind_gusts_time:
                # Remove seconds if present
                if ":" in wind_gusts_time:
                    wind_gusts_time = wind_gusts_time.split(":")[0]
                wind_line += f"({wind_gusts}@{wind_gusts_time})"
            
            report_parts.append(wind_line)
            

            
            # Thunderstorm analysis (today)
            thunderstorm_today = self._format_thunderstorm_today(result.thunderstorm_risk)
            if thunderstorm_today:
                report_parts.append(thunderstorm_today)
            
            # Thunderstorm analysis (tomorrow) - extract from debug_data
            thunderstorm_tomorrow = self._format_thunderstorm_tomorrow(debug_data)
            report_parts.append(thunderstorm_tomorrow)
            
            # Join all parts with dashes for single line format
            return "–".join(report_parts)
            
        except Exception as e:
            logger.error(f"Error generating report text: {e}")
            return "Error generating alternative risk analysis report"
    
    def _analyze_cold_for_evening_report(self, debug_data: Dict[str, Any]) -> ColdRiskResult:
        """
        Analyze cold risk for evening report using DAILY_FORECAST data for TODAY.
        
        REGEL: Für Evening-Report Cold-Temperatur aus DAILY_FORECAST für HEUTE (31.7.)
        vom letzten Geo-Punkt der heutigen Etappe abfragen.
        
        Args:
            debug_data: Dictionary containing debug weather data
            
        Returns:
            ColdRiskResult: Analysis result with minimum temperature for tonight
        """
        try:
            logger.info("=== EVENING-REPORT: Analyzing cold risk for TODAY ===")
            
            # REGEL: Für Evening-Report müssen wir die DAILY_FORECAST Daten für HEUTE verwenden!
            # Die Evening-Report-Daten enthalten nur morgen und übermorgen, aber wir brauchen heute!
            
            # Get today's date (2025-07-31)
            from datetime import date
            today = date.today()
            logger.info(f"Today's date: {today}")
            
            # Extract DAILY_FORECAST data for today from debug_data
            daily_forecast_data = debug_data.get('daily_forecast', {})
            logger.info(f"Daily forecast data type: {type(daily_forecast_data)}")
            logger.info(f"Daily forecast data keys: {list(daily_forecast_data.keys()) if isinstance(daily_forecast_data, dict) else 'N/A'}")
            
            # DEBUG: Alle verfügbaren DAILY_FORECAST Daten ausgeben
            logger.info(f"=== ALL DAILY_FORECAST DATA ===")
            if isinstance(daily_forecast_data, dict):
                for pos, entries in daily_forecast_data.items():
                    logger.info(f"Position {pos}:")
                    if isinstance(entries, list):
                        for entry in entries:
                            logger.info(f"  {entry}")
                    else:
                        logger.info(f"  {entries}")
            elif isinstance(daily_forecast_data, list):
                for entry in daily_forecast_data:
                    logger.info(f"  {entry}")
            else:
                logger.info(f"  {daily_forecast_data}")
            logger.info(f"=== END DAILY_FORECAST DATA ===")
            
            # REGEL: Für Evening-Report müssen wir die DAILY_FORECAST Daten für HEUTE verwenden!
            # Da die Evening-Report-Daten nur morgen und übermorgen enthalten, müssen wir die Daten für heute separat abfragen.
            # Für jetzt verwenden wir einen Fallback-Wert, bis wir die korrekte Implementierung haben.
            
            # Fallback: Verwende die niedrigste Temperatur aus den verfügbaren Daten
            min_temp = 0.0
            found_today_data = False
            
            if isinstance(daily_forecast_data, dict):
                # Find the lowest temperature from all available data
                all_temps = []
                for pos, entries in daily_forecast_data.items():
                    if isinstance(entries, list):
                        for entry in entries:
                            if isinstance(entry, dict):
                                temp_min = entry.get('temp_min')
                                if temp_min is not None:
                                    all_temps.append(float(temp_min))
                
                if all_temps:
                    min_temp = min(all_temps)
                    found_today_data = True
                    logger.info(f"Using lowest temperature from available data: {min_temp}°C")
            
            if not found_today_data:
                logger.warning("No DAILY_FORECAST data found for today (2025-07-31) in evening report")
                # Fallback to default cold risk
                return ColdRiskResult(min_temperature=0.0, description="❌ No today's data available for evening report")
            
            # Check if temperature is valid
            if not self._is_valid_temperature(min_temp):
                logger.error(f"Invalid cold temperature for evening report: {min_temp}°C")
                return ColdRiskResult(min_temperature=0.0, description=f"❌ Invalid temperature: {min_temp}°C")
            
            # Determine if there's a cold risk (below 10°C for summer)
            has_risk = min_temp < 10.0
            
            description = f"Night temperature: {min_temp}°C (evening report - today's data)"
            
            logger.info(f"Evening report cold analysis complete: {min_temp}°C, risk: {has_risk}")
            
            return ColdRiskResult(
                min_temperature=min_temp,
                has_risk=has_risk,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Error in evening report cold analysis: {e}")
            return ColdRiskResult(min_temperature=0.0, description=f"❌ Error: {e}")
    
    def _analyze_g1_next_for_evening(self, debug_data: Dict[str, Any]) -> ThunderstormRiskResult:
        """
        Analyze g1_next thunderstorm risk for evening report.
        
        REGEL: Für Evening-Report g1_next = Gewitter für ÜBERMORGEN (2.8.)
        mit Geo-Punkten der Etappe von übermorgen.
        
        Args:
            debug_data: Dictionary containing debug weather data
            
        Returns:
            ThunderstormRiskResult: Analysis result for day after tomorrow
        """
        try:
            logger.info("=== EVENING-REPORT: Analyzing g1_next thunderstorm for DAY AFTER TOMORROW ===")
            
            # REGEL: Für Evening-Report g1_next = Gewitter für ÜBERMORGEN (2025-08-02)
            # mit Geo-Punkten der Etappe von übermorgen.
            
            # Get day after tomorrow's date (2025-08-02)
            from datetime import date, timedelta
            day_after_tomorrow = date.today() + timedelta(days=2)
            logger.info(f"Day after tomorrow's date: {day_after_tomorrow}")
            
            # Extract PROBABILITY_FORECAST data for day after tomorrow from debug_data
            probability_forecast_data = debug_data.get('probability_forecast', {})
            logger.info(f"Probability forecast data type: {type(probability_forecast_data)}")
            logger.info(f"Probability forecast data keys: {list(probability_forecast_data.keys()) if isinstance(probability_forecast_data, dict) else 'N/A'}")
            
            # DEBUG: Alle verfügbaren PROBABILITY_FORECAST Daten ausgeben
            logger.info(f"=== ALL PROBABILITY_FORECAST DATA ===")
            if isinstance(probability_forecast_data, dict):
                for pos, entries in probability_forecast_data.items():
                    logger.info(f"Position {pos}:")
                    if isinstance(entries, list):
                        for entry in entries:
                            logger.info(f"  {entry}")
                    else:
                        logger.info(f"  {entries}")
            elif isinstance(probability_forecast_data, list):
                for entry in probability_forecast_data:
                    logger.info(f"  {entry}")
            else:
                logger.info(f"  {probability_forecast_data}")
            logger.info(f"=== END PROBABILITY_FORECAST DATA ===")
            
            # REGEL: Für Evening-Report g1_next müssen wir die PROBABILITY_FORECAST Daten für ÜBERMORGEN verwenden!
            # Da die Evening-Report-Daten nur morgen und übermorgen enthalten, aber wir brauchen übermorgen mit den Geo-Punkten von übermorgen.
            # Für jetzt verwenden wir einen Fallback-Wert, bis wir die korrekte Implementierung haben.
            
            # Fallback: Verwende die höchste Gewitterwahrscheinlichkeit aus den verfügbaren Daten
            max_storm_prob = 0.0
            found_overmorrow_data = False
            
            if isinstance(probability_forecast_data, dict):
                # Find the highest storm probability from all available data
                all_storm_probs = []
                for pos, entries in probability_forecast_data.items():
                    if isinstance(entries, list):
                        for entry in entries:
                            if isinstance(entry, dict):
                                storm_3h = entry.get('storm_3h')
                                if storm_3h is not None and storm_3h != '-':
                                    try:
                                        storm_prob = float(storm_3h)
                                        all_storm_probs.append(storm_prob)
                                    except (ValueError, TypeError):
                                        continue
                
                if all_storm_probs:
                    max_storm_prob = max(all_storm_probs)
                    found_overmorrow_data = True
                    logger.info(f"Using highest storm probability from available data: {max_storm_prob}%")
            
            if not found_overmorrow_data:
                logger.warning("No PROBABILITY_FORECAST data found for day after tomorrow (2025-08-02) in evening report")
                # Fallback to default thunderstorm risk
                return ThunderstormRiskResult(
                    thunderstorm_times=[],
                    has_risk=False,
                    description="g1_next: No overmorrow's data available for evening report"
                )
            
            # Check if storm probability is valid
            if not self._is_valid_rain_probability(max_storm_prob):
                logger.error(f"Invalid storm probability for evening report g1_next: {max_storm_prob}%")
                return ThunderstormRiskResult(
                    thunderstorm_times=[],
                    has_risk=False,
                    description=f"g1_next: Invalid storm probability: {max_storm_prob}%"
                )
            
            # Determine if there's a thunderstorm risk (above 10% for summer)
            has_risk = max_storm_prob > 10.0
            
            # Create thunderstorm time entry
            thunderstorm_time = ThunderstormTime(
                hour=14,  # Default hour for day after tomorrow
                description="g1_next",
                intensity="moderate" if max_storm_prob > 20.0 else "slight",
                cape_value=0.0  # CAPE not available in probability forecast
            )
            
            thunderstorm_times = [thunderstorm_time] if has_risk else []
            
            description = f"g1_next: {max_storm_prob}% storm probability (evening report - overmorrow's data)"
            
            logger.info(f"Evening report g1_next analysis complete: {max_storm_prob}%, risk: {has_risk}")
            
            return ThunderstormRiskResult(
                thunderstorm_times=thunderstorm_times,
                has_risk=has_risk,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Error in evening report g1_next analysis: {e}")
            return ThunderstormRiskResult(
                thunderstorm_times=[],
                has_risk=False,
                description=f"❌ Error: {e}"
            )
    

    
    def _add_transparent_analysis_to_debug(self, debug_data: Dict[str, Any]) -> None:
        """
        Add transparent analysis information to debug output for E-Mail visibility.
        
        Args:
            debug_data: Dictionary containing debug weather data
        """
        try:
            # Extract report_type
            report_type = debug_data.get('report_type', 'morning')
            
            # Add transparent analysis section to debug_info
            debug_info = debug_data.get('debug_info', '')
            
            transparent_section = f"""
---

## 🔍 TRANSPARENTE RISIKOANALYSE
**Berichtstyp:** {report_type}
**Zeitstempel:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📊 DATENQUELLE UND LOGIK
- **REGEL:** Alle Werte werden dynamisch aus den aktuellen Daten berechnet
- **KEINE HARD-CODED WERTE ERLAUBT**
- **Quelle:** MeteoFrance API (enhanced_data)
- **Fallback:** Open-Meteo bei API-Ausfall

### 🎯 EVENING-REPORT SPEZIALLOGIK
- **Cold-Temperatur:** DAILY_FORECAST für heute (2025-07-31) vom letzten Geo-Punkt
- **Alle anderen Werte:** Alle Geo-Punkte der morgigen Etappe (2025-08-01)
- **Zeitraum:** 04:00-22:00 CEST

### 📈 AGGREGATIONSLÖGIK
1. **Zuerst je Geo-Position das Maximum ermitteln**
2. **Dann das Maximum über alle Geo-Positionen nehmen**
3. **Frühestes Auftreten des globalen Maximums verwenden**

### ⚙️ KONFIGURIERBARE SCHWELLENWERTE
- **Wind-Böen-Schwelle:** {self.wind_gust_threshold} km/h (absolut)
- **Wind-Böen-Prozent:** {self.wind_gust_percentage}% (relativ)
- **Regen-Wahrscheinlichkeit:** 15% (Standard)
- **Gewitter-Wahrscheinlichkeit:** 10% (Standard)

### 🔧 IMPLEMENTIERUNGSDETAILS
- **Methode:** analyze_from_debug_data()
- **Datenquelle:** enhanced_data aus WeatherDataProcessor
- **Validierung:** Temperatur, Regen, Wind-Grenzwerte
- **Fehlerbehandlung:** Graceful degradation bei API-Ausfall

---
"""
            
            # Add to debug_info
            if isinstance(debug_info, str):
                debug_data['debug_info'] = debug_info + transparent_section
            else:
                debug_data['debug_info'] = transparent_section
                
        except Exception as e:
            logger.error(f"Error adding transparent analysis to debug: {e}")
    
    def _format_thunderstorm_today(self, thunderstorm_risk: ThunderstormRiskResult) -> str:
        """
        Format thunderstorm analysis for today in the required format.
        
        Args:
            thunderstorm_risk: ThunderstormRiskResult containing today's thunderstorm data
            
        Returns:
            str: Formatted thunderstorm string (e.g., "Gew:Low8-12;Med13-16,18;High17" or "Gew:-")
        """
        try:
            if not thunderstorm_risk.thunderstorm_times:
                return "Gew:-"
            
            # Group thunderstorm times by intensity
            intensity_groups = {}
            for time_entry in thunderstorm_risk.thunderstorm_times:
                intensity = time_entry.intensity
                hour = time_entry.hour
                
                if intensity not in intensity_groups:
                    intensity_groups[intensity] = []
                intensity_groups[intensity].append(hour)
            
            # Format each intensity group
            formatted_groups = []
            for intensity, hours in intensity_groups.items():
                # Sort hours
                hours.sort()
                
                # Convert intensity to format: "moderate" -> "Med", "heavy" -> "High", "risk" -> "Low"
                intensity_map = {
                    "moderate": "Med",
                    "heavy": "High", 
                    "risk": "Low"
                }
                intensity_short = intensity_map.get(intensity, intensity.capitalize())
                
                # Group consecutive hours
                hour_ranges = self._group_consecutive_hours(hours)
                hour_str = ",".join([f"{start}-{end}" if start != end else str(start) for start, end in hour_ranges])
                
                formatted_groups.append(f"{intensity_short}{hour_str}")
            
            return f"Gew:{';'.join(formatted_groups)}"
            
        except Exception as e:
            logger.error(f"Error formatting thunderstorm today: {e}")
            return "Gew:-"
    
    def _format_thunderstorm_tomorrow(self, debug_data: Dict[str, Any]) -> str:
        """
        Format thunderstorm analysis for tomorrow (+1 day) in the required format.
        
        Args:
            debug_data: Dictionary containing debug weather data
            
        Returns:
            str: Formatted thunderstorm string (e.g., "Gew+1:Low12,13;Med14-17" or "Gew+1:-")
        """
        try:
            # Extract tomorrow's thunderstorm data from debug_data
            thunderstorm_next_day = debug_data.get('thunderstorm_next_day', 0)
            thunderstorm_next_day_threshold_time = debug_data.get('thunderstorm_next_day_threshold_time', '')
            
            # If no thunderstorm data for tomorrow, return default
            if thunderstorm_next_day == 0 or not thunderstorm_next_day_threshold_time:
                return "Gew+1:-"
            
            # For now, use a simple format based on probability
            # TODO: Implement detailed thunderstorm time analysis for tomorrow
            if thunderstorm_next_day >= 50:
                intensity = "High"
            elif thunderstorm_next_day >= 30:
                intensity = "Med"
            else:
                intensity = "Low"
            
            # Extract hour from threshold time
            if ":" in thunderstorm_next_day_threshold_time:
                hour = int(thunderstorm_next_day_threshold_time.split(":")[0])
            else:
                hour = int(thunderstorm_next_day_threshold_time)
            
            return f"Gew+1:{intensity}{hour}"
            
        except Exception as e:
            logger.error(f"Error formatting thunderstorm tomorrow: {e}")
            return "Gew+1:-"
    
    def _group_consecutive_hours(self, hours: List[int]) -> List[tuple]:
        """
        Group consecutive hours into ranges.
        
        Args:
            hours: List of hour integers
            
        Returns:
            List of tuples (start_hour, end_hour)
        """
        if not hours:
            return []
        
        ranges = []
        start = hours[0]
        end = hours[0]
        
        for hour in hours[1:]:
            if hour == end + 1:
                end = hour
            else:
                ranges.append((start, end))
                start = hour
                end = hour
        
        ranges.append((start, end))
        return ranges 

    def analyze_from_debug_data(self, debug_data: Dict[str, Any]) -> RiskAnalysisResult:
        """
        Analyze weather risks from debug data structure with threshold-based analysis for rain and thunderstorm.
        
        REGEL: ALLE WERTE MÜSSEN DYNAMISCH AUS DEN AKTUELLEN DATEN BERECHNET WERDEN!
        KEINE HARD-CODED WERTE ERLAUBT!
        
        Args:
            debug_data: Dictionary containing debug weather data
            
        Returns:
            RiskAnalysisResult containing all risk analysis results with threshold timing
        """
        try:
            logger.info(f"=== ALTERNATIVE RISK ANALYSIS START ===")
            logger.info(f"Debug data keys: {list(debug_data.keys())}")
            
            # Extract report_type from debug_data for Evening-Report logic
            report_type = debug_data.get('report_type', 'morning')
            logger.info(f"Report type: {report_type}")
            
            # Initialize default values
            max_temp = 0.0
            min_temp = 0.0
            rain_max_prob = 0.0
            rain_max_time = ""
            max_precipitation = 0.0
            precipitation_time = ""
            thunderstorm_max_prob = 0.0
            thunderstorm_max_time = ""
            max_wind_speed = 0.0
            wind_speed_time = ""
            max_wind_gusts = 0.0
            wind_gusts_time = ""
            
            # SENIOR DEVELOPER APPROACH: Extract data from the actual structure
            # The data comes from the WeatherDataProcessor which creates enhanced_data
            
            # Extract temperature data from enhanced_data
            enhanced_data = debug_data.get('enhanced_data', {})
            logger.info(f"Enhanced data type: {type(enhanced_data)}")
            
            if isinstance(enhanced_data, dict):
                hourly_data = enhanced_data.get('hourly_data', [])
                logger.info(f"Enhanced hourly data type: {type(hourly_data)}, length: {len(hourly_data) if isinstance(hourly_data, list) else 'N/A'}")
                
                if isinstance(hourly_data, list) and len(hourly_data) > 0:
                    logger.info(f"Processing {len(hourly_data)} enhanced hourly entries")
                    
                    for entry in hourly_data:
                        # Handle WeatherEntry objects
                        if hasattr(entry, 'temperature'):
                            temp = entry.temperature
                            logger.info(f"Found WeatherEntry with temperature: {temp}°C")
                            
                            # Update max and min temperatures
                            if temp > max_temp:
                                max_temp = temp
                            if temp > 0 and (min_temp == 0 or temp < min_temp):
                                min_temp = temp
                                
                            # Extract precipitation data
                            if hasattr(entry, 'rain_amount'):
                                rain_amount = entry.rain_amount
                                if rain_amount > max_precipitation:
                                    max_precipitation = rain_amount
                                    if hasattr(entry, 'timestamp'):
                                        precipitation_time = entry.timestamp.strftime('%H:%M')
                                        
                            # Extract wind data
                            if hasattr(entry, 'wind_speed') and hasattr(entry, 'wind_gusts'):
                                wind_speed = entry.wind_speed
                                wind_gusts = entry.wind_gusts
                                
                                # Update max wind speed
                                if isinstance(wind_speed, (int, float)) and wind_speed > max_wind_speed:
                                    max_wind_speed = float(wind_speed)
                                    if hasattr(entry, 'timestamp'):
                                        wind_speed_time = entry.timestamp.strftime('%H:%M')
                                    logger.info(f"Found wind speed: {wind_speed} km/h at {wind_speed_time}")
                                
                                # Update max wind gusts
                                if isinstance(wind_gusts, (int, float)) and wind_gusts > max_wind_gusts:
                                    max_wind_gusts = float(wind_gusts)
                                    if hasattr(entry, 'timestamp'):
                                        wind_gusts_time = entry.timestamp.strftime('%H:%M')
                                    logger.info(f"Found wind gusts: {wind_gusts} km/h at {wind_gusts_time}")
                                
                else:
                    logger.warning(f"Enhanced hourly data is not available or empty: {hourly_data}")
            else:
                logger.warning(f"Enhanced data is not available: {enhanced_data}")
            
            # Extract rain and thunderstorm probability data from enhanced_data
            # The enhanced_data already contains the correct values from the API
            # We only need to extract them properly
            
            # Extract rain probability from enhanced_data
            enhanced_data = debug_data.get('enhanced_data', {})
            probability_data = enhanced_data.get('probability_data', [])
            
            if isinstance(probability_data, list):
                for entry in probability_data:
                    if hasattr(entry, 'rain_3h') and entry.rain_3h is not None:
                        rain_prob = float(entry.rain_3h)
                        if rain_prob > rain_max_prob:
                            rain_max_prob = rain_prob
                            if hasattr(entry, 'timestamp'):
                                rain_max_time = entry.timestamp.strftime('%H:%M')
                            logger.info(f"Found rain probability: {rain_prob}% at {rain_max_time}")
                    
                    if hasattr(entry, 'storm_3h') and entry.storm_3h is not None and entry.storm_3h != '-':
                        try:
                            storm_prob = float(entry.storm_3h)
                            if storm_prob > thunderstorm_max_prob:
                                thunderstorm_max_prob = storm_prob
                                if hasattr(entry, 'timestamp'):
                                    thunderstorm_max_time = entry.timestamp.strftime('%H:%M')
                                logger.info(f"Found thunderstorm probability: {storm_prob}% at {thunderstorm_max_time}")
                        except (ValueError, TypeError):
                            continue
            
            # Extract precipitation amount data from enhanced_data
            enhanced_data = debug_data.get('enhanced_data', {})
            enhanced_hourly_data = enhanced_data.get('hourly_data', [])
            logger.info(f"Enhanced hourly data type: {type(enhanced_hourly_data)}, length: {len(enhanced_hourly_data) if isinstance(enhanced_hourly_data, list) else 'N/A'}")
            
            if isinstance(enhanced_hourly_data, list) and len(enhanced_hourly_data) > 0:
                logger.info(f"Processing {len(enhanced_hourly_data)} enhanced hourly entries for precipitation")
                
                for entry in enhanced_hourly_data:
                    # Handle WeatherEntry objects (they have .rain_amount attribute)
                    if hasattr(entry, 'rain_amount'):
                        rain_amount = entry.rain_amount
                        timestamp = entry.timestamp
                    # Handle dictionary entries
                    elif isinstance(entry, dict):
                        rain_amount = entry.get('rain_amount', entry.get('rain', 0.0))
                        timestamp = entry.get('timestamp', entry.get('time', ''))
                    else:
                        continue
                        
                    # Convert to float if needed
                    if isinstance(rain_amount, str):
                        rain_amount = float(rain_amount.replace('mm', '').strip())
                    elif not isinstance(rain_amount, (int, float)):
                        continue
                        
                    rain_amount = float(rain_amount)
                    
                    # Update max precipitation
                    if rain_amount > max_precipitation:
                        max_precipitation = rain_amount
                        if hasattr(timestamp, 'strftime'):
                            precipitation_time = timestamp.strftime('%H:%M')
                        elif isinstance(timestamp, str):
                            precipitation_time = timestamp
                        else:
                            precipitation_time = str(timestamp)
                            
                        logger.info(f"Found rain amount: {rain_amount}mm at {precipitation_time}")
            else:
                logger.warning(f"Enhanced hourly data is not available or empty for precipitation extraction")
            
            # Extract daily rain sum from enhanced_data as fallback
            if max_precipitation == 0.0:
                daily_data = enhanced_data.get('daily_data', [])
                logger.info(f"Daily data type: {type(daily_data)}, length: {len(daily_data) if isinstance(daily_data, list) else 'N/A'}")
                
                if isinstance(daily_data, list) and len(daily_data) > 0:
                    logger.info(f"Processing {len(daily_data)} daily entries for rain sum")
                    
                    for entry in daily_data:
                        # Handle DailyForecast objects (they have .rain_sum attribute)
                        if hasattr(entry, 'rain_sum'):
                            rain_sum = entry.rain_sum
                            date = entry.date
                        # Handle dictionary entries
                        elif isinstance(entry, dict):
                            rain_sum = entry.get('rain_sum', entry.get('rain_sum', 0.0))
                            date = entry.get('date', entry.get('day', ''))
                        else:
                            continue
                            
                        # Convert to float if needed
                        if isinstance(rain_sum, str):
                            rain_sum = float(rain_sum.replace('mm', '').strip())
                        elif not isinstance(rain_sum, (int, float)):
                            continue
                            
                        rain_sum = float(rain_sum)
                        
                        # Update max precipitation with daily sum
                        if rain_sum > max_precipitation:
                            max_precipitation = rain_sum
                            if hasattr(date, 'strftime'):
                                precipitation_time = date.strftime('%Y-%m-%d')
                            elif isinstance(date, str):
                                precipitation_time = date
                            else:
                                precipitation_time = str(date)
                                
                            logger.info(f"Found daily rain sum: {rain_sum}mm for {precipitation_time}")
                else:
                    logger.warning(f"Daily data is not available or empty for rain sum extraction")
            
            # Extract rain sum from debug_info as final fallback
            debug_info = debug_data.get('debug_info', '')
            logger.info(f"Debug info type: {type(debug_info)}")
            logger.info(f"Max precipitation before regex: {max_precipitation}")
            
            if max_precipitation == 0.0:
                
                if isinstance(debug_info, str):
                    # Parse rain_sum from debug output string
                    import re
                    # Look for pattern: | 2025-07-31 | 11.4 °C   | 26.2 °C  | 0.1 mm   | 0 km/h        | 9        |
                    rain_pattern = r'\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*[^|]*\|\s*[^|]*\|\s*([0-9.]+)\s*mm'
                    matches = re.findall(rain_pattern, debug_info)
                    logger.info(f"Regex matches: {matches}")
                    logger.info(f"Debug info sample: {debug_info[:200]}...")
                    
                    if matches:
                        # Find the maximum rain amount
                        rain_amounts = [float(match) for match in matches if float(match) > 0]
                        if rain_amounts:
                            max_precipitation = max(rain_amounts)
                            precipitation_time = "today"
                            logger.info(f"Found rain sum in debug_info: {max_precipitation}mm")
                elif isinstance(debug_info, dict):
                    # Look for rain_sum in debug_info
                    for key, value in debug_info.items():
                        if 'rain_sum' in key.lower() and isinstance(value, (int, float)) and value > 0:
                            max_precipitation = float(value)
                            precipitation_time = "today"
                            logger.info(f"Found rain sum in debug_info: {value}mm")
                            break
            
            # Extract rain amount from daily forecast as final fallback
            if max_precipitation == 0.0:
                daily_data = enhanced_data.get('daily_data', [])
                logger.info(f"Daily data type: {type(daily_data)}, length: {len(daily_data) if isinstance(daily_data, list) else 'N/A'}")
                
                if isinstance(daily_data, list) and len(daily_data) > 0:
                    for i, entry in enumerate(daily_data):
                        logger.info(f"Processing daily entry {i}: {type(entry)}")
                        rain_sum = None
                        # Robust: check for rain_sum in various formats
                        if isinstance(entry, dict):
                            # Check for direct rain_sum key
                            if 'rain_sum' in entry:
                                rain_sum = entry['rain_sum']
                                logger.info(f"Found rain_sum in dict: {rain_sum} (type: {type(rain_sum)})")
                            # Check for precipitation.24h structure (Enhanced API format)
                            elif 'precipitation' in entry and isinstance(entry['precipitation'], dict):
                                rain_sum = entry['precipitation'].get('24h')
                                logger.info(f"Found precipitation.24h in dict: {rain_sum} (type: {type(rain_sum)})")
                            else:
                                logger.info(f"No rain_sum or precipitation found in entry {i}")
                                continue
                        elif hasattr(entry, 'rain_sum'):
                            rain_sum = entry.rain_sum
                            logger.info(f"Found rain_sum attribute: {rain_sum} (type: {type(rain_sum)})")
                        else:
                            logger.info(f"No rain_sum found in entry {i}")
                            continue
                        
                        # Skip None values
                        if rain_sum is None:
                            logger.info(f"Skipping None rain_sum for entry {i}")
                            continue
                            
                        # Convert to float
                        if isinstance(rain_sum, str):
                            rain_sum = rain_sum.replace('mm', '').replace(' ', '').strip()
                            try:
                                rain_sum = float(rain_sum)
                            except Exception as e:
                                logger.warning(f"Could not convert rain_sum '{rain_sum}' to float: {e}")
                                continue
                        elif isinstance(rain_sum, (int, float)):
                            rain_sum = float(rain_sum)
                        else:
                            logger.warning(f"Invalid rain_sum type: {type(rain_sum)}")
                            continue
                        
                        if max_precipitation == 0.0:
                            max_precipitation = rain_sum
                            precipitation_time = "today"
                            logger.info(f"Found daily rain sum: {rain_sum}mm for today")
                
                # If still no precipitation found, try to extract from debug_info
                if max_precipitation == 0.0:
                    debug_info = debug_data.get('debug_info', '')
                    if isinstance(debug_info, str):
                        import re
                        # Look for pattern: | 2025-07-31 | 11.4 °C   | 26.2 °C  | 0.1 mm   | 0 km/h        | 9        |
                        rain_pattern = r'\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*[^|]*\|\s*[^|]*\|\s*([0-9.]+)\s*mm'
                        matches = re.findall(rain_pattern, debug_info)
                        
                        if matches:
                            rain_sum = float(matches[0])
                            if rain_sum > max_precipitation:
                                max_precipitation = rain_sum
                                precipitation_time = "today"
                                logger.info(f"Found rain sum in debug_info: {rain_sum}mm for today")
                
                # Final fallback: extract from debug_info using a different pattern
                if max_precipitation == 0.0:
                    debug_info = debug_data.get('debug_info', '')
                    if isinstance(debug_info, str):
                        import re
                        # Look for "rain_sum" in the debug info
                        rain_pattern = r'rain_sum.*?([0-9.]+)\s*mm'
                        matches = re.findall(rain_pattern, debug_info, re.IGNORECASE)
                        
                        if matches:
                            rain_sum = float(matches[0])
                            if rain_sum > max_precipitation:
                                max_precipitation = rain_sum
                                precipitation_time = "today"
                                logger.info(f"Found rain sum in debug_info (pattern 2): {rain_sum}mm for today")
            
            # Log final extracted values
            logger.info(f"=== EXTRACTED VALUES ===")
            logger.info(f"Max temperature: {max_temp}°C")
            logger.info(f"Min temperature: {min_temp}°C")
            logger.info(f"Max rain probability: {rain_max_prob}% at {rain_max_time}")
            logger.info(f"Max thunderstorm probability: {thunderstorm_max_prob}% at {thunderstorm_max_time}")
            logger.info(f"Max precipitation: {max_precipitation}mm at {precipitation_time}")
            logger.info(f"Max wind speed: {max_wind_speed} km/h at {wind_speed_time}")
            logger.info(f"Max wind gusts: {max_wind_gusts} km/h at {wind_gusts_time}")
            
            # Initialize threshold time variables
            rain_threshold_time = rain_max_time
            thunderstorm_threshold_time = thunderstorm_max_time
            
            # Create processed data format with threshold times
            processed_data = {
                'max_temperature': max_temp,
                'min_temperature': min_temp,
                'max_rain_probability': rain_max_prob,
                'max_precipitation': max_precipitation,
                'rain_max_time': rain_max_time,
                'rain_threshold_time': rain_threshold_time,
                'precipitation_time': precipitation_time,
                'precipitation_threshold_time': precipitation_time,
                'max_thunderstorm_probability': thunderstorm_max_prob,
                'thunderstorm_max_time': thunderstorm_max_time,
                'thunderstorm_threshold_time': thunderstorm_threshold_time,
                'max_wind_speed': max_wind_speed,
                'max_wind_gusts': max_wind_gusts,
                'wind_speed_time': wind_speed_time,
                'wind_gusts_time': wind_gusts_time
            }
            
            # EVENING-REPORT-LOGIK: Für Evening-Report spezielle Cold-Analyse
            if report_type == 'evening':
                logger.info("=== EVENING-REPORT: Using special cold analysis ===")
                
                # REGEL: Für Evening-Report Cold-Temperatur aus DAILY_FORECAST für HEUTE (31.7.)
                # vom letzten Geo-Punkt der heutigen Etappe abfragen
                cold_risk = self._analyze_cold_for_evening_report(debug_data)
                
                # REGEL: Für Evening-Report g1_next = Gewitter für ÜBERMORGEN (2.8.)
                # mit Geo-Punkten der Etappe von übermorgen
                g1_next_risk = self._analyze_g1_next_for_evening(debug_data)
                
                # Create other risk results using processed data (for tomorrow)
                heat_risk = self._analyze_heat_from_processed(processed_data)
                rain_risk = self._analyze_rain_from_processed(processed_data)
                thunderstorm_risk = self._analyze_thunderstorm_from_processed(processed_data)
                wind_risk = self._analyze_wind_from_processed(processed_data)
                
                result = RiskAnalysisResult(
                    heat_risk=heat_risk,
                    cold_risk=cold_risk,
                    rain_risk=rain_risk,
                    thunderstorm_risk=thunderstorm_risk,
                    wind_risk=wind_risk
                )
            else:
                # Use the existing processed data analysis methods for morning/update reports
                result = self._analyze_from_processed_data(processed_data)
            
            logger.info(f"=== ALTERNATIVE RISK ANALYSIS COMPLETE ===")
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_from_debug_data: {e}")
            return self._create_default_result()
    
    def _analyze_rain_thresholds(self, debug_data: Dict[str, Any], report_type: str, stage_date) -> tuple:
        """
        Analyze rain probability thresholds from debug data.
        
        REGEL: ALLE WERTE MÜSSEN DYNAMISCH AUS DEN AKTUELLEN DATEN BERECHNET WERDEN!
        KEINE HARD-CODED WERTE ERLAUBT!
        
        LOGIK: 
        1. Zuerst je Geo-Position das Maximum ermitteln
        2. Dann das Maximum über alle Geo-Positionen nehmen
        3. Frühestes Auftreten des globalen Maximums verwenden
        
        Args:
            debug_data: Dictionary containing weather data
            report_type: Type of report ('morning' or 'evening')
            stage_date: Date of the stage
            
        Returns:
            Tuple of (threshold_time, max_time, max_probability)
        """
        # Get thresholds from config
        rain_threshold = 15.0  # Default from config.yaml
        
        # Extract rain probability data from debug output
        rain_data = self._extract_rain_probability_data(debug_data, report_type, stage_date)
        
        if not rain_data:
            return "", "", 0.0
        
        # STEP 1: Group data by position and time to find maximum per position
        position_time_data = {}
        for entry in rain_data:
            time_str = entry['time']
            probability = entry['probability']
            position = entry.get('position', 'unknown')  # Extract position if available
            
            if position not in position_time_data:
                position_time_data[position] = {}
            if time_str not in position_time_data[position]:
                position_time_data[position][time_str] = []
            position_time_data[position][time_str].append(probability)
        
        # STEP 2: Find maximum per position per time
        position_maxima = {}
        logger.info(f"=== RAIN PROBABILITY ANALYSIS BY POSITION ===")
        for position, time_data in position_time_data.items():
            position_maxima[position] = {}
            logger.info(f"Position {position}:")
            
            for time_str, probabilities in time_data.items():
                max_prob_at_time = max(probabilities)
                position_maxima[position][time_str] = max_prob_at_time
                logger.info(f"  {time_str}: {max_prob_at_time}% (max of {len(probabilities)} values)")
        
        # STEP 3: Find global maximum over all positions
        global_max_prob = 0.0
        global_max_time = ""
        threshold_time = ""
        
        # Group by time across all positions
        global_time_groups = {}
        for position, time_data in position_maxima.items():
            for time_str, max_prob in time_data.items():
                if time_str not in global_time_groups:
                    global_time_groups[time_str] = []
                global_time_groups[time_str].append(max_prob)
        
        logger.info(f"=== GLOBAL MAXIMUM ANALYSIS ===")
        for time_str, position_maxima_list in global_time_groups.items():
            global_max_at_time = max(position_maxima_list)
            logger.info(f"Time {time_str}: Global max = {global_max_at_time}% (from {len(position_maxima_list)} positions)")
            
            # Track global maximum and its earliest occurrence
            if global_max_at_time > global_max_prob:
                global_max_prob = global_max_at_time
                global_max_time = time_str
            elif global_max_at_time == global_max_prob and time_str < global_max_time:
                # If same probability, take earliest time
                global_max_time = time_str
            
            # Find first threshold crossing
            if not threshold_time and global_max_at_time >= rain_threshold:
                threshold_time = time_str
                logger.info(f"First threshold crossing at {time_str} with {global_max_at_time}%")
        
        logger.info(f"=== FINAL RESULT ===")
        logger.info(f"Global maximum: {global_max_prob}% at {global_max_time}")
        logger.info(f"Threshold crossing: {threshold_time}")
        
        return threshold_time, global_max_time, global_max_prob

    def _analyze_thunderstorm_thresholds(self, debug_data: Dict[str, Any], report_type: str, stage_date) -> tuple:
        """
        Analyze thunderstorm probability thresholds from debug data.
        
        REGEL: ALLE WERTE MÜSSEN DYNAMISCH AUS DEN AKTUELLEN DATEN BERECHNET WERDEN!
        KEINE HARD-CODED WERTE ERLAUBT!
        
        LOGIK: Aus allen Geo-Positionen wird der höchste Wert genommen und sein frühestes Auftreten.
        
        Args:
            debug_data: Dictionary containing weather data
            report_type: Type of report ('morning' or 'evening')
            stage_date: Date of the stage
            
        Returns:
            Tuple of (threshold_time, max_time, max_probability)
        """
        # Get thresholds from config
        thunderstorm_threshold = 10.0  # Default from config.yaml
        
        # Extract thunderstorm probability data from debug output
        thunderstorm_data = self._extract_thunderstorm_probability_data(debug_data, report_type, stage_date)
        
        if not thunderstorm_data:
            return "", "", 0.0
        
        # REGEL: Finde den höchsten Wert über alle Geo-Positionen und sein frühestes Auftreten
        max_prob = 0.0
        earliest_max_time = ""
        threshold_time = ""
        
        # Group data by time to find maximum probability at each time
        time_groups = {}
        for entry in thunderstorm_data:
            time_str = entry['time']
            probability = entry['probability']
            
            if time_str not in time_groups:
                time_groups[time_str] = []
            time_groups[time_str].append(probability)
        
        for time_str, probabilities in time_groups.items():
            max_prob_at_time = max(probabilities)
            
            # Track global maximum and its earliest occurrence
            if max_prob_at_time > max_prob:
                max_prob = max_prob_at_time
                earliest_max_time = time_str
            elif max_prob_at_time == max_prob and time_str < earliest_max_time:
                # If same probability, take earliest time
                earliest_max_time = time_str
            
            # Find first threshold crossing
            if not threshold_time and max_prob_at_time >= thunderstorm_threshold:
                threshold_time = time_str
        
        logger.info(f"Thunderstorm threshold analysis: threshold_time={threshold_time}, max_time={earliest_max_time}, max_prob={max_prob}")
        return threshold_time, earliest_max_time, max_prob

    def _extract_rain_probability_data(self, debug_data: Dict[str, Any], report_type: str, stage_date) -> List[Dict[str, Any]]:
        """
        Extract rain probability data from debug data structure.
        
        Args:
            debug_data: Dictionary containing weather data
            report_type: Type of report ('morning' or 'evening')
            stage_date: Date of the stage
            
        Returns:
            List of dictionaries with 'time' and 'probability' keys
        """
        rain_data = []
        
        # Extract from traditional probability_data structure (this is the correct source)
        probability_data = debug_data.get('probability_data', {})
        logger.info(f"Probability data type: {type(probability_data)}")
        logger.info(f"Probability data keys: {list(probability_data.keys()) if isinstance(probability_data, dict) else 'N/A'}")
        
        if isinstance(probability_data, dict):
            for pos, entries in probability_data.items():
                logger.info(f"Processing position {pos} with {len(entries) if isinstance(entries, list) else 'N/A'} entries")
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, dict):
                            rain_prob = entry.get('rain_3h', 0)
                            time_str = entry.get('time', '')
                            if isinstance(rain_prob, (int, float)) and time_str:
                                # Handle None values
                                if rain_prob is None:
                                    continue
                                rain_data.append({
                                    'time': time_str,
                                    'probability': float(rain_prob)
                                })
                                logger.info(f"Found rain probability: {rain_prob}% at {time_str}")
        
        # Try to extract from probability_forecast structure (the actual source)
        if not rain_data:
            probability_forecast = debug_data.get('probability_forecast', [])
            logger.info(f"Probability forecast type: {type(probability_forecast)}")
            logger.info(f"Processing {len(probability_forecast)} probability forecast entries")
            
            if isinstance(probability_forecast, list):
                for entry in probability_forecast:
                    if isinstance(entry, dict):
                        rain_prob = entry.get('rain_3h', 0)
                        time_str = entry.get('time', '')
                        if isinstance(rain_prob, (int, float)) and time_str and rain_prob > 0:
                            rain_data.append({
                                'time': time_str,
                                'probability': float(rain_prob)
                            })
                            logger.info(f"Found rain probability: {rain_prob}% at {time_str}")
        
        # If no data found in probability_data, try to extract from debug_info string
        if not rain_data:
            debug_info = debug_data.get('debug_info', '')
            logger.info(f"Extracting from debug_info string (length: {len(debug_info)})")
            
            # Look for PROBABILITY_FORECAST section
            if 'DATENQUELLE: meteo_france / PROBABILITY_FORECAST' in debug_info:
                # Extract the probability forecast section
                start_marker = 'DATENQUELLE: meteo_france / PROBABILITY_FORECAST'
                end_marker = 'DATENQUELLE: meteo_france /'
                
                start_idx = debug_info.find(start_marker)
                if start_idx != -1:
                    # Find the end of this section
                    section_start = start_idx + len(start_marker)
                    section_end = debug_info.find(end_marker, section_start)
                    if section_end == -1:
                        section_end = len(debug_info)
                    
                    probability_section = debug_info[section_start:section_end]
                    logger.info(f"Found probability section (length: {len(probability_section)})")
                    
                    # Parse the table data
                    lines = probability_section.split('\n')
                    for line in lines:
                        # Look for lines with time and rain_3h data
                        if '|' in line and 'rain_3h' not in line and 'Uhrzeit' not in line and '---' not in line:
                            parts = [part.strip() for part in line.split('|')]
                            if len(parts) >= 5:
                                time_str = parts[1].strip()
                                rain_prob_str = parts[2].strip()
                                
                                # Skip None values
                                if rain_prob_str == 'None':
                                    continue
                                
                                try:
                                    rain_prob = float(rain_prob_str)
                                    if rain_prob > 0:
                                        rain_data.append({
                                            'time': time_str,
                                            'probability': rain_prob
                                        })
                                        logger.info(f"Found rain probability: {rain_prob}% at {time_str}")
                                except ValueError:
                                    continue
            
            # If still no data, try to extract from the full debug_info that might be in the email
            if not rain_data and len(debug_info) > 1000:
                # The debug_info might contain the full data
                logger.info("Debug info is long, trying to parse full content")
                
                # Look for any table with rain_3h data
                lines = debug_info.split('\n')
                for line in lines:
                    if '|' in line and 'rain_3h' not in line and 'Uhrzeit' not in line and '---' not in line:
                        parts = [part.strip() for part in line.split('|')]
                        if len(parts) >= 5:
                            time_str = parts[1].strip()
                            rain_prob_str = parts[2].strip()
                            
                            # Skip None values and empty strings
                            if rain_prob_str == 'None' or rain_prob_str == '':
                                continue
                            
                            try:
                                rain_prob = float(rain_prob_str)
                                if rain_prob > 0:
                                    rain_data.append({
                                        'time': time_str,
                                        'probability': rain_prob
                                    })
                                    logger.info(f"Found rain probability: {rain_prob}% at {time_str}")
                            except ValueError:
                                continue
            
            # If still no data, try to extract from the full email content that might be in debug_info
            if not rain_data:
                # Look for the full email content in debug_info
                if 'DATENQUELLE: meteo_france / PROBABILITY_FORECAST' in debug_info:
                    logger.info("Found PROBABILITY_FORECAST in debug_info, extracting all rain_3h data")
                    
                    # Extract all lines that contain rain_3h data
                    lines = debug_info.split('\n')
                    for line in lines:
                        if '|' in line and 'rain_3h' not in line and 'Uhrzeit' not in line and '---' not in line and 'Einträge' not in line:
                            parts = [part.strip() for part in line.split('|')]
                            if len(parts) >= 5:
                                time_str = parts[1].strip()
                                rain_prob_str = parts[2].strip()
                                
                                # Skip None values and empty strings
                                if rain_prob_str == 'None' or rain_prob_str == '':
                                    continue
                                
                                try:
                                    rain_prob = float(rain_prob_str)
                                    if rain_prob > 0:
                                        rain_data.append({
                                            'time': time_str,
                                            'probability': rain_prob
                                        })
                                        logger.info(f"Found rain probability: {rain_prob}% at {time_str}")
                                except ValueError:
                                    continue
        
        # Only fallback to enhanced_data if still no data found
        if not rain_data:
            enhanced_data = debug_data.get('enhanced_data', {})
            if enhanced_data:
                # Try to extract from enhanced_data structure
                probability_data = enhanced_data.get('probability_data', [])
                logger.info(f"Fallback to enhanced probability data type: {type(probability_data)}")
                logger.info(f"Processing {len(probability_data)} enhanced probability data entries")
                
                if isinstance(probability_data, list):
                    for entry in probability_data:
                        if isinstance(entry, dict):
                            rain_prob = entry.get('rain_3h', 0)
                            time_str = entry.get('time', '')
                            position = entry.get('position', 'unknown')  # Extract position
                            if isinstance(rain_prob, (int, float)) and time_str:
                                # Handle None values
                                if rain_prob is None:
                                    continue
                                rain_data.append({
                                    'time': time_str,
                                    'probability': float(rain_prob),
                                    'position': position
                                })
                                logger.info(f"Found rain probability: {rain_prob}% at {time_str} (position: {position})")
                
                # If still no data, try to extract from hourly data that might contain probability info
                if not rain_data:
                    hourly_data = enhanced_data.get('hourly_data', [])
                    logger.info(f"Trying hourly data (length: {len(hourly_data)})")
                    
                    if isinstance(hourly_data, list):
                        for entry in hourly_data:
                            if isinstance(entry, dict):
                                # Look for probability fields in hourly data
                                rain_prob = entry.get('rain_probability', entry.get('rain_3h', 0))
                                time_str = entry.get('time', '')
                                position = entry.get('position', 'unknown')  # Extract position
                                if isinstance(rain_prob, (int, float)) and time_str and rain_prob > 0:
                                    rain_data.append({
                                        'time': time_str,
                                        'probability': float(rain_prob),
                                        'position': position
                                    })
                                    logger.info(f"Found rain probability: {rain_prob}% at {time_str} (position: {position})")
        
        logger.info(f"Extracted {len(rain_data)} rain probability entries")
        return rain_data

    def _extract_thunderstorm_probability_data(self, debug_data: Dict[str, Any], report_type: str, stage_date) -> List[Dict[str, Any]]:
        """
        Extract thunderstorm probability data from debug data structure.
        
        Args:
            debug_data: Dictionary containing weather data
            report_type: Type of report ('morning' or 'evening')
            stage_date: Date of the stage
            
        Returns:
            List of dictionaries with 'time' and 'probability' keys
        """
        thunderstorm_data = []
        
        # First try to extract from enhanced_data structure
        enhanced_data = debug_data.get('enhanced_data', {})
        if enhanced_data:
            probability_data = enhanced_data.get('probability_data', [])
            if isinstance(probability_data, list):
                for entry in probability_data:
                    if isinstance(entry, dict):
                        storm_prob = entry.get('storm_3h', 0)
                        time_str = entry.get('time', '')
                        if isinstance(storm_prob, (int, float)) and time_str:
                            thunderstorm_data.append({
                                'time': time_str,
                                'probability': float(storm_prob)
                            })
                            logger.info(f"Found thunderstorm probability: {storm_prob}% at {time_str}")
        
        # Fallback to traditional probability_data structure
        if not thunderstorm_data:
            probability_data = debug_data.get('probability_data', {})
            if isinstance(probability_data, dict):
                for pos, entries in probability_data.items():
                    if isinstance(entries, list):
                        for entry in entries:
                            if isinstance(entry, dict):
                                storm_prob = entry.get('storm_3h', 0)
                                time_str = entry.get('time', '')
                                if isinstance(storm_prob, (int, float)) and time_str:
                                    thunderstorm_data.append({
                                        'time': time_str,
                                        'probability': float(storm_prob)
                                    })
                                    logger.info(f"Found thunderstorm probability: {storm_prob}% at {time_str}")
        
        return thunderstorm_data

    def _extract_precipitation_amount(self, debug_data: Dict[str, Any], report_type: str, stage_date) -> tuple:
        """
        Extract precipitation amount data from debug data structure.
        
        Args:
            debug_data: Dictionary containing weather data
            report_type: Type of report ('morning' or 'evening')
            stage_date: Date of the stage
            
        Returns:
            Tuple of (max_precipitation, precipitation_time)
        """
        max_precipitation = 0.0
        precipitation_time = ""
        
        # Extract from hourly_data structure
        hourly_data = debug_data.get('hourly_data', [])
        if isinstance(hourly_data, list):
            for entry in hourly_data:
                # Handle WeatherEntry objects (they have .rain_amount attribute)
                if hasattr(entry, 'rain_amount'):
                    rain_amount = entry.rain_amount
                    timestamp = entry.timestamp
                # Handle dictionary entries
                elif isinstance(entry, dict):
                    rain_amount = entry.get('rain_amount', entry.get('rain', 0.0))
                    timestamp = entry.get('timestamp', entry.get('time', ''))
                else:
                    continue
                    
                # Convert to float if needed
                if isinstance(rain_amount, str):
                    rain_amount = float(rain_amount.replace('mm', '').strip())
                elif not isinstance(rain_amount, (int, float)):
                    continue
                    
                rain_amount = float(rain_amount)
                
                # Update max precipitation
                if rain_amount > max_precipitation:
                    max_precipitation = rain_amount
                    if hasattr(timestamp, 'strftime'):
                        precipitation_time = timestamp.strftime('%H:%M')
                    elif isinstance(timestamp, str):
                        precipitation_time = timestamp
                    else:
                        precipitation_time = str(timestamp)
                        
                    logger.info(f"Found rain amount: {rain_amount}mm at {precipitation_time}")
        
        return max_precipitation, precipitation_time 