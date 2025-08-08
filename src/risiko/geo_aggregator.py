"""
GEO-point aggregation module.

This module aggregates weather data from multiple geographical points
across different stages for comprehensive risk analysis.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


@dataclass
class GeoPoint:
    """Represents a geographical point with coordinates and stage information."""
    lat: float
    lon: float
    stage_name: str
    stage_date: date
    point_type: str  # "start", "middle", "end"


@dataclass
class AggregatedWeatherData:
    """Aggregated weather data from multiple GEO-points."""
    forecast_entries: List[Dict[str, Any]]
    stage_name: str
    stage_date: date
    point_count: int


class GeoAggregator:
    """Aggregates weather data from multiple geographical points."""
    
    def __init__(self):
        """Initialize the GEO aggregator."""
        pass
    
    def aggregate_stage_weather(self, weather_data_by_point: Dict[str, Dict[str, Any]]) -> AggregatedWeatherData:
        """
        Aggregate weather data from all points of a stage.
        
        Args:
            weather_data_by_point: Dictionary mapping point IDs to weather data
            
        Returns:
            AggregatedWeatherData: Combined weather data from all points
        """
        try:
            all_forecast_entries = []
            stage_name = None
            stage_date = None
            point_count = 0
            
            for point_id, weather_data in weather_data_by_point.items():
                if not weather_data or 'forecast' not in weather_data:
                    logger.warning(f"Missing or invalid weather data for point {point_id}")
                    continue
                
                forecast_entries = weather_data['forecast']
                if not forecast_entries:
                    continue
                
                # Extract stage information from first valid entry
                if stage_name is None and forecast_entries:
                    stage_name = weather_data.get('stage_name', 'Unknown')
                    stage_date_str = weather_data.get('stage_date')
                    if stage_date_str:
                        try:
                            stage_date = datetime.strptime(stage_date_str, '%Y-%m-%d').date()
                        except ValueError:
                            stage_date = date.today()
                
                # Add all forecast entries from this point
                all_forecast_entries.extend(forecast_entries)
                point_count += 1
            
            if not all_forecast_entries:
                raise ValueError("No valid weather data found from any GEO-points")
            
            # Sort by timestamp to ensure chronological order
            all_forecast_entries.sort(key=lambda x: x.get('dt', 0))
            
            return AggregatedWeatherData(
                forecast_entries=all_forecast_entries,
                stage_name=stage_name or 'Unknown',
                stage_date=stage_date or date.today(),
                point_count=point_count
            )
            
        except Exception as e:
            logger.error(f"Error aggregating stage weather data: {e}")
            raise ValueError(f"Failed to aggregate weather data: {str(e)}")
    
    def aggregate_night_temperature(self, weather_data_by_point: Dict[str, Dict[str, Any]], 
                                  night_hours: tuple = (22, 6)) -> Optional[float]:
        """
        Aggregate night temperature from the last point of today's stage.
        
        Args:
            weather_data_by_point: Dictionary mapping point IDs to weather data
            night_hours: Tuple of (start_hour, end_hour) for night period
            
        Returns:
            Optional[float]: Minimum night temperature, or None if not available
        """
        try:
            night_start, night_end = night_hours
            night_temperatures = []
            
            for point_id, weather_data in weather_data_by_point.items():
                if not weather_data or 'forecast' not in weather_data:
                    continue
                
                forecast_entries = weather_data['forecast']
                for entry in forecast_entries:
                    if 'dt' not in entry or 'T' not in entry:
                        continue
                    
                    # Convert timestamp to hour
                    entry_datetime = datetime.fromtimestamp(entry['dt'])
                    hour = entry_datetime.hour
                    
                    # Check if hour is in night period
                    if night_start <= night_end:
                        # Same day (e.g., 22:00-06:00)
                        if hour >= night_start or hour <= night_end:
                            temp_value = entry['T'].get('value')
                            if temp_value is not None:
                                night_temperatures.append(float(temp_value))
                    else:
                        # Cross midnight (e.g., 22:00-06:00)
                        if hour >= night_start or hour <= night_end:
                            temp_value = entry['T'].get('value')
                            if temp_value is not None:
                                night_temperatures.append(float(temp_value))
            
            if night_temperatures:
                return min(night_temperatures)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error aggregating night temperature: {e}")
            return None
    
    def get_stage_geopoints(self, stage_name: str, stage_date: date) -> List[GeoPoint]:
        """
        Get GEO-points for a specific stage and date.
        
        Args:
            stage_name: Name of the stage
            stage_date: Date of the stage
            
        Returns:
            List[GeoPoint]: List of geographical points for the stage
        """
        # This would typically load from etappen.json
        # For now, return a placeholder implementation
        return [
            GeoPoint(lat=42.0, lon=9.0, stage_name=stage_name, stage_date=stage_date, point_type="start"),
            GeoPoint(lat=42.1, lon=9.1, stage_name=stage_name, stage_date=stage_date, point_type="middle"),
            GeoPoint(lat=42.2, lon=9.2, stage_name=stage_name, stage_date=stage_date, point_type="end")
        ] 