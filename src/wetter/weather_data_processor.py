"""
Weather data processor using enhanced MeteoFrance API.

This module processes weather data using the stable and comprehensive
MeteoFrance API implementation with unified data structures.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .enhanced_meteofrance_api import EnhancedMeteoFranceAPI
from .unified_weather_data import UnifiedWeatherData, WeatherDataPoint

logger = logging.getLogger(__name__)


class WeatherDataProcessor:
    """
    Weather data processor using enhanced MeteoFrance API.
    
    This class provides stable and comprehensive weather data processing
    using the official MeteoFrance API with unified data structures.
    """
    
    def __init__(self):
        """Initialize the weather data processor."""
        self.api = EnhancedMeteoFranceAPI()
        logger.info("WeatherDataProcessor initialized with enhanced MeteoFrance API")
    
    def get_stage_weather_data(self, stage_coordinates: List[List[float]], stage_name: str) -> UnifiedWeatherData:
        """
        Get weather data for all points of a stage.
        
        Args:
            stage_coordinates: List of [lat, lon] coordinate pairs
            stage_name: Name of the stage
            
        Returns:
            UnifiedWeatherData containing data for all stage points
        """
        try:
            logger.info(f"Processing weather data for stage: {stage_name}")
            logger.info(f"Number of coordinate points: {len(stage_coordinates)}")
            
            unified_data = UnifiedWeatherData()
            unified_data.stage_name = stage_name
            unified_data.stage_date = datetime.now().strftime('%Y-%m-%d')
            
            for i, coord in enumerate(stage_coordinates):
                if len(coord) >= 2:
                    lat, lon = coord[0], coord[1]
                    location_name = f"{stage_name}_point_{i+1}"
                    
                    try:
                        logger.info(f"Fetching data for point {i+1}: {location_name} ({lat}, {lon})")
                        
                        # Get complete forecast data from enhanced API
                        complete_data = self.api.get_complete_forecast_data(lat, lon, location_name)
                        
                        # Create data point with hourly data
                        data_point = WeatherDataPoint(
                            latitude=lat,
                            longitude=lon,
                            location_name=location_name
                        )
                        
                        # Add all hourly entries
                        for entry in complete_data['hourly_data']:
                            data_point.add_entry(entry)
                        
                        unified_data.add_data_point(data_point)
                        
                        logger.info(f"Successfully added data for {location_name} ({len(complete_data['hourly_data'])} entries)")
                        
                    except Exception as e:
                        logger.error(f"Failed to get data for point {i+1} ({location_name}): {e}")
                        # Continue with other points instead of failing completely
                        continue
            
            if not unified_data.data_points:
                raise RuntimeError(f"No weather data could be fetched for stage {stage_name}")
            
            logger.info(f"Successfully processed weather data for stage {stage_name} with {len(unified_data.data_points)} points")
            return unified_data
            
        except Exception as e:
            logger.error(f"Failed to process weather data for stage {stage_name}: {e}")
            raise RuntimeError(f"Failed to process weather data for stage {stage_name}: {str(e)}")
    
    def get_weather_summary(self, unified_data: UnifiedWeatherData, 
                          start_time: datetime, end_time: datetime,
                          report_type: str = 'morning') -> Dict[str, Any]:
        """
        Get comprehensive weather summary for the specified time range.
        
        Args:
            unified_data: UnifiedWeatherData object
            start_time: Start of time range
            end_time: End of time range
            report_type: Type of report (morning, evening, update)
            
        Returns:
            Dictionary containing comprehensive weather summary
        """
        try:
            logger.info(f"Generating weather summary for {unified_data.stage_name}")
            logger.info(f"Time range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
            
            # Use enhanced API for comprehensive summary
            summary = self.api.get_weather_summary_with_probabilities(unified_data, start_time, end_time)
            
            # Add enhanced data structure for alternative risk analysis
            enhanced_data = self._prepare_enhanced_data_for_analysis(unified_data, start_time, end_time, report_type)
            summary['enhanced_data'] = enhanced_data
            
            logger.info(f"Successfully generated weather summary for {unified_data.stage_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate weather summary: {e}")
            raise RuntimeError(f"Failed to generate weather summary: {str(e)}")
    
    def _prepare_enhanced_data_for_analysis(self, unified_data: UnifiedWeatherData, 
                                          start_time: datetime, end_time: datetime,
                                          report_type: str = 'morning') -> Dict[str, Any]:
        """
        Prepare enhanced data structure for alternative risk analysis.
        
        Args:
            unified_data: UnifiedWeatherData object
            start_time: Start of time range
            end_time: End of time range
            report_type: Type of report (morning, evening, update)
            
        Returns:
            Dictionary containing enhanced data for analysis
        """
        try:
            enhanced_data = {
                'hourly_data': [],
                'daily_data': [],
                'probability_data': [],
                'thunderstorm_data': [],
                'location_name': unified_data.stage_name,
                'stage_date': unified_data.stage_date,
                'report_type': report_type,  # Add report type for debug info
                'unified_data': unified_data  # Add unified_data for GEO coordinate debug
            }
            
            # Convert unified data to enhanced format
            for point in unified_data.data_points:
                # Get hourly data for this point
                hourly_entries = point.get_entries_for_time_range(start_time, end_time)
                enhanced_data['hourly_data'].extend(hourly_entries)
                
                # For now, we'll need to fetch probability data separately
                # This could be enhanced to store probability data in unified structure
                try:
                    complete_data = self.api.get_complete_forecast_data(
                        point.latitude, point.longitude, point.location_name
                    )
                    
                    # Add probability data
                    enhanced_data['probability_data'].extend(complete_data.get('probability_data', []))
                    
                    # Add thunderstorm data
                    enhanced_data['thunderstorm_data'].extend(complete_data.get('thunderstorm_data', []))
                    
                    # Add daily data (only once)
                    if not enhanced_data['daily_data']:
                        enhanced_data['daily_data'] = complete_data.get('daily_data', [])
                        
                except Exception as e:
                    logger.warning(f"Failed to get enhanced data for {point.location_name}: {e}")
                    continue
            
            # Add tomorrow's thunderstorm forecast
            try:
                thunderstorm_tomorrow = self.get_thunderstorm_forecast_tomorrow(unified_data)
                enhanced_data['thunderstorm_tomorrow'] = thunderstorm_tomorrow
            except Exception as e:
                logger.warning(f"Failed to get tomorrow's thunderstorm forecast: {e}")
                enhanced_data['thunderstorm_tomorrow'] = {}
            
            logger.info(f"Prepared enhanced data with {len(enhanced_data['hourly_data'])} hourly entries")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Failed to prepare enhanced data: {e}")
            return {}
    
    def get_thunderstorm_forecast_tomorrow(self, unified_data: UnifiedWeatherData) -> Dict[str, Any]:
        """
        Get thunderstorm forecast for tomorrow (+1 day).
        
        Args:
            unified_data: UnifiedWeatherData object
            
        Returns:
            Dictionary containing tomorrow's thunderstorm forecast
        """
        try:
            logger.info(f"Getting tomorrow's thunderstorm forecast for {unified_data.stage_name}")
            
            # Use enhanced API for thunderstorm forecast
            thunderstorm_forecast = self.api.get_thunderstorm_forecast_tomorrow(unified_data)
            
            logger.info(f"Successfully retrieved thunderstorm forecast for {unified_data.stage_name}")
            return thunderstorm_forecast
            
        except Exception as e:
            logger.error(f"Failed to get thunderstorm forecast: {e}")
            raise RuntimeError(f"Failed to get thunderstorm forecast: {str(e)}")
    
    def get_rain_probability_data(self, unified_data: UnifiedWeatherData, 
                                start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get rain probability data for the specified time range.
        
        Args:
            unified_data: UnifiedWeatherData object
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of rain probability data entries
        """
        try:
            logger.info(f"Getting rain probability data for {unified_data.stage_name}")
            
            # For now, we'll need to fetch probability data separately
            # This could be enhanced to store probability data in the unified structure
            rain_probability_data = []
            
            for point in unified_data.data_points:
                try:
                    # Get complete data for this point to access probability data
                    complete_data = self.api.get_complete_forecast_data(
                        point.latitude, point.longitude, point.location_name
                    )
                    
                    # Filter probability data for the time range
                    for prob_entry in complete_data['rain_probability_data']:
                        if start_time <= prob_entry['timestamp'] <= end_time:
                            rain_probability_data.append(prob_entry)
                            
                except Exception as e:
                    logger.warning(f"Failed to get probability data for {point.location_name}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(rain_probability_data)} rain probability entries")
            return rain_probability_data
            
        except Exception as e:
            logger.error(f"Failed to get rain probability data: {e}")
            return []
    
    def get_debug_info(self, unified_data: UnifiedWeatherData, 
                      start_time: datetime, end_time: datetime) -> str:
        """
        Get detailed debug information for the weather data.
        
        Args:
            unified_data: UnifiedWeatherData object
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            Formatted debug information string
        """
        try:
            # Use enhanced API for debug info
            summary = self.api.get_weather_summary_with_probabilities(unified_data, start_time, end_time)
            return summary.get('debug_info', 'No debug info available')
            
        except Exception as e:
            logger.error(f"Failed to generate debug info: {e}")
            return f"Error generating debug info: {str(e)}"


# Convenience functions for backward compatibility
def process_stage_weather_data(stage_coordinates: List[List[float]], stage_name: str) -> UnifiedWeatherData:
    """
    Process weather data for a stage.
    
    Args:
        stage_coordinates: List of [lat, lon] coordinate pairs
        stage_name: Name of the stage
        
    Returns:
        UnifiedWeatherData containing stage weather data
    """
    processor = WeatherDataProcessor()
    return processor.get_stage_weather_data(stage_coordinates, stage_name)


def get_weather_summary_for_stage(unified_data: UnifiedWeatherData, 
                                start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """
    Get weather summary for a stage.
    
    Args:
        unified_data: UnifiedWeatherData object
        start_time: Start of time range
        end_time: End of time range
        
    Returns:
        Dictionary containing weather summary
    """
    processor = WeatherDataProcessor()
    return processor.get_weather_summary(unified_data, start_time, end_time)