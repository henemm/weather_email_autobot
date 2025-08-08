"""
Weather Debug Output Module

This module generates comprehensive debug output for weather data from MeteoFrance API
following the specification in example_weather_debug_2025-07-30.md
"""

import os
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

try:
    from meteofrance_api.client import MeteoFranceClient
    from meteofrance_api.model import Forecast
except ImportError:
    MeteoFranceClient = None
    Forecast = None

try:
    from src.position.etappenlogik import get_current_stage, get_stage_coordinates
    from src.wetter.fetch_meteofrance import get_forecast, get_alerts
except ImportError:
    try:
        from position.etappenlogik import get_current_stage, get_stage_coordinates
        from wetter.fetch_meteofrance import get_forecast, get_alerts
    except ImportError:
        get_current_stage = None
        get_stage_coordinates = None
        get_forecast = None
        get_alerts = None

logger = logging.getLogger(__name__)


class WeatherDebugOutput:
    """
    Generates comprehensive debug output for weather data from MeteoFrance API.
    
    This class creates debug output following the specification in 
    example_weather_debug_2025-07-30.md with tabular data for all stage positions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the debug output generator.
        
        Args:
            config: Configuration dictionary containing debug settings and startdatum
        """
        self.config = config
        self.debug_config = config.get("debug", {})
        self.startdatum = config.get("startdatum")
        self.output_directory = self.debug_config.get("output_directory", "output/debug")
        
        # Ensure output directory exists
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize MeteoFrance client
        self.client = MeteoFranceClient() if MeteoFranceClient else None
        
    def should_generate_debug(self) -> bool:
        """
        Check if debug output should be generated.
        
        Returns:
            True if debug is enabled, False otherwise
        """
        return self.debug_config.get("enabled", False)
    
    def get_target_date(self, report_type: str) -> date:
        """
        Determine the target date for debug output based on report type.
        
        Args:
            report_type: Type of report ('morning', 'evening', 'dynamic', 'update')
            
        Returns:
            Target date for the debug output
        """
        if not self.startdatum:
            return date.today()
        
        try:
            start_date = datetime.strptime(self.startdatum, "%Y-%m-%d").date()
            current_date = date.today()
            days_since_start = (current_date - start_date).days
            
            if days_since_start < 0:
                return current_date
            
            # For evening reports, show tomorrow's data
            if report_type == "evening":
                return start_date + timedelta(days=days_since_start + 1)
            else:
                return start_date + timedelta(days=days_since_start)
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating target date: {e}")
            return date.today()
    
    def get_target_dates_for_report_type(self, report_type: str) -> Dict[str, date]:
        """
        Get all relevant target dates for a report type.
        
        Args:
            report_type: Type of report ('morning', 'evening', 'dynamic', 'update')
            
        Returns:
            Dictionary with date keys and corresponding dates
        """
        if not self.startdatum:
            today = date.today()
            return {
                'current': today,
                'tomorrow': today + timedelta(days=1),
                'day_after_tomorrow': today + timedelta(days=2)
            }
        
        try:
            start_date = datetime.strptime(self.startdatum, "%Y-%m-%d").date()
            current_date = date.today()
            days_since_start = (current_date - start_date).days
            
            if days_since_start < 0:
                today = current_date
                return {
                    'current': today,
                    'tomorrow': today + timedelta(days=1),
                    'day_after_tomorrow': today + timedelta(days=2)
                }
            
            # Calculate dates based on report type
            if report_type == "morning":
                current_day = start_date + timedelta(days=days_since_start)
                tomorrow = start_date + timedelta(days=days_since_start + 1)
                return {
                    'current': current_day,
                    'tomorrow': tomorrow,
                    'thunderstorm_plus1': tomorrow  # Gewitter +1 = morgen
                }
            elif report_type == "evening":
                tomorrow = start_date + timedelta(days=days_since_start + 1)
                day_after_tomorrow = start_date + timedelta(days=days_since_start + 2)
                return {
                    'tomorrow': tomorrow,
                    'day_after_tomorrow': day_after_tomorrow,
                    'thunderstorm_plus1': day_after_tomorrow,  # Gewitter +1 = übermorgen
                    'night_temp': start_date + timedelta(days=days_since_start)  # Heute für Nacht-Temp
                }
            elif report_type == "update":
                current_day = start_date + timedelta(days=days_since_start)
                tomorrow = start_date + timedelta(days=days_since_start + 1)
                return {
                    'current': current_day,
                    'tomorrow': tomorrow,
                    'thunderstorm_plus1': tomorrow  # Gewitter +1 = morgen
                }
            else:  # dynamic
                current_day = start_date + timedelta(days=days_since_start)
                tomorrow = start_date + timedelta(days=days_since_start + 1)
                return {
                    'current': current_day,
                    'tomorrow': tomorrow,
                    'thunderstorm_plus1': tomorrow
                }
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating target dates: {e}")
            today = date.today()
            return {
                'current': today,
                'tomorrow': today + timedelta(days=1),
                'day_after_tomorrow': today + timedelta(days=2)
            } 

    def get_stage_positions(self, report_type: str) -> List[Tuple[str, float, float]]:
        """
        Get all positions for the current stage.
        
        Args:
            report_type: Type of report ('morning', 'evening', 'dynamic', 'update')
            
        Returns:
            List of tuples (location_name, latitude, longitude)
        """
        if not get_current_stage or not get_stage_coordinates:
            logger.error("Stage logic functions not available")
            return []
        
        try:
            # Get current stage for morning/dynamic/update, next stage for evening
            if report_type == "evening":
                # For evening reports, we need the next stage
                try:
                    from src.position.etappenlogik import get_next_stage
                    stage = get_next_stage(self.config)
                except ImportError:
                    try:
                        from position.etappenlogik import get_next_stage
                        stage = get_next_stage(self.config)
                    except ImportError:
                        logger.error("get_next_stage function not available")
                        stage = None
            else:
                stage = get_current_stage(self.config)
            
            if not stage:
                logger.warning("No stage available for debug output")
                return []
            
            coordinates = get_stage_coordinates(stage)
            stage_name = stage.get("name", "Unknown Stage")
            
            # Create location names for each point
            positions = []
            for i, (lat, lon) in enumerate(coordinates):
                location_name = f"{stage_name}_P{i+1}"
                positions.append((location_name, lat, lon))
            
            return positions
            
        except Exception as e:
            logger.error(f"Error getting stage positions: {e}")
            return []
    
    def fetch_meteofrance_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch comprehensive weather data from MeteoFrance API.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary containing all available weather data
        """
        if not self.client:
            logger.error("MeteoFrance client not available")
            return {}
        
        try:
            # Fetch forecast data
            forecast = self.client.get_forecast(latitude, longitude)
            
            if not forecast.forecast or len(forecast.forecast) == 0:
                logger.warning(f"No forecast data received for {latitude}, {longitude}")
                return {}
            
            # Extract different data types
            result = {
                'forecast': self._extract_forecast_data(forecast.forecast),
                'daily_forecast': self._extract_daily_forecast_data(forecast.daily_forecast) if hasattr(forecast, 'daily_forecast') else [],
                'probability_forecast': self._extract_probability_forecast_data(forecast.probability_forecast) if hasattr(forecast, 'probability_forecast') else [],
                'rain_data': self._extract_rain_data(forecast.forecast),
                'alerts': self._extract_alerts_data(latitude, longitude)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching MeteoFrance data: {e}")
            return {}
    
    def _extract_forecast_data(self, forecast_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract hourly forecast data."""
        extracted_data = []
        
        for entry in forecast_entries:
            try:
                # Extract temperature (korrekte API-Struktur)
                temp_data = entry.get('T', {})
                temperature = temp_data.get('value', 0.0) if isinstance(temp_data, dict) else 0.0
                
                # Extract wind data (korrekte API-Struktur)
                wind_data = entry.get('wind', {})
                wind_speed = wind_data.get('speed', 0.0) if isinstance(wind_data, dict) else 0.0
                gusts = wind_data.get('gust', 0.0) if isinstance(wind_data, dict) else 0.0
                
                # Extract rain data (korrekte API-Struktur)
                rain_data = entry.get('rain', {})
                rain_amount = rain_data.get('1h', 0.0) if isinstance(rain_data, dict) else 0.0
                
                # Extract weather condition (korrekte API-Struktur)
                weather_data = entry.get('weather', {})
                condition = weather_data.get('desc', 'Unknown') if isinstance(weather_data, dict) else 'Unknown'
                icon = weather_data.get('icon', 'unknown') if isinstance(weather_data, dict) else 'unknown'
                
                # Extract thunderstorm probability
                thunderstorm = False
                if condition.lower() in ['thunderstorm', 'orages', 'risque d\'orages']:
                    thunderstorm = True
                
                # Extract and convert timestamp properly (korrekte API-Struktur)
                timestamp = entry.get('dt', '')  # 'dt' statt 'datetime'!
                time_str = self._convert_timestamp_to_readable(timestamp)
                
                extracted_data.append({
                    'time': time_str,
                    'dt': timestamp,  # Keep original timestamp for date filtering
                    'temperature': temperature,
                    'wind_speed': wind_speed,
                    'gusts': gusts,
                    'rain': rain_amount,
                    'icon': icon,
                    'condition': condition,
                    'thunderstorm': thunderstorm
                })
                
            except Exception as e:
                logger.warning(f"Error extracting forecast entry: {e}")
                continue
        
        return extracted_data
    
    def _extract_daily_forecast_data(self, daily_forecast: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract daily forecast data."""
        extracted_data = []
        
        # Handle case where daily_forecast might not be a list
        if not isinstance(daily_forecast, list):
            logger.warning(f"Daily forecast is not a list: {type(daily_forecast)}")
            return extracted_data
        
        for entry in daily_forecast:
            try:
                # Handle case where entry might be a float or other non-dict type
                if not isinstance(entry, dict):
                    logger.warning(f"Skipping non-dict daily forecast entry: {type(entry)}")
                    continue
                
                # Safely extract nested values with proper fallbacks (korrekte API-Struktur)
                temp_min = 0.0
                temp_max = 0.0
                rain_sum = 0.0
                wind_gust_max = 0.0
                uv_index = 0
                
                # Extract temperature data (korrekte API-Struktur)
                temp_data = entry.get('T', {})
                if isinstance(temp_data, dict):
                    temp_min = temp_data.get('min', 0.0)  # Direkt min/max, nicht nested!
                    temp_max = temp_data.get('max', 0.0)
                
                # Extract rain data (korrekte API-Struktur: 'precipitation' statt 'rain'!)
                precipitation_data = entry.get('precipitation', {})
                if isinstance(precipitation_data, dict):
                    rain_sum = precipitation_data.get('24h', 0.0)
                
                # Extract wind data (falls vorhanden)
                wind_data = entry.get('wind', {})
                if isinstance(wind_data, dict):
                    gust_data = wind_data.get('gust', {})
                    if isinstance(gust_data, dict):
                        wind_gust_max = gust_data.get('max', 0.0)
                
                # Extract UV data (korrekte API-Struktur: direkt 'uv')
                uv_index = entry.get('uv', 0)
                
                # Convert timestamp to readable date format
                timestamp = entry.get('dt', '')
                day_str = self._convert_timestamp_to_readable(timestamp, format_str="%Y-%m-%d") or 'Unknown'
                
                extracted_data.append({
                    'day': day_str,
                    'dt': timestamp,  # Keep original timestamp for date filtering
                    'temp_min': temp_min,
                    'temp_max': temp_max,
                    'rain_sum': rain_sum,
                    'wind_gust_max': wind_gust_max,
                    'uv_index': uv_index
                })
            except Exception as e:
                logger.warning(f"Error extracting daily forecast entry: {e}")
                continue
        
        return extracted_data
    
    def _extract_probability_forecast_data(self, probability_forecast: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract probability forecast data."""
        extracted_data = []
        
        for entry in probability_forecast:
            try:
                # Extract and convert timestamp properly
                timestamp = entry.get('dt', '')
                time_str = self._convert_timestamp_to_readable(timestamp)
                
                # Extract probability data (korrekte API-Struktur)
                rain_3h = entry.get('rain', {}).get('3h', '-') if isinstance(entry.get('rain'), dict) else '-'
                snow_3h = entry.get('snow', {}).get('3h', '-') if isinstance(entry.get('snow'), dict) else '-'
                freezing_3h = entry.get('freezing', 0)  # Direkt 'freezing', nicht 'freezing_rain'
                
                extracted_data.append({
                    'time': time_str,
                    'dt': timestamp,  # Keep original timestamp for date filtering
                    'rain_3h': rain_3h,
                    'snow_3h': snow_3h,
                    'freezing_rain_3h': freezing_3h,
                    'storm_3h': '-'  # Nicht in der API verfügbar
                })
            except Exception as e:
                logger.warning(f"Error extracting probability forecast entry: {e}")
                continue
        
        return extracted_data
    
    def _extract_rain_data(self, forecast_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract minute-by-minute rain data."""
        extracted_data = []
        
        for entry in forecast_entries:
            try:
                # Extract and convert timestamp properly (korrekte API-Struktur)
                timestamp = entry.get('dt', '')  # 'dt' statt 'datetime'!
                time_str = self._convert_timestamp_to_readable(timestamp)
                
                rain_data = entry.get('rain', {})
                rain_mm = rain_data.get('1h', 0.0) if isinstance(rain_data, dict) else 0.0
                
                # Determine rain intensity
                if rain_mm == 0.0:
                    rain_intensity = '-'
                elif rain_mm < 0.5:
                    rain_intensity = 'leicht'
                elif rain_mm < 2.0:
                    rain_intensity = 'mäßig'
                else:
                    rain_intensity = 'stark'
                
                extracted_data.append({
                    'time': time_str,
                    'dt': timestamp,  # Keep original timestamp for date filtering
                    'rain_mm': rain_mm,
                    'rain_intensity': rain_intensity
                })
                
            except Exception as e:
                logger.warning(f"Error extracting rain data entry: {e}")
                continue
        
        return extracted_data
    
    def _extract_alerts_data(self, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """Extract weather alerts data."""
        if not get_alerts:
            return []
        
        try:
            alerts = get_alerts(latitude, longitude)
            extracted_alerts = []
            
            for alert in alerts:
                # Get proper level and color
                level = getattr(alert, 'level', 0)
                color = self._get_alert_color(level)
                level_desc = self._get_alert_level_description(level)
                
                # Extract timestamps properly
                begin_time = 'Unknown'
                end_time = 'Unknown'
                
                if hasattr(alert, 'begin') and alert.begin is not None:
                    try:
                        if isinstance(alert.begin, str):
                            begin_time = self._convert_timestamp_to_readable(alert.begin, "%Y-%m-%d %H:%M")
                        elif isinstance(alert.begin, datetime):
                            begin_time = alert.begin.strftime('%Y-%m-%d %H:%M')
                        else:
                            begin_time = 'Unknown'
                    except Exception as e:
                        logger.warning(f"Error formatting alert.begin: {e}")
                        begin_time = 'Unknown'
                
                if hasattr(alert, 'end') and alert.end is not None:
                    try:
                        if isinstance(alert.end, str):
                            end_time = self._convert_timestamp_to_readable(alert.end, "%Y-%m-%d %H:%M")
                        elif isinstance(alert.end, datetime):
                            end_time = alert.end.strftime('%Y-%m-%d %H:%M')
                        else:
                            end_time = 'Unknown'
                    except Exception as e:
                        logger.warning(f"Error formatting alert.end: {e}")
                        end_time = 'Unknown'
                
                extracted_alerts.append({
                    'phenomenon': getattr(alert, 'phenomenon', 'Unknown'),
                    'level': level,
                    'level_desc': level_desc,
                    'color': color,
                    'begin': begin_time,
                    'end': end_time,
                    'description': getattr(alert, 'description', 'Keine Beschreibung')
                })
            
            return extracted_alerts
            
        except Exception as e:
            logger.warning(f"Error extracting alerts data: {e}")
            return []
    
    def _convert_timestamp_to_readable(self, timestamp, format_str: str = "%H:%M") -> str:
        """
        Convert timestamp to readable time format.
        
        Args:
            timestamp: Timestamp (string, int, or datetime object)
            format_str: Format string for datetime.strftime (default: "%H:%M")
            
        Returns:
            Readable time string in specified format
        """
        if not timestamp:
            return 'Unknown'
        
        try:
            # Handle integer timestamps (UNIX timestamps)
            if isinstance(timestamp, int):
                if timestamp > 1000000000:  # Likely UNIX timestamp
                    dt = datetime.fromtimestamp(timestamp)
                    return dt.strftime(format_str)
                else:
                    return str(timestamp)
            
            # Convert to string if needed
            timestamp_str = str(timestamp)
            
            # Try ISO format first
            if 'T' in timestamp_str or '-' in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                return dt.strftime(format_str)
            
            # Try UNIX timestamp as string
            if timestamp_str.isdigit():
                timestamp_int = int(timestamp_str)
                if timestamp_int > 1000000000:  # Likely UNIX timestamp
                    dt = datetime.fromtimestamp(timestamp_int)
                    return dt.strftime(format_str)
            
            # If all else fails, return as is
            return timestamp_str
            
        except (ValueError, OSError, TypeError) as e:
            logger.warning(f"Failed to convert timestamp '{timestamp}': {e}")
            return 'Unknown'
    
    def _get_alert_color(self, level: int) -> str:
        """Convert alert level to color."""
        color_map = {
            1: 'grün',
            2: 'gelb', 
            3: 'orange',
            4: 'rot'
        }
        return color_map.get(level, 'unbekannt')
    
    def _get_alert_level_description(self, level: int) -> str:
        """Convert alert level to description."""
        level_map = {
            1: 'grün',
            2: 'gelb',
            3: 'orange', 
            4: 'rot'
        }
        return level_map.get(level, 'unbekannt')
    
    def _count_valid_invalid_entries(self, data: List[Dict[str, Any]], time_field: str = 'time') -> tuple:
        """
        Count valid and invalid entries in data.
        
        Args:
            data: List of data entries
            time_field: Field name to check for validity
            
        Returns:
            Tuple of (valid_count, invalid_count)
        """
        valid_count = 0
        invalid_count = 0
        
        for entry in data:
            time_value = entry.get(time_field, '')
            if time_value and time_value != 'Unknown' and time_value != '-':
                valid_count += 1
            else:
                invalid_count += 1
        
        return valid_count, invalid_count 

    def generate_debug_output(self, report_type: str) -> str:
        """
        Generate complete debug output for all stage positions.
        
        Args:
            report_type: Type of report ('morning', 'evening', 'dynamic', 'update')
            
        Returns:
            Formatted debug output string
        """
        if not self.should_generate_debug():
            return ""
        
        try:
            target_date = self.get_target_date(report_type)
            positions = self.get_stage_positions(report_type)
            
            if not positions:
                return "\n--- DEBUG INFO ---\nNo stage positions available for debug output\n"
            
            debug_lines = []
            debug_lines.append("# DEBUG DATENEXPORT – Rohdatenübersicht MeteoFrance")
            debug_lines.append("")
            debug_lines.append(f"Ziel: Vollständige und nachvollziehbare Darstellung der verwendeten Rohdaten aus der MeteoFrance API zur Risikobewertung am {target_date.strftime('%Y-%m-%d')}")
            debug_lines.append("")
            
            # Add report type specific information
            target_dates = self.get_target_dates_for_report_type(report_type)
            debug_lines.append(f"**Berichtstyp:** {report_type}")
            debug_lines.append("")
            
            # Show relevant dates for this report type
            if report_type == "morning":
                debug_lines.append("**Relevante Daten:**")
                debug_lines.append(f"- Hauptdaten: {target_dates.get('current', target_date).strftime('%Y-%m-%d')} (aktueller Tag)")
                debug_lines.append(f"- Gewitter +1: {target_dates.get('tomorrow', target_date).strftime('%Y-%m-%d')} (morgen)")
                debug_lines.append("")
            elif report_type == "evening":
                debug_lines.append("**Relevante Daten:**")
                debug_lines.append(f"- Hauptdaten: {target_dates.get('tomorrow', target_date).strftime('%Y-%m-%d')} (morgen)")
                debug_lines.append(f"- Gewitter +1: {target_dates.get('day_after_tomorrow', target_date).strftime('%Y-%m-%d')} (übermorgen)")
                debug_lines.append(f"- Nacht-Temperatur: {target_dates.get('night_temp', target_date).strftime('%Y-%m-%d')} (heute)")
                debug_lines.append("")
            elif report_type == "update":
                debug_lines.append("**Relevante Daten:**")
                debug_lines.append(f"- Hauptdaten: {target_dates.get('current', target_date).strftime('%Y-%m-%d')} (aktueller Tag)")
                debug_lines.append(f"- Gewitter +1: {target_dates.get('tomorrow', target_date).strftime('%Y-%m-%d')} (morgen)")
                debug_lines.append("")
            elif report_type == "dynamic":
                debug_lines.append("**Relevante Daten:**")
                debug_lines.append(f"- Hauptdaten: {target_dates.get('current', target_date).strftime('%Y-%m-%d')} (aktueller Tag)")
                debug_lines.append(f"- Gewitter +1: {target_dates.get('tomorrow', target_date).strftime('%Y-%m-%d')} (morgen)")
                debug_lines.append("")
            
            debug_lines.append("**HINWEIS:** Die folgenden Daten zeigen nur die für den Berichtstyp relevanten Zeitpunkte (04:00-22:00).")
            debug_lines.append("")
            
            # Determine data sources based on report type
            data_sources = self._get_data_sources_for_report_type(report_type)
            
            # Generate output by data source (not by position)
            for data_source in data_sources:
                debug_lines.extend(self._generate_data_source_section(
                    data_source, positions, target_date, report_type
                ))
                debug_lines.append("")
            
            debug_output = "\n".join(debug_lines)
            
            # Save to file if enabled
            if self.debug_config.get("save_debug_files", True):
                self._save_debug_file(debug_output, target_date, report_type)
            
            return debug_output
            
        except Exception as e:
            logger.error(f"Error generating debug output: {e}")
            return f"\n--- DEBUG INFO ---\nError generating debug output: {str(e)}\n"
    
    def _get_data_sources_for_report_type(self, report_type: str) -> List[str]:
        """
        Get data sources based on report type.
        
        Args:
            report_type: Type of report ('morning', 'evening', 'dynamic', 'update')
            
        Returns:
            List of data source names in priority order
        """
        if report_type == 'dynamic':
            # For dynamic reports, prioritize rain data
            return ['rain', 'forecast', 'daily_forecast', 'probability_forecast', 'alerts']
        else:
            # For morning/evening/update reports, standard order
            return ['forecast', 'daily_forecast', 'probability_forecast', 'rain', 'alerts']
    
    def _generate_data_source_section(self, data_source: str, positions: List[Tuple[str, float, float]], 
                                    target_date: date, report_type: str) -> List[str]:
        """
        Generate debug output for a specific data source across all positions.
        
        Args:
            data_source: Name of the data source
            positions: List of (location_name, latitude, longitude) tuples
            target_date: Target date for the data
            report_type: Type of report
            
        Returns:
            List of debug output lines
        """
        debug_lines = []
        
        # Add data source header with strong visual separation
        debug_lines.append("---")
        debug_lines.append(f"## DATENQUELLE: meteo_france / {data_source.upper()}")
        debug_lines.append(f"Datum: {target_date.strftime('%Y-%m-%d')}")
        debug_lines.append(f"Berichtstyp: {report_type}")
        debug_lines.append("---")
        debug_lines.append("")
        
        # Collect all data for aggregation
        all_position_data = []
        
        # Process each position for this data source
        for location_name, latitude, longitude in positions:
            position_data = self._generate_position_data_for_source(
                data_source, location_name, latitude, longitude, target_date, report_type
            )
            debug_lines.extend(position_data)
            debug_lines.append("")
            
            # Store data for aggregation
            all_position_data.append({
                'location_name': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'data': self._get_raw_data_for_source(data_source, latitude, longitude, target_date, report_type)
            })
        
        # Aggregated data section removed - no added value
        
        return debug_lines
    
    def _generate_position_data_for_source(self, data_source: str, location_name: str, 
                                         latitude: float, longitude: float, target_date: date, report_type: str) -> List[str]:
        """
        Generate debug output for a specific position and data source.
        
        Args:
            data_source: Name of the data source
            location_name: Name of the location
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            target_date: Target date for the data
            report_type: Type of report
            
        Returns:
            List of debug output lines
        """
        debug_lines = []
        
        try:
            # Fetch data for this position
            weather_data = self.fetch_meteofrance_data(latitude, longitude)
            
            if not weather_data:
                debug_lines.append(f"### Position: {location_name} ({latitude}, {longitude})")
                debug_lines.append("**FEHLER:** Keine Daten verfügbar - API-Fehler oder fehlende Verbindung")
                debug_lines.append("")
                return debug_lines
            
            # Generate position header
            debug_lines.append(f"### Position: {location_name} ({latitude}, {longitude})")
            debug_lines.append("")
            
            # Generate appropriate table based on data source
            if data_source == 'forecast' and weather_data.get('forecast'):
                debug_lines.extend(self._generate_forecast_table_for_position(
                    weather_data['forecast'], report_type
                ))
            elif data_source == 'daily_forecast' and weather_data.get('daily_forecast'):
                try:
                    debug_lines.extend(self._generate_daily_forecast_table_for_position(
                        weather_data['daily_forecast'], report_type
                    ))
                except Exception as e:
                    logger.error(f"Error generating daily forecast table for {location_name}: {e}")
                    debug_lines.append("**FEHLER:** " + str(e))
            elif data_source == 'probability_forecast' and weather_data.get('probability_forecast'):
                try:
                    debug_lines.extend(self._generate_probability_forecast_table_for_position(
                        weather_data['probability_forecast'], report_type
                    ))
                except Exception as e:
                    logger.error(f"Error generating probability forecast table for {location_name}: {e}")
                    debug_lines.append("**FEHLER:** " + str(e))
            elif data_source == 'rain' and weather_data.get('rain_data'):
                debug_lines.extend(self._generate_rain_data_table_for_position(
                    weather_data['rain_data'], report_type
                ))
            elif data_source == 'alerts' and weather_data.get('alerts'):
                debug_lines.extend(self._generate_alerts_table_for_position(
                    weather_data['alerts'], report_type
                ))
            else:
                debug_lines.append("**Keine Daten verfügbar für diese Datenquelle**")
            
        except Exception as e:
            logger.error(f"Error generating position data for {location_name}: {e}")
            debug_lines.append(f"### Position: {location_name} ({latitude}, {longitude})")
            debug_lines.append("**FEHLER:** " + str(e))
        
        return debug_lines
    
    def _filter_forecast_data_by_report_type(self, forecast_data: List[Dict[str, Any]], report_type: str) -> List[Dict[str, Any]]:
        """
        Filter forecast data based on report type and relevant time windows.
        
        Args:
            forecast_data: List of forecast entries
            report_type: Type of report ('morning', 'evening', 'dynamic', 'update')
            
        Returns:
            Filtered list of forecast entries
        """
        if not forecast_data:
            return []
        
        # Get target dates for this report type
        target_dates = self.get_target_dates_for_report_type(report_type)
        
        filtered_data = []
        
        for entry in forecast_data:
            time_str = entry.get('time', 'Unknown')
            if time_str == 'Unknown':
                continue
            
            try:
                # Parse time string (HH:MM format)
                hour = int(time_str.split(':')[0])
                
                # Get the date from the entry's timestamp
                timestamp = entry.get('dt', '')
                if not timestamp:
                    continue
                
                # Convert timestamp to date
                entry_date = self._convert_timestamp_to_date(timestamp)
                if not entry_date:
                    continue
                
                # Check if this entry is for the relevant date(s)
                is_relevant_date = False
                if report_type == 'morning':
                    # Morning report: current day only
                    is_relevant_date = entry_date == target_dates.get('current')
                elif report_type == 'evening':
                    # Evening report: tomorrow and day after tomorrow
                    is_relevant_date = (entry_date == target_dates.get('tomorrow') or 
                                      entry_date == target_dates.get('day_after_tomorrow'))
                elif report_type == 'update':
                    # Update report: current day only
                    is_relevant_date = entry_date == target_dates.get('current')
                elif report_type == 'dynamic':
                    # Dynamic report: current day only
                    is_relevant_date = entry_date == target_dates.get('current')
                else:
                    # Default: current day only
                    is_relevant_date = entry_date == target_dates.get('current')
                
                # Apply time window filtering based on report type
                if is_relevant_date:
                    if report_type == 'morning':
                        # Morning report: 04:00-22:00 for current day
                        if 4 <= hour <= 22:
                            filtered_data.append(entry)
                    elif report_type == 'evening':
                        # Evening report: 04:00-22:00 for tomorrow and day after tomorrow
                        if 4 <= hour <= 22:
                            filtered_data.append(entry)
                    elif report_type == 'update':
                        # Update report: 04:00-22:00 for current day
                        if 4 <= hour <= 22:
                            filtered_data.append(entry)
                    elif report_type == 'dynamic':
                        # Dynamic report: 04:00-22:00 for current day
                        if 4 <= hour <= 22:
                            filtered_data.append(entry)
                    else:
                        # Default: include all data for relevant date
                        filtered_data.append(entry)
                    
            except (ValueError, IndexError):
                # If time parsing fails, skip the entry
                continue
        
        return filtered_data
    
    def _convert_timestamp_to_date(self, timestamp) -> Optional[date]:
        """
        Convert timestamp to date object.
        
        Args:
            timestamp: Timestamp from API
            
        Returns:
            Date object or None if conversion fails
        """
        try:
            if isinstance(timestamp, str):
                # Try parsing as ISO format
                if 'T' in timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    # Try parsing as Unix timestamp
                    dt = datetime.fromtimestamp(float(timestamp))
            elif isinstance(timestamp, (int, float)):
                # Unix timestamp
                dt = datetime.fromtimestamp(timestamp)
            else:
                return None
            
            return dt.date()
            
        except (ValueError, TypeError, OSError):
            logger.warning(f"Failed to convert timestamp to date: {timestamp}")
            return None
    
    def _get_time_window_description(self, report_type: str) -> str:
        """
        Get description of relevant time window for report type.
        
        Args:
            report_type: Type of report
            
        Returns:
            Time window description
        """
        if report_type == 'morning':
            return "04:00-22:00 (aktueller Tag)"
        elif report_type == 'evening':
            return "04:00-22:00 (morgen und übermorgen)"
        elif report_type == 'update':
            return "04:00-22:00 (aktueller Tag)"
        elif report_type == 'dynamic':
            return "04:00-22:00 (aktueller Tag)"
        else:
            return "04:00-22:00 (aktueller Tag)"
    
    def _generate_forecast_table_for_position(self, forecast_data: List[Dict[str, Any]], report_type: str = 'morning') -> List[str]:
        """Generate forecast table for a single position (relevant entries only)."""
        lines = []
        
        # Filter data based on report type and time window
        filtered_data = self._filter_forecast_data_by_report_type(forecast_data, report_type)
        
        # Count valid and invalid entries
        valid_count, invalid_count = self._count_valid_invalid_entries(filtered_data)
        total_count = len(filtered_data)
        original_count = len(forecast_data)
        
        lines.append(f"**Einträge:** {total_count} von {original_count} (gültig: {valid_count}, ungültig: {invalid_count})")
        lines.append(f"**Zeitraum:** {self._get_time_window_description(report_type)}")
        lines.append("")
        
        # Only show table if we have data
        if not filtered_data:
            lines.append("**Keine relevanten Daten verfügbar**")
            lines.append("")
            return lines
        
        # Table header
        lines.append("| Uhrzeit | temperature | wind_speed | gusts | rain | icon | condition     | thunderstorm |")
        lines.append("|---------|-------------|------------|-------|------|------|----------------|--------------|")
        
        # Table rows (show ALL entries in relevant time window)
        for entry in filtered_data:
            time_str = entry.get('time', 'Unknown')
            temp = entry.get('temperature', 0.0)
            wind_speed = entry.get('wind_speed', 0.0)
            gusts = entry.get('gusts', 0.0)
            rain = entry.get('rain', 0.0)
            icon = entry.get('icon', 'unknown')
            condition = entry.get('condition', 'Unknown')
            thunderstorm = entry.get('thunderstorm', False)
            
            lines.append(f"| {time_str}   | {temp:.1f} °C      | {wind_speed:.0f} km/h     | {gusts:.0f} km/h| {rain:.1f}mm| {icon} | {condition:<14} | {str(thunderstorm).lower():<12} |")
        
        lines.append("")
        return lines
    

    
    def _generate_daily_forecast_table_for_position(self, daily_data: List[Dict[str, Any]], report_type: str = 'morning') -> List[str]:
        """Generate daily forecast table for a single position (relevant days only)."""
        lines = []
        
        # Filter data for relevant days based on report type
        target_dates = self.get_target_dates_for_report_type(report_type)
        filtered_data = []
        
        for entry in daily_data:
            try:
                day_str = entry.get('day', '')
                if not day_str or day_str == 'Unknown':
                    continue
                
                # Parse the date from the day string
                entry_date = datetime.strptime(day_str, "%Y-%m-%d").date()
                
                # Check if this day is relevant for the report type
                is_relevant = False
                if report_type == 'morning':
                    # Morning report: current day and tomorrow
                    is_relevant = (entry_date == target_dates.get('current') or 
                                 entry_date == target_dates.get('tomorrow'))
                elif report_type == 'evening':
                    # Evening report: tomorrow and day after tomorrow
                    is_relevant = (entry_date == target_dates.get('tomorrow') or 
                                 entry_date == target_dates.get('day_after_tomorrow'))
                else:
                    # Other reports: current day and tomorrow
                    is_relevant = (entry_date == target_dates.get('current') or 
                                 entry_date == target_dates.get('tomorrow'))
                
                if is_relevant:
                    filtered_data.append(entry)
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing date from daily forecast entry: {e}")
                continue
        
        # Count valid and invalid entries
        valid_count, invalid_count = self._count_valid_invalid_entries(filtered_data, 'day')
        total_count = len(filtered_data)
        original_count = len(daily_data)
        
        lines.append(f"**Einträge:** {total_count} von {original_count} (gültig: {valid_count}, ungültig: {invalid_count})")
        lines.append("")
        
        # Only show table if we have data
        if not filtered_data:
            lines.append("**Keine relevanten Daten verfügbar**")
            lines.append("")
            return lines
        
        # Table header
        lines.append("| Tag        | temp_min | temp_max | rain_sum | wind_gust_max | uv_index |")
        lines.append("|------------|----------|----------|----------|----------------|----------|")
        
        # Table rows (show filtered entries only)
        for entry in filtered_data:
            try:
                day = entry.get('day', 'Unknown') or 'Unknown'
                temp_min = entry.get('temp_min', 0.0) or 0.0
                temp_max = entry.get('temp_max', 0.0) or 0.0
                rain_sum = entry.get('rain_sum', 0.0) or 0.0
                wind_gust_max = entry.get('wind_gust_max', 0.0) or 0.0
                uv_index = entry.get('uv_index', 0) or 0
                
                lines.append(f"| {day} | {temp_min:.1f} °C   | {temp_max:.1f} °C  | {rain_sum:.1f} mm   | {wind_gust_max:.0f} km/h        | {uv_index}        |")
            except Exception as e:
                logger.warning(f"Error formatting daily forecast row: {e}")
                lines.append(f"| Unknown | 0.0 °C   | 0.0 °C  | 0.0 mm   | 0 km/h        | 0        |")
        
        lines.append("")
        return lines
    
    def _generate_probability_forecast_table_for_position(self, prob_data: List[Dict[str, Any]], report_type: str = 'morning') -> List[str]:
        """Generate probability forecast table for a single position (relevant day only)."""
        lines = []
        
        # Filter data for relevant day based on report type
        target_dates = self.get_target_dates_for_report_type(report_type)
        filtered_data = []
        
        for entry in prob_data:
            try:
                timestamp = entry.get('dt', '')
                if not timestamp:
                    continue
                
                # Convert timestamp to date
                entry_date = self._convert_timestamp_to_date(timestamp)
                if not entry_date:
                    continue
                
                # Check if this entry is for the relevant date(s)
                is_relevant = False
                if report_type == 'morning':
                    # Morning report: current day only
                    is_relevant = entry_date == target_dates.get('current')
                elif report_type == 'evening':
                    # Evening report: tomorrow and day after tomorrow
                    is_relevant = (entry_date == target_dates.get('tomorrow') or 
                                 entry_date == target_dates.get('day_after_tomorrow'))
                else:
                    # Other reports: current day only
                    is_relevant = entry_date == target_dates.get('current')
                
                if is_relevant:
                    filtered_data.append(entry)
                    
            except Exception as e:
                logger.warning(f"Error filtering probability forecast entry: {e}")
                continue
        
        # Count valid and invalid entries
        valid_count, invalid_count = self._count_valid_invalid_entries(filtered_data)
        total_count = len(filtered_data)
        original_count = len(prob_data)
        
        lines.append(f"**Einträge:** {total_count} von {original_count} (gültig: {valid_count}, ungültig: {invalid_count})")
        lines.append("")
        
        # Only show table if we have data
        if not filtered_data:
            lines.append("**Keine relevanten Daten verfügbar**")
            lines.append("")
            return lines
        
        # Table header
        lines.append("| Uhrzeit | rain_3h | snow_3h | freezing_rain_3h | storm_3h |")
        lines.append("|---------|---------|---------|------------------|----------|")
        
        # Table rows (show filtered entries only)
        for entry in filtered_data:
            time_str = entry.get('time', 'Unknown')
            rain_3h = entry.get('rain_3h', '-')
            snow_3h = entry.get('snow_3h', '-')
            freezing_rain_3h = entry.get('freezing_rain_3h', '-')
            storm_3h = entry.get('storm_3h', '-')
            
            lines.append(f"| {time_str}   | {rain_3h}       | {snow_3h}       | {freezing_rain_3h}                | {storm_3h}        |")
        
        lines.append("")
        return lines
    
    def _generate_rain_data_table_for_position(self, rain_data: List[Dict[str, Any]], report_type: str = 'morning') -> List[str]:
        """Generate rain data table for a single position (relevant day only)."""
        lines = []
        
        # Filter data for relevant day based on report type
        target_dates = self.get_target_dates_for_report_type(report_type)
        filtered_data = []
        
        for entry in rain_data:
            try:
                timestamp = entry.get('dt', '')
                if not timestamp:
                    continue
                
                # Convert timestamp to date
                entry_date = self._convert_timestamp_to_date(timestamp)
                if not entry_date:
                    continue
                
                # Check if this entry is for the relevant date(s)
                is_relevant = False
                if report_type == 'morning':
                    # Morning report: current day only
                    is_relevant = entry_date == target_dates.get('current')
                elif report_type == 'evening':
                    # Evening report: tomorrow and day after tomorrow
                    is_relevant = (entry_date == target_dates.get('tomorrow') or 
                                 entry_date == target_dates.get('day_after_tomorrow'))
                else:
                    # Other reports: current day only
                    is_relevant = entry_date == target_dates.get('current')
                
                if is_relevant:
                    filtered_data.append(entry)
                    
            except Exception as e:
                logger.warning(f"Error filtering rain data entry: {e}")
                continue
        
        # Count valid and invalid entries
        valid_count, invalid_count = self._count_valid_invalid_entries(filtered_data)
        total_count = len(filtered_data)
        original_count = len(rain_data)
        
        lines.append(f"**Einträge:** {total_count} von {original_count} (gültig: {valid_count}, ungültig: {invalid_count})")
        lines.append("")
        
        # Only show table if we have data
        if not filtered_data:
            lines.append("**Keine relevanten Daten verfügbar**")
            lines.append("")
            return lines
        
        # Table header
        lines.append("| Uhrzeit | rain_mm | rain_intensity |")
        lines.append("|---------|---------|----------------|")
        
        # Table rows (show filtered entries only)
        for entry in filtered_data:
            time_str = entry.get('time', 'Unknown')
            rain_mm = entry.get('rain_mm', 0.0)
            rain_intensity = entry.get('rain_intensity', '-')
            
            lines.append(f"| {time_str}   | {rain_mm:.1f}mm   | {rain_intensity}              |")
        
        lines.append("")
        return lines
    
    def _generate_alerts_table_for_position(self, alerts_data: List[Dict[str, Any]], report_type: str = 'morning') -> List[str]:
        """Generate alerts table for a single position (all entries)."""
        lines = []
        
        # Count valid and invalid entries
        valid_count, invalid_count = self._count_valid_invalid_entries(alerts_data, 'phenomenon')
        total_count = len(alerts_data)
        
        lines.append(f"**Einträge:** {total_count} (gültig: {valid_count}, ungültig: {invalid_count})")
        lines.append("")
        
        # Only show table if we have data
        if not alerts_data:
            lines.append("**Keine Warnungen verfügbar**")
            lines.append("")
            return lines
        
        # Table header
        lines.append("| Phänomen   | Stufe | Farbe  | Beginn           | Ende             | Beschreibung                      |")
        lines.append("|------------|-------|--------|------------------|------------------|-----------------------------------|")
        
        # Table rows (show ALL entries)
        for alert in alerts_data:
            phenomenon = alert.get('phenomenon', 'Unknown') or 'Unknown'
            level = alert.get('level', 0)
            level_desc = alert.get('level_desc', 'unbekannt') or 'unbekannt'
            color = alert.get('color', 'unbekannt') or 'unbekannt'
            begin = alert.get('begin', 'Unknown') or 'Unknown'
            end = alert.get('end', 'Unknown') or 'Unknown'
            description = alert.get('description', 'Keine Beschreibung') or 'Keine Beschreibung'
            
            lines.append(f"| {phenomenon:<10} | {level_desc:<5} | {color:<6} | {begin:<16} | {end:<16} | {description:<33} |")
        
        lines.append("")
        return lines
    
    def _get_raw_data_for_source(self, data_source: str, latitude: float, longitude: float, 
                                target_date: date, report_type: str) -> List[Dict[str, Any]]:
        """
        Get raw data for a specific source and position for aggregation.
        
        Args:
            data_source: Name of the data source
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            target_date: Target date for the data
            report_type: Type of report
            
        Returns:
            List of raw data entries
        """
        try:
            weather_data = self.fetch_meteofrance_data(latitude, longitude)
            
            if data_source == 'forecast' and weather_data.get('forecast'):
                return self._filter_forecast_data_by_report_type(weather_data['forecast'], report_type)
            elif data_source == 'daily_forecast' and weather_data.get('daily_forecast'):
                return self._filter_daily_forecast_data_by_report_type(weather_data['daily_forecast'], report_type)
            elif data_source == 'probability_forecast' and weather_data.get('probability_forecast'):
                return self._filter_probability_forecast_data_by_report_type(weather_data['probability_forecast'], report_type)
            elif data_source == 'rain' and weather_data.get('rain_data'):
                return self._filter_rain_data_by_report_type(weather_data['rain_data'], report_type)
            else:
                return []
                
        except Exception as e:
            logger.warning(f"Error getting raw data for {data_source}: {e}")
            return []
    
    def _filter_daily_forecast_data_by_report_type(self, daily_data: List[Dict[str, Any]], report_type: str) -> List[Dict[str, Any]]:
        """Filter daily forecast data based on report type."""
        target_dates = self.get_target_dates_for_report_type(report_type)
        filtered_data = []
        
        for entry in daily_data:
            try:
                day_str = entry.get('day', '')
                if not day_str or day_str == 'Unknown':
                    continue
                
                entry_date = datetime.strptime(day_str, "%Y-%m-%d").date()
                
                is_relevant = False
                if report_type == 'morning':
                    is_relevant = (entry_date == target_dates.get('current') or 
                                 entry_date == target_dates.get('tomorrow'))
                elif report_type == 'evening':
                    is_relevant = (entry_date == target_dates.get('tomorrow') or 
                                 entry_date == target_dates.get('day_after_tomorrow'))
                else:
                    is_relevant = (entry_date == target_dates.get('current') or 
                                 entry_date == target_dates.get('tomorrow'))
                
                if is_relevant:
                    filtered_data.append(entry)
                    
            except (ValueError, TypeError):
                continue
        
        return filtered_data
    
    def _filter_probability_forecast_data_by_report_type(self, prob_data: List[Dict[str, Any]], report_type: str) -> List[Dict[str, Any]]:
        """Filter probability forecast data based on report type."""
        target_dates = self.get_target_dates_for_report_type(report_type)
        filtered_data = []
        
        for entry in prob_data:
            try:
                timestamp = entry.get('dt', '')
                if not timestamp:
                    continue
                
                entry_date = self._convert_timestamp_to_date(timestamp)
                if not entry_date:
                    continue
                
                is_relevant = False
                if report_type == 'morning':
                    is_relevant = entry_date == target_dates.get('current')
                elif report_type == 'evening':
                    is_relevant = (entry_date == target_dates.get('tomorrow') or 
                                 entry_date == target_dates.get('day_after_tomorrow'))
                else:
                    is_relevant = entry_date == target_dates.get('current')
                
                if is_relevant:
                    filtered_data.append(entry)
                    
            except Exception:
                continue
        
        return filtered_data
    
    def _filter_rain_data_by_report_type(self, rain_data: List[Dict[str, Any]], report_type: str) -> List[Dict[str, Any]]:
        """Filter rain data based on report type."""
        target_dates = self.get_target_dates_for_report_type(report_type)
        filtered_data = []
        
        for entry in rain_data:
            try:
                timestamp = entry.get('dt', '')
                if not timestamp:
                    continue
                
                entry_date = self._convert_timestamp_to_date(timestamp)
                if not entry_date:
                    continue
                
                is_relevant = False
                if report_type == 'morning':
                    is_relevant = entry_date == target_dates.get('current')
                elif report_type == 'evening':
                    is_relevant = (entry_date == target_dates.get('tomorrow') or 
                                 entry_date == target_dates.get('day_after_tomorrow'))
                else:
                    is_relevant = entry_date == target_dates.get('current')
                
                if is_relevant:
                    filtered_data.append(entry)
                    
            except Exception:
                continue
        
        return filtered_data
    
    def _generate_aggregated_data_section(self, data_source: str, all_position_data: List[Dict[str, Any]], 
                                        target_date: date, report_type: str) -> List[str]:
        """
        Generate aggregated data section showing summary across all positions.
        
        Args:
            data_source: Name of the data source
            all_position_data: List of position data dictionaries
            target_date: Target date for the data
            report_type: Type of report
            
        Returns:
            List of debug output lines for aggregated section
        """
        debug_lines = []
        
        # Add aggregated section header
        debug_lines.append("### 📊 AGGREGIERTE DATEN (alle Positionen)")
        debug_lines.append("")
        
        # Generate appropriate aggregated table based on data source
        if data_source == 'forecast':
            debug_lines.extend(self._generate_aggregated_forecast_table(all_position_data, report_type))
        elif data_source == 'daily_forecast':
            debug_lines.extend(self._generate_aggregated_daily_forecast_table(all_position_data, report_type))
        elif data_source == 'probability_forecast':
            debug_lines.extend(self._generate_aggregated_probability_forecast_table(all_position_data, report_type))
        elif data_source == 'rain':
            debug_lines.extend(self._generate_aggregated_rain_table(all_position_data, report_type))
        elif data_source == 'alerts':
            debug_lines.extend(self._generate_aggregated_alerts_table(all_position_data, report_type))
        
        debug_lines.append("")
        return debug_lines
    
    def _generate_aggregated_forecast_table(self, all_position_data: List[Dict[str, Any]], report_type: str) -> List[str]:
        """Generate aggregated forecast table across all positions."""
        lines = []
        
        # Collect all forecast data
        all_forecast_data = []
        for pos_data in all_position_data:
            location_name = pos_data['location_name']
            for entry in pos_data['data']:
                entry_copy = entry.copy()
                entry_copy['location'] = location_name
                all_forecast_data.append(entry_copy)
        
        if not all_forecast_data:
            lines.append("**Keine aggregierten Daten verfügbar**")
            return lines
        
        # Group by time
        time_groups = {}
        for entry in all_forecast_data:
            time_str = entry.get('time', 'Unknown')
            if time_str not in time_groups:
                time_groups[time_str] = []
            time_groups[time_str].append(entry)
        
        # Table header
        lines.append("| Uhrzeit | Position | temperature | wind_speed | gusts | rain | condition |")
        lines.append("|---------|----------|-------------|------------|-------|------|-----------|")
        
        # Sort times and show all positions for each time
        sorted_times = sorted(time_groups.keys())
        for time_str in sorted_times:
            entries = time_groups[time_str]
            for entry in entries:
                location = entry.get('location', 'Unknown')
                temp = entry.get('temperature', 0.0)
                wind_speed = entry.get('wind_speed', 0.0)
                gusts = entry.get('gusts', 0.0)
                rain = entry.get('rain', 0.0)
                condition = entry.get('condition', 'Unknown')
                
                lines.append(f"| {time_str}   | {location:<9} | {temp:.1f} °C      | {wind_speed:.0f} km/h     | {gusts:.0f} km/h| {rain:.1f}mm| {condition:<9} |")
        
        return lines
    
    def _generate_aggregated_daily_forecast_table(self, all_position_data: List[Dict[str, Any]], report_type: str) -> List[str]:
        """Generate aggregated daily forecast table across all positions."""
        lines = []
        
        # Collect all daily forecast data
        all_daily_data = []
        for pos_data in all_position_data:
            location_name = pos_data['location_name']
            for entry in pos_data['data']:
                entry_copy = entry.copy()
                entry_copy['location'] = location_name
                all_daily_data.append(entry_copy)
        
        if not all_daily_data:
            lines.append("**Keine aggregierten Daten verfügbar**")
            return lines
        
        # Group by day
        day_groups = {}
        for entry in all_daily_data:
            day_str = entry.get('day', 'Unknown')
            if day_str not in day_groups:
                day_groups[day_str] = []
            day_groups[day_str].append(entry)
        
        # Table header
        lines.append("| Tag        | Position | temp_min | temp_max | rain_sum | wind_gust_max | uv_index |")
        lines.append("|------------|----------|----------|----------|----------|----------------|----------|")
        
        # Sort days and show all positions for each day
        sorted_days = sorted(day_groups.keys())
        for day_str in sorted_days:
            entries = day_groups[day_str]
            for entry in entries:
                location = entry.get('location', 'Unknown')
                temp_min = entry.get('temp_min', 0.0)
                temp_max = entry.get('temp_max', 0.0)
                rain_sum = entry.get('rain_sum', 0.0)
                wind_gust_max = entry.get('wind_gust_max', 0.0)
                uv_index = entry.get('uv_index', 0)
                
                lines.append(f"| {day_str} | {location:<9} | {temp_min:.1f} °C   | {temp_max:.1f} °C  | {rain_sum:.1f} mm   | {wind_gust_max:.0f} km/h        | {uv_index}        |")
        
        return lines
    
    def _generate_aggregated_probability_forecast_table(self, all_position_data: List[Dict[str, Any]], report_type: str) -> List[str]:
        """Generate aggregated probability forecast table across all positions."""
        lines = []
        
        # Collect all probability forecast data
        all_prob_data = []
        for pos_data in all_position_data:
            location_name = pos_data['location_name']
            for entry in pos_data['data']:
                entry_copy = entry.copy()
                entry_copy['location'] = location_name
                all_prob_data.append(entry_copy)
        
        if not all_prob_data:
            lines.append("**Keine aggregierten Daten verfügbar**")
            return lines
        
        # Group by time
        time_groups = {}
        for entry in all_prob_data:
            time_str = entry.get('time', 'Unknown')
            if time_str not in time_groups:
                time_groups[time_str] = []
            time_groups[time_str].append(entry)
        
        # Table header
        lines.append("| Uhrzeit | Position | rain_3h | snow_3h | freezing_rain_3h | storm_3h |")
        lines.append("|---------|----------|---------|---------|------------------|----------|")
        
        # Sort times and show all positions for each time
        sorted_times = sorted(time_groups.keys())
        for time_str in sorted_times:
            entries = time_groups[time_str]
            for entry in entries:
                location = entry.get('location', 'Unknown')
                rain_3h = entry.get('rain_3h', '-')
                snow_3h = entry.get('snow_3h', '-')
                freezing_rain_3h = entry.get('freezing_rain_3h', '-')
                storm_3h = entry.get('storm_3h', '-')
                
                lines.append(f"| {time_str}   | {location:<9} | {rain_3h}       | {snow_3h}       | {freezing_rain_3h}                | {storm_3h}        |")
        
        return lines
    
    def _generate_aggregated_rain_table(self, all_position_data: List[Dict[str, Any]], report_type: str) -> List[str]:
        """Generate aggregated rain table across all positions."""
        lines = []
        
        # Collect all rain data
        all_rain_data = []
        for pos_data in all_position_data:
            location_name = pos_data['location_name']
            for entry in pos_data['data']:
                entry_copy = entry.copy()
                entry_copy['location'] = location_name
                all_rain_data.append(entry_copy)
        
        if not all_rain_data:
            lines.append("**Keine aggregierten Daten verfügbar**")
            return lines
        
        # Group by time
        time_groups = {}
        for entry in all_rain_data:
            time_str = entry.get('time', 'Unknown')
            if time_str not in time_groups:
                time_groups[time_str] = []
            time_groups[time_str].append(entry)
        
        # Table header
        lines.append("| Uhrzeit | Position | rain_mm | rain_intensity |")
        lines.append("|---------|----------|---------|----------------|")
        
        # Sort times and show all positions for each time
        sorted_times = sorted(time_groups.keys())
        for time_str in sorted_times:
            entries = time_groups[time_str]
            for entry in entries:
                location = entry.get('location', 'Unknown')
                rain_mm = entry.get('rain_mm', 0.0)
                rain_intensity = entry.get('rain_intensity', '-')
                
                lines.append(f"| {time_str}   | {location:<9} | {rain_mm:.1f}mm   | {rain_intensity}              |")
        
        return lines
    
    def _generate_aggregated_alerts_table(self, all_position_data: List[Dict[str, Any]], report_type: str) -> List[str]:
        """Generate aggregated alerts table across all positions."""
        lines = []
        
        # Collect all alerts data
        all_alerts_data = []
        for pos_data in all_position_data:
            location_name = pos_data['location_name']
            # For alerts, we need to fetch fresh data since it's not in the stored data
            try:
                alerts = self._extract_alerts_data(pos_data['latitude'], pos_data['longitude'])
                for alert in alerts:
                    alert_copy = alert.copy()
                    alert_copy['location'] = location_name
                    all_alerts_data.append(alert_copy)
            except Exception:
                continue
        
        if not all_alerts_data:
            lines.append("**Keine aggregierten Warnungen verfügbar**")
            return lines
        
        # Table header
        lines.append("| Position | Phänomen   | Stufe | Farbe  | Beginn           | Ende             | Beschreibung                      |")
        lines.append("|----------|------------|-------|--------|------------------|------------------|-----------------------------------|")
        
        # Show all alerts with position
        for alert in all_alerts_data:
            location = alert.get('location', 'Unknown')
            phenomenon = alert.get('phenomenon', 'Unknown')
            level = alert.get('level', 0)
            level_desc = alert.get('level_desc', 'unbekannt')
            color = alert.get('color', 'unbekannt')
            begin = alert.get('begin', 'Unknown')
            end = alert.get('end', 'Unknown')
            description = alert.get('description', 'Keine Beschreibung')
            
            lines.append(f"| {location:<9} | {phenomenon:<10} | {level_desc:<5} | {color:<6} | {begin:<16} | {end:<16} | {description:<33} |")
        
        return lines
    
    def _save_debug_file(self, debug_output: str, target_date: date, report_type: str):
        """Save debug output to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weather_debug_{target_date.strftime('%Y-%m-%d')}_{report_type}_{timestamp}.md"
            filepath = os.path.join(self.output_directory, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(debug_output)
            
            logger.info(f"Debug output saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving debug file: {e}")


def generate_weather_debug_output(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Generate weather debug output for email attachment.
    
    Args:
        report_data: Dictionary containing report information
        config: Configuration dictionary
        
    Returns:
        Debug output string or empty string if debug is disabled
    """
    try:
        debug_generator = WeatherDebugOutput(config)
        report_type = report_data.get('report_type', 'morning')
        
        return debug_generator.generate_debug_output(report_type)
        
    except Exception as e:
        logger.error(f"Error generating weather debug output: {e}")
        return f"\n--- DEBUG INFO ---\nError generating weather debug output: {str(e)}\n" 