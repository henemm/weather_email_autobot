"""
Integrated debug module for report workflow.

This module provides debug functionality that can be enabled via configuration
to output raw data, validate thresholds, and compare with generated reports
during normal report generation.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from src.wetter.debug_raw_data import (
        get_raw_weather_data,
        format_raw_data_output,
        compare_raw_data_with_report,
        save_debug_output,
        DebugWeatherData
    )
    from src.wetter.fetch_meteofrance import get_forecast, get_thunderstorm
    from src.logic.analyse_weather import analyze_weather_data
    from src.model.datatypes import WeatherData, WeatherPoint
except ImportError:
    from debug_raw_data import (
        get_raw_weather_data,
        format_raw_data_output,
        compare_raw_data_with_report,
        save_debug_output,
        DebugWeatherData
    )
    from fetch_meteofrance import get_forecast, get_thunderstorm
    from ..logic.analyse_weather import analyze_weather_data
    from ..model.datatypes import WeatherData, WeatherPoint

logger = logging.getLogger(__name__)


@dataclass
class ReportDebugInfo:
    """Debug information for a report generation."""
    timestamp: datetime
    location_name: str
    latitude: float
    longitude: float
    raw_data: Optional[DebugWeatherData]
    weather_analysis: Optional[Any]
    report_values: Dict[str, Any]
    comparison_results: Optional[Dict[str, Any]]
    debug_files: List[str]


class ReportDebugger:
    """Debug helper for report generation workflow."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize debugger with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.debug_config = config.get("debug", {})
        self.enabled = self.debug_config.get("enabled", False)
        self.output_directory = self.debug_config.get("output_directory", "output/debug")
        
        if self.enabled:
            os.makedirs(self.output_directory, exist_ok=True)
            logger.info(f"Report debugger enabled. Output directory: {self.output_directory}")
    
    def should_debug(self) -> bool:
        """Check if debugging is enabled."""
        return self.enabled
    
    def debug_weather_data_collection(
        self,
        latitude: float,
        longitude: float,
        location_name: str,
        hours_ahead: int = 24
    ) -> Optional[DebugWeatherData]:
        """
        Debug weather data collection process.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            location_name: Human-readable location name
            hours_ahead: Number of hours to fetch
            
        Returns:
            DebugWeatherData if debugging is enabled, None otherwise
        """
        if not self.should_debug():
            return None
        
        try:
            logger.debug(f"Collecting debug data for {location_name}")
            raw_data = get_raw_weather_data(latitude, longitude, location_name, hours_ahead)
            
            if self.debug_config.get("save_debug_files", True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{location_name.lower()}_raw_data_{timestamp}.txt"
                filepath = os.path.join(self.output_directory, filename)
                save_debug_output(raw_data, filepath)
                logger.debug(f"Raw data saved to {filepath}")
            
            return raw_data
            
        except Exception as e:
            logger.error(f"Failed to collect debug data for {location_name}: {e}")
            return None
    
    def debug_weather_analysis(
        self,
        weather_data: WeatherData,
        location_name: str
    ) -> Optional[Any]:
        """
        Debug weather analysis process.
        
        Args:
            weather_data: Weather data to analyze
            location_name: Location name for logging
            
        Returns:
            Weather analysis result if debugging is enabled, None otherwise
        """
        if not self.should_debug():
            return None
        
        try:
            logger.debug(f"Analyzing weather data for {location_name}")
            analysis = analyze_weather_data(weather_data, self.config)
            
            if self.debug_config.get("save_debug_files", True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{location_name.lower()}_analysis_{timestamp}.json"
                filepath = os.path.join(self.output_directory, filename)
                
                # Convert analysis to dict for JSON serialization
                analysis_dict = {
                    "max_temperature": analysis.max_temperature,
                    "max_precipitation": analysis.max_precipitation,
                    "max_rain_probability": analysis.max_rain_probability,
                    "max_thunderstorm_probability": analysis.max_thunderstorm_probability,
                    "max_wind_speed": analysis.max_wind_speed,
                    "max_wind_gusts": analysis.max_wind_gusts,
                    "max_cloud_cover": analysis.max_cloud_cover,
                    "risk": analysis.risk,
                    "summary": analysis.summary,
                    "risks_count": len(analysis.risks)
                }
                
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(analysis_dict, f, indent=2, default=str)
                
                logger.debug(f"Weather analysis saved to {filepath}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze weather data for {location_name}: {e}")
            return None
    
    def debug_report_comparison(
        self,
        raw_data: DebugWeatherData,
        report_values: Dict[str, Any],
        location_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Debug comparison between raw data and report values.
        
        Args:
            raw_data: Raw weather data
            report_values: Values from generated report
            location_name: Location name for logging
            
        Returns:
            Comparison results if debugging is enabled, None otherwise
        """
        if not self.should_debug():
            return None
        
        try:
            logger.debug(f"Comparing raw data with report for {location_name}")
            comparison = compare_raw_data_with_report(raw_data, report_values, self.config)
            
            if self.debug_config.get("save_debug_files", True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{location_name.lower()}_comparison_{timestamp}.json"
                filepath = os.path.join(self.output_directory, filename)
                
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(comparison, f, indent=2, default=str)
                
                logger.debug(f"Comparison results saved to {filepath}")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare data for {location_name}: {e}")
            return None
    
    def debug_threshold_validation(
        self,
        weather_data: WeatherData,
        location_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Debug threshold validation process.
        
        Args:
            weather_data: Weather data to validate
            location_name: Location name for logging
            
        Returns:
            Threshold validation results if debugging is enabled, None otherwise
        """
        if not self.should_debug():
            return None
        
        try:
            logger.debug(f"Validating thresholds for {location_name}")
            thresholds = self.config.get("thresholds", {})
            
            validation_results = {
                "location": location_name,
                "timestamp": datetime.now().isoformat(),
                "thresholds": thresholds,
                "crossings": [],
                "issues": []
            }
            
            # Check each weather point for threshold crossings
            for point in weather_data.points:
                time_str = point.time.strftime("%H:%M")
                crossings = []
                
                # Check precipitation probability
                if point.rain_probability is not None:
                    threshold = thresholds.get("rain_probability", 25.0)
                    if point.rain_probability >= threshold:
                        crossings.append(f"Rain probability {point.rain_probability}% >= {threshold}%")
                
                # Check thunderstorm probability
                if point.thunderstorm_probability is not None:
                    threshold = thresholds.get("thunderstorm_probability", 20.0)
                    if point.thunderstorm_probability >= threshold:
                        crossings.append(f"Thunderstorm probability {point.thunderstorm_probability}% >= {threshold}%")
                
                # Check precipitation amount
                if point.precipitation is not None:
                    threshold = thresholds.get("rain_amount", 2.0)
                    if point.precipitation >= threshold:
                        crossings.append(f"Precipitation amount {point.precipitation}mm >= {threshold}mm")
                
                # Check wind speed
                if point.wind_speed is not None:
                    threshold = thresholds.get("wind_speed", 40.0)
                    if point.wind_speed >= threshold:
                        crossings.append(f"Wind speed {point.wind_speed}km/h >= {threshold}km/h")
                
                if crossings:
                    validation_results["crossings"].append({
                        "time": time_str,
                        "crossings": crossings
                    })
            
            if self.debug_config.get("save_debug_files", True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{location_name.lower()}_thresholds_{timestamp}.json"
                filepath = os.path.join(self.output_directory, filename)
                
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(validation_results, f, indent=2, default=str)
                
                logger.debug(f"Threshold validation saved to {filepath}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate thresholds for {location_name}: {e}")
            return None
    
    def generate_debug_summary(
        self,
        debug_info: ReportDebugInfo
    ) -> str:
        """
        Generate a debug summary for the report generation.
        
        Args:
            debug_info: Debug information from report generation
            
        Returns:
            Formatted debug summary
        """
        if not self.should_debug():
            return ""
        
        summary_lines = []
        summary_lines.append("=" * 60)
        summary_lines.append("DEBUG SUMMARY")
        summary_lines.append("=" * 60)
        summary_lines.append(f"Location: {debug_info.location_name}")
        summary_lines.append(f"Timestamp: {debug_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        summary_lines.append(f"Coordinates: {debug_info.latitude}, {debug_info.longitude}")
        
        if debug_info.raw_data:
            summary_lines.append(f"Raw data points: {len(debug_info.raw_data.time_points)}")
        
        if debug_info.weather_analysis:
            summary_lines.append(f"Analysis completed: Yes")
            summary_lines.append(f"Max rain probability: {debug_info.weather_analysis.max_rain_probability}%")
            summary_lines.append(f"Max thunderstorm probability: {debug_info.weather_analysis.max_thunderstorm_probability}%")
        
        if debug_info.comparison_results:
            issues = debug_info.comparison_results.get("issues", [])
            if issues:
                summary_lines.append(f"Comparison issues: {len(issues)}")
                for issue in issues:
                    summary_lines.append(f"  - {issue}")
            else:
                summary_lines.append("Comparison: No issues found")
        
        if debug_info.debug_files:
            summary_lines.append(f"Debug files generated: {len(debug_info.debug_files)}")
            for file in debug_info.debug_files:
                summary_lines.append(f"  - {file}")
        
        summary_lines.append("=" * 60)
        
        return "\n".join(summary_lines)
    
    def log_debug_info(self, debug_info: ReportDebugInfo) -> None:
        """
        Log debug information to console and files.
        
        Args:
            debug_info: Debug information to log
        """
        if not self.should_debug():
            return
        
        # Generate summary
        summary = self.generate_debug_summary(debug_info)
        
        # Log to console
        logger.info(summary)
        
        # Save summary to file
        if self.debug_config.get("save_debug_files", True):
            timestamp = debug_info.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{debug_info.location_name.lower()}_debug_summary_{timestamp}.txt"
            filepath = os.path.join(self.output_directory, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary)
                f.write("\n\n")
                
                # Add raw data if available
                if debug_info.raw_data:
                    f.write("RAW WEATHER DATA:\n")
                    f.write("-" * 40)
                    f.write("\n")
                    f.write(format_raw_data_output(debug_info.raw_data))
                    f.write("\n\n")
                
                # Add comparison results if available
                if debug_info.comparison_results:
                    f.write("COMPARISON RESULTS:\n")
                    f.write("-" * 40)
                    f.write("\n")
                    import json
                    f.write(json.dumps(debug_info.comparison_results, indent=2, default=str))
            
            logger.debug(f"Debug summary saved to {filepath}")


def create_report_debugger(config: Dict[str, Any]) -> ReportDebugger:
    """
    Create a report debugger instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        ReportDebugger instance
    """
    return ReportDebugger(config) 


if __name__ == "__main__":
    import sys
    import os
    # Ensure src/ is in sys.path for absolute imports
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.wetter.fire_risk_massif import FireRiskMassif
    from src.wetter.weather_data_processor import WeatherDataProcessor
    import yaml

    # Example GR20 coordinates (replace with actual list as needed)
    GR20_POINTS = [
        (41.5912, 9.2806, "Conca"),
        (41.7358, 9.2042, "Col de Bavella"),
        (41.9181, 8.9247, "Vizzavona"),
        (42.3061, 9.1500, "Corte"),
        (42.4181, 8.9247, "Haut Asco"),
        (42.4900, 8.9000, "Calenzana"),
        # Add more as needed
    ]

    # Load config for thresholds
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    fire_risk = FireRiskMassif()
    processor = WeatherDataProcessor(config)

    print("Stage | Lat | Lon | Massif | FireWarn | MaxTemp | MaxRain | MaxRainProb | MaxThunderProb | MaxWind | MaxWindGusts")
    print("-"*120)
    for lat, lon, name in GR20_POINTS:
        massif_id = fire_risk._get_massif_for_coordinates(lat, lon)
        massif_name = fire_risk._get_massif_name(massif_id) if massif_id else "-"
        fire_warn = fire_risk.format_fire_warnings(lat, lon)
        report = processor.process_weather_data(lat, lon, name)
        max_temp = report.get("max_temperature", "-")
        max_rain = report.get("max_precipitation", "-")
        max_rain_prob = report.get("max_rain_probability", "-")
        max_thunder_prob = report.get("max_thunderstorm_probability", "-")
        max_wind = report.get("wind_speed", "-")
        max_wind_gusts = report.get("max_wind_speed", "-")
        print(f"{name} | {lat:.4f} | {lon:.4f} | {massif_name} | {fire_warn} | {max_temp} | {max_rain} | {max_rain_prob} | {max_thunder_prob} | {max_wind} | {max_wind_gusts}") 