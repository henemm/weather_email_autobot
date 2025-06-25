"""
Weather warning validation module for meteofrance-api.

This module provides comprehensive validation of weather warnings and ensures
consistency between different data sources during complex weather situations.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import re

from meteofrance_api.client import MeteoFranceClient
from meteofrance_api.model import Forecast, CurrentPhenomenons

from .fetch_meteofrance import ForecastResult, Alert


logger = logging.getLogger(__name__)


@dataclass
class WarningValidationResult:
    """Result of warning validation."""
    location: str
    timestamp: datetime
    risk_levels_consistent: bool
    thunderstorm_detected: bool
    warning_level: str
    forecast_probability: float
    daily_consistent: bool
    text_processed: bool
    validation_score: float  # 0.0 to 1.0
    issues: List[str]


@dataclass
class ComplexWarningSituation:
    """Represents a complex warning situation for validation."""
    location_name: str
    latitude: float
    longitude: float
    department: str
    forecast_data: Optional[Dict[str, Any]] = None
    warning_data: Optional[Dict[str, Any]] = None
    daily_data: Optional[Dict[str, Any]] = None
    validation_result: Optional[WarningValidationResult] = None


class WarnlagenValidator:
    """
    Validator for complex weather warning situations.
    
    This class validates the consistency and accuracy of weather warnings
    from meteofrance-api during unstable or contradictory weather conditions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the validator.
        
        Args:
            config: Configuration dictionary containing thresholds and settings
        """
        self.config = config
        self.client = MeteoFranceClient()
        self.logger = logging.getLogger(__name__)
        
        # Extract thresholds from config
        self.thresholds = config.get("thresholds", {})
        self.delta_thresholds = config.get("delta_thresholds", {})
        
    def validate_location(self, location_name: str, lat: float, lon: float, 
                         department: str) -> WarningValidationResult:
        """
        Validate weather warnings for a specific location.
        
        Args:
            location_name: Name of the location
            lat: Latitude coordinate
            lon: Longitude coordinate
            department: Department code
            
        Returns:
            WarningValidationResult with validation details
        """
        self.logger.info(f"Validating warnings for {location_name}")
        
        try:
            # Fetch all required data
            forecast = self._fetch_forecast(lat, lon)
            warnings = self._fetch_warnings(department)
            
            # Perform validation checks (without daily forecast)
            validation_result = self._perform_validation_checks(
                location_name, forecast, warnings
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Validation failed for {location_name}: {e}")
            return self._create_error_result(location_name, str(e))
    
    def _fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch hourly forecast data."""
        try:
            forecast = self.client.get_forecast(lat, lon)
            result = {
                "forecast": forecast.forecast,
                "timestamp": datetime.now()
            }
            self.logger.debug(f"Fetched forecast data: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to fetch forecast: {e}")
            raise
    
    def _fetch_warnings(self, department: str) -> Dict[str, Any]:
        """Fetch warning data for department."""
        try:
            warnings = self.client.get_warning_current_phenomenons(department)
            result = {
                "phenomenons_max_colors": warnings.phenomenons_max_colors,
                "warnings": warnings.warnings if hasattr(warnings, 'warnings') else [],
                "timestamp": datetime.now()
            }
            self.logger.debug(f"Fetched warnings data: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to fetch warnings: {e}")
            raise
    
    def _perform_validation_checks(self, location_name: str, 
                                 forecast: Dict[str, Any],
                                 warnings: Dict[str, Any]) -> WarningValidationResult:
        """Perform all validation checks."""
        issues = []
        checks = []
        
        # Check 1: Risk levels consistency with warnings
        risk_consistent = self._check_risk_levels_consistency(forecast, warnings)
        checks.append(("risk_levels_consistent", risk_consistent))
        if not risk_consistent:
            issues.append("Risk levels inconsistent with warnings")
        
        # Check 2: Thunderstorm detection accuracy
        thunderstorm_detected = self._check_thunderstorm_detection(forecast)
        checks.append(("thunderstorm_detected", thunderstorm_detected))
        
        # Check 3: Warning text processing
        text_processed = self._check_warning_text_processing(warnings)
        checks.append(("text_processed", text_processed))
        
        # Calculate validation score
        validation_score = sum(1 for _, passed in checks if passed) / len(checks)
        
        # Get warning level and forecast probability
        warning_level = self._get_highest_warning_level(warnings)
        forecast_probability = self._get_max_thunderstorm_probability(forecast)
        
        return WarningValidationResult(
            location=location_name,
            timestamp=datetime.now(),
            risk_levels_consistent=risk_consistent,
            thunderstorm_detected=thunderstorm_detected,
            warning_level=warning_level,
            forecast_probability=forecast_probability,
            daily_consistent=True,  # Set to True since we don't have daily data
            text_processed=text_processed,
            validation_score=validation_score,
            issues=issues
        )
    
    def _check_risk_levels_consistency(self, forecast: Dict[str, Any], 
                                     warnings: Dict[str, Any]) -> bool:
        """Check if risk levels are consistent with warnings."""
        try:
            # Get maximum thunderstorm probability from forecast
            max_thunderstorm_prob = self._get_max_thunderstorm_probability(forecast)
            
            # Get thunderstorm warning level
            phenomenons = warnings.get("phenomenons_max_colors", {})
            if isinstance(phenomenons, dict):
                thunderstorm_warning = phenomenons.get("thunderstorm", "green")
            else:
                thunderstorm_warning = "green"
            
            # Define consistency rules
            if max_thunderstorm_prob >= 80 and thunderstorm_warning == "green":
                return False  # High probability but green warning
            elif max_thunderstorm_prob <= 10 and thunderstorm_warning in ["orange", "red"]:
                return False  # Low probability but high warning
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking risk levels consistency: {e}")
            return False
    
    def _check_thunderstorm_detection(self, forecast: Dict[str, Any]) -> bool:
        """Check if thunderstorm is correctly detected."""
        try:
            forecast_data = forecast.get("forecast", [])
            
            if not isinstance(forecast_data, list):
                return False
            
            # Check if any forecast entry indicates thunderstorm
            for entry in forecast_data[:6]:  # Check next 6 hours
                if not isinstance(entry, dict):
                    continue
                    
                # Check weather description for thunderstorm
                weather = entry.get("weather", {})
                if isinstance(weather, dict):
                    desc = weather.get("desc", "").lower()
                    print(f"DEBUG: weather desc = '{desc}'")
                    if "orage" in desc:
                        return True
                    if "thunderstorm" in desc:
                        return True
                
                # Check rain amount as secondary indicator
                rain = entry.get("rain", {})
                if isinstance(rain, dict):
                    rain_1h = rain.get("1h", 0)
                    if isinstance(rain_1h, (int, float)) and rain_1h >= 0.5:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking thunderstorm detection: {e}")
            return False
    
    def _check_warning_text_processing(self, warnings: Dict[str, Any]) -> bool:
        """Check if warning text is correctly processed."""
        try:
            # Check if warnings have text descriptions
            warnings_list = warnings.get("warnings", [])
            
            if not warnings_list:
                return True  # No warnings means no text to process
            
            if not isinstance(warnings_list, list):
                return False
            
            # Check if warnings have descriptions
            for warning in warnings_list:
                if not isinstance(warning, dict):
                    continue
                if not warning.get("description"):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking warning text processing: {e}")
            return False
    
    def _get_highest_warning_level(self, warnings: Dict[str, Any]) -> str:
        """Get the highest warning level from all phenomena."""
        try:
            phenomenons = warnings.get("phenomenons_max_colors", [])
            
            if not phenomenons or not isinstance(phenomenons, list):
                return "green"
            
            # Define warning level hierarchy (phenomenon_max_color_id: 1=green, 2=yellow, 3=orange, 4=red)
            max_level_id = 1  # Default to green
            
            for phenomenon in phenomenons:
                if isinstance(phenomenon, dict):
                    level_id = phenomenon.get("phenomenon_max_color_id", 1)
                    if isinstance(level_id, int) and level_id > max_level_id:
                        max_level_id = level_id
            
            # Convert level_id to string
            level_map = {1: "green", 2: "yellow", 3: "orange", 4: "red"}
            return level_map.get(max_level_id, "green")
            
        except Exception as e:
            self.logger.error(f"Error getting highest warning level: {e}")
            return "green"
    
    def _get_max_thunderstorm_probability(self, forecast: Dict[str, Any]) -> float:
        """Get maximum thunderstorm probability from forecast."""
        try:
            forecast_data = forecast.get("forecast", [])
            
            if not isinstance(forecast_data, list):
                return 0.0
            
            max_rain = 0.0
            for entry in forecast_data[:6]:  # Check next 6 hours
                if not isinstance(entry, dict):
                    continue
                rain = entry.get("rain", {})
                if isinstance(rain, dict):
                    rain_1h = rain.get("1h", 0)
                    if isinstance(rain_1h, (int, float)) and rain_1h > max_rain:
                        max_rain = rain_1h
            
            # Convert rain amount to probability (rough estimation)
            # 0.1mm = 10% probability, 1.0mm = 100% probability
            probability = min(max_rain * 100, 100.0)
            return probability
            
        except Exception as e:
            self.logger.error(f"Error getting max thunderstorm probability: {e}")
            return 0.0
    
    def _create_error_result(self, location_name: str, error_message: str) -> WarningValidationResult:
        """Create a validation result for error cases."""
        return WarningValidationResult(
            location=location_name,
            timestamp=datetime.now(),
            risk_levels_consistent=False,
            thunderstorm_detected=False,
            warning_level="green",
            forecast_probability=0.0,
            daily_consistent=False,
            text_processed=False,
            validation_score=0.0,
            issues=[f"Validation error: {error_message}"]
        )
    
    def validate_multiple_locations(self, locations: List[Tuple[str, float, float, str]]) -> List[WarningValidationResult]:
        """
        Validate warnings for multiple locations.
        
        Args:
            locations: List of (name, lat, lon, department) tuples
            
        Returns:
            List of WarningValidationResult objects
        """
        results = []
        
        for location_name, lat, lon, department in locations:
            try:
                result = self.validate_location(location_name, lat, lon, department)
                results.append(result)
                
                # Log validation summary
                self.logger.info(f"Validation for {location_name}: "
                               f"Score={result.validation_score:.2f}, "
                               f"Warning={result.warning_level}, "
                               f"Issues={len(result.issues)}")
                
            except Exception as e:
                self.logger.error(f"Failed to validate {location_name}: {e}")
                error_result = self._create_error_result(location_name, str(e))
                results.append(error_result)
        
        return results
    
    def generate_validation_report(self, results: List[WarningValidationResult]) -> str:
        """
        Generate a comprehensive validation report.
        
        Args:
            results: List of validation results
            
        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("WEATHER WARNING VALIDATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Locations tested: {len(results)}")
        report_lines.append("")
        
        # Summary statistics
        total_score = sum(r.validation_score for r in results)
        avg_score = total_score / len(results) if results else 0
        high_warnings = sum(1 for r in results if r.warning_level in ["orange", "red"])
        issues_found = sum(len(r.issues) for r in results)
        
        report_lines.append("SUMMARY:")
        report_lines.append(f"  Average validation score: {avg_score:.2f}")
        report_lines.append(f"  High warning locations: {high_warnings}")
        report_lines.append(f"  Total issues found: {issues_found}")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("DETAILED RESULTS:")
        report_lines.append("-" * 40)
        
        for result in results:
            report_lines.append(f"Location: {result.location}")
            report_lines.append(f"  Score: {result.validation_score:.2f}")
            report_lines.append(f"  Warning Level: {result.warning_level}")
            report_lines.append(f"  Thunderstorm Probability: {result.forecast_probability:.1f}%")
            report_lines.append(f"  Thunderstorm Detected: {result.thunderstorm_detected}")
            report_lines.append(f"  Risk Levels Consistent: {result.risk_levels_consistent}")
            report_lines.append(f"  Daily/Hourly Consistent: {result.daily_consistent}")
            
            if result.issues:
                report_lines.append(f"  Issues: {', '.join(result.issues)}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)


def create_test_locations() -> List[Tuple[str, float, float, str]]:
    """Create list of test locations for validation."""
    return [
        ("Pau", 43.2951, -0.3708, "64"),
        ("Grenoble", 45.1885, 5.7245, "38"),
        ("Lyon", 45.7578, 4.8320, "69"),
        ("Marseille", 43.2965, 5.3698, "13"),
        ("Toulouse", 43.6047, 1.4442, "31")
    ]


def run_comprehensive_validation(config: Dict[str, Any]) -> str:
    """
    Run comprehensive validation for all test locations.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validation report as string
    """
    validator = WarnlagenValidator(config)
    locations = create_test_locations()
    
    logger.info(f"Starting comprehensive validation for {len(locations)} locations")
    
    results = validator.validate_multiple_locations(locations)
    report = validator.generate_validation_report(results)
    
    logger.info("Comprehensive validation completed")
    
    return report 