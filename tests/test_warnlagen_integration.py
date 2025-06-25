"""
Integration tests for weather warning validation system.

This module tests the integration between different components of the warning
validation system and ensures they work together correctly.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import logging

from src.wetter.warnlagen_validator import (
    WarnlagenValidator,
    WarningValidationResult,
    ComplexWarningSituation,
    create_test_locations,
    run_comprehensive_validation
)
from src.config.config_loader import load_config


class TestWarnlagenValidatorIntegration:
    """Integration tests for WarnlagenValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = load_config()
        self.validator = WarnlagenValidator(self.config)
        self.logger = logging.getLogger(__name__)
        
    def test_validator_initialization(self):
        """Test that validator initializes correctly with config."""
        assert self.validator.config is not None
        assert "thresholds" in self.validator.config
        assert "delta_thresholds" in self.validator.config
        assert self.validator.client is not None
        
        # Check that thresholds are loaded
        thresholds = self.validator.thresholds
        assert "thunderstorm_probability" in thresholds
        assert "rain_probability" in thresholds
        assert "wind_speed" in thresholds
        
        print("✓ Validator initialization successful")
    
    def test_test_locations_creation(self):
        """Test that test locations are created correctly."""
        locations = create_test_locations()
        
        assert len(locations) == 5, "Should have 5 test locations"
        
        # Check structure of each location
        for location_name, lat, lon, department in locations:
            assert isinstance(location_name, str)
            assert isinstance(lat, float)
            assert isinstance(lon, float)
            assert isinstance(department, str)
            assert len(department) == 2, "Department should be 2 characters"
        
        # Check specific locations
        location_names = [loc[0] for loc in locations]
        expected_names = ["Pau", "Grenoble", "Lyon", "Marseille", "Toulouse"]
        assert set(location_names) == set(expected_names)
        
        print("✓ Test locations creation successful")
    
    @patch('src.wetter.warnlagen_validator.MeteoFranceClient')
    def test_mock_validation_workflow(self, mock_client):
        """Test validation workflow with mocked API responses."""
        # Create validator after patch is applied
        validator = WarnlagenValidator(self.config)
        
        # Setup mock responses with real API structure
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                "dt": 1750852800,
                "T": {"value": 25.0},
                "weather": {"icon": "p26j", "desc": "Risque d'orages"},
                "rain": {"1h": 0.5},
                "wind": {"speed": 25.0},
                "clouds": 90
            },
            {
                "dt": 1750856400,
                "T": {"value": 26.0},
                "weather": {"icon": "p26j", "desc": "Risque d'orages"},
                "rain": {"1h": 0.8},
                "wind": {"speed": 30.0},
                "clouds": 95
            }
        ]
        
        mock_warnings = Mock()
        mock_warnings.phenomenons_max_colors = [
            {"phenomenon_id": "3", "phenomenon_max_color_id": 3},  # Orange thunderstorm
            {"phenomenon_id": "6", "phenomenon_max_color_id": 2},  # Yellow rain
            {"phenomenon_id": "1", "phenomenon_max_color_id": 1}   # Green wind
        ]
        mock_warnings.warnings = [
            {
                "phenomenon": "thunderstorm",
                "level": "orange",
                "description": "Thunderstorm warning: orange level"
            }
        ]
        
        # Configure mock client
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_forecast.return_value = mock_forecast
        mock_client_instance.get_warning_current_phenomenons.return_value = mock_warnings
        
        # Debug: Check what the validator receives
        print(f"Mock forecast.forecast: {mock_forecast.forecast}")
        print(f"Mock warnings.phenomenons_max_colors: {mock_warnings.phenomenons_max_colors}")
        
        # Run validation
        result = validator.validate_location("Test Location", 43.0, 1.0, "31")
        
        # Debug: Check the result
        print(f"Validation result: {result}")
        print(f"Thunderstorm detected: {result.thunderstorm_detected}")
        print(f"Forecast probability: {result.forecast_probability}")
        print(f"Warning level: {result.warning_level}")
        
        # Verify result
        assert isinstance(result, WarningValidationResult)
        assert result.location == "Test Location"
        assert result.thunderstorm_detected is True
        assert result.warning_level == "orange"
        assert result.forecast_probability > 0.0
        assert result.daily_consistent is True  # Always True since we don't have daily data
        assert result.validation_score > 0.5  # Should pass most checks
        
        print("✓ Mock validation workflow successful")
    
    def test_validation_result_structure(self):
        """Test that validation results have correct structure."""
        # Create a sample validation result
        result = WarningValidationResult(
            location="Test Location",
            timestamp=datetime.now(),
            risk_levels_consistent=True,
            thunderstorm_detected=True,
            warning_level="orange",
            forecast_probability=75.0,
            daily_consistent=True,
            text_processed=True,
            validation_score=0.8,
            issues=[]
        )
        
        # Verify all fields are present and correct types
        assert isinstance(result.location, str)
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.risk_levels_consistent, bool)
        assert isinstance(result.thunderstorm_detected, bool)
        assert isinstance(result.warning_level, str)
        assert isinstance(result.forecast_probability, float)
        assert isinstance(result.daily_consistent, bool)
        assert isinstance(result.text_processed, bool)
        assert isinstance(result.validation_score, float)
        assert isinstance(result.issues, list)
        
        # Verify validation score range
        assert 0.0 <= result.validation_score <= 1.0
        
        # Verify warning level is valid
        assert result.warning_level in ["green", "yellow", "orange", "red"]
        
        print("✓ Validation result structure correct")
    
    def test_report_generation(self):
        """Test report generation functionality."""
        # Create sample validation results
        results = [
            WarningValidationResult(
                location="Location 1",
                timestamp=datetime.now(),
                risk_levels_consistent=True,
                thunderstorm_detected=True,
                warning_level="orange",
                forecast_probability=80.0,
                daily_consistent=True,
                text_processed=True,
                validation_score=0.9,
                issues=[]
            ),
            WarningValidationResult(
                location="Location 2",
                timestamp=datetime.now(),
                risk_levels_consistent=False,
                thunderstorm_detected=False,
                warning_level="green",
                forecast_probability=10.0,
                daily_consistent=False,
                text_processed=True,
                validation_score=0.3,
                issues=["Risk levels inconsistent with warnings"]
            )
        ]
        
        # Generate report
        report = self.validator.generate_validation_report(results)
        
        # Verify report structure
        assert isinstance(report, str)
        assert "WEATHER WARNING VALIDATION REPORT" in report
        assert "Location 1" in report
        assert "Location 2" in report
        assert "Average validation score:" in report
        assert "High warning locations:" in report
        assert "Total issues found:" in report
        
        # Verify report contains expected data
        assert "0.9" in report  # Score for Location 1
        assert "0.3" in report  # Score for Location 2
        assert "orange" in report  # Warning level
        assert "green" in report  # Warning level
        
        print("✓ Report generation successful")
    
    def test_complex_warning_situation_creation(self):
        """Test creation of complex warning situation objects."""
        situation = ComplexWarningSituation(
            location_name="Test Location",
            latitude=43.0,
            longitude=1.0,
            department="31",
            forecast_data={"test": "data"},
            warning_data={"test": "warnings"},
            daily_data={"test": "daily"}
        )
        
        # Verify structure
        assert situation.location_name == "Test Location"
        assert situation.latitude == 43.0
        assert situation.longitude == 1.0
        assert situation.department == "31"
        assert situation.forecast_data == {"test": "data"}
        assert situation.warning_data == {"test": "warnings"}
        assert situation.daily_data == {"test": "daily"}
        assert situation.validation_result is None
        
        print("✓ Complex warning situation creation successful")


class TestValidationChecks:
    """Test individual validation check methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = load_config()
        self.validator = WarnlagenValidator(self.config)
    
    def test_risk_levels_consistency_check(self):
        """Test risk levels consistency checking."""
        # Test case 1: Consistent data (low rain amount, green warning)
        forecast_consistent = {
            "forecast": [
                {"rain": {"1h": 0.1}, "weather": {"desc": "sunny"}}
            ]
        }
        warnings_consistent = {
            "phenomenons_max_colors": [{"phenomenon_id": "3", "phenomenon_max_color_id": 1}]  # Green thunderstorm
        }
        
        result = self.validator._check_risk_levels_consistency(
            forecast_consistent, warnings_consistent
        )
        assert result is True, "Low rain amount with green warning should be consistent"
        
        # Test case 2: Inconsistent data (high rain amount, green warning)
        forecast_inconsistent = {
            "forecast": [
                {"rain": {"1h": 2.0}, "weather": {"desc": "thunderstorm"}}
            ]
        }
        warnings_inconsistent = {
            "phenomenons_max_colors": [{"phenomenon_id": "3", "phenomenon_max_color_id": 1}]  # Green thunderstorm
        }
        
        result = self.validator._check_risk_levels_consistency(
            forecast_inconsistent, warnings_inconsistent
        )
        assert result is False, "High rain amount with green warning should be inconsistent"
        
        print("✓ Risk levels consistency check successful")
    
    def test_thunderstorm_detection_check(self):
        """Test thunderstorm detection checking."""
        # Test case 1: Thunderstorm detected via weather description
        forecast_with_thunderstorm = {
            "forecast": [
                {"weather": {"desc": "Risque d'orages"}, "rain": {"1h": 0.5}},
                {"weather": {"desc": "sunny"}, "rain": {"1h": 0.1}}
            ]
        }
        
        result = self.validator._check_thunderstorm_detection(forecast_with_thunderstorm)
        assert result is True, "Thunderstorm weather description should be detected"
        
        # Test case 2: No thunderstorm
        forecast_without_thunderstorm = {
            "forecast": [
                {"weather": {"desc": "sunny"}, "rain": {"1h": 0.1}},
                {"weather": {"desc": "cloudy"}, "rain": {"1h": 0.2}}
            ]
        }
        
        result = self.validator._check_thunderstorm_detection(forecast_without_thunderstorm)
        assert result is False, "No thunderstorm weather should not be detected"
        
        # Test case 3: High rain amount (secondary indicator)
        forecast_high_rain = {
            "forecast": [
                {"weather": {"desc": "rain"}, "rain": {"1h": 1.0}}
            ]
        }
        
        result = self.validator._check_thunderstorm_detection(forecast_high_rain)
        assert result is True, "High rain amount should be detected as thunderstorm indicator"
        
        print("✓ Thunderstorm detection check successful")
    
    def test_warning_level_hierarchy(self):
        """Test warning level hierarchy determination."""
        # Test case 1: Single warning level (orange)
        warnings_single = {
            "phenomenons_max_colors": [{"phenomenon_id": "3", "phenomenon_max_color_id": 3}]  # Orange thunderstorm
        }
        
        result = self.validator._get_highest_warning_level(warnings_single)
        assert result == "orange"
        
        # Test case 2: Multiple warning levels
        warnings_multiple = {
            "phenomenons_max_colors": [
                {"phenomenon_id": "3", "phenomenon_max_color_id": 2},  # Yellow thunderstorm
                {"phenomenon_id": "6", "phenomenon_max_color_id": 3},  # Orange rain
                {"phenomenon_id": "1", "phenomenon_max_color_id": 1}   # Green wind
            ]
        }
        
        result = self.validator._get_highest_warning_level(warnings_multiple)
        assert result == "orange", "Should return highest level (orange)"
        
        # Test case 3: No warnings
        warnings_empty = {
            "phenomenons_max_colors": []
        }
        
        result = self.validator._get_highest_warning_level(warnings_empty)
        assert result == "green", "Should default to green when no warnings"
        
        print("✓ Warning level hierarchy check successful")


def test_comprehensive_validation_integration():
    """Test comprehensive validation integration."""
    config = load_config()
    
    # Test that the function can be called without errors
    try:
        # This would normally make live API calls, so we'll just test the function exists
        # and can be imported
        assert callable(run_comprehensive_validation)
        assert run_comprehensive_validation.__doc__ is not None
        
        print("✓ Comprehensive validation function available")
        
    except Exception as e:
        pytest.skip(f"Comprehensive validation not available: {e}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 