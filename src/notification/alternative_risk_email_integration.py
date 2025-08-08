"""
Alternative risk analysis email integration.

This module integrates the alternative risk analysis into the existing
email generation pipeline.
"""

from typing import Dict, Any, Optional
import logging

from src.risiko.alternative_risk_analysis import AlternativeRiskAnalyzer
from src.risiko.geo_aggregator import GeoAggregator, AggregatedWeatherData

logger = logging.getLogger(__name__)


class AlternativeRiskEmailIntegration:
    """Integrates alternative risk analysis into email generation."""
    
    def __init__(self):
        """Initialize the email integration."""
        self.risk_analyzer = AlternativeRiskAnalyzer()
        self.geo_aggregator = GeoAggregator()
    
    def generate_alternative_risk_report(self, weather_data_by_point: Dict[str, Dict[str, Any]], 
                                       stage_name: str, stage_date: str) -> Optional[str]:
        """
        Generate alternative risk report for email integration.
        
        Args:
            weather_data_by_point: Weather data from multiple GEO-points
            stage_name: Name of the stage
            stage_date: Date of the stage
            
        Returns:
            Optional[str]: Alternative risk report text, or None if generation fails
        """
        try:
            # Aggregate weather data from all GEO-points
            aggregated_data = self.geo_aggregator.aggregate_stage_weather(weather_data_by_point)
            
            # Prepare weather data for analysis
            weather_data = {
                'forecast': aggregated_data.forecast_entries,
                'stage_name': stage_name,
                'stage_date': stage_date
            }
            
            # Perform alternative risk analysis
            risk_result = self.risk_analyzer.analyze_all_risks(weather_data)
            
            # Generate report text
            report_text = self.risk_analyzer.generate_report_text(risk_result)
            
            logger.info(f"Generated alternative risk report for stage {stage_name}")
            return report_text
            
        except Exception as e:
            logger.error(f"Error generating alternative risk report: {e}")
            return None
    
    def integrate_into_email_content(self, existing_email_content: str, 
                                   alternative_risk_report: str) -> str:
        """
        Integrate alternative risk report into existing email content.
        
        Args:
            existing_email_content: Existing email content
            alternative_risk_report: Alternative risk report text
            
        Returns:
            str: Combined email content
        """
        try:
            # Append alternative risk report to existing content
            combined_content = existing_email_content + "\n\n" + alternative_risk_report
            
            logger.info("Successfully integrated alternative risk report into email content")
            return combined_content
            
        except Exception as e:
            logger.error(f"Error integrating alternative risk report: {e}")
            return existing_email_content
    
    def get_night_temperature_info(self, weather_data_by_point: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Get night temperature information for evening reports.
        
        Args:
            weather_data_by_point: Weather data from multiple GEO-points
            
        Returns:
            Optional[str]: Night temperature information, or None if not available
        """
        try:
            night_temp = self.geo_aggregator.aggregate_night_temperature(weather_data_by_point)
            
            if night_temp is not None:
                return f"Night temperature: {night_temp}°C"
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting night temperature info: {e}")
            return None
    
    def validate_weather_data(self, weather_data_by_point: Dict[str, Dict[str, Any]]) -> bool:
        """
        Validate weather data before processing.
        
        Args:
            weather_data_by_point: Weather data from multiple GEO-points
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            if not weather_data_by_point:
                logger.warning("No weather data provided")
                return False
            
            valid_points = 0
            for point_id, weather_data in weather_data_by_point.items():
                if weather_data and 'forecast' in weather_data and weather_data['forecast']:
                    valid_points += 1
            
            if valid_points == 0:
                logger.warning("No valid weather data found in any GEO-point")
                return False
            
            logger.info(f"Validated weather data from {valid_points} GEO-points")
            return True
            
        except Exception as e:
            logger.error(f"Error validating weather data: {e}")
            return False 