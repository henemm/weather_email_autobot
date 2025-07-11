"""
Weather data processor for Météo-France API.

This module processes raw weather data from Météo-France API and converts it
into the format expected by the report generator.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pytz  # Am Anfang der Datei ergänzen

from meteofrance_api.client import MeteoFranceClient
# TEMPORARILY DISABLED: from src.fire.fire_risk_zone import FireRiskZone
# TEMPORARILY DISABLED: from ..fire.fire_risk_zone import FireRiskZone

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
        report_type: str = 'morning',
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Process weather data for a location and return report-ready format.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            location_name: Name of the location
            report_type: Type of report ('morning', 'evening', 'update')
            hours_ahead: Number of hours ahead to fetch
            
        Returns:
            Dictionary containing processed weather data
        """
        try:
            client = MeteoFranceClient()
            forecast = client.get_forecast(latitude, longitude)
            
            if not forecast.forecast:
                logger.error(f"No forecast data for {location_name}")
                return self._create_empty_result()
            
            processed_data = self._process_forecast_data(
                forecast.forecast[:hours_ahead], 
                location_name,
                latitude,
                longitude,
                report_type
            )
            
            logger.info(f"Processed weather data for {location_name} ({report_type} report)")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process weather data for {location_name}: {e}")
            return self._create_empty_result()
    
    def _process_forecast_data(
        self, 
        forecast_entries: List[Dict], 
        location_name: str,
        latitude: float,
        longitude: float,
        report_type: str = 'morning'
    ) -> Dict[str, Any]:
        """
        Process forecast entries into report-ready format using unified aggregation logic.
        The only difference between report types is the target date:
        - morning/update: current date (today)
        - evening: current date + 1 (tomorrow)
        All other logic (time window, aggregation, etc.) is identical.
        """
        # Use current date as base, not startdatum from config
        # startdatum is only used to determine the current stage, not the weather data date
        base_date = datetime.now().date()
        
        # Determine target date based on report type
        if report_type == 'evening':
            target_date = base_date + timedelta(days=1)
        else:
            target_date = base_date  # morning and update reports use current date
            
        # Special debug output for evening reports
        if report_type == 'evening':
            self._debug_evening_report_aggregation(location_name, latitude, longitude, target_date)
        elif report_type == 'morning':
            self._debug_morning_report_aggregation(location_name, latitude, longitude, target_date)
        elif report_type == 'update':
            self._debug_update_report_aggregation(location_name, latitude, longitude, target_date)
            
        # Get global maxima across all points of the stage
        global_maxima = self._calculate_global_maxima_for_stage(report_type, target_date)
        
        # Unified: always use 05-17 Uhr window for all types
        main_weather_data = self._calculate_weather_data_for_day(
            latitude, longitude, location_name, target_date, 5, 17
        )
        # Debug-Ausgaben für alle Typen
        temps = main_weather_data.get('raw_temperatures', [])
        print(f"[TEMP-DEBUG] {location_name} ({latitude:.5f}, {longitude:.5f}) | Temps: {temps} | Max: {main_weather_data.get('max_temperature', '-')} | Date: {target_date}")
        rain_probs = main_weather_data.get('raw_rain_probabilities', [])
        print(f"[RAINW-DEBUG] {location_name} ({latitude:.5f}, {longitude:.5f}) | RegenW: {rain_probs} | Max: {main_weather_data.get('max_rain_probability', '-')} | Date: {target_date}")
        precips = main_weather_data.get('raw_precipitations', [])
        print(f"[REGEN-DEBUG] {location_name} ({latitude:.5f}, {longitude:.5f}) | Regen: {precips} | Max: {main_weather_data.get('max_precipitation', '-')} | Date: {target_date}")
        # Thunderstorm next day logic remains as before
        thunderstorm_next_day = self._calculate_thunderstorm_next_day(
            latitude, longitude, location_name, report_type
        )
        # Night min temperature only for evening reports (last geopoint, 22-05 Uhr)
        min_temperature = 0.0
        if report_type == 'evening':
            min_temperature = self._calculate_min_temperature(latitude, longitude, location_name)
        # TEMPORARILY DISABLED: Fire risk warning - calculate global maximum across all stage points
        fire_risk_warning = ""
        # try:
        #     fire_risk = FireRiskZone()
        #     
        #     # For evening reports, we need to get the fire risk for tomorrow's stage
        #     if report_type == 'evening':
        #         # Dynamically get tomorrow's stage coordinates from etappen.json
        #         import json
        #         import yaml
        #         
        #         # Load etappen.json
        #         with open('etappen.json', 'r', encoding='utf-8') as f:
        #             etappen = json.load(f)
        #         
        #         # Load config.yaml for startdatum
        #         with open('config.yaml', 'r', encoding='utf-8') as f:
        #             config = yaml.safe_load(f)
        #         startdatum = config.get('startdatum', '2025-06-21')
        #         start_date = datetime.strptime(startdatum, '%Y-%m-%d').date()
        #         
        #         # Calculate tomorrow's stage index
        #         base_date = datetime.now().date()
        #         tomorrow_stage_index = (base_date - start_date).days + 1
        #         
        #         if 0 <= tomorrow_stage_index < len(etappen):
        #             tomorrow_stage = etappen[tomorrow_stage_index]
        #             tomorrow_coordinates = tomorrow_stage['punkte']
        #             
        #             # Check fire risk for all points of tomorrow's stage
        #             max_fire_level = 0
        #             for coord in tomorrow_coordinates:
        #                 lat, lon = coord['lat'], coord['lon']
        #                 try:
        #                     warning = fire_risk.format_fire_warnings(lat, lon)
        #                     if warning and "WARN" in warning:
        #                             max_fire_level = max(max_fire_level, 3)  # WARN = Level 3
        #                         elif warning and "HIGH" in warning:
        #                             max_fire_level = max(max_fire_level, 4)  # HIGH = Level 4
        #                         elif warning and "MAX" in warning:
        #                             max_fire_level = max(max_fire_level, 5)  # MAX = Level 5
        #                 except Exception as e:
        #                     logger.warning(f"Failed to check fire risk for tomorrow stage point ({lat}, {lon}): {e}")
        #             
        #             # Set fire risk warning based on maximum level found
        #             if max_fire_level >= 3:
        #                 fire_risk_warning = "WARN Waldbrand"
        #             elif max_fire_level >= 4:
        #                 fire_risk_warning = "HIGH Waldbrand"
        #             elif max_fire_level >= 5:
        #                 fire_risk_warning = "MAX Waldbrand"
        #         else:
        #             logger.warning(f"Tomorrow stage index {tomorrow_stage_index} out of range (0-{len(etappen)-1})")
        #     else:
        #         # For morning/update reports, check current stage
        #         fire_risk_warning = fire_risk.format_fire_warnings(latitude, longitude)
        #         
        # except Exception as e:
        #     logger.warning(f"Failed to fetch fire risk warning for {location_name} ({latitude}, {longitude}): {e}")
        # Build report data using the correct data source
        # For evening reports: use main_weather_data (current stage) for main values, global_maxima only for stage-wide aggregation
        if report_type == 'evening':
            # Use main_weather_data for the primary values (from current stage)
            report_data = {
                'max_temperature': main_weather_data.get('max_temperature', 0.0),
                'max_temperature_time': main_weather_data.get('max_temperature_time', ''),
                'min_temperature': min_temperature,  # Night temperature from current stage
                'min_temperature_time': main_weather_data.get('min_temperature_time', ''),
                'max_precipitation': main_weather_data.get('max_precipitation', 0.0),
                'precipitation_time': main_weather_data.get('precipitation_time', ''),
                'max_rain_probability': main_weather_data.get('max_rain_probability', 0.0),
                'rain_max_time': main_weather_data.get('rain_max_time', ''),
                'max_thunderstorm_probability': main_weather_data.get('max_thunderstorm_probability', 0.0),
                'max_wind_speed': main_weather_data.get('max_wind_speed', 0.0),
                'wind_speed_time': main_weather_data.get('wind_speed_time', ''),
                'max_wind_gusts': main_weather_data.get('max_wind_gusts', 0.0),
                'wind_gusts_time': global_maxima.get('wind_gusts_time', ''),
                'wind_speed': main_weather_data.get('wind_speed', 0.0),
                'thunderstorm_threshold_pct': main_weather_data.get('thunderstorm_threshold_pct', 0),
                'thunderstorm_threshold_time': main_weather_data.get('thunderstorm_threshold_time', ''),
                'thunderstorm_max_time': global_maxima.get('thunderstorm_max_time', ''),
                'rain_threshold_pct': main_weather_data.get('rain_threshold_pct', 0),
                'rain_threshold_time': main_weather_data.get('rain_threshold_time', ''),
                'rain_total_time': global_maxima.get('precipitation_time', ''),
                'thunderstorm_next_day': thunderstorm_next_day.get('thunderstorm_next_day', 0),
                'thunderstorm_next_day_threshold_time': thunderstorm_next_day.get('thunderstorm_next_day_threshold_time', ''),
                'thunderstorm_next_day_max_time': thunderstorm_next_day.get('thunderstorm_next_day_max_time', ''),
                'location': location_name,
                'report_type': report_type,
                'target_date': main_weather_data.get('target_date', ''),
                'thunderstorm_next_day_date': thunderstorm_next_day.get('target_date', ''),
                'data_source': 'meteofrance-api',
                'processed_at': datetime.now().isoformat(),
                'fire_risk_warning': fire_risk_warning,
            }
        else:
            # Use global_maxima for morning/update reports (current stage)
            report_data = {
                'max_temperature': global_maxima.get('max_temperature', 0.0),
                'max_temperature_time': global_maxima.get('max_temperature_time', ''),
                'min_temperature': global_maxima.get('min_temperature', min_temperature),
                'min_temperature_time': global_maxima.get('min_temperature_time', ''),
                'max_precipitation': global_maxima.get('max_precipitation', 0.0),
                'precipitation_time': global_maxima.get('precipitation_time', ''),
                'max_rain_probability': global_maxima.get('max_rain_probability', 0.0),
                'rain_max_time': global_maxima.get('rain_max_time', ''),
                'max_thunderstorm_probability': global_maxima.get('max_thunderstorm_probability', 0.0),
                'max_wind_speed': global_maxima.get('max_wind_speed', 0.0),
                'wind_speed_time': global_maxima.get('wind_speed_time', ''),
                'max_wind_gusts': global_maxima.get('max_wind_gusts', 0.0),
                'wind_gusts_time': global_maxima.get('wind_gusts_time', ''),
                'wind_speed': global_maxima.get('wind_speed', 0.0),
                'thunderstorm_threshold_pct': main_weather_data.get('thunderstorm_threshold_pct', 0),
                'thunderstorm_threshold_time': main_weather_data.get('thunderstorm_threshold_time', ''),
                'thunderstorm_max_time': global_maxima.get('thunderstorm_max_time', ''),
                'rain_threshold_pct': main_weather_data.get('rain_threshold_pct', 0),
                'rain_threshold_time': main_weather_data.get('rain_threshold_time', ''),
                'rain_total_time': global_maxima.get('precipitation_time', ''),
                'thunderstorm_next_day': thunderstorm_next_day.get('thunderstorm_next_day', 0),
                'thunderstorm_next_day_threshold_time': thunderstorm_next_day.get('thunderstorm_next_day_threshold_time', ''),
                'thunderstorm_next_day_max_time': thunderstorm_next_day.get('thunderstorm_next_day_max_time', ''),
                'location': location_name,
                'report_type': report_type,
                'target_date': main_weather_data.get('target_date', ''),
                'thunderstorm_next_day_date': thunderstorm_next_day.get('target_date', ''),
                'data_source': 'meteofrance-api',
                'processed_at': datetime.now().isoformat(),
                'fire_risk_warning': fire_risk_warning,
            }
        return report_data
    
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
            if rain_1h is not None:
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
        # Only use precipitation probability if it's actually provided by the API
        if precipitation_probability is not None:
            return float(precipitation_probability)
        
        # If no API probability, estimate based on weather condition
        if weather_condition:
            weather_lower = weather_condition.lower()
            
            # Check for rain indicators
            rain_indicators = [
                'averse', 'averses', 'pluie', 'pluies', 'rain', 'rains',
                'averse orageuse', 'averses orageuses', 'orage', 'orages'
            ]
            
            is_rain = any(indicator in weather_lower for indicator in rain_indicators)
            
            if is_rain:
                # If there's actual precipitation, estimate based on amount
                if precipitation_amount and precipitation_amount > 0:
                    if precipitation_amount >= 2.0:
                        return 80.0  # Heavy rain
                    elif precipitation_amount >= 1.0:
                        return 60.0  # Moderate rain
                    elif precipitation_amount >= 0.5:
                        return 40.0  # Light rain
                    else:
                        return 30.0  # Very light rain
                else:
                    # Weather description suggests rain but no precipitation amount
                    return 20.0  # Low probability of rain
            
            # Check for clear weather indicators (low rain probability)
            clear_weather_indicators = [
                'ensoleillé', 'ciel clair', 'eclaircies', 'clear', 'sunny',
                'beau temps', 'peu nuageux'
            ]
            
            is_clear = any(indicator in weather_lower for indicator in clear_weather_indicators)
            
            if is_clear:
                return 5.0  # Very low probability of rain
        
        # Default: no rain probability information available
        return None
    

    
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
            'rain_probability_time': '',
            'precipitation_amount_time': '',
            'thunderstorm_time': '',
            'wind_speed_time': '',
            'wind_gusts_time': ''
        }
        for point in time_points:
            # Handle both datetime objects and strings
            dt_val = point['datetime']
            if isinstance(dt_val, str):
                try:
                    dt_obj = datetime.fromisoformat(dt_val.replace('Z', '+00:00'))
                    time_str = dt_obj.strftime('%H')
                except Exception:
                    time_str = '00'
            else:
                time_str = dt_val.strftime('%H')
            # Temperatur
            if point['temperature'] is not None and point['temperature'] > max_values['temperature']:
                max_values['temperature'] = point['temperature']
                max_values['temperature_time'] = time_str
            # Regenmenge
            if point['precipitation_amount'] is not None and point['precipitation_amount'] > max_values['precipitation_amount']:
                max_values['precipitation_amount'] = point['precipitation_amount']
                max_values['precipitation_amount_time'] = time_str
            # Regenwahrscheinlichkeit
            rain_prob = point.get('rain_probability') or point.get('precipitation_probability')
            if rain_prob is not None and rain_prob > max_values['rain_probability']:
                max_values['rain_probability'] = rain_prob
                max_values['rain_probability_time'] = time_str
            # Thunderstorm
            if point['thunderstorm_probability'] is not None and point['thunderstorm_probability'] > max_values['thunderstorm_probability']:
                max_values['thunderstorm_probability'] = point['thunderstorm_probability']
                max_values['thunderstorm_time'] = time_str
            # Wind
            if point['wind_speed'] is not None and point['wind_speed'] > max_values['wind_speed']:
                max_values['wind_speed'] = point['wind_speed']
                max_values['wind_speed_time'] = time_str
            if point['wind_gusts'] is not None and point['wind_gusts'] > max_values['wind_gusts']:
                max_values['wind_gusts'] = point['wind_gusts']
                max_values['wind_gusts_time'] = time_str
        # Für Kompatibilität: precipitation_time/rain_time wie bisher
        max_values['precipitation_time'] = max_values['precipitation_amount_time']
        max_values['rain_time'] = max_values['rain_probability_time']
        # Korrigiere rain_total_time (sollte die Zeit der Regenmenge sein)
        max_values['rain_total_time'] = max_values['precipitation_amount_time']
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
            dt_val = point['datetime']
            if isinstance(dt_val, str):
                try:
                    dt_obj = datetime.fromisoformat(dt_val.replace('Z', '+00:00'))
                    time_str = dt_obj.strftime('%H')
                except Exception:
                    time_str = '00'
            else:
                time_str = dt_val.strftime('%H')
            if (point['thunderstorm_probability'] and 
                point['thunderstorm_probability'] >= thunderstorm_threshold and
                crossings['thunderstorm']['value'] == 0):
                crossings['thunderstorm'] = {
                    'value': point['thunderstorm_probability'],
                    'time': time_str
                }
            rain_prob = point.get('rain_probability') or point.get('precipitation_probability')
            if (rain_prob and 
                rain_prob >= rain_threshold and
                crossings['rain']['value'] == 0):
                crossings['rain'] = {
                    'value': rain_prob,
                    'time': time_str
                }
        return crossings
    
    def _calculate_min_temperature(self, latitude: float, longitude: float, location_name: str) -> float:
        """
        Calculate minimum temperature for evening reports.
        
        According to email_format.mdc specification:
        - min_temp: Last geopoint of today's stage, 22:00–05:00
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location  
            location_name: Name of the location
            
        Returns:
            Minimum temperature for the night period
        """
        try:
            client = MeteoFranceClient()
            forecast = client.get_forecast(latitude, longitude)
            
            if not forecast.forecast:
                logger.warning(f"No forecast data for min_temperature calculation for {location_name}")
                return 0.0
            
            # Get today's date
            today_date = datetime.now().date()
            
            # Find entries for tonight (22:00-05:00)
            night_entries = []
            for entry in forecast.forecast:
                try:
                    dt_timestamp = entry.get('dt')
                    if not dt_timestamp:
                        continue
                        
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    entry_date = entry_datetime.date()
                    hour = entry_datetime.hour
                    
                    # Check if this is for today and night time (22:00-23:59 is today, 00:00-05:00 is tomorrow)
                    if ((entry_date == today_date and hour >= 22) or 
                        (entry_date == today_date + timedelta(days=1) and hour <= 5)):
                        temperature = self._extract_temperature(entry)
                        if temperature is not None:
                            night_entries.append(temperature)
                            
                except Exception as e:
                    logger.warning(f"Failed to process night forecast entry: {e}")
                    continue
            
            if night_entries:
                min_temp = min(night_entries)
                logger.info(f"Calculated min_temperature for {location_name}: {min_temp}°C from {len(night_entries)} night entries")
                return min_temp
            else:
                logger.warning(f"No night temperature data found for {location_name}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to calculate min_temperature for {location_name}: {e}")
            return 0.0
    
    def _calculate_weather_data_for_day(
        self, 
        latitude: float, 
        longitude: float, 
        location_name: str,
        target_date: datetime.date,
        start_hour: int = 4,
        end_hour: int = 22,
        return_raw: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate weather data for a specific day and time window (now 04:00–22:00).
        Optionally return all raw temperature values for debugging.
        Note: Maxima/minima may shift compared to previous 05–17 Uhr logic.
        """
        try:
            client = MeteoFranceClient()
            forecast = client.get_forecast(latitude, longitude)
            if not forecast.forecast:
                logger.warning(f"No forecast data for {location_name} on {target_date}")
                return self._create_empty_result()
            # Initialize lists before processing entries
            time_points = []
            raw_temperatures = []
            raw_rain_probabilities = []
            raw_precipitations = []
            max_temp_found = 0.0
            for entry in forecast.forecast:
                try:
                    dt_timestamp = entry.get('dt')
                    if not dt_timestamp:
                        continue
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    entry_date = entry_datetime.date()
                    hour = entry_datetime.hour
                    # Only consider entries in the new window 04:00–22:00
                    if entry_date == target_date and start_hour <= hour <= end_hour:
                        temperature = self._extract_temperature(entry)
                        if temperature is not None:
                            raw_temperatures.append(temperature)
                        weather_condition = self._extract_weather_condition(entry)
                        wind_speed = self._extract_wind_speed(entry)
                        wind_gusts = self._extract_wind_gusts(entry)
                        precipitation_probability = entry.get('precipitation_probability')
                        precipitation_amount = self._extract_precipitation_amount(entry)
                        thunderstorm_probability = self._determine_thunderstorm_probability(
                            weather_condition, precipitation_probability
                        )
                        rain_probability = self._determine_rain_probability(
                            weather_condition, precipitation_probability, precipitation_amount
                        )
                        if rain_probability is not None:
                            raw_rain_probabilities.append(rain_probability)
                        if precipitation_amount is not None:
                            raw_precipitations.append(precipitation_amount)
                        time_point = {
                            'datetime': entry_datetime,
                            'temperature': temperature,
                            'wind_speed': wind_speed,
                            'wind_gusts': wind_gusts,
                            'precipitation_probability': precipitation_probability,
                            'precipitation_amount': precipitation_amount,
                            'thunderstorm_probability': thunderstorm_probability,
                            'rain_probability': rain_probability,
                            'weather_condition': weather_condition,
                            'latitude': latitude,
                            'longitude': longitude
                        }
                        time_points.append(time_point)
                except Exception as e:
                    logger.warning(f"Failed to process forecast entry: {e}")
                    continue
            if max_temp_found < 15.0 and target_date.month in [6, 7, 8]:
                logger.warning(f"MeteoFrance temperatures too low for summer ({max_temp_found}°C), trying Open-Meteo fallback")
                try:
                    from .fetch_openmeteo import fetch_openmeteo_forecast
                    openmeteo_data = fetch_openmeteo_forecast(latitude, longitude)
                    return self._process_openmeteo_data(openmeteo_data, latitude, longitude, location_name, target_date, start_hour, end_hour)
                except Exception as e:
                    logger.warning(f"Open-Meteo fallback failed: {e}")
            if not time_points:
                logger.warning(f"No weather data found for {location_name} on {target_date} between {start_hour:02d}:00-{end_hour:02d}:00")
                return self._create_empty_result()
            # Only pretty tabular debug output will be shown elsewhere
            # ... rest of function unchanged ...
            
            # Sammle pro Etappenpunkt alle Werte und berechne Min/Max je Kategorie inkl. Zeitstempel
            # Nach allen Etappenpunkten: berechne das globale Min/Max über alle Punkte
            # Am Ende jeder Tabelle: Ausgabe der Min/Max je Kategorie
            # Am Ende aller Tabellen: Ausgabe der globalen Min/Max

            # Am Anfang der Funktion, die alle Etappenpunkte eines Tages verarbeitet (z.B. in der Hauptschleife):
            global_stats_list = []

            # Nach dem Sammeln von time_points für einen Etappenpunkt:

            # Initialisiere Min/Max für diesen Etappenpunkt
            stage_stats = {
                'temperature_max': float('-inf'), 'temperature_max_time': '',
                'temperature_min': float('inf'), 'temperature_min_time': '',
                'rain_probability_max': float('-inf'), 'rain_probability_max_time': '',
                'precipitation_amount_max': float('-inf'), 'precipitation_amount_max_time': '',
                'wind_speed_max': float('-inf'), 'wind_speed_max_time': '',
                'wind_gusts_max': float('-inf'), 'wind_gusts_max_time': '',
                'thunderstorm_probability_max': 0.0, 'thunderstorm_probability_max_time': ''
            }
            for t in time_points:
                # Temperatur
                if t['temperature'] is not None:
                    if t['temperature'] > stage_stats['temperature_max']:
                        stage_stats['temperature_max'] = t['temperature']
                        stage_stats['temperature_max_time'] = t['datetime']
                    if t['temperature'] < stage_stats['temperature_min']:
                        stage_stats['temperature_min'] = t['temperature']
                        stage_stats['temperature_min_time'] = t['datetime']
                # Regenwahrscheinlichkeit
                rain_prob = t.get('rain_probability') or t.get('precipitation_probability')
                if rain_prob is not None:
                    if rain_prob > stage_stats['rain_probability_max']:
                        stage_stats['rain_probability_max'] = rain_prob
                        stage_stats['rain_probability_max_time'] = t['datetime']
                # Regenmenge
                if t['precipitation_amount'] is not None:
                    if t['precipitation_amount'] > stage_stats['precipitation_amount_max']:
                        stage_stats['precipitation_amount_max'] = t['precipitation_amount']
                        stage_stats['precipitation_amount_max_time'] = t['datetime']
                # Wind
                if t['wind_speed'] is not None:
                    if t['wind_speed'] > stage_stats['wind_speed_max']:
                        stage_stats['wind_speed_max'] = t['wind_speed']
                        stage_stats['wind_speed_max_time'] = t['datetime']
                # Böen
                if t['wind_gusts'] is not None:
                    if t['wind_gusts'] > stage_stats['wind_gusts_max']:
                        stage_stats['wind_gusts_max'] = t['wind_gusts']
                        stage_stats['wind_gusts_max_time'] = t['datetime']
                # Gewitter
                if t['thunderstorm_probability'] is not None:
                    if t['thunderstorm_probability'] > stage_stats['thunderstorm_probability_max']:
                        stage_stats['thunderstorm_probability_max'] = t['thunderstorm_probability']
                        stage_stats['thunderstorm_probability_max_time'] = t['datetime']

            # Ausgabe der Min/Max für diesen Etappenpunkt
            print(f"[MAXIMA] {location_name}: TempMax: {stage_stats['temperature_max']}°C@{stage_stats['temperature_max_time'].strftime('%H')} | TempMin: {stage_stats['temperature_min']}°C@{stage_stats['temperature_min_time'].strftime('%H')} | RainWMax: {stage_stats['rain_probability_max']}%@{stage_stats['rain_probability_max_time'].strftime('%H')} | RainMax: {stage_stats['precipitation_amount_max']}mm@{stage_stats['precipitation_amount_max_time'].strftime('%H')} | WindMax: {stage_stats['wind_speed_max']}km/h@{stage_stats['wind_speed_max_time'].strftime('%H')} | GustsMax: {stage_stats['wind_gusts_max']}km/h@{stage_stats['wind_gusts_max_time'].strftime('%H')} | ThunderMax: {stage_stats['thunderstorm_probability_max']}%@{stage_stats['thunderstorm_probability_max_time'].strftime('%H')}")

            # Sammle alle stage_stats in einer Liste (z.B. global_stage_stats.append(stage_stats))
            global_stats_list.append(stage_stats)

            # Nach allen Etappenpunkten:
            global_max = {
                'temperature_max': float('-inf'), 'temperature_max_time': '',
                'temperature_min': float('inf'), 'temperature_min_time': '',
                'rain_probability_max': float('-inf'), 'rain_probability_max_time': '',
                'precipitation_amount_max': float('-inf'), 'precipitation_amount_max_time': '',
                'wind_speed_max': float('-inf'), 'wind_speed_max_time': '',
                'wind_gusts_max': float('-inf'), 'wind_gusts_max_time': '',
                'thunderstorm_probability_max': 0.0, 'thunderstorm_probability_max_time': ''
            }
            for stats in global_stats_list:
                if stats['temperature_max'] > global_max['temperature_max']:
                    global_max['temperature_max'] = stats['temperature_max']
                    global_max['temperature_max_time'] = stats['temperature_max_time']
                if stats['temperature_min'] < global_max['temperature_min']:
                    global_max['temperature_min'] = stats['temperature_min']
                    global_max['temperature_min_time'] = stats['temperature_min_time']
                if stats['rain_probability_max'] > global_max['rain_probability_max']:
                    global_max['rain_probability_max'] = stats['rain_probability_max']
                    global_max['rain_probability_max_time'] = stats['rain_probability_max_time']
                if stats['precipitation_amount_max'] > global_max['precipitation_amount_max']:
                    global_max['precipitation_amount_max'] = stats['precipitation_amount_max']
                    global_max['precipitation_amount_max_time'] = stats['precipitation_amount_max_time']
                if stats['wind_speed_max'] > global_max['wind_speed_max']:
                    global_max['wind_speed_max'] = stats['wind_speed_max']
                    global_max['wind_speed_max_time'] = stats['wind_speed_max_time']
                if stats['wind_gusts_max'] > global_max['wind_gusts_max']:
                    global_max['wind_gusts_max'] = stats['wind_gusts_max']
                    global_max['wind_gusts_max_time'] = stats['wind_gusts_max_time']
                if stats['thunderstorm_probability_max'] > global_max['thunderstorm_probability_max']:
                    global_max['thunderstorm_probability_max'] = stats['thunderstorm_probability_max']
                    global_max['thunderstorm_probability_max_time'] = stats['thunderstorm_probability_max_time']

            print(f"[GLOBAL-MAXIMA] TempMax: {global_max['temperature_max']}°C@{global_max['temperature_max_time'].strftime('%H')} | TempMin: {global_max['temperature_min']}°C@{global_max['temperature_min_time'].strftime('%H')} | RainWMax: {global_max['rain_probability_max']}%@{global_max['rain_probability_max_time'].strftime('%H')} | RainMax: {global_max['precipitation_amount_max']}mm@{global_max['precipitation_amount_max_time'].strftime('%H')} | WindMax: {global_max['wind_speed_max']}km/h@{global_max['wind_speed_max_time'].strftime('%H')} | GustsMax: {global_max['wind_gusts_max']}km/h@{global_max['wind_gusts_max_time'].strftime('%H')} | ThunderMax: {global_max['thunderstorm_probability_max']}%@{global_max['thunderstorm_probability_max_time'].strftime('%H')}")

            # Für evening: Min-Temp nur vom letzten Etappenpunkt verwenden (stage_stats['temperature_min'])
            # Für evening: Datenbasis = nächster Tag, Gewitter+1 = übernächster Tag (Logik wie bisher)
            # Calculate aggregated values
            max_values = self._calculate_max_values(time_points)
            threshold_crossings = self._calculate_threshold_crossings(time_points)
            
            # Use global maxima instead of local maxima from raw_* lists
            result = {
                'max_temperature': global_max['temperature_max'],
                'max_temperature_time': global_max['temperature_max_time'],
                'min_temperature': global_max['temperature_min'],
                'min_temperature_time': global_max['temperature_min_time'],
                'max_rain_probability': global_max['rain_probability_max'],
                'rain_max_time': global_max['rain_probability_max_time'],
                'max_precipitation': global_max['precipitation_amount_max'],
                'rain_total_time': global_max['precipitation_amount_max_time'],
                'max_wind_speed': global_max['wind_speed_max'],
                'wind_max_time': global_max['wind_speed_max_time'],
                'max_wind_gusts': global_max['wind_gusts_max'],
                'wind_gusts_max_time': global_max['wind_gusts_max_time'],
                'max_thunderstorm_probability': global_max['thunderstorm_probability_max'],
                'thunderstorm_max_time': global_max['thunderstorm_probability_max_time'],
                # Keep raw data for debugging
                'raw_temperatures': raw_temperatures,
                'raw_rain_probabilities': raw_rain_probabilities,
                'raw_precipitations': raw_precipitations,
                # Build result
                'wind_speed': max_values['wind_speed'],
                'thunderstorm_threshold_pct': threshold_crossings['thunderstorm']['value'],
                'thunderstorm_threshold_time': threshold_crossings['thunderstorm']['time'],
                'rain_threshold_pct': threshold_crossings['rain']['value'],
                'rain_threshold_time': threshold_crossings['rain']['time'],
                'location': location_name,
                'target_date': target_date.isoformat(),
                'time_window': f"{start_hour:02d}:00-{end_hour:02d}:00",
                'data_source': 'meteofrance-api',
                'processed_at': datetime.now().isoformat(),
            }
            # Füge alle bisherigen Felder aus max_values und threshold_crossings hinzu
            result.update(max_values)
            result.update(threshold_crossings)
            logger.info(f"Calculated weather data for {location_name} on {target_date} ({start_hour:02d}:00-{end_hour:02d}:00): "
                       f"max_temp={max_values['temperature']}°C, "
                       f"max_thunderstorm={max_values['thunderstorm_probability']}%")
            return result
        except Exception as e:
            logger.error(f"Failed to calculate weather data for {location_name} on {target_date}: {e}")
            return self._create_empty_result()
    
    def _process_openmeteo_data(
        self, 
        openmeteo_data: Dict[str, Any],
        latitude: float, 
        longitude: float, 
        location_name: str,
        target_date: datetime.date,
        start_hour: int = 5,
        end_hour: int = 17
    ) -> Dict[str, Any]:
        """
        Process Open-Meteo data when MeteoFrance temperatures are unrealistic.
        """
        try:
            hourly = openmeteo_data.get("hourly", {})
            if not hourly:
                logger.warning(f"No hourly data in Open-Meteo response for {location_name}")
                return self._create_empty_result()
            
            times = hourly.get("time", [])
            temperatures = hourly.get("temperature_2m", [])
            precipitations = hourly.get("precipitation", [])
            precipitation_probabilities = hourly.get("precipitation_probability", [])
            
            time_points = []
            raw_temperatures = []
            raw_rain_probabilities = []
            raw_precipitations = []
            
            for i, time_str in enumerate(times):
                try:
                    time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    time_date = time_obj.date()
                    time_hour = time_obj.hour
                    
                    # Check if this is for the target date and time window
                    if time_date == target_date and start_hour <= time_hour <= end_hour:
                        temperature = temperatures[i] if i < len(temperatures) else None
                        precipitation = precipitations[i] if i < len(precipitations) else None
                        precipitation_probability = precipitation_probabilities[i] if i < len(precipitation_probabilities) else None
                        
                        if temperature is not None:
                            raw_temperatures.append(temperature)
                        if precipitation_probability is not None:
                            raw_rain_probabilities.append(precipitation_probability)
                        if precipitation is not None:
                            raw_precipitations.append(precipitation)
                        
                        time_point = {
                            'datetime': time_obj,
                            'temperature': temperature,
                            'wind_speed': None,  # Open-Meteo doesn't provide this in hourly
                            'wind_gusts': None,
                            'precipitation_probability': precipitation_probability,
                            'precipitation_amount': precipitation,
                            'thunderstorm_probability': None,  # Open-Meteo doesn't provide this
                            'rain_probability': precipitation_probability,
                            'weather_condition': None,
                            'latitude': latitude,
                            'longitude': longitude
                        }
                        time_points.append(time_point)
                        
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to process Open-Meteo time entry: {e}")
                    continue
            
            if not time_points:
                logger.warning(f"No Open-Meteo data found for {location_name} on {target_date} between {start_hour:02d}:00-{end_hour:02d}:00")
                return self._create_empty_result()
            
            # Calculate aggregated values
            max_values = self._calculate_max_values(time_points)
            threshold_crossings = self._calculate_threshold_crossings(time_points)
            
            result = {
                'max_temperature': max(raw_temperatures) if raw_temperatures else 0.0,
                'raw_temperatures': raw_temperatures,
                'max_rain_probability': max(raw_rain_probabilities) if raw_rain_probabilities else 0.0,
                'raw_rain_probabilities': raw_rain_probabilities,
                'max_precipitation': max(raw_precipitations) if raw_precipitations else 0.0,
                'raw_precipitations': raw_precipitations,
                'max_thunderstorm_probability': max_values['thunderstorm_probability'],
                'max_wind_speed': max_values['wind_speed'],
                'wind_speed': max_values['wind_speed'],
                'thunderstorm_threshold_pct': threshold_crossings['thunderstorm']['value'],
                'thunderstorm_threshold_time': threshold_crossings['thunderstorm']['time'],
                'thunderstorm_max_time': max_values['thunderstorm_time'],
                'rain_threshold_pct': threshold_crossings['rain']['value'],
                'rain_threshold_time': threshold_crossings['rain']['time'],
                'rain_max_time': max_values['rain_time'],
                'rain_total_time': max_values['precipitation_time'],
                'location': location_name,
                'target_date': target_date.isoformat(),
                'time_window': f"{start_hour:02d}:00-{end_hour:02d}:00",
                'data_source': 'open-meteo',
                'processed_at': datetime.now().isoformat(),
            }
            
            result.update(max_values)
            result.update(threshold_crossings)
            
            logger.info(f"Calculated Open-Meteo weather data for {location_name} on {target_date} ({start_hour:02d}:00-{end_hour:02d}:00): "
                       f"max_temp={max_values['temperature']}°C, "
                       f"max_thunderstorm={max_values['thunderstorm_probability']}%")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process Open-Meteo data for {location_name} on {target_date}: {e}")
            return self._create_empty_result()
    
    def _calculate_thunderstorm_next_day(
        self, 
        latitude: float, 
        longitude: float, 
        location_name: str,
        report_type: str
    ) -> Dict[str, Any]:
        """
        Calculate 'Gewitter +1' (thunderstorm next day) data according to specification.
        
        According to email_format.mdc:
        - Morning Report: Gewitter +1 = morgen (05-17 Uhr)
        - Evening Report: Gewitter +1 = übermorgen (05-17 Uhr)  
        - Update Report: Gewitter +1 = morgen (05-17 Uhr)
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            location_name: Name of the location
            report_type: Type of report ('morning', 'evening', 'update')
            
        Returns:
            Dictionary containing thunderstorm data for the next day
        """
        # Use current date as base, consistent with _process_forecast_data
        current_date = datetime.now().date()
        
        # Determine target date based on report type
        if report_type == 'evening':
            # Evening report: Gewitter +1 = übermorgen
            target_date = current_date + timedelta(days=2)
            logger.info(f"Evening report: calculating Gewitter +1 for {target_date} (übermorgen)")
        else:
            # Morning and Update report: Gewitter +1 = morgen
            target_date = current_date + timedelta(days=1)
            logger.info(f"{report_type.capitalize()} report: calculating Gewitter +1 for {target_date} (morgen)")
        
        # Calculate weather data for the target date (05-17 Uhr)
        weather_data = self._calculate_weather_data_for_day(
            latitude, longitude, location_name, target_date, 5, 17
        )
        
        # Extract thunderstorm-specific data
        thunderstorm_data = {
            'thunderstorm_next_day': weather_data.get('max_thunderstorm_probability', 0),
            'thunderstorm_next_day_threshold_time': weather_data.get('thunderstorm_threshold_time', ''),
            'thunderstorm_next_day_max_time': weather_data.get('thunderstorm_max_time', ''),
            'target_date': target_date.isoformat(),
            'report_type': report_type
        }
        
        return thunderstorm_data
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result when no data is available."""
        return {
            'max_temperature': 0.0,
            'min_temperature': 0.0,
            'max_precipitation': 0.0,
            'max_rain_probability': 0.0,
            'max_thunderstorm_probability': 0.0,
            'max_wind_speed': 0.0,
            'max_wind_gusts': 0.0,  # Add wind gusts
            'wind_speed': 0.0,
            'thunderstorm_threshold_pct': 0,
            'thunderstorm_threshold_time': '',
            'thunderstorm_max_time': '',
            'rain_threshold_pct': 0,
            'rain_threshold_time': '',
            'rain_max_time': '',
            'rain_total_time': '',
            'thunderstorm_next_day': 0,
            'thunderstorm_next_day_threshold_time': '',
            'thunderstorm_next_day_max_time': '',
            'location': 'Unknown',
            'report_type': 'morning',
            'target_date': '',
            'thunderstorm_next_day_date': '',
            'data_source': 'meteofrance-api',
            'processed_at': datetime.now().isoformat(),
            'fire_risk_warning': '',
        }

    def _print_timestamp_debug(self, label: str, weather_points: list, param_filter=None):
        """
        Print all raw hourly data for a given label and list of WeatherPoint objects in TIMESTAMP-DEBUG format.
        Optionally filter for specific parameters (e.g. only thunderstorm).
        """
        for point in weather_points:
            time_str = point.time.strftime('%Y-%m-%d %H:%M:%S (CEST)')
            temp = f"{point.temperature:.1f}°C" if point.temperature is not None else "-"
            rainw = f"{point.rain_probability:.1f}%" if point.rain_probability is not None else "-"
            rain = f"{point.precipitation:.1f}mm" if point.precipitation is not None else "-"
            wind = f"{point.wind_speed:.0f}km/h" if point.wind_speed is not None else "-"
            gusts = f"{point.wind_gusts:.0f}km/h" if point.wind_gusts is not None else "-"
            thunder = f"{point.thunderstorm_probability:.1f}%" if point.thunderstorm_probability is not None else "-"
            
            print(f"[TIMESTAMP-DEBUG] {label} | {time_str} | Temp: {temp} | RainW: {rainw} | Rain: {rain} | Wind: {wind} | Gusts: {gusts} | Thunder: {thunder}")
        
        # Print tabular summary for this point
        if weather_points:
            self._print_tabular_summary(label, weather_points)

    def _print_tabular_summary(self, label: str, weather_points: list):
        """
        Print tabular summary with Min/Max values for a list of weather points.
        """
        if not weather_points:
            return
            
        # Sort points by hour
        sorted_points = sorted(weather_points, key=lambda p: p.time.hour)
        
        # Print header
        print(f"{label}")
        print("+-------+--------+--------+--------+--------+--------+--------+")
        print("| Hour  |  Temp  | RainW% | Rainmm |  Wind  | Gusts  | Thund% |")
        print("+-------+--------+--------+--------+--------+--------+--------+")
        
        # Print data rows
        for point in sorted_points:
            hour = point.time.strftime('%H')
            temp = f"{point.temperature:.1f}" if point.temperature is not None else " -"
            rainw = f"{point.rain_probability:.1f}" if point.rain_probability is not None else " -"
            rain = f"{point.precipitation:.1f}" if point.precipitation is not None else " -"
            wind = f"{point.wind_speed:.1f}" if point.wind_speed is not None else " -"
            gusts = f"{point.wind_gusts:.1f}" if point.wind_gusts is not None else " -"
            thunder = f"{point.thunderstorm_probability:.1f}" if point.thunderstorm_probability is not None else " -"
            
            print(f"|  {hour}   | {temp:>6} | {rainw:>6} | {rain:>6} | {wind:>6} | {gusts:>6} | {thunder:>6} |")
        
        # Calculate and print Min/Max summary
        temps = [p.temperature for p in weather_points if p.temperature is not None]
        rain_probs = [p.rain_probability for p in weather_points if p.rain_probability is not None]
        precipitations = [p.precipitation for p in weather_points if p.precipitation is not None]
        wind_speeds = [p.wind_speed for p in weather_points if p.wind_speed is not None]
        wind_gusts = [p.wind_gusts for p in weather_points if p.wind_gusts is not None]
        thunderstorms = [p.thunderstorm_probability for p in weather_points if p.thunderstorm_probability is not None]
        
        print("+-------+--------+--------+--------+--------+--------+--------+")
        
        # Min row
        min_temp = f"{min(temps):.1f}" if temps else " -"
        min_rainw = f"{min(rain_probs):.1f}" if rain_probs else " -"
        min_rain = f"{min(precipitations):.1f}" if precipitations else " -"
        min_wind = f"{min(wind_speeds):.1f}" if wind_speeds else " -"
        min_gusts = f"{min(wind_gusts):.1f}" if wind_gusts else " -"
        min_thunder = f"{min(thunderstorms):.1f}" if thunderstorms else " -"
        print(f"|  Min  | {min_temp:>6} | {min_rainw:>6} | {min_rain:>6} | {min_wind:>6} | {min_gusts:>6} | {min_thunder:>6} |")
        
        # Max row
        max_temp = f"{max(temps):.1f}" if temps else " -"
        max_rainw = f"{max(rain_probs):.1f}" if rain_probs else " -"
        max_rain = f"{max(precipitations):.1f}" if precipitations else " -"
        max_wind = f"{max(wind_speeds):.1f}" if wind_speeds else " -"
        max_gusts = f"{max(wind_gusts):.1f}" if wind_gusts else " -"
        max_thunder = f"{max(thunderstorms):.1f}" if thunderstorms else " -"
        print(f"|  Max  | {max_temp:>6} | {max_rainw:>6} | {max_rain:>6} | {max_wind:>6} | {max_gusts:>6} | {max_thunder:>6} |")
        
        print("+-------+--------+--------+--------+--------+--------+--------+")
        print()

    def _print_global_summary(self, stage_name: str, all_points_data: list):
        """
        Print global summary for all points of a stage.
        """
        all_temps = []
        all_rain_probs = []
        all_precipitations = []
        all_wind_speeds = []
        all_wind_gusts = []
        all_thunderstorms = []
        
        for label, points in all_points_data:
            for point in points:
                if point.temperature is not None:
                    all_temps.append((point.temperature, point.time, label))
                if point.rain_probability is not None:
                    all_rain_probs.append((point.rain_probability, point.time, label))
                if point.precipitation is not None:
                    all_precipitations.append((point.precipitation, point.time, label))
                if point.wind_speed is not None:
                    all_wind_speeds.append((point.wind_speed, point.time, label))
                if point.wind_gusts is not None:
                    all_wind_gusts.append((point.wind_gusts, point.time, label))
                if point.thunderstorm_probability is not None:
                    all_thunderstorms.append((point.thunderstorm_probability, point.time, label))
        
        print(f"📊 GLOBAL MAXIMA for {stage_name}:")
        
        if all_temps:
            max_temp_data = max(all_temps, key=lambda x: x[0])
            min_temp_data = min(all_temps, key=lambda x: x[0])
            print(f"   🌡️  Global max temp: {max_temp_data[0]:.1f}°C@{max_temp_data[1].strftime('%H')} ({max_temp_data[2]})")
            print(f"   ❄️  Global min temp: {min_temp_data[0]:.1f}°C@{min_temp_data[1].strftime('%H')} ({min_temp_data[2]})")
        
        if all_rain_probs:
            max_rain_prob_data = max(all_rain_probs, key=lambda x: x[0])
            print(f"   💧 Global max rain prob: {max_rain_prob_data[0]:.1f}%@{max_rain_prob_data[1].strftime('%H')} ({max_rain_prob_data[2]})")
        
        if all_precipitations:
            max_precip_data = max(all_precipitations, key=lambda x: x[0])
            print(f"   🌊 Global max precip: {max_precip_data[0]:.1f}mm@{max_precip_data[1].strftime('%H')} ({max_precip_data[2]})")
        
        if all_wind_speeds:
            max_wind_data = max(all_wind_speeds, key=lambda x: x[0])
            print(f"   🌪️  Global max wind: {max_wind_data[0]:.0f}km/h@{max_wind_data[1].strftime('%H')} ({max_wind_data[2]})")
        
        if all_wind_gusts:
            max_gusts_data = max(all_wind_gusts, key=lambda x: x[0])
            print(f"   🌪️  Global max gusts: {max_gusts_data[0]:.0f}km/h@{max_gusts_data[1].strftime('%H')} ({max_gusts_data[2]})")
        
        if all_thunderstorms:
            max_thunder_data = max(all_thunderstorms, key=lambda x: x[0])
            print(f"   🔥 Global max thunder: {max_thunder_data[0]:.1f}%@{max_thunder_data[1].strftime('%H')} ({max_thunder_data[2]})")
        
        print()

    def _debug_evening_report_aggregation(self, location_name: str, latitude: float, longitude: float, target_date: datetime.date):
        """
        Detailed debug output for evening report aggregation showing:
        1. Night values for last point of Capanelle with temp minimum
        2. Day values for all three points of SanPetru with intermediate sums and global max
        3. Verification that temp-min combines with night values for overall night minimum
        4. Max values for Usciolu (next day) for thunderstorm probability only
        """
        print(f"\n{'='*80}")
        print(f"🌙 EVENING REPORT DEBUG: {location_name} ({latitude:.5f}, {longitude:.5f})")
        print(f"{'='*80}")
        
        try:
            # 1. Nacht: Letzter Punkt heute (22–05 Uhr)
            print(f"\n--- ROHDATEN: Nacht (letzter Punkt heute, 22–05 Uhr) ---")
            night_points = self._get_night_points_of_last_today_point(location_name, latitude, longitude, target_date)
            self._print_timestamp_debug(f"{location_name} (Nacht)", night_points)
            
            # 2. Tag: Alle Punkte morgen (05–17 Uhr)
            tomorrow_points = self._get_all_points_of_stage('tomorrow', target_date)
            for idx, (label, points) in enumerate(tomorrow_points):
                print(f"\n--- ROHDATEN: Tag (Punkt {idx+1} morgen: {label}, 05–17 Uhr) ---")
                self._print_timestamp_debug(f"{label} (Tag)", points)
            
            # Global summary for tomorrow's stage
            if tomorrow_points:
                stage_name = tomorrow_points[0][0].split(' Point ')[0] if tomorrow_points[0][0] else "Tomorrow"
                self._print_global_summary(stage_name, tomorrow_points)
            
            # 3. Gewitter+1: Alle Punkte übermorgen (05–17 Uhr, nur Thunderstorm)
            day_after_points = self._get_all_points_of_stage('day_after_tomorrow', target_date)
            for idx, (label, points) in enumerate(day_after_points):
                print(f"\n--- ROHDATEN: Übermorgen (Punkt {idx+1}: {label}, 05–17 Uhr, nur Thunderstorm) ---")
                self._print_timestamp_debug(f"{label} (Thunderstorm+1)", points)
            
            # Global summary for day after tomorrow's stage (thunderstorm only)
            if day_after_points:
                stage_name = day_after_points[0][0].split(' Point ')[0] if day_after_points[0][0] else "Day After Tomorrow"
                print(f"📊 GLOBAL THUNDERSTORM MAXIMA for {stage_name}:")
                all_thunderstorms = []
                for label, points in day_after_points:
                    for point in points:
                        if point.thunderstorm_probability is not None:
                            all_thunderstorms.append((point.thunderstorm_probability, point.time, label))
                
                if all_thunderstorms:
                    max_thunder_data = max(all_thunderstorms, key=lambda x: x[0])
                    print(f"   🔥 Global max thunder: {max_thunder_data[0]:.1f}%@{max_thunder_data[1].strftime('%H')} ({max_thunder_data[2]})")
                print()
            
            print(f"\n{'='*80}")
            print("✅ EVENING REPORT DEBUG COMPLETE")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"❌ Error in evening report debug: {e}")
            logger.error(f"Failed to perform detailed evening aggregation debug for {location_name}: {e}")

    def _debug_morning_report_aggregation(self, location_name: str, latitude: float, longitude: float, target_date: datetime.date):
        """
        Detailed debug output for morning report aggregation showing:
        1. Day values for all points of current stage (05:00-17:00)
        2. Global maxima across all points
        3. Threshold crossings and timing
        4. Thunderstorm +1 for tomorrow
        """
        print(f"\n{'='*80}")
        print(f"🌅 MORNING REPORT DEBUG: {location_name} ({latitude:.5f}, {longitude:.5f})")
        print(f"{'='*80}")
        
        try:
            # 1. Tag: Alle Punkte heute (05–17 Uhr)
            today_points = self._get_all_points_of_stage('today', target_date)
            for idx, (label, points) in enumerate(today_points):
                print(f"\n--- ROHDATEN: Tag (Punkt {idx+1} heute: {label}, 05–17 Uhr) ---")
                self._print_timestamp_debug(f"{label} (Tag)", points)
            
            # Global summary for today's stage
            if today_points:
                stage_name = today_points[0][0].split(' Point ')[0] if today_points[0][0] else "Today"
                self._print_global_summary(stage_name, today_points)
            
            # 2. Gewitter+1: Alle Punkte morgen (05–17 Uhr, nur Thunderstorm)
            tomorrow_points = self._get_all_points_of_stage('tomorrow', target_date)
            for idx, (label, points) in enumerate(tomorrow_points):
                print(f"\n--- ROHDATEN: Gewitter+1 (Punkt {idx+1} morgen: {label}, 05–17 Uhr, nur Thunderstorm) ---")
                self._print_timestamp_debug(f"{label} (Thunderstorm+1)", points)
            
            # Global summary for tomorrow's stage (thunderstorm only)
            if tomorrow_points:
                stage_name = tomorrow_points[0][0].split(' Point ')[0] if tomorrow_points[0][0] else "Tomorrow"
                print(f"📊 GLOBAL THUNDERSTORM MAXIMA for {stage_name}:")
                all_thunderstorms = []
                for label, points in tomorrow_points:
                    for point in points:
                        if point.thunderstorm_probability is not None:
                            all_thunderstorms.append((point.thunderstorm_probability, point.time, label))
                
                if all_thunderstorms:
                    max_thunder_data = max(all_thunderstorms, key=lambda x: x[0])
                    print(f"   🔥 Global max thunder: {max_thunder_data[0]:.1f}%@{max_thunder_data[1].strftime('%H')} ({max_thunder_data[2]})")
                print()
            
            print(f"\n{'='*80}")
            print("✅ MORNING REPORT DEBUG COMPLETE")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"❌ Error in morning report debug: {e}")
            logger.error(f"Failed to perform detailed morning aggregation debug for {location_name}: {e}")

    def _debug_update_report_aggregation(self, location_name: str, latitude: float, longitude: float, target_date: datetime.date):
        """
        Detailed debug output for update report aggregation showing:
        1. Day values for all points of current stage (05:00-17:00)
        2. Global maxima across all points
        3. Changed values that triggered the update
        4. Thunderstorm +1 for tomorrow
        """
        print(f"\n{'='*80}")
        print(f"🚨 UPDATE REPORT DEBUG: {location_name} ({latitude:.5f}, {longitude:.5f})")
        print(f"{'='*80}")
        
        try:
            # 1. Tag: Alle Punkte heute (05–17 Uhr)
            today_points = self._get_all_points_of_stage('today', target_date)
            for idx, (label, points) in enumerate(today_points):
                print(f"\n--- ROHDATEN: Tag (Punkt {idx+1} heute: {label}, 05–17 Uhr) ---")
                self._print_timestamp_debug(f"{label} (Tag)", points)
            
            # Global summary for today's stage
            if today_points:
                stage_name = today_points[0][0].split(' Point ')[0] if today_points[0][0] else "Today"
                self._print_global_summary(stage_name, today_points)
            
            # 2. Gewitter+1: Alle Punkte morgen (05–17 Uhr, nur Thunderstorm)
            tomorrow_points = self._get_all_points_of_stage('tomorrow', target_date)
            for idx, (label, points) in enumerate(tomorrow_points):
                print(f"\n--- ROHDATEN: Gewitter+1 (Punkt {idx+1} morgen: {label}, 05–17 Uhr, nur Thunderstorm) ---")
                self._print_timestamp_debug(f"{label} (Thunderstorm+1)", points)
            
            # Global summary for tomorrow's stage (thunderstorm only)
            if tomorrow_points:
                stage_name = tomorrow_points[0][0].split(' Point ')[0] if tomorrow_points[0][0] else "Tomorrow"
                print(f"📊 GLOBAL THUNDERSTORM MAXIMA for {stage_name}:")
                all_thunderstorms = []
                for label, points in tomorrow_points:
                    for point in points:
                        if point.thunderstorm_probability is not None:
                            all_thunderstorms.append((point.thunderstorm_probability, point.time, label))
                
                if all_thunderstorms:
                    max_thunder_data = max(all_thunderstorms, key=lambda x: x[0])
                    print(f"   🔥 Global max thunder: {max_thunder_data[0]:.1f}%@{max_thunder_data[1].strftime('%H')} ({max_thunder_data[2]})")
                print()
            
            print(f"\n{'='*80}")
            print("✅ UPDATE REPORT DEBUG COMPLETE")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"❌ Error in update report debug: {e}")
            logger.error(f"Failed to perform detailed update aggregation debug for {location_name}: {e}")

    def _get_night_points_of_last_today_point(self, location_name: str, latitude: float, longitude: float, target_date: datetime.date):
        """
        Get all weather points for the last point of today's stage.
        Returns a list of WeatherPoint objects for debugging.
        """
        try:
            # For now, use the provided coordinates (this should be the last point of today's stage)
            client = MeteoFranceClient()
            forecast = client.get_forecast(latitude, longitude)
            
            if not forecast.forecast:
                return []
            
            today_date = datetime.now().date()
            points = []
            
            print(f"🌙 Fetching night data for {location_name} ({latitude:.5f}, {longitude:.5f})")
            
            for entry in forecast.forecast:
                try:
                    dt_timestamp = entry.get('dt')
                    if not dt_timestamp:
                        continue
                        
                    entry_datetime = datetime.fromtimestamp(dt_timestamp)
                    entry_date = entry_datetime.date()
                    hour = entry_datetime.hour
                    
                    # Night time: 22:00-23:59 today OR 00:00-05:00 tomorrow
                    is_night = ((entry_date == today_date and hour >= 22) or 
                               (entry_date == today_date + timedelta(days=1) and hour <= 5))
                    
                    if is_night:
                        # Create a simple WeatherPoint-like object for debugging
                        from dataclasses import dataclass
                        @dataclass
                        class DebugWeatherPoint:
                            time: datetime
                            temperature: Optional[float]
                            rain_probability: Optional[float]
                            precipitation: Optional[float]
                            wind_speed: Optional[float]
                            wind_gusts: Optional[float]
                            thunderstorm_probability: Optional[float]
                        
                        temperature = self._extract_temperature(entry)
                        wind_speed = self._extract_wind_speed(entry)
                        wind_gusts = self._extract_wind_gusts(entry)
                        precipitation_amount = self._extract_precipitation_amount(entry)
                        weather_condition = self._extract_weather_condition(entry)
                        precipitation_probability = entry.get('precipitation_probability')
                        
                        thunderstorm_probability = self._determine_thunderstorm_probability(
                            weather_condition, precipitation_probability
                        )
                        rain_probability = self._determine_rain_probability(
                            weather_condition, precipitation_probability, precipitation_amount
                        )
                        
                        debug_point = DebugWeatherPoint(
                            time=entry_datetime,
                            temperature=temperature,
                            rain_probability=rain_probability,
                            precipitation=precipitation_amount,
                            wind_speed=wind_speed,
                            wind_gusts=wind_gusts,
                            thunderstorm_probability=thunderstorm_probability
                        )
                        points.append(debug_point)
                        
                except Exception as e:
                    logger.warning(f"Failed to process night forecast entry: {e}")
                    continue
            
            print(f"🌙 Found {len(points)} night weather points for {location_name}")
            return points
            
        except Exception as e:
            logger.error(f"Failed to get night points for {location_name}: {e}")
            return []

    def _get_all_points_of_stage(self, stage_type: str, target_date: datetime.date):
        """
        Get weather points for all coordinates of a stage (from etappen.json).
        stage_type: 'today', 'tomorrow', 'day_after_tomorrow'
        Returns a list of tuples: (label, points_list)
        """
        import json
        import yaml
        try:
            # Lade Etappen aus etappen.json
            with open('etappen.json', 'r', encoding='utf-8') as f:
                etappen = json.load(f)
            
            # Lade config.yaml für startdatum
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            startdatum = config.get('startdatum', '2025-06-21')
            start_date = datetime.strptime(startdatum, '%Y-%m-%d').date()
            
            # Ermittle aktuelle Etappe (heute), morgen, übermorgen
            base_date = datetime.now().date()
            if stage_type == 'today':
                stage_index = (base_date - start_date).days
            elif stage_type == 'tomorrow':
                stage_index = (base_date - start_date).days + 1
            elif stage_type == 'day_after_tomorrow':
                stage_index = (base_date - start_date).days + 2
            else:
                return []
            
            if stage_index < 0 or stage_index >= len(etappen):
                print(f"⚠️  Stage index {stage_index} out of range (0-{len(etappen)-1}) for {stage_type}")
                return []
            
            stage = etappen[stage_index]
            stage_name = stage['name']
            coordinates = stage['punkte']  # Changed from 'coordinates' to 'punkte'
            
            print(f"🔍 Fetching weather data for {stage_name} ({stage_type}, index {stage_index})")
            
            client = MeteoFranceClient()
            results = []
            
            for i, coord in enumerate(coordinates):
                lat, lon = coord['lat'], coord['lon']
                label = f"{stage_name} Point {i+1} ({lat:.5f}, {lon:.5f})"
                
                try:
                    forecast = client.get_forecast(lat, lon)
                    points = []
                    
                    if forecast.forecast:
                        for entry in forecast.forecast:
                            try:
                                dt_timestamp = entry.get('dt')
                                if not dt_timestamp:
                                    continue
                                    
                                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                                entry_date = entry_datetime.date()
                                
                                # Filter by target date and time window (05:00-17:00)
                                if entry_date == target_date and 5 <= entry_datetime.hour <= 17:
                                    # Create a simple WeatherPoint-like object for debugging
                                    from dataclasses import dataclass
                                    @dataclass
                                    class DebugWeatherPoint:
                                        time: datetime
                                        temperature: Optional[float]
                                        rain_probability: Optional[float]
                                        precipitation: Optional[float]
                                        wind_speed: Optional[float]
                                        wind_gusts: Optional[float]
                                        thunderstorm_probability: Optional[float]
                                    
                                    temperature = self._extract_temperature(entry)
                                    wind_speed = self._extract_wind_speed(entry)
                                    wind_gusts = self._extract_wind_gusts(entry)
                                    precipitation_amount = self._extract_precipitation_amount(entry)
                                    weather_condition = self._extract_weather_condition(entry)
                                    precipitation_probability = entry.get('precipitation_probability')
                                    
                                    thunderstorm_probability = self._determine_thunderstorm_probability(
                                        weather_condition, precipitation_probability
                                    )
                                    rain_probability = self._determine_rain_probability(
                                        weather_condition, precipitation_probability, precipitation_amount
                                    )
                                    
                                    debug_point = DebugWeatherPoint(
                                        time=entry_datetime,
                                        temperature=temperature,
                                        rain_probability=rain_probability,
                                        precipitation=precipitation_amount,
                                        wind_speed=wind_speed,
                                        wind_gusts=wind_gusts,
                                        thunderstorm_probability=thunderstorm_probability
                                    )
                                    points.append(debug_point)
                                    
                            except Exception as e:
                                logger.warning(f"Failed to process forecast entry for {label}: {e}")
                                continue
                    
                    print(f"📊 Found {len(points)} weather points for {label}")
                    results.append((label, points))
                    
                except Exception as e:
                    logger.error(f"Failed to get weather data for {label}: {e}")
                    results.append((label, []))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get stage points: {e}")
            return []

    def _get_stage_index_for_date(self, date: datetime.date, etappen: list) -> Optional[int]:
        """
        Ermittle den Index der Etappe für ein bestimmtes Datum anhand von startdatum aus config.yaml.
        """
        try:
            import yaml
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            startdatum = config.get('startdatum')
            if not startdatum:
                return None
            start_date = datetime.strptime(startdatum, '%Y-%m-%d').date()
            delta = (date - start_date).days
            if 0 <= delta < len(etappen):
                return delta
            return None
        except Exception as e:
            logger.error(f"Failed to determine stage index for date {date}: {e}")
            return None

    def _calculate_global_maxima_for_stage(self, report_type: str, target_date: datetime.date) -> Dict[str, Any]:
        """
        Calculate global maxima across all points of a stage by extracting from debug output.
        
        Args:
            report_type: Type of report ('morning', 'evening', 'update')
            target_date: Target date for weather data
            
        Returns:
            Dictionary with global maxima values
        """
        try:
            # Get stage type based on report type
            if report_type == 'evening':
                stage_type = 'tomorrow'  # Evening report uses tomorrow's stage
            else:
                stage_type = 'today'  # Morning and update reports use today's stage
            
            # Get all points for the stage
            stage_points = self._get_all_points_of_stage(stage_type, target_date)
            
            if not stage_points:
                logger.warning(f"No stage points found for {stage_type} on {target_date}")
                return {}
            
            # Extract global maxima from the debug output format
            all_temps = []
            all_rain_probs = []
            all_precipitations = []
            all_wind_speeds = []
            all_wind_gusts = []
            all_thunderstorms = []
            
            for label, points in stage_points:
                for point in points:
                    if point.temperature is not None:
                        all_temps.append((point.temperature, point.time, label))
                    if point.rain_probability is not None:
                        all_rain_probs.append((point.rain_probability, point.time, label))
                    if point.precipitation is not None:
                        all_precipitations.append((point.precipitation, point.time, label))
                    if point.wind_speed is not None:
                        all_wind_speeds.append((point.wind_speed, point.time, label))
                    if point.wind_gusts is not None:
                        all_wind_gusts.append((point.wind_gusts, point.time, label))
                    if point.thunderstorm_probability is not None:
                        all_thunderstorms.append((point.thunderstorm_probability, point.time, label))
            
            # Calculate global maxima
            global_maxima = {}
            
            if all_temps:
                max_temp_data = max(all_temps, key=lambda x: x[0])
                min_temp_data = min(all_temps, key=lambda x: x[0])
                global_maxima.update({
                    'max_temperature': max_temp_data[0],
                    'max_temperature_time': max_temp_data[1].strftime('%H'),
                    'min_temperature': min_temp_data[0],
                    'min_temperature_time': min_temp_data[1].strftime('%H')
                })
            
            if all_rain_probs:
                max_rain_prob_data = max(all_rain_probs, key=lambda x: x[0])
                global_maxima.update({
                    'max_rain_probability': max_rain_prob_data[0],
                    'rain_max_time': max_rain_prob_data[1].strftime('%H')
                })
            
            if all_precipitations:
                max_precip_data = max(all_precipitations, key=lambda x: x[0])
                global_maxima.update({
                    'max_precipitation': max_precip_data[0],
                    'precipitation_time': max_precip_data[1].strftime('%H')
                })
            
            if all_wind_speeds:
                max_wind_data = max(all_wind_speeds, key=lambda x: x[0])
                global_maxima.update({
                    'max_wind_speed': max_wind_data[0],
                    'wind_speed_time': max_wind_data[1].strftime('%H')
                })
            
            if all_wind_gusts:
                max_gusts_data = max(all_wind_gusts, key=lambda x: x[0])
                global_maxima.update({
                    'max_wind_gusts': max_gusts_data[0],
                    'wind_gusts_time': max_gusts_data[1].strftime('%H')
                })
            
            if all_thunderstorms:
                max_thunder_data = max(all_thunderstorms, key=lambda x: x[0])
                global_maxima.update({
                    'max_thunderstorm_probability': max_thunder_data[0],
                    'thunderstorm_max_time': max_thunder_data[1].strftime('%H')
                })
            
            # Set default wind_speed to max_wind_speed if available
            if 'max_wind_speed' in global_maxima:
                global_maxima['wind_speed'] = global_maxima['max_wind_speed']
            
            logger.info(f"Calculated global maxima for {stage_type} stage: {global_maxima}")
            return global_maxima
            
        except Exception as e:
            logger.error(f"Failed to calculate global maxima for stage: {e}")
            return {}


def process_weather_data_for_report(
    latitude: float,
    longitude: float,
    location_name: str,
    config: Dict[str, Any],
    report_type: str = 'morning',
    hours_ahead: int = 24
) -> Dict[str, Any]:
    """
    Process weather data for report generation.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        location_name: Name of the location
        config: Configuration dictionary
        report_type: Type of report ('morning', 'evening', 'update')
        hours_ahead: Number of hours ahead to fetch
        
    Returns:
        Dictionary containing processed weather data
    """
    processor = WeatherDataProcessor(config)
    return processor.process_weather_data(latitude, longitude, location_name, report_type, hours_ahead) 