#!/usr/bin/env python3
"""
Morning-Evening Refactor Implementation

This module implements the specific requirements from morning-evening-refactor.md:
- Specific data sources (meteo_france / DAILY_FORECAST, FORECAST, etc.)
- Specific output formats (N8, D24, R0.2@6(1.40@16), etc.)
- Debug output with # DEBUG DATENEXPORT marker
- Persistence to .data/weather_reports/YYYY-MM-DD/{etappenname}.json
"""

import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class WeatherThresholdData:
    """Data structure for threshold and maximum values with timing."""
    threshold_value: Optional[float] = None
    threshold_time: Optional[str] = None
    max_value: Optional[float] = None
    max_time: Optional[str] = None
    geo_points: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.geo_points is None:
            self.geo_points = []

@dataclass
class WeatherReportData:
    """Complete weather report data structure."""
    stage_name: str
    report_date: date
    report_type: str  # 'morning' or 'evening'
    
    # Weather elements
    night: WeatherThresholdData
    day: WeatherThresholdData
    rain_mm: WeatherThresholdData
    rain_percent: WeatherThresholdData
    wind: WeatherThresholdData
    gust: WeatherThresholdData
    thunderstorm: WeatherThresholdData
    thunderstorm_plus_one: WeatherThresholdData
    risks: WeatherThresholdData
    risk_zonal: WeatherThresholdData
    
    # Debug information
    debug_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.debug_info is None:
            self.debug_info = {}

class MorningEveningRefactor:
    """
    Implementation of the morning-evening refactor requirements.
    
    This class handles:
    - Specific data source mapping (meteo_france / DAILY_FORECAST, etc.)
    - Threshold logic for each weather element
    - Result output formatting (N8, D24, R0.2@6(1.40@16), etc.)
    - Debug output generation
    - Persistence to JSON files
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the refactor implementation.
        
        Args:
            config: Configuration dictionary from config.yaml
        """
        self.config = config
        self.thresholds = {
            'rain_amount': config.get('thresholds', {}).get('rain_amount', 0.2),
            'rain_probability': config.get('thresholds', {}).get('rain_probability', 20.0),
            'wind_speed': config.get('thresholds', {}).get('wind_speed', 10.0),
            'wind_gust_threshold': config.get('thresholds', {}).get('wind_gust_threshold', 20.0),
            'wind_gust_percentage': config.get('thresholds', {}).get('wind_gust_percentage', 50.0),
            'temperature': config.get('thresholds', {}).get('temperature', 25.0),
            'thunderstorm_probability': config.get('thresholds', {}).get('thunderstorm_probability', 10.0),
            'thunderstorm_warning_level': config.get('thresholds', {}).get('thunderstorm_warning_level', 'low')
        }
        
        # Ensure data directory exists
        self.data_dir = ".data/weather_reports"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_stage_coordinates(self, stage_name: str) -> List[Tuple[float, float]]:
        """
        Get coordinates for a specific stage from etappen.yaml.
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            List of (lat, lon) coordinate tuples
        """
        try:
            from src.position.etappenlogik import get_stage_info
            stage_info = get_stage_info(self.config)
            
            if stage_info and stage_info.get("name") == stage_name:
                return stage_info.get("coordinates", [])
            
            # If not current stage, load from etappen.json
            import json
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            for etappe in etappen_data:
                if etappe.get("name") == stage_name:
                    # Convert punkte to coordinates format
                    punkte = etappe.get("punkte", [])
                    coordinates = [(point["lat"], point["lon"]) for point in punkte]
                    return coordinates
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get coordinates for stage {stage_name}: {e}")
            return []
    
    def fetch_weather_data(self, stage_name: str, target_date: date) -> Dict[str, Any]:
        """
        Fetch weather data from meteo_france API for specific data sources.
        
        Args:
            stage_name: Name of the stage
            target_date: Target date for weather data
            
        Returns:
            Dictionary with weather data from different sources
        """
        try:
            from meteofrance_api import MeteoFranceClient
            
            client = MeteoFranceClient()
            coordinates = self.get_stage_coordinates(stage_name)
            
            if not coordinates:
                logger.error(f"No coordinates found for stage {stage_name}")
                return {}
            
            # Fetch data for ALL coordinates (G1, G2, G3)
            hourly_data = []
            
            for i, (lat, lon) in enumerate(coordinates):
                # Fetch raw forecast data for this coordinate
                forecast = client.get_forecast(lat, lon)
                
                if hasattr(forecast, 'forecast') and forecast.forecast:
                    hourly_data.append({
                        'data': forecast.forecast
                    })
                else:
                    logger.warning(f"No forecast data available for coordinate {i+1} ({lat}, {lon})")
                    # Add empty data to maintain structure
                    hourly_data.append({
                        'data': []
                    })
            
            # Structure the data for processing
            weather_data = {
                'daily_forecast': {'daily': []},  # Will be populated from first coordinate
                'hourly_data': hourly_data,
                'probability_forecast': []  # Will be populated for all coordinates
            }
            
            # Add daily forecast from ALL coordinates
            daily_forecast_data = []
            for i, (lat, lon) in enumerate(coordinates):
                forecast = client.get_forecast(lat, lon)
                if hasattr(forecast, 'daily_forecast') and forecast.daily_forecast:
                    daily_forecast_data.extend(forecast.daily_forecast)
                else:
                    logger.warning(f"No daily forecast data available for coordinate {i+1} ({lat}, {lon})")
            
            weather_data['daily_forecast'] = {'daily': daily_forecast_data}
            
            # Add probability forecast for all coordinates
            probability_forecast = []
            for i, (lat, lon) in enumerate(coordinates):
                forecast = client.get_forecast(lat, lon)
                if hasattr(forecast, 'probability_forecast') and forecast.probability_forecast:
                    probability_forecast.append({
                        'data': forecast.probability_forecast
                    })
                else:
                    logger.warning(f"No probability forecast data available for coordinate {i+1} ({lat}, {lon})")
                    # Add empty data to maintain structure
                    probability_forecast.append({
                        'data': []
                    })
            
            weather_data['probability_forecast'] = probability_forecast
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Failed to fetch weather data for {stage_name}: {e}")
            return {}
    
    def process_night_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process night data (temp_min from DAILY_FORECAST) using unified processing.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date
            report_type: 'morning' or 'evening'
            
        Returns:
            WeatherThresholdData for night temperature
        """
        try:
            # Get stage coordinates to find the last point (T1G3)
            import json
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            # Find current stage
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (target_date - start_date).days
            stage_idx = days_since_start  # Today's stage for Night
            
            if stage_idx >= len(etappen_data):
                logger.error(f"Stage index {stage_idx} out of range")
                return WeatherThresholdData()
            
            stage = etappen_data[stage_idx]
            stage_points = stage.get('punkte', [])
            
            if not stage_points:
                logger.error(f"No points found for stage {stage['name']}")
                return WeatherThresholdData()
            
            # Get the last point's coordinates (T1G3)
            last_point = stage_points[-1]
            last_lat, last_lon = last_point['lat'], last_point['lon']
            
            # Fetch weather data for the last point using EnhancedMeteoFranceAPI
            from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
            api = EnhancedMeteoFranceAPI()
            last_point_name = f"{stage['name']}_point_{len(stage_points)}"
            
            # Fetch weather data for the last point (T1G3 - Marseille)
            last_point_data = api.get_complete_forecast_data(last_lat, last_lon, last_point_name)
            
            # Extract daily forecast data
            daily_forecast = last_point_data.get('daily_forecast', {})
            if 'daily' not in daily_forecast:
                logger.error(f"No daily forecast data for {last_point_name}")
                return WeatherThresholdData()
            
            daily_data = daily_forecast['daily']
            
            # Find the entry for the target date
            target_date_str = target_date.strftime('%Y-%m-%d')
            point_value = None
            
            for day_data in daily_data:
                entry_dt = day_data.get('dt')
                if entry_dt:
                    entry_date = datetime.fromtimestamp(entry_dt).date()
                    entry_date_str = entry_date.strftime('%Y-%m-%d')
                    
                    if entry_date_str == target_date_str:
                        # Extract temp_min value
                        point_value = day_data.get('T', {}).get('min')
                        break
            
            if point_value is None:
                logger.error(f"No temperature data found for {target_date_str}")
                return WeatherThresholdData()
            
            # Create result with T1G3 reference (last point of today's stage - Marseille)
            geo_points = [{"T1G3": point_value}]
            
            # Round values for temperature display
            rounded_value = round(point_value)
            
            result = WeatherThresholdData(
                threshold_value=rounded_value,  # For night (temp_min)
                threshold_time=None,  # Daily data has no specific time
                max_value=rounded_value,  # For night (temp_min)
                max_time=None,  # Daily data has no specific time
                geo_points=geo_points
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process night data: {e}")
            return WeatherThresholdData()
    
    def process_day_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process day data (temp_max from DAILY_FORECAST).
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date
            report_type: 'morning' or 'evening'
            
        Returns:
            WeatherThresholdData for day temperature
        """
        try:
            # Get the correct stage and date based on report type
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (target_date - start_date).days
            
            # For Evening report: Day = temp_max of all points of tomorrow's stage for tomorrow
            # For Morning report: Day = temp_max of all points of today's stage for today
            if report_type == 'evening':
                stage_idx = days_since_start + 1  # Tomorrow's stage
                stage_date = target_date + timedelta(days=1)  # Tomorrow's date
            else:  # morning
                stage_idx = days_since_start  # Today's stage
                stage_date = target_date  # Today's date
            
            # Get stage coordinates
            import json
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            if stage_idx >= len(etappen_data):
                logger.error(f"Stage index {stage_idx} out of range")
                return WeatherThresholdData()
            
            stage = etappen_data[stage_idx]
            stage_points = stage.get('punkte', [])
            
            if not stage_points:
                logger.error(f"No points found for stage {stage['name']}")
                return WeatherThresholdData()
            
            # Fetch weather data for all points
            from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
            api = EnhancedMeteoFranceAPI()
            
            geo_points = []
            max_temp = None
            
            for i, point in enumerate(stage_points):
                lat, lon = point['lat'], point['lon']
                point_name = f"{stage['name']}_point_{i+1}"
                
                # Fetch weather data for this point
                point_data = api.get_complete_forecast_data(lat, lon, point_name)
                
                # Get temp_max from daily forecast
                daily_forecast = point_data.get('daily_forecast', {})
                daily_data = daily_forecast.get('daily', [])
                
                for entry in daily_data:
                    entry_date = entry.get('date')
                    # Handle datetime.date objects
                    if isinstance(entry_date, date):
                        if entry_date == stage_date:
                            # Get temp_max from temperature object
                            temperature = entry.get('temperature', {})
                        temp_max = temperature.get('max') if temperature else None
                        
                        if temp_max is not None:
                            # Day uses today's stage for morning, tomorrow's stage for evening
                            if report_type == 'morning':
                                tg_ref = f"T1G{i+1}"
                            else:  # evening
                                tg_ref = f"T2G{i+1}"
                            geo_points.append({tg_ref: temp_max})
                            
                            # Track the maximum temperature
                            if max_temp is None or temp_max > max_temp:
                                max_temp = temp_max
                        break
            
            if max_temp is not None:
                return WeatherThresholdData(
                    threshold_value=round(max_temp),
                    threshold_time=None,  # Day is daily max, no specific time
                    max_value=round(max_temp),
                    max_time=None,
                    geo_points=geo_points
                )
            
            return WeatherThresholdData()
            
        except Exception as e:
            logger.error(f"Failed to process day data: {e}")
            return WeatherThresholdData()
    
    def process_rain_mm_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process rain (mm) data using unified processing logic.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date
            report_type: 'morning' or 'evening'
            
        Returns:
            WeatherThresholdData for rain (mm)
        """
        try:
            # Get the correct stage and date based on report type
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (target_date - start_date).days
            
            # For Evening report: Rain = rain maximum of all points of tomorrow's stage for tomorrow
            # For Morning report: Rain = rain maximum of all points of today's stage for today
            if report_type == 'evening':
                stage_date = target_date  # Use target_date (tomorrow) directly
            else:  # morning
                stage_date = target_date  # Today's date
            
            # Use unified processing with rain data extractor
            rain_threshold = self.thresholds.get('rain_amount', 0.2)
            rain_extractor = lambda h: h.get('rain', {}).get('1h', 0)
            
            result = self._process_unified_hourly_data(weather_data, stage_date, rain_extractor, rain_threshold, report_type, 'rain_mm')
            
            # Round values for rain (mm)
            if result.threshold_value is not None:
                result.threshold_value = round(result.threshold_value, 1)
            if result.max_value is not None:
                result.max_value = round(result.max_value, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process rain mm data: {e}")
            return WeatherThresholdData()
    
    def process_rain_percent_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process rain probability data from PROBABILITY_FORECAST using rain_3h.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date
            report_type: 'morning' or 'evening'
            
        Returns:
            WeatherThresholdData for rain probability
        """
        try:
            # Get the correct stage and date based on report type
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (target_date - start_date).days
            
            # For Evening report: PRain = rain probability maximum of all points of tomorrow's stage for tomorrow
            # For Morning report: PRain = rain probability maximum of all points of today's stage for today
            if report_type == 'evening':
                stage_idx = days_since_start + 1  # Tomorrow's stage
                stage_date = target_date + timedelta(days=1)  # Tomorrow's date
            else:  # morning
                stage_idx = days_since_start  # Today's stage
                stage_date = target_date  # Today's date
            
            # Get stage coordinates
            import json
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            if stage_idx >= len(etappen_data):
                logger.error(f"Stage index {stage_idx} out of range")
                return WeatherThresholdData()
            
            stage = etappen_data[stage_idx]
            stage_points = stage.get('punkte', [])
            
            if not stage_points:
                logger.error(f"No points found for stage {stage['name']}")
                return WeatherThresholdData()
            
            # Get probability forecast data from weather_data
            probability_forecast = weather_data.get('probability_forecast', [])
            rain_prob_threshold = self.thresholds.get('rain_probability', 15)
            
            # Process probability forecast data for each geo point
            geo_points = []
            global_max_prob = None
            global_max_time = None
            global_threshold_prob = None
            global_threshold_time = None
            
            # Process each geo point with its own probability data
            for i, point in enumerate(stage_points):
                point_max_prob = None
                point_max_time = None
                point_threshold_prob = None
                point_threshold_time = None
                point_prob_data = {}
                
                # Get probability data for this specific point
                point_probability_data = probability_forecast[i] if i < len(probability_forecast) else None
                
                if point_probability_data and 'data' in point_probability_data:
                    # Process 3-hour interval data for this point
                    for entry in point_probability_data['data']:
                        if 'dt' in entry and 'rain' in entry:
                            entry_time = datetime.fromtimestamp(entry['dt'])
                            entry_date = entry_time.date()
                            
                            if entry_date == stage_date:
                                # Get 3h rain probability (handle None values)
                                rain_prob_raw = entry.get('rain', {}).get('3h', 0)
                                rain_prob = rain_prob_raw if rain_prob_raw is not None else 0
                                
                                # Ensure we have a valid numeric value
                                if rain_prob is None:
                                    rain_prob = 0
                                
                                # Only use 3-hour intervals: 05:00, 08:00, 11:00, 14:00, 17:00
                                hour = entry_time.hour
                                if hour in [5, 8, 11, 14, 17]:
                                    hour_str = entry_time.strftime('%H')
                                    point_prob_data[hour_str] = rain_prob
                                    
                                    # Track maximum for this point
                                    if point_max_prob is None or rain_prob > point_max_prob:
                                        point_max_prob = rain_prob
                                        point_max_time = hour_str
                                    
                                    # Track threshold (earliest time when rain >= threshold)
                                    if rain_prob >= rain_prob_threshold and point_threshold_time is None:
                                        point_threshold_prob = rain_prob
                                        point_threshold_time = hour_str
                
                # Store point data with T-G reference
                tg_ref = self._get_tg_reference(report_type, 'rain_percent', i)
                geo_points.append({tg_ref: point_prob_data})
                
                # Update global maximum
                if point_max_prob is not None:
                    if global_max_prob is None or point_max_prob > global_max_prob:
                        global_max_prob = point_max_prob
                        global_max_time = point_max_time
                
                # Update global threshold (earliest time across all points)
                if point_threshold_time is not None:
                    if global_threshold_time is None or point_threshold_time < global_threshold_time:
                        global_threshold_prob = point_threshold_prob
                        global_threshold_time = point_threshold_time
            
            return WeatherThresholdData(
                threshold_value=global_threshold_prob,
                threshold_time=global_threshold_time,
                max_value=global_max_prob,
                max_time=global_max_time,
                geo_points=geo_points
            )
            
        except Exception as e:
            logger.error(f"Failed to process rain percent data: {e}")
            return WeatherThresholdData()

    def process_wind_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process wind data using unified processing logic.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date
            report_type: 'morning' or 'evening'
            
        Returns:
            WeatherThresholdData for wind
        """
        try:
            # Get the correct stage and date based on report type
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (target_date - start_date).days
            
            # For Evening report: Wind = wind maximum of all points of tomorrow's stage for tomorrow
            # For Morning report: Wind = wind maximum of all points of today's stage for today
            if report_type == 'evening':
                stage_date = target_date  # Use target_date (tomorrow) directly
            else:  # morning
                stage_date = target_date  # Today's date
            
            # Use unified processing with wind data extractor
            wind_threshold = self.thresholds.get('wind_speed', 1.0)
            wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
            
            result = self._process_unified_hourly_data(weather_data, stage_date, wind_extractor, wind_threshold, report_type, 'wind')
            
            # Debug output
            logger.info(f"Wind processing result: threshold_time={result.threshold_time}, threshold_value={result.threshold_value}, max_time={result.max_time}, max_value={result.max_value}")
            
            # Round values for wind
            if result.threshold_value is not None:
                result.threshold_value = round(result.threshold_value, 1)
            if result.max_value is not None:
                result.max_value = round(result.max_value, 1)
            
            logger.info(f"Wind processing final result: threshold_time={result.threshold_time}, threshold_value={result.threshold_value}, max_time={result.max_time}, max_value={result.max_value}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process wind data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return WeatherThresholdData()
    
    def process_gust_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process gust data using unified processing logic.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date
            report_type: 'morning' or 'evening'
            
        Returns:
            WeatherThresholdData for gust
        """
        try:
            # Get the correct stage and date based on report type
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            days_since_start = (target_date - start_date).days
            
            # For Evening report: Gust = gust maximum of all points of tomorrow's stage for tomorrow
            # For Morning report: Gust = gust maximum of all points of today's stage for today
            if report_type == 'evening':
                stage_date = target_date  # Use target_date (tomorrow) directly
            else:  # morning
                stage_date = target_date  # Today's date
            
            # Use unified processing with gust data extractor
            gust_threshold = self.thresholds.get('wind_gust_threshold', 5.0)
            gust_extractor = lambda h: h.get('wind', {}).get('gust', 0)
            
            result = self._process_unified_hourly_data(weather_data, stage_date, gust_extractor, gust_threshold, report_type, 'gust')
            
            # Round values for gust
            if result.threshold_value is not None:
                result.threshold_value = round(result.threshold_value, 1)
            if result.max_value is not None:
                result.max_value = round(result.max_value, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process gust data: {e}")
            return WeatherThresholdData()

    def process_thunderstorm_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process thunderstorm data from hourly forecast data.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date for the report
            report_type: Type of report ('morning' or 'evening')
            
        Returns:
            WeatherThresholdData with threshold and maximum values
        """
        result = WeatherThresholdData()
        result.geo_points = []
        
        if not weather_data or 'hourly_data' not in weather_data:
            logger.warning(f"No hourly data available for thunderstorm processing on {target_date}")
            return result
        
        hourly_data = weather_data['hourly_data']
        threshold = self.thresholds.get('thunderstorm', 'med')
        
        # Get the correct stage and date based on report type
        start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
        days_since_start = (target_date - start_date).days
        
        # For Evening report: Thunderstorm = thunderstorm maximum of all points of tomorrow's stage for tomorrow
        # For Morning report: Thunderstorm = thunderstorm maximum of all points of today's stage for today
        if report_type == 'evening':
            stage_date = target_date  # Use target_date (tomorrow) directly
        else:  # morning
            stage_date = target_date  # Today's date
        
        # Thunderstorm level mapping
        thunderstorm_levels = {
            'Risque d\'orages': 'low',
            'Averses orageuses': 'med', 
            'Orages': 'high'
        }
        
        # Level hierarchy for threshold comparison
        level_hierarchy = {'low': 1, 'med': 2, 'high': 3}
        threshold_level = level_hierarchy.get(threshold, 2)  # Default to 'med'
        
        # Process each geo point
        for geo_index, geo_data in enumerate(hourly_data):
            if not geo_data or 'data' not in geo_data:
                continue
                
            geo_name = f"G{geo_index + 1}"
            max_level = None
            max_level_time = None
            threshold_level_found = None
            threshold_level_time = None
            
            # Process hourly data for this geo point
            for hour_data in geo_data['data']:
                if not hour_data or 'dt' not in hour_data:
                    continue
                    
                try:
                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                    hour_date = hour_time.date()
                    
                    # Only process data for the stage date
                    if hour_date != stage_date:
                        continue
                    
                    # Extract weather condition
                    condition = hour_data.get('condition', '')
                    if not condition and 'weather' in hour_data:
                        weather_data = hour_data['weather']
                        condition = weather_data.get('desc', '')
                    thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                    
                    if thunderstorm_level == 'none':
                        continue
                    
                    hour_str = str(hour_time.hour)
                    current_level_value = level_hierarchy.get(thunderstorm_level, 0)
                    
                    # Check for threshold (first occurrence meeting threshold)
                    if (current_level_value >= threshold_level and 
                        threshold_level_found is None):
                        threshold_level_found = thunderstorm_level
                        threshold_level_time = hour_str
                    
                    # Check for maximum (highest level)
                    if (max_level is None or 
                        current_level_value > level_hierarchy.get(max_level, 0)):
                        max_level = thunderstorm_level
                        max_level_time = hour_str
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing thunderstorm data for {geo_name}: {e}")
                    continue
            
            # Add geo point data
            geo_point = {
                'name': geo_name,
                'threshold_value': threshold_level_found,
                'threshold_time': threshold_level_time,
                'max_value': max_level,
                'max_time': max_level_time
            }
            result.geo_points.append(geo_point)
            
            # Update overall result
            if threshold_level_found and (result.threshold_value is None or 
                                        threshold_level_time < result.threshold_time):
                result.threshold_value = threshold_level_found
                result.threshold_time = threshold_level_time
            
            if max_level and (result.max_value is None or 
                             level_hierarchy.get(max_level, 0) > level_hierarchy.get(result.max_value, 0)):
                result.max_value = max_level
                result.max_time = max_level_time
        
        return result
    
    def process_thunderstorm_plus_one_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process thunderstorm data for +1 day from hourly forecast data.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date for the report
            report_type: Type of report ('morning' or 'evening')
            
        Returns:
            WeatherThresholdData with threshold and maximum values for +1 day
        """
        # Calculate +1 day
        plus_one_date = target_date + timedelta(days=1)
        
        # For Evening report: Thunderstorm (+1) = thunderstorm maximum of all points of over-tomorrow's stage for over-tomorrow
        # For Morning report: Thunderstorm (+1) = thunderstorm maximum of all points of tomorrow's stage for tomorrow
        if report_type == 'evening':
            stage_date = plus_one_date + timedelta(days=1)  # Over-tomorrow's date
        else:  # morning
            stage_date = plus_one_date  # Tomorrow's date
        
        # Use the same logic as thunderstorm but for the correct stage_date
        result = WeatherThresholdData()
        result.geo_points = []
        
        if not weather_data or 'hourly_data' not in weather_data:
            logger.warning(f"No hourly data available for thunderstorm (+1) processing on {stage_date}")
            return result
        
        hourly_data = weather_data['hourly_data']
        threshold = self.thresholds.get('thunderstorm', 'med')
        
        # Thunderstorm level mapping
        thunderstorm_levels = {
            'Risque d\'orages': 'low',
            'Averses orageuses': 'med', 
            'Orages': 'high'
        }
        
        # Level hierarchy for threshold comparison
        level_hierarchy = {'low': 1, 'med': 2, 'high': 3}
        threshold_level = level_hierarchy.get(threshold, 2)  # Default to 'med'
        
        # Process each geo point
        for geo_index, geo_data in enumerate(hourly_data):
            if not geo_data or 'data' not in geo_data:
                continue
                
            geo_name = f"G{geo_index + 1}"
            max_level = None
            max_level_time = None
            threshold_level_found = None
            threshold_level_time = None
            
            # Process hourly data for this geo point
            for hour_data in geo_data['data']:
                if not hour_data or 'dt' not in hour_data:
                    continue
                    
                try:
                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                    hour_date = hour_time.date()
                    
                    # Only process data for the stage date
                    if hour_date != stage_date:
                        continue
                    
                    # Extract weather condition
                    condition = hour_data.get('condition', '')
                    if not condition and 'weather' in hour_data:
                        weather_data = hour_data['weather']
                        condition = weather_data.get('desc', '')
                    thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                    
                    if thunderstorm_level == 'none':
                        continue
                    
                    hour_str = str(hour_time.hour)
                    current_level_value = level_hierarchy.get(thunderstorm_level, 0)
                    
                    # Check for threshold (first occurrence meeting threshold)
                    if (current_level_value >= threshold_level and 
                        threshold_level_found is None):
                        threshold_level_found = thunderstorm_level
                        threshold_level_time = hour_str
                    
                    # Check for maximum (highest level)
                    if (max_level is None or 
                        current_level_value > level_hierarchy.get(max_level, 0)):
                        max_level = thunderstorm_level
                        max_level_time = hour_str
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing thunderstorm (+1) data for {geo_name}: {e}")
                    continue
            
            # Add geo point data
            geo_point = {
                'name': geo_name,
                'threshold_value': threshold_level_found,
                'threshold_time': threshold_level_time,
                'max_value': max_level,
                'max_time': max_level_time
            }
            result.geo_points.append(geo_point)
            
            # Update overall result
            if threshold_level_found and (result.threshold_value is None or 
                                        threshold_level_time < result.threshold_time):
                result.threshold_value = threshold_level_found
                result.threshold_time = threshold_level_time
            
            if max_level and (result.max_value is None or 
                             level_hierarchy.get(max_level, 0) > level_hierarchy.get(result.max_value, 0)):
                result.max_value = max_level
                result.max_time = max_level_time
        
        return result
    
    def process_risks_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process risks/warnings data - DISABLED: Vigilance API not in current specification.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date for the report
            report_type: Type of report ('morning' or 'evening')
            
        Returns:
            WeatherThresholdData with threshold and maximum values
        """
        result = WeatherThresholdData()
        result.geo_points = []
        
        # DISABLED: Vigilance API is not part of current specification
        # This function previously called MeteoFrance Vigilance API which is not allowed
        logger.info(f"Risks data processing disabled - Vigilance API not in current specification")
        return result
    
    def process_risk_zonal_data(self, weather_data: Dict[str, Any], stage_name: str, target_date: date, report_type: str) -> WeatherThresholdData:
        """
        Process risk zonal data from hourly forecast data.
        
        Args:
            weather_data: Weather data from API
            stage_name: Name of the stage
            target_date: Target date for the report
            report_type: Type of report ('morning' or 'evening')
            
        Returns:
            WeatherThresholdData with threshold and maximum values
        """
        result = WeatherThresholdData()
        result.geo_points = []
        
        try:
            if not weather_data or 'hourly_data' not in weather_data:
                logger.warning(f"No hourly data available for risk zonal processing on {target_date}")
                return result
            
            hourly_data = weather_data['hourly_data']
            threshold = self.thresholds.get('risk_zonal', 2) # Default to level 2 (Orange)
            
            # Risk Zonal level mapping
            risk_zonal_levels = {
                1: 'L',  # Gelb
                2: 'M',  # Orange  
                3: 'H',  # Rot
                4: 'R'   # Violett
            }
            
            # Level hierarchy for threshold comparison
            level_hierarchy = {'L': 1, 'M': 2, 'H': 3, 'R': 4}
            threshold_level = threshold
            
            max_level = None
            max_level_time = None
            threshold_level_found = None
            threshold_level_time = None
            
            # Process each geo point
            for geo_index, geo_data in enumerate(hourly_data):
                if not geo_data or 'data' not in geo_data:
                    continue
                    
                geo_name = f"G{geo_index + 1}"
                
                # Process hourly data for this geo point
                for hour_data in geo_data['data']:
                    if not hour_data or 'dt' not in hour_data:
                        continue
                        
                    try:
                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                        hour_date = hour_time.date()
                        
                        # Only process data for the target date
                        if hour_date != target_date:
                            continue
                        
                        # Extract weather condition
                        condition = hour_data.get('condition', '')
                        if not condition and 'weather' in hour_data:
                            weather_data = hour_data['weather']
                            condition = weather_data.get('desc', '')
                        
                        # Map condition to risk zonal level
                        risk_zonal_level = 'none'
                        if 'pluie' in condition.lower() or 'inondation' in condition.lower():
                            risk_zonal_level = 'L' # Gelb
                        elif 'orage' in condition.lower():
                            risk_zonal_level = 'M' # Orange
                        elif 'orages' in condition.lower():
                            risk_zonal_level = 'H' # Rot
                        elif 'orage violette' in condition.lower():
                            risk_zonal_level = 'R' # Violett
                        
                        current_level_value = level_hierarchy.get(risk_zonal_level, 0)
                        
                        # Check for threshold (first occurrence meeting threshold)
                        if (current_level_value >= threshold_level and 
                            threshold_level_found is None):
                            threshold_level_found = risk_zonal_level
                            threshold_level_time = str(hour_time.hour)
                            
                        # Check for maximum (highest level)
                        if (max_level is None or 
                            current_level_value > level_hierarchy.get(max_level, 0)):
                            max_level = risk_zonal_level
                            max_level_time = str(hour_time.hour)
                            
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error processing risk zonal data for {geo_name}: {e}")
                        continue
                
                # Add geo point data
                geo_point = {
                    'name': geo_name,
                    'threshold_value': threshold_level_found,
                    'threshold_time': threshold_level_time,
                    'max_value': max_level,
                    'max_time': max_level_time
                }
                result.geo_points.append(geo_point)
                
                # Update overall result
                if threshold_level_found:
                    result.threshold_value = threshold_level_found
                    result.threshold_time = threshold_level_time
                
                if max_level:
                    result.max_value = max_level
                    result.max_time = max_level_time
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process risk zonal data for {stage_name}: {e}")
            return result
    
    def format_result_output(self, report_data: WeatherReportData) -> str:
        """
        Format the result output according to specifications.
        
        Args:
            report_data: Complete weather report data
            
        Returns:
            Formatted result string (max 160 chars)
        """
        try:
            parts = []
            
            # Night
            if report_data.night.threshold_value is not None:
                parts.append(f"N{report_data.night.threshold_value}")
            else:
                parts.append("N-")
            
            # Day
            if report_data.day.threshold_value is not None:
                parts.append(f"D{report_data.day.threshold_value}")
            else:
                parts.append("D-")
            
            # Rain (mm)
            if report_data.rain_mm.threshold_value is not None:
                threshold_part = f"{report_data.rain_mm.threshold_value}@{report_data.rain_mm.threshold_time}"
                if report_data.rain_mm.max_value != report_data.rain_mm.threshold_value:
                    max_part = f"({report_data.rain_mm.max_value}@{report_data.rain_mm.max_time})"
                    parts.append(f"R{threshold_part}{max_part}")
                else:
                    parts.append(f"R{threshold_part}")
            else:
                parts.append("R-")
            
            # Rain (%)
            if report_data.rain_percent.threshold_value is not None and report_data.rain_percent.threshold_value > 0:
                threshold_part = f"{report_data.rain_percent.threshold_value}%@{report_data.rain_percent.threshold_time}"
                if report_data.rain_percent.max_value != report_data.rain_percent.threshold_value:
                    max_part = f"({report_data.rain_percent.max_value}%@{report_data.rain_percent.max_time})"
                    parts.append(f"PR{threshold_part}{max_part}")
                else:
                    parts.append(f"PR{threshold_part}")
            else:
                parts.append("PR-")
            
            # Wind
            if report_data.wind.threshold_value is not None:
                threshold_part = f"{report_data.wind.threshold_value}@{report_data.wind.threshold_time}"
                if report_data.wind.max_value != report_data.wind.threshold_value:
                    max_part = f"({report_data.wind.max_value}@{report_data.wind.max_time})"
                    parts.append(f"W{threshold_part}{max_part}")
                else:
                    parts.append(f"W{threshold_part}")
            else:
                parts.append("W-")
            
            # Gust
            if report_data.gust.threshold_value is not None:
                threshold_part = f"{report_data.gust.threshold_value}@{report_data.gust.threshold_time}"
                if report_data.gust.max_value != report_data.gust.threshold_value:
                    max_part = f"({report_data.gust.max_value}@{report_data.gust.max_time})"
                    parts.append(f"G{threshold_part}{max_part}")
                else:
                    parts.append(f"G{threshold_part}")
            else:
                parts.append("G-")
            
            # Thunderstorm
            if report_data.thunderstorm.threshold_value is not None:
                # Map level to single letter
                level_mapping = {'low': 'L', 'med': 'M', 'high': 'H'}
                threshold_level = level_mapping.get(report_data.thunderstorm.threshold_value, report_data.thunderstorm.threshold_value)
                max_level = level_mapping.get(report_data.thunderstorm.max_value, report_data.thunderstorm.max_value)
                
                threshold_part = f"{threshold_level}@{report_data.thunderstorm.threshold_time}"
                if report_data.thunderstorm.max_value != report_data.thunderstorm.threshold_value:
                    max_part = f"{max_level}@{report_data.thunderstorm.max_time}"
                    parts.append(f"TH:{threshold_part}({max_part})")
                else:
                    parts.append(f"TH:{threshold_part}")
            elif report_data.thunderstorm.max_value is not None:
                # Show maximum even if threshold not reached
                level_mapping = {'low': 'L', 'med': 'M', 'high': 'H'}
                max_level = level_mapping.get(report_data.thunderstorm.max_value, report_data.thunderstorm.max_value)
                max_part = f"{max_level}@{report_data.thunderstorm.max_time}"
                parts.append(f"TH:{max_part}")
            else:
                parts.append("TH-")
            
            # Thunderstorm (+1)
            if report_data.thunderstorm_plus_one.threshold_value is not None:
                # Map level to single letter
                level_mapping = {'low': 'L', 'med': 'M', 'high': 'H'}
                threshold_level = level_mapping.get(report_data.thunderstorm_plus_one.threshold_value, report_data.thunderstorm_plus_one.threshold_value)
                max_level = level_mapping.get(report_data.thunderstorm_plus_one.max_value, report_data.thunderstorm_plus_one.max_value)
                
                threshold_part = f"{threshold_level}@{report_data.thunderstorm_plus_one.threshold_time}"
                if report_data.thunderstorm_plus_one.max_value != report_data.thunderstorm_plus_one.threshold_value:
                    max_part = f"{max_level}@{report_data.thunderstorm_plus_one.max_time}"
                    parts.append(f"S+1:{threshold_part}({max_part})")
                else:
                    parts.append(f"S+1:{threshold_part}")
            else:
                parts.append("S+1:-")
            
            # Risks (Warnungen) - EXAKT wie spezifiziert
            if report_data.risks.threshold_value is not None:
                threshold_part = f"{report_data.risks.threshold_value}@{report_data.risks.threshold_time}"
                if report_data.risks.max_value != report_data.risks.threshold_value:
                    max_part = f"({report_data.risks.max_value}@{report_data.risks.max_time})"
                    parts.append(f"HR:{threshold_part}TH:{max_part}")
                else:
                    parts.append(f"HR:{threshold_part}TH:{threshold_part}")
            else:
                parts.append("HR:-TH:-")
            
            # Risk Zonal - EXAKT wie spezifiziert
            if report_data.risk_zonal.threshold_value is not None:
                parts.append(f"Z:{report_data.risk_zonal.threshold_value}")
            else:
                parts.append("Z:-")
            
            result = f"{report_data.stage_name}: {' '.join(parts)}"
            
            # Ensure max 160 characters
            if len(result) > 160:
                logger.warning(f"Result output exceeds 160 characters: {len(result)}")
                # Truncate if necessary
                result = result[:157] + "..."
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to format result output: {e}")
            return f"{report_data.stage_name}: ERROR"
    
    def _get_tg_reference(self, report_type: str, data_type: str, point_index: int) -> str:
        """
        Get T-G reference based on report type and data type.
        
        Args:
            report_type: 'morning' or 'evening'
            data_type: 'night', 'day', 'rain_mm', 'rain_percent', 'wind', 'gust', 'thunderstorm', 'thunderstorm_plus_one'
            point_index: 0-based point index
            
        Returns:
            T-G reference string (e.g., 'T1G1', 'T2G2')
        """
        if data_type == 'night':
            # Night: always today's stage (T1)
            return f"T1G{point_index + 1}"
        elif data_type == 'day':
            # Day: today's stage for morning, tomorrow's stage for evening
            if report_type == 'morning':
                return f"T1G{point_index + 1}"
            else:  # evening
                return f"T2G{point_index + 1}"
        elif data_type in ['rain_mm', 'rain_percent', 'wind', 'gust', 'thunderstorm']:
            # These use the same logic as 'day'
            if report_type == 'morning':
                return f"T1G{point_index + 1}"
            else:  # evening
                return f"T2G{point_index + 1}"
        elif data_type == 'thunderstorm_plus_one':
            # Thunderstorm (+1): tomorrow's stage for morning, day after tomorrow for evening
            if report_type == 'morning':
                return f"T2G{point_index + 1}"
            else:  # evening
                return f"T3G{point_index + 1}"
        else:
            # Default fallback
            return f"G{point_index + 1}"
        
    def _add_threshold_maximum_tables(self, debug_lines: List[str], report_data: WeatherReportData, 
                                    data_type: str, value_extractor: callable, threshold_key: str,
                                    unit: str = "", value_formatter: callable = None):
        """
        Add threshold and maximum tables as per specification.
        
        Args:
            debug_lines: List to append debug lines to
            report_data: Weather report data
            data_type: Data type for T-G reference
            value_extractor: Function to extract value from hour_data
            threshold_key: Threshold key from config
            unit: Unit suffix (e.g., "%", "mm")
            value_formatter: Optional function to format values
        """
        # TODO: Implement this helper function to reduce code duplication
        pass

    def generate_debug_output(self, report_data: WeatherReportData) -> str:
        """
        Generate debug output with # DEBUG DATENEXPORT marker.
        
        Args:
            report_data: Complete weather report data
            
        Returns:
            Debug output string
        """
        try:
            debug_lines = []
            debug_lines.append("# DEBUG DATENEXPORT")
            debug_lines.append("")
            
            # Check if debug is enabled in config
            if not self.config.get('debug', {}).get('enabled', False):
                return "\n".join(debug_lines)
            
            # Berichts-Typ
            debug_lines.append(f"Berichts-Typ: {report_data.report_type}")
            debug_lines.append("")
            
            # Calculate stage information based on start date
            start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
            today = report_data.report_date
            days_since_start = (today - start_date).days
            
            # Get stage information
            import json
            with open("etappen.json", "r") as f:
                etappen_data = json.load(f)
            
            # Calculate stage indices
            today_stage_idx = days_since_start
            tomorrow_stage_idx = days_since_start + 1
            day_after_tomorrow_stage_idx = days_since_start + 2
            
            # Get stage names
            today_stage = etappen_data[today_stage_idx] if today_stage_idx < len(etappen_data) else None
            tomorrow_stage = etappen_data[tomorrow_stage_idx] if tomorrow_stage_idx < len(etappen_data) else None
            day_after_tomorrow_stage = etappen_data[day_after_tomorrow_stage_idx] if day_after_tomorrow_stage_idx < len(etappen_data) else None
            
            # heute: Datum von heute, heutiger Etappenname, Anzahl Etappen-Punkte
            if today_stage:
                today_points_count = len(today_stage.get('punkte', []))
                debug_lines.append(f"heute: {today.strftime('%Y-%m-%d')}, {today_stage['name']}, {today_points_count} Punkte")
                # Add T1G coordinates
                for i, point in enumerate(today_stage.get('punkte', [])):
                    debug_lines.append(f"  T1G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
            else:
                debug_lines.append(f"heute: {today.strftime('%Y-%m-%d')}, keine Etappe verfügbar, 0 Punkte")
            
            # morgen: Datum von morgen, morgiger Etappenname, Anzahl Etappen-Punkte
            tomorrow = today + timedelta(days=1)
            if tomorrow_stage:
                tomorrow_points_count = len(tomorrow_stage.get('punkte', []))
                debug_lines.append(f"morgen: {tomorrow.strftime('%Y-%m-%d')}, {tomorrow_stage['name']}, {tomorrow_points_count} Punkte")
                # Add T2G coordinates
                for i, point in enumerate(tomorrow_stage.get('punkte', [])):
                    debug_lines.append(f"  T2G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
            else:
                debug_lines.append(f"morgen: {tomorrow.strftime('%Y-%m-%d')}, keine Etappe verfügbar, 0 Punkte")
            
            # übermorgen: only for evening reports
            if report_data.report_type == 'evening':
                day_after_tomorrow = today + timedelta(days=2)
                if day_after_tomorrow_stage:
                    day_after_tomorrow_points_count = len(day_after_tomorrow_stage.get('punkte', []))
                    debug_lines.append(f"übermorgen: {day_after_tomorrow.strftime('%Y-%m-%d')}, {day_after_tomorrow_stage['name']}, {day_after_tomorrow_points_count} Punkte")
                    # Add T3G coordinates
                    for i, point in enumerate(day_after_tomorrow_stage.get('punkte', [])):
                        debug_lines.append(f"  T3G{i+1} \"lat\": {point['lat']}, \"lon\": {point['lon']}")
                else:
                    debug_lines.append(f"übermorgen: {day_after_tomorrow.strftime('%Y-%m-%d')}, keine Etappe verfügbar, 0 Punkte")
            
            debug_lines.append("")
            
            # Night data debug (temp_min)
            if report_data.night.geo_points:
                debug_lines.append("NIGHT (N) - temp_min:")
                for i, point in enumerate(report_data.night.geo_points):
                    for geo, value in point.items():
                        # Night always uses today's stage (T1)
                        tg_ref = f"T1G{i+1}"
                        debug_lines.append(f"{tg_ref} | {value}")
                debug_lines.append("=========")
                debug_lines.append(f"MIN | {report_data.night.max_value}")
                debug_lines.append("")
            
            # Day data debug (temp_max)
            if report_data.day.geo_points:
                debug_lines.append("DAY (D) - temp_max:")
                for i, point in enumerate(report_data.day.geo_points):
                    for geo, value in point.items():
                        # Day uses today's stage for morning, tomorrow's stage for evening
                        if report_data.report_type == 'morning':
                            tg_ref = f"T1G{i+1}"
                        else:  # evening
                            tg_ref = f"T2G{i+1}"
                        debug_lines.append(f"{tg_ref} | {value}")
                debug_lines.append("=========")
                debug_lines.append(f"MAX | {report_data.day.max_value}")
                debug_lines.append("")
            
            # Rain mm data debug
            if report_data.rain_mm.geo_points:
                debug_lines.append("RAIN(MM)")
                for i, point in enumerate(report_data.rain_mm.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'rain_mm', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Rain (mm)")
                    
                    # Get raw hourly data for this geo point - show all 24 hours
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            # Create a dictionary of all hours with default value 0
                            all_hours = {str(hour): 0 for hour in range(24)}
                            
                            # Fill in actual data
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    # Use the SAME date logic as the processing functions
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date  # Use target_date (tomorrow) directly
                                    else:
                                        target_date = report_data.report_date  # Today's date
                                    if hour_date == target_date:
                                        time_str = str(hour_time.hour)
                                        rain_value = hour_data.get('rain', {}).get('1h', 0)
                                        all_hours[time_str] = rain_value
                            
                            # Display only hours 4:00 - 19:00 (as per specification)
                            for hour in range(4, 20):  # 4 to 19 inclusive
                                time_str = str(hour)
                                rain_value = all_hours[time_str]
                                debug_lines.append(f"{time_str}:00 | {rain_value}")
                    
                    # Add threshold and maximum for this point from processed data
                    debug_lines.append("=========")
                    # Calculate threshold and maximum for this specific point
                    point_threshold_time = None
                    point_threshold_value = None
                    point_max_time = None
                    point_max_value = None
                    
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if report_data.report_type == 'evening':
                                        target_date = report_data.report_date
                                    else:
                                        target_date = report_data.report_date
                                    if hour_date == target_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        rain_value = hour_data.get('rain', {}).get('1h', 0)
                                        
                                        # Track maximum (only if value > 0)
                                        if rain_value > 0 and (point_max_value is None or rain_value > point_max_value):
                                            point_max_value = rain_value
                                            point_max_time = str(hour_time.hour)
                                        
                                        # Track threshold (earliest time when rain >= threshold)
                                        if rain_value >= self.thresholds['rain_amount'] and point_threshold_time is None:
                                            point_threshold_time = str(hour_time.hour)
                                            point_threshold_value = rain_value
                    
                    # Add threshold and maximum for this point
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Add threshold and maximum tables as per specification
                if report_data.rain_mm.threshold_time is not None:
                    debug_lines.append("Threshold")
                    debug_lines.append("GEO | Time | mm")
                    for i, point in enumerate(report_data.rain_mm.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'rain_mm', i)
                        # Get threshold for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                point_threshold_time = None
                                point_threshold_value = None
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if report_data.report_type == 'evening':
                                            target_date = report_data.report_date
                                        else:
                                            target_date = report_data.report_date
                                        if hour_date == target_date:
                                            # Apply time filter: only 4:00 - 19:00 Uhr
                                            hour = hour_time.hour
                                            if hour < 4 or hour > 19:
                                                continue
                                            
                                            rain_value = hour_data.get('rain', {}).get('1h', 0)
                                            if rain_value >= self.thresholds['rain_amount'] and point_threshold_time is None:
                                                point_threshold_time = str(hour_time.hour)
                                                point_threshold_value = rain_value
                                                break
                                if point_threshold_time is not None:
                                    debug_lines.append(f"{tg_ref} | {point_threshold_time}:00 | {point_threshold_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"Threshold | {report_data.rain_mm.threshold_time}:00 | {report_data.rain_mm.threshold_value}")
                    debug_lines.append("")
                
                if report_data.rain_mm.max_time is not None:
                    debug_lines.append("Maximum:")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.rain_mm.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'rain_mm', i)
                        # Get maximum for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                point_max_time = None
                                point_max_value = None
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if report_data.report_type == 'evening':
                                            target_date = report_data.report_date
                                        else:
                                            target_date = report_data.report_date
                                        if hour_date == target_date:
                                            # Apply time filter: only 4:00 - 19:00 Uhr
                                            hour = hour_time.hour
                                            if hour < 4 or hour > 19:
                                                continue
                                            
                                            rain_value = hour_data.get('rain', {}).get('1h', 0)
                                            if point_max_value is None or rain_value > point_max_value:
                                                point_max_value = rain_value
                                                point_max_time = str(hour_time.hour)
                                if point_max_time is not None:
                                    debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.rain_mm.max_time}:00 | {report_data.rain_mm.max_value}")
                    debug_lines.append("")
            
            # Rain percent data debug
            if report_data.rain_percent.geo_points:
                debug_lines.append("RAIN(%)")
                for i, point in enumerate(report_data.rain_percent.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'rain_percent', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Rain (%)")
                    
                    # Get probability forecast data for this geo point
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        probability_forecast = self._last_weather_data.get('probability_forecast', [])
                        if i < len(probability_forecast) and 'data' in probability_forecast[i]:
                            # Get the correct stage date
                            if report_data.report_type == 'evening':
                                stage_date = report_data.report_date + timedelta(days=1)  # Tomorrow's date
                            else:
                                stage_date = report_data.report_date  # Today's date
                            
                            # Process 3-hour interval data for this point
                            for entry in probability_forecast[i]['data']:
                                if 'dt' in entry and 'rain' in entry:
                                    entry_time = datetime.fromtimestamp(entry['dt'])
                                    entry_date = entry_time.date()
                                    
                                    if entry_date == stage_date:
                                        # Get 3h rain probability
                                        rain_prob_raw = entry.get('rain', {}).get('3h', 0)
                                        rain_prob = rain_prob_raw if rain_prob_raw is not None else 0
                                        
                                        # Only use 3-hour intervals: 05:00, 08:00, 11:00, 14:00, 17:00
                                        hour = entry_time.hour
                                        if hour in [5, 8, 11, 14, 17]:
                                            hour_str = entry_time.strftime('%H')
                                            debug_lines.append(f"{hour_str}:00 | {rain_prob}")
                    
                    # Add threshold and maximum for this point from processed data
                    debug_lines.append("=========")
                    if report_data.rain_percent.threshold_time is not None:
                        debug_lines.append(f"{report_data.rain_percent.threshold_time}:00 | {report_data.rain_percent.threshold_value}% (Threshold)")
                    if report_data.rain_percent.max_time is not None:
                        debug_lines.append(f"{report_data.rain_percent.max_time}:00 | {report_data.rain_percent.max_value}% (Max)")
                    debug_lines.append("")
                
                # Add threshold and maximum tables as per specification
                if report_data.rain_percent.threshold_time is not None:
                    debug_lines.append("Threshold")
                    debug_lines.append("GEO | Time | %")
                    for i, point in enumerate(report_data.rain_percent.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'rain_percent', i)
                        # Get threshold for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            probability_forecast = self._last_weather_data.get('probability_forecast', [])
                            if i < len(probability_forecast) and 'data' in probability_forecast[i]:
                                # Get the correct stage date
                                if report_data.report_type == 'evening':
                                    stage_date = report_data.report_date + timedelta(days=1)
                                else:
                                    stage_date = report_data.report_date
                                
                                point_threshold_time = None
                                point_threshold_value = None
                                rain_prob_threshold = self.thresholds.get('rain_probability', 15)
                                
                                for entry in probability_forecast[i]['data']:
                                    if 'dt' in entry and 'rain' in entry:
                                        entry_time = datetime.fromtimestamp(entry['dt'])
                                        entry_date = entry_time.date()
                                        
                                        if entry_date == stage_date:
                                            rain_prob = entry.get('rain', {}).get('3h', 0)
                                            hour = entry_time.hour
                                            if hour in [5, 8, 11, 14, 17]:
                                                if rain_prob >= rain_prob_threshold and point_threshold_time is None:
                                                    point_threshold_time = str(entry_time.hour)
                                                    point_threshold_value = rain_prob
                                                    break
                                
                                if point_threshold_time is not None:
                                    debug_lines.append(f"{tg_ref} | {point_threshold_time}:00 | {point_threshold_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"Threshold | {report_data.rain_percent.threshold_time}:00 | {report_data.rain_percent.threshold_value}")
                    debug_lines.append("")
                
                if report_data.rain_percent.max_time is not None:
                    debug_lines.append("Maximum:")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.rain_percent.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'rain_percent', i)
                        # Get maximum for this point from processed data
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            probability_forecast = self._last_weather_data.get('probability_forecast', [])
                            if i < len(probability_forecast) and 'data' in probability_forecast[i]:
                                # Get the correct stage date
                                if report_data.report_type == 'evening':
                                    stage_date = report_data.report_date + timedelta(days=1)
                                else:
                                    stage_date = report_data.report_date
                                
                                point_max_time = None
                                point_max_value = None
                                
                                for entry in probability_forecast[i]['data']:
                                    if 'dt' in entry and 'rain' in entry:
                                        entry_time = datetime.fromtimestamp(entry['dt'])
                                        entry_date = entry_time.date()
                                        
                                        if entry_date == stage_date:
                                            rain_prob = entry.get('rain', {}).get('3h', 0)
                                            hour = entry_time.hour
                                            if hour in [5, 8, 11, 14, 17]:
                                                if point_max_value is None or rain_prob > point_max_value:
                                                    point_max_value = rain_prob
                                                    point_max_time = str(entry_time.hour)
                                
                                if point_max_time is not None:
                                    debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.rain_percent.max_time}:00 | {report_data.rain_percent.max_value}")
                    debug_lines.append("")
                

            
            # Wind data debug
            if report_data.wind.geo_points:
                debug_lines.append("WIND")
                for i, point in enumerate(report_data.wind.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Wind (km/h)")
                    
                    # Get raw hourly data for this geo point
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        debug_lines.append(f"{time_str}:00 | {wind_speed}")
                    
                    # Calculate threshold and maximum for this point from raw data
                    point_threshold_time = None
                    point_max_time = None
                    point_max_value = None
                    point_threshold_value = None
                    
                    # Extract time and wind data from raw hourly data
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        
                                        # Track maximum
                                        if point_max_value is None or wind_speed > point_max_value:
                                            point_max_value = wind_speed
                                            point_max_time = time_str
                                        
                                        # Track threshold (earliest time when wind >= threshold)
                                        if wind_speed >= self.thresholds.get('wind_speed', 10) and point_threshold_time is None:
                                            point_threshold_time = time_str
                                            point_threshold_value = wind_speed
                    
                    # Add threshold and maximum for this point
                    debug_lines.append("=========")
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Use processed data from report_data.wind
                global_max_value = report_data.wind.max_value
                global_max_time = report_data.wind.max_time
                
                # Add threshold and maximum tables as per specification
                # Always show threshold table, even if no threshold reached
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | km/h")
                wind_threshold = self.thresholds.get('wind_speed', 1.0)
                for i, point in enumerate(report_data.wind.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                    # Calculate threshold for this point using the same logic as processing
                    point_threshold_time = None
                    point_threshold_value = None
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        # Use the same extractor as in processing
                                        wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                        if wind_speed >= wind_threshold and point_threshold_time is None:
                                            point_threshold_time = str(hour_time.hour)
                                            point_threshold_value = wind_speed
                                            break
                    if point_threshold_time is not None:
                        debug_lines.append(f"{tg_ref} | {point_threshold_time}:00 | {point_threshold_value}")
                    else:
                        debug_lines.append(f"{tg_ref} | - | -")
                debug_lines.append("=========")
                if report_data.wind.threshold_time is not None:
                    debug_lines.append(f"Threshold | {report_data.wind.threshold_time}:00 | {report_data.wind.threshold_value}")
                else:
                    debug_lines.append("Threshold | - | -")
                debug_lines.append("")
                
                if global_max_time is not None:
                    debug_lines.append("Maximum:")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.wind.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)
                        # Calculate maximum for this point
                        point_max_time = None
                        point_max_value = None
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if hour_date == report_data.report_date:
                                            # Apply time filter: only 4:00 - 19:00 Uhr
                                            hour = hour_time.hour
                                            if hour < 4 or hour > 19:
                                                continue
                                            
                                            wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                            if point_max_value is None or wind_speed > point_max_value:
                                                point_max_value = wind_speed
                                                point_max_time = str(hour_time.hour)
                        if point_max_time is not None:
                            debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {global_max_time}:00 | {global_max_value}")
                    debug_lines.append("")
            
            # Gust data debug
            if report_data.gust.geo_points:
                debug_lines.append("GUST")
                for i, point in enumerate(report_data.gust.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Gust (km/h)")
                    
                    # Get raw hourly data for this geo point
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        gust_value = hour_data.get('wind', {}).get('gust', 0)
                                        debug_lines.append(f"{time_str}:00 | {gust_value}")
                    
                    # Calculate threshold and maximum for this point
                    point_threshold_time = None
                    point_max_time = None
                    point_max_value = None
                    point_threshold_value = None
                    
                    # Extract time and gust data from the point
                    for geo, time_data in point.items():
                        if isinstance(time_data, dict):
                            for time_str, gust_value in time_data.items():
                                # Track maximum
                                if point_max_value is None or gust_value > point_max_value:
                                    point_max_value = gust_value
                                    point_max_time = time_str
                                
                                # Track threshold (earliest time when gust >= threshold)
                                if gust_value >= self.thresholds.get('wind_gust_threshold', 5.0) and point_threshold_time is None:
                                    point_threshold_time = time_str
                                    point_threshold_value = gust_value
                    
                    # Add threshold and maximum for this point
                    debug_lines.append("=========")
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Add threshold and maximum tables as per specification
                if report_data.gust.threshold_time is not None:
                    debug_lines.append("Threshold")
                    debug_lines.append("GEO | Time | km/h")
                    for i, point in enumerate(report_data.gust.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                        # Calculate threshold for this point
                        point_threshold_time = None
                        point_threshold_value = None
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if hour_date == report_data.report_date:
                                            gust_value = hour_data.get('wind', {}).get('gust', 0)
                                            if gust_value >= self.thresholds.get('wind_gust_threshold', 5.0) and point_threshold_time is None:
                                                point_threshold_time = str(hour_time.hour)
                                                point_threshold_value = gust_value
                                                break
                        if point_threshold_time is not None:
                            debug_lines.append(f"{tg_ref} | {point_threshold_time}:00 | {point_threshold_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"Threshold | {report_data.gust.threshold_time}:00 | {report_data.gust.threshold_value}")
                    debug_lines.append("")
                
                if report_data.gust.max_time is not None:
                    debug_lines.append("Maximum:")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.gust.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)
                        # Calculate maximum for this point
                        point_max_time = None
                        point_max_value = None
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if hour_date == report_data.report_date:
                                            gust_value = hour_data.get('wind', {}).get('gust', 0)
                                            if point_max_value is None or gust_value > point_max_value:
                                                point_max_value = gust_value
                                                point_max_time = str(hour_time.hour)
                        if point_max_time is not None:
                            debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.gust.max_time}:00 | {report_data.gust.max_value}")
                    debug_lines.append("")
            
            # Thunderstorm data debug
            if report_data.thunderstorm.geo_points:
                debug_lines.append("THUNDERSTORM")
                for i, point in enumerate(report_data.thunderstorm.geo_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'thunderstorm', i)
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Storm")
                    
                    # Get raw hourly data for this geo point
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            # Show only 4:00 - 19:00 Uhr (as per specification)
                            for hour in range(4, 20):  # 4 to 19 inclusive
                                time_str = str(hour)
                                thunderstorm_level = 'none'
                                
                                # Find matching hour data
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if hour_date == report_data.report_date and hour_time.hour == hour:
                                            weather_data = hour_data.get('weather', {})
                                            condition = weather_data.get('desc', '')
                                            
                                            # Check for thunderstorm conditions
                                            thunderstorm_levels = {
                                                'Risque d\'orages': 'low',
                                                'Averses orageuses': 'med', 
                                                'Orages': 'high'
                                            }
                                            thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                                            break
                                
                                debug_lines.append(f"{time_str}:00 | {thunderstorm_level}")
                    
                    # Calculate threshold and maximum for this point from raw data
                    point_threshold_time = None
                    point_max_time = None
                    point_max_value = None
                    point_threshold_value = None
                    
                    # Extract time and thunderstorm data from raw hourly data
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == report_data.report_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        time_str = str(hour_time.hour)
                                        weather_data = hour_data.get('weather', {})
                                        condition = weather_data.get('desc', '')
                                        
                                        # Check for thunderstorm conditions
                                        thunderstorm_levels = {
                                            'Risque d\'orages': 'low',
                                            'Averses orageuses': 'med', 
                                            'Orages': 'high'
                                        }
                                        thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                                        
                                        if thunderstorm_level != 'none':
                                            # Track maximum (highest level)
                                            if point_max_value is None or thunderstorm_level > point_max_value:
                                                point_max_value = thunderstorm_level
                                                point_max_time = time_str
                                            
                                            # Track threshold (earliest time when storm >= threshold)
                                            if thunderstorm_level >= self.thresholds['thunderstorm'] and point_threshold_time is None:
                                                point_threshold_time = time_str
                                                point_threshold_value = thunderstorm_level
                    
                    # Add threshold and maximum for this point
                    debug_lines.append("=========")
                    if point_threshold_time is not None:
                        debug_lines.append(f"{point_threshold_time}:00 | {point_threshold_value} (Threshold)")
                    if point_max_time is not None:
                        debug_lines.append(f"{point_max_time}:00 | {point_max_value} (Max)")
                    debug_lines.append("")
                
                # Add threshold and maximum tables as per specification
                if report_data.thunderstorm.threshold_time is not None:
                    debug_lines.append("Threshold")
                    debug_lines.append("GEO | Time | level")
                    for i, point in enumerate(report_data.thunderstorm.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'thunderstorm', i)
                        # Calculate threshold for this point
                        point_threshold_time = None
                        point_threshold_value = None
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if hour_date == report_data.report_date:
                                            weather_data = hour_data.get('weather', {})
                                            condition = weather_data.get('desc', '')
                                            thunderstorm_levels = {
                                                'Risque d\'orages': 'low',
                                                'Averses orageuses': 'med', 
                                                'Orages': 'high'
                                            }
                                            thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                                            if thunderstorm_level >= self.thresholds['thunderstorm'] and point_threshold_time is None:
                                                point_threshold_time = str(hour_time.hour)
                                                point_threshold_value = thunderstorm_level
                                                break
                        if point_threshold_time is not None:
                            debug_lines.append(f"{tg_ref} | {point_threshold_time}:00 | {point_threshold_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"Threshold | {report_data.thunderstorm.threshold_time}:00 | {report_data.thunderstorm.threshold_value}")
                    debug_lines.append("")
                
                if report_data.thunderstorm.max_time is not None:
                    debug_lines.append("Maximum:")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.thunderstorm.geo_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'thunderstorm', i)
                        # Calculate maximum for this point
                        point_max_time = None
                        point_max_value = None
                        if hasattr(self, '_last_weather_data') and self._last_weather_data:
                            hourly_data = self._last_weather_data.get('hourly_data', [])
                            if i < len(hourly_data) and 'data' in hourly_data[i]:
                                for hour_data in hourly_data[i]['data']:
                                    if 'dt' in hour_data:
                                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                                        hour_date = hour_time.date()
                                        if hour_date == report_data.report_date:
                                            weather_data = hour_data.get('weather', {})
                                            condition = weather_data.get('desc', '')
                                            thunderstorm_levels = {
                                                'Risque d\'orages': 'low',
                                                'Averses orageuses': 'med', 
                                                'Orages': 'high'
                                            }
                                            thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                                            if thunderstorm_level != 'none':
                                                if point_max_value is None or thunderstorm_level > point_max_value:
                                                    point_max_value = thunderstorm_level
                                                    point_max_time = str(hour_time.hour)
                        if point_max_time is not None:
                            debug_lines.append(f"{tg_ref} | {point_max_time}:00 | {point_max_value}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.thunderstorm.max_time}:00 | {report_data.thunderstorm.max_value}")
                    debug_lines.append("")
                    debug_lines.append("GEO | Time | Max")
                    for point in report_data.thunderstorm.geo_points:
                        if point['max_time'] is not None:
                            debug_lines.append(f"{point['name']} | {point['max_time']} | {point['max_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.thunderstorm.max_time} | {report_data.thunderstorm.max_value}")
                    debug_lines.append("")
            
            # Thunderstorm (+1) data debug
            if report_data.thunderstorm_plus_one.geo_points:
                debug_lines.append("THUNDERSTORM (+1)")
                
                # Calculate stage date for thunderstorm (+1)
                plus_one_date = report_data.report_date + timedelta(days=1)
                if report_data.report_type == 'evening':
                    stage_date = plus_one_date + timedelta(days=1)  # Over-tomorrow's date
                else:  # morning
                    stage_date = plus_one_date  # Tomorrow's date
                
                # Thunderstorm level mapping
                thunderstorm_levels = {
                    'Risque d\'orages': 'low',
                    'Averses orageuses': 'med', 
                    'Orages': 'high'
                }
                
                for i, point in enumerate(report_data.thunderstorm_plus_one.geo_points):
                    # Thunderstorm (+1): tomorrow's stage for morning, day after tomorrow for evening
                    if report_data.report_type == 'morning':
                        tg_ref = f"T2G{i+1}"
                    else:  # evening
                        tg_ref = f"T3G{i+1}"
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Storm")
                    
                    # Generate hourly data from API data
                    if hasattr(self, '_last_weather_data') and self._last_weather_data:
                        hourly_data = self._last_weather_data.get('hourly_data', [])
                        if i < len(hourly_data) and 'data' in hourly_data[i]:
                            for hour_data in hourly_data[i]['data']:
                                if 'dt' in hour_data:
                                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                                    hour_date = hour_time.date()
                                    if hour_date == stage_date:
                                        # Apply time filter: only 4:00 - 19:00 Uhr
                                        hour = hour_time.hour
                                        if hour < 4 or hour > 19:
                                            continue
                                        
                                        # Extract weather condition
                                        condition = hour_data.get('condition', '')
                                        if not condition and 'weather' in hour_data:
                                            weather_data = hour_data['weather']
                                            condition = weather_data.get('desc', '')
                                        thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                                        debug_lines.append(f"{hour_time.strftime('%H')}:00 | {thunderstorm_level}")
                    
                    debug_lines.append("=========")
                    if point['threshold_time'] is not None:
                        debug_lines.append(f"{point['threshold_time']}:00 | {point['threshold_value']} (Threshold)")
                    if point['max_time'] is not None:
                        debug_lines.append(f"{point['max_time']}:00 | {point['max_value']} (Max)")
                    debug_lines.append("")
                
                # Add global threshold and maximum info
                if report_data.thunderstorm_plus_one.threshold_time is not None:
                    debug_lines.append("Threshold (+1)")
                    debug_lines.append("GEO | Time | level")
                    for i, point in enumerate(report_data.thunderstorm_plus_one.geo_points):
                        if point['threshold_time'] is not None:
                            # Thunderstorm (+1): tomorrow's stage for morning, day after tomorrow for evening
                            if report_data.report_type == 'morning':
                                tg_ref = f"T2G{i+1}"
                            else:  # evening
                                tg_ref = f"T3G{i+1}"
                            debug_lines.append(f"{tg_ref} | {point['threshold_time']} | {point['threshold_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"Threshold | {report_data.thunderstorm_plus_one.threshold_time} | {report_data.thunderstorm_plus_one.threshold_value}")
                    debug_lines.append("")
                
                if report_data.thunderstorm_plus_one.max_time is not None:
                    debug_lines.append("Maximum (+1)")
                    debug_lines.append("GEO | Time | Max")
                    for i, point in enumerate(report_data.thunderstorm_plus_one.geo_points):
                        if point['max_time'] is not None:
                            # Thunderstorm (+1): tomorrow's stage for morning, day after tomorrow for evening
                            if report_data.report_type == 'morning':
                                tg_ref = f"T2G{i+1}"
                            else:  # evening
                                tg_ref = f"T3G{i+1}"
                            debug_lines.append(f"{tg_ref} | {point['max_time']} | {point['max_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.thunderstorm_plus_one.max_time} | {report_data.thunderstorm_plus_one.max_value}")
                    debug_lines.append("")
            
            # Risks (Warnungen) data debug
            if report_data.risks.geo_points:
                debug_lines.append("Risks (Warnungen) Data:")
                for point in report_data.risks.geo_points:
                    debug_lines.append(f"{point['name']}")
                    debug_lines.append("Time | Warnung")
                    if point['threshold_time'] is not None:
                        debug_lines.append(f"{point['threshold_time']}:00 | {point['threshold_value']}")
                    debug_lines.append("=========")
                    if point['threshold_time'] is not None:
                        debug_lines.append(f"{point['threshold_time']}:00 | {point['threshold_value']} (Threshold)")
                    if point['max_time'] is not None:
                        debug_lines.append(f"{point['max_time']}:00 | {point['max_value']} (Max)")
                    debug_lines.append("")
                
                # Add global threshold and maximum info
                if report_data.risks.threshold_time is not None:
                    debug_lines.append("Threshold (Warnungen)")
                    debug_lines.append("GEO | Time | Warnung")
                    for point in report_data.risks.geo_points:
                        if point['threshold_time'] is not None:
                            debug_lines.append(f"{point['name']} | {point['threshold_time']} | {point['threshold_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"Threshold | {report_data.risks.threshold_time} | {report_data.risks.threshold_value}")
                    debug_lines.append("")
                
                if report_data.risks.max_time is not None:
                    debug_lines.append("Maximum (Warnungen)")
                    debug_lines.append("GEO | Time | Max")
                    for point in report_data.risks.geo_points:
                        if point['max_time'] is not None:
                            debug_lines.append(f"{point['name']} | {point['max_time']} | {point['max_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.risks.max_time} | {report_data.risks.max_value}")
                    debug_lines.append("")
            
            # Risk Zonal data debug
            if report_data.risk_zonal.geo_points:
                debug_lines.append("Risk Zonal Data:")
                for i, point in enumerate(report_data.risk_zonal.geo_points):
                    # Risk Zonal uses today's stage (T1) for morning, tomorrow's stage (T2) for evening
                    if report_data.report_type == 'morning':
                        tg_ref = f"T1G{i+1}"
                    else:  # evening
                        tg_ref = f"T2G{i+1}"
                    debug_lines.append(f"{tg_ref}")
                    debug_lines.append("Time | Risiko")
                    if point['threshold_time'] is not None:
                        debug_lines.append(f"{point['threshold_time']}:00 | {point['threshold_value']}")
                    debug_lines.append("=========")
                    if point['threshold_time'] is not None:
                        debug_lines.append(f"{point['threshold_time']}:00 | {point['threshold_value']} (Threshold)")
                    if point['max_time'] is not None:
                        debug_lines.append(f"{point['max_time']}:00 | {point['max_value']} (Max)")
                    debug_lines.append("")
                
                # Add global threshold and maximum info
                if report_data.risk_zonal.threshold_time is not None:
                    debug_lines.append("Threshold (Risiko)")
                    debug_lines.append("GEO | Time | Risiko")
                    for point in report_data.risk_zonal.geo_points:
                        if point['threshold_time'] is not None:
                            debug_lines.append(f"{point['name']} | {point['threshold_time']} | {point['threshold_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"Threshold | {report_data.risk_zonal.threshold_time} | {report_data.risk_zonal.threshold_value}")
                    debug_lines.append("")
                
                if report_data.risk_zonal.max_time is not None:
                                    debug_lines.append("Maximum (Risiko)")
                debug_lines.append("GEO | Time | Max")
                for i, point in enumerate(report_data.risk_zonal.geo_points):
                    if point['max_time'] is not None:
                        # Risk Zonal uses today's stage (T1) for morning, tomorrow's stage (T2) for evening
                        if report_data.report_type == 'morning':
                            tg_ref = f"T1G{i+1}"
                        else:  # evening
                            tg_ref = f"T2G{i+1}"
                        debug_lines.append(f"{tg_ref} | {point['max_time']} | {point['max_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.risk_zonal.max_time} | {report_data.risk_zonal.max_value}")
                    debug_lines.append("")
            
            return "\n".join(debug_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate debug output: {e}")
            return "# DEBUG DATENEXPORT\nError generating debug output"
    
    def save_persistence_data(self, report_data: WeatherReportData) -> bool:
        """
        Save weather report data to JSON file for persistence.
        
        Args:
            report_data: Complete weather report data
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create date directory
            date_str = report_data.report_date.strftime('%Y-%m-%d')
            date_dir = os.path.join(self.data_dir, date_str)
            os.makedirs(date_dir, exist_ok=True)
            
            # Create filename
            filename = f"{report_data.stage_name}.json"
            filepath = os.path.join(date_dir, filename)
            
            # Convert to dictionary
            data_dict = asdict(report_data)
            
            # Add metadata
            data_dict['generated_at'] = datetime.now().isoformat()
            data_dict['version'] = 'morning-evening-refactor-v1'
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(data_dict, f, indent=2, default=str)
            
            logger.info(f"Saved persistence data to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save persistence data: {e}")
            return False
    
    def generate_report(self, stage_name: str, report_type: str, target_date: str) -> Tuple[str, str]:
        """
        Generate complete weather report with result and debug output.
        
        Args:
            stage_name: Name of the stage
            report_type: 'morning' or 'evening'
            target_date: Target date for the report (string format YYYY-MM-DD)
            
        Returns:
            Tuple of (result_output, debug_output)
        """
        try:
            # Convert target_date string to date object
            if isinstance(target_date, str):
                target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
            else:
                target_date_obj = target_date
            
            logger.info(f"Generating {report_type} report for {stage_name} on {target_date_obj}")
            
            # Fetch weather data
            weather_data = self.fetch_weather_data(stage_name, target_date_obj)
            
            # Store weather data for debug output
            self._last_weather_data = weather_data
            
            if not weather_data:
                logger.error(f"No weather data available for {stage_name}")
                return f"{stage_name}: NO DATA", "# DEBUG DATENEXPORT\nNo weather data available"
            
            # Process weather elements
            night_data = self.process_night_data(weather_data, stage_name, target_date_obj, report_type)
            day_data = self.process_day_data(weather_data, stage_name, target_date_obj, report_type)
            rain_mm_data = self.process_rain_mm_data(weather_data, stage_name, target_date_obj, report_type)
            rain_percent_data = self.process_rain_percent_data(weather_data, stage_name, target_date_obj, report_type)
            wind_data = self.process_wind_data(weather_data, stage_name, target_date_obj, report_type)
            gust_data = self.process_gust_data(weather_data, stage_name, target_date_obj, report_type)
            thunderstorm_data = self.process_thunderstorm_data(weather_data, stage_name, target_date_obj, report_type)
            thunderstorm_plus_one_data = self.process_thunderstorm_plus_one_data(weather_data, stage_name, target_date_obj, report_type)
            risks_data = self.process_risks_data(weather_data, stage_name, target_date_obj, report_type)
            risk_zonal_data = self.process_risk_zonal_data(weather_data, stage_name, target_date_obj, report_type)
            
            # Create report data structure
            report_data = WeatherReportData(
                stage_name=stage_name,
                report_date=target_date_obj,
                report_type=report_type,
                night=night_data,
                day=day_data,
                rain_mm=rain_mm_data,
                rain_percent=rain_percent_data,
                wind=wind_data,
                gust=gust_data,
                thunderstorm=thunderstorm_data,
                thunderstorm_plus_one=thunderstorm_plus_one_data,
                risks=risks_data,
                risk_zonal=risk_zonal_data
            )
            
            # Generate outputs
            result_output = self.format_result_output(report_data)
            debug_output = self.generate_debug_output(report_data)
            
            # Save persistence data
            self.save_persistence_data(report_data)
            
            logger.info(f"Generated {report_type} report for {stage_name}")
            return result_output, debug_output
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return f"{stage_name}: ERROR", f"# DEBUG DATENEXPORT\nError: {str(e)}" 

    def _process_unified_hourly_data(self, weather_data: Dict[str, Any], target_date: date, 
                                   data_extractor: callable, threshold_value: float, 
                                   report_type: str = None, data_type: str = None) -> WeatherThresholdData:
        """
        Unified method to process hourly weather data with consistent threshold and maximum logic.
        
        Args:
            weather_data: Weather data from API
            target_date: Target date for processing
            data_extractor: Function to extract value from hour_data (e.g., lambda h: h.get('rain', {}).get('1h', 0))
            threshold_value: Threshold value to check against
            report_type: 'morning' or 'evening' for T-G reference generation
            data_type: Data type for T-G reference generation
            
        Returns:
            WeatherThresholdData with consistent processing
        """
        try:
            hourly_data = weather_data.get('hourly_data', [])
            geo_points = []
            global_max_value = None
            global_max_time = None
            global_threshold_value = None
            global_threshold_time = None
            
            # Process each geo point
            for i, point_data in enumerate(hourly_data):
                if 'data' in point_data:
                    point_max_value = None
                    point_max_time = None
                    point_threshold_value = None
                    point_threshold_time = None
                    point_hourly_data = {}
                    
                    # Process hourly data for this point
                    for hour_data in point_data['data']:
                        if 'dt' in hour_data:
                            hour_time = datetime.fromtimestamp(hour_data['dt'])
                            hour_date = hour_time.date()
                            
                            if hour_date == target_date:
                                # Apply time filter: only 4:00 - 19:00 Uhr (as per specification)
                                hour = hour_time.hour
                                if hour < 4 or hour > 19:
                                    continue
                                
                                # Extract value using the provided extractor function
                                value = data_extractor(hour_data)
                                hour_str = hour_time.strftime('%H')
                                point_hourly_data[hour_str] = value
                                
                                # Check threshold (earliest time when value >= threshold)
                                if value >= threshold_value and point_threshold_time is None:
                                    point_threshold_time = hour_str
                                    point_threshold_value = value
                                
                                # Track maximum for this point (only if value > 0)
                                if value > 0 and (point_max_value is None or value > point_max_value):
                                    point_max_value = value
                                    point_max_time = hour_str
                    
                    # Store point data with T-G reference if available
                    if report_type and data_type:
                        tg_ref = self._get_tg_reference(report_type, data_type, i)
                        geo_points.append({tg_ref: point_hourly_data})
                    else:
                        # Fallback to G reference if T-G reference not available
                        geo_points.append({f'G{i+1}': point_hourly_data})
                    
                    # Update global maximum
                    if point_max_value is not None:
                        if global_max_value is None or point_max_value > global_max_value:
                            global_max_value = point_max_value
                            global_max_time = point_max_time
                    
                    # Update global threshold (earliest time across all points)
                    if point_threshold_time is not None:
                        if global_threshold_time is None or point_threshold_time < global_threshold_time:
                            global_threshold_time = point_threshold_time
                            global_threshold_value = point_threshold_value
            
            # Return result with consistent logic
            return WeatherThresholdData(
                threshold_value=global_threshold_value,
                threshold_time=global_threshold_time,
                max_value=global_max_value,
                max_time=global_max_time,
                geo_points=geo_points
            )
            
        except Exception as e:
            logger.error(f"Failed to process unified hourly data: {e}")
            return WeatherThresholdData()

    def _process_unified_daily_data(self, weather_data: Dict[str, Any], target_date: date, 
                                  data_extractor: callable, report_type: str = None, data_type: str = None) -> WeatherThresholdData:
        """
        Unified method to process daily weather data with consistent logic.
        
        Args:
            weather_data: Weather data from API
            target_date: Target date for processing
            data_extractor: Function to extract value from daily_data (e.g., lambda d: d.get('temperature', {}).get('min'))
            report_type: 'morning' or 'evening' for T-G reference generation
            data_type: Data type for T-G reference generation
            
        Returns:
            WeatherThresholdData with consistent processing
        """
        try:
            # Get daily forecast data (it's a dict with one entry, not a list)
            daily_forecast = weather_data.get('daily_forecast', {})
            geo_points = []
            global_min_value = None
            global_max_value = None
            
            # Get the single daily forecast entry
            if 'daily' in daily_forecast:
                daily_data = daily_forecast['daily']
                
                # Find the entry for the target date
                target_date_str = target_date.strftime('%Y-%m-%d')
                point_value = None
                
                for day_data in daily_data:
                    # Use dt (timestamp) instead of date
                    entry_dt = day_data.get('dt')
                    if entry_dt:
                        # Convert timestamp to date
                        from datetime import datetime
                        entry_date = datetime.fromtimestamp(entry_dt).date()
                        entry_date_str = entry_date.strftime('%Y-%m-%d')
                        
                        if entry_date_str == target_date_str:
                            # Extract value using the provided extractor function
                            point_value = data_extractor(day_data)
                            break
                
                # For Night data, we need the value from the LAST point of today's stage (T1G3)
                # Find the last coordinate's data
                if report_type and data_type:
                    # Get stage coordinates to find the last point
                    import json
                    with open("etappen.json", "r") as f:
                        etappen_data = json.load(f)
                    
                    # Find current stage
                    start_date = datetime.strptime(self.config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
                    days_since_start = (target_date - start_date).days
                    stage_idx = days_since_start  # Today's stage for Night
                    
                    if stage_idx < len(etappen_data):
                        stage = etappen_data[stage_idx]
                        stage_points = stage.get('punkte', [])
                        
                        if stage_points:
                            # Get the last point's coordinates
                            last_point = stage_points[-1]
                            last_lat, last_lon = last_point['lat'], last_point['lon']
                            
                            # Find the data for this specific coordinate
                            from src.wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
                            api = EnhancedMeteoFranceAPI()
                            last_point_name = f"{stage['name']}_point_{len(stage_points)}"
                            
                            # Fetch weather data for the last point
                            last_point_data = api.get_complete_forecast_data(last_lat, last_lon, last_point_name)
                            last_daily_forecast = last_point_data.get('daily_forecast', {})
                            
                            if 'daily' in last_daily_forecast:
                                last_daily_data = last_daily_forecast['daily']
                                
                                # Find the entry for the target date
                                target_date_str = target_date.strftime('%Y-%m-%d')
                                last_point_value = None
                                
                                for day_data in last_daily_data:
                                    entry_dt = day_data.get('dt')
                                    if entry_dt:
                                        entry_date = datetime.fromtimestamp(entry_dt).date()
                                        entry_date_str = entry_date.strftime('%Y-%m-%d')
                                        
                                        if entry_date_str == target_date_str:
                                            last_point_value = data_extractor(day_data)
                                            break
                                
                                # Use the last point's value
                                point_value = last_point_value
                                tg_ref = "T1G3"
                                geo_points.append({tg_ref: point_value})
                            else:
                                # Fallback to original value
                                tg_ref = "T1G3"
                                geo_points.append({tg_ref: point_value})
                        else:
                            # Fallback
                            geo_points.append({'G3': point_value})
                    else:
                        # Fallback
                        geo_points.append({'G3': point_value})
                else:
                    # Fallback
                    geo_points.append({'G3': point_value})
                
                # Update global min/max
                if point_value is not None:
                    global_min_value = point_value
                    global_max_value = point_value
            
            # Return result with consistent logic
            return WeatherThresholdData(
                threshold_value=global_min_value,  # For night (temp_min)
                threshold_time=None,  # Daily data has no specific time
                max_value=global_max_value,  # For day (temp_max)
                max_time=None,  # Daily data has no specific time
                geo_points=geo_points
            )
            
        except Exception as e:
            logger.error(f"Failed to process unified daily data: {e}")
            return WeatherThresholdData()