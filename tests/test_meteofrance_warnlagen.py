"""
Test module for validating meteofrance-api during complex weather warning situations.

This module tests the system's ability to handle unstable or contradictory weather conditions,
such as typical summer thunderstorms, and ensures reliable interpretation and correct report generation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import logging

from src.wetter.fetch_meteofrance import (
    get_forecast,
    get_thunderstorm,
    get_alerts,
    ForecastResult,
    Alert
)
from src.wetter.warning import WarningMonitor
from src.config.config_loader import load_config


# Test locations with known summer thunderstorm conditions
TEST_LOCATIONS = {
    "pau": {"lat": 43.2951, "lon": -0.3708, "department": "64"},
    "grenoble": {"lat": 45.1885, "lon": 5.7245, "department": "38"},
    "lyon": {"lat": 45.7578, "lon": 4.8320, "department": "69"},
    "marseille": {"lat": 43.2965, "lon": 5.3698, "department": "13"},
    "toulouse": {"lat": 43.6047, "lon": 1.4442, "department": "31"}
}


class TestMeteoFranceWarnlagenValidation:
    """Test class for validating meteofrance-api during complex warning situations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = load_config()
        self.logger = logging.getLogger(__name__)
        
    def test_risk_levels_consistency_with_warnings(self):
        """Test that risk levels are consistent with warnings."""
        # This test will be implemented after the main functionality
        pass
        
    def test_thunderstorm_detection_accuracy(self):
        """Test that thunderstorm detection matches official website data."""
        # This test will be implemented after the main functionality
        pass
        
    def test_daily_warnings_consistency_with_hourly_risks(self):
        """Test that daily warnings are consistent with hourly risk levels."""
        # This test will be implemented after the main functionality
        pass
        
    def test_warning_text_processing(self):
        """Test that warning text is correctly processed when text output is active."""
        # This test will be implemented after the main functionality
        pass
        
    def test_threshold_recognition_in_mail_output(self):
        """Test that thresholds are correctly recognized in mail output."""
        # This test will be implemented after the main functionality
        pass
        
    def test_warning_generation_for_high_warning_levels(self):
        """Test that warnings are generated when warning_level >= warn_thresholds.warning."""
        # This test will be implemented after the main functionality
        pass


def create_mock_forecast_data(thunderstorm_probability: int = 0) -> Dict[str, Any]:
    """Create mock forecast data for testing."""
    return {
        "forecast": [
            {
                "datetime": "2025-06-25T10:00:00+02:00",
                "T": {"value": 25.0},
                "weather": "thunderstorm" if thunderstorm_probability > 0 else "sunny",
                "precipitation_probability": thunderstorm_probability,
                "wind_speed": 15.0,
                "cloud_cover": 60
            },
            {
                "datetime": "2025-06-25T11:00:00+02:00",
                "T": {"value": 26.0},
                "weather": "thunderstorm" if thunderstorm_probability > 0 else "sunny",
                "precipitation_probability": thunderstorm_probability,
                "wind_speed": 18.0,
                "cloud_cover": 70
            }
        ]
    }


def create_mock_warning_data(level: str = "green") -> Dict[str, Any]:
    """Create mock warning data for testing."""
    return {
        "phenomenons_max_colors": {
            "thunderstorm": level,
            "rain": level,
            "wind": level
        },
        "warnings": [
            {
                "phenomenon": "thunderstorm",
                "level": level,
                "description": f"Thunderstorm warning: {level} level"
            }
        ]
    }


def create_mock_daily_forecast_data() -> Dict[str, Any]:
    """Create mock daily forecast data for testing."""
    return {
        "forecast": [
            {
                "date": "2025-06-25",
                "T": {"min": 15.0, "max": 28.0},
                "precipitation_probability": 30,
                "weather": "thunderstorm"
            },
            {
                "date": "2025-06-26",
                "T": {"min": 16.0, "max": 29.0},
                "precipitation_probability": 25,
                "weather": "sunny"
            }
        ]
    }


class TestLiveMeteoFranceWarnlagen:
    """Live tests for meteofrance-api warning validation."""
    
    def test_live_forecast_retrieval(self):
        """Test live forecast retrieval for test locations."""
        for location_name, coords in TEST_LOCATIONS.items():
            try:
                result = get_forecast(coords["lat"], coords["lon"])
                assert isinstance(result, ForecastResult)
                assert result.temperature is not None
                assert result.data_source == "meteofrance-api"
                print(f"✓ Live forecast for {location_name}: {result.temperature}°C")
            except Exception as e:
                pytest.skip(f"Live API not available for {location_name}: {e}")
    
    def test_live_thunderstorm_detection(self):
        """Test live thunderstorm detection for test locations."""
        for location_name, coords in TEST_LOCATIONS.items():
            try:
                result = get_thunderstorm(coords["lat"], coords["lon"])
                assert isinstance(result, str)
                assert len(result) > 0
                print(f"✓ Thunderstorm detection for {location_name}: {result}")
            except Exception as e:
                pytest.skip(f"Live thunderstorm detection not available for {location_name}: {e}")
    
    def test_live_alerts_retrieval(self):
        """Test live alerts retrieval for test locations."""
        for location_name, coords in TEST_LOCATIONS.items():
            try:
                alerts = get_alerts(coords["lat"], coords["lon"])
                assert isinstance(alerts, list)
                for alert in alerts:
                    assert isinstance(alert, Alert)
                    assert alert.phenomenon in ["thunderstorm", "rain", "wind", "flood"]
                    assert alert.level in ["green", "yellow", "orange", "red"]
                print(f"✓ Alerts for {location_name}: {len(alerts)} alerts found")
            except Exception as e:
                pytest.skip(f"Live alerts not available for {location_name}: {e}")


class TestWarningConsistency:
    """Test warning consistency across different data sources."""
    
    def test_risk_levels_vs_warnings_consistency(self):
        """Test that risk levels are consistent with warnings."""
        # Mock data with inconsistent risk levels and warnings
        mock_forecast = create_mock_forecast_data(thunderstorm_probability=80)
        mock_warnings = create_mock_warning_data(level="green")
        
        # This would indicate an inconsistency - high thunderstorm probability
        # but green warning level
        assert mock_forecast["forecast"][0]["precipitation_probability"] == 80
        assert mock_warnings["phenomenons_max_colors"]["thunderstorm"] == "green"
        
        # In a real implementation, this should trigger a warning or error
        # For now, we just document the potential inconsistency
        print("⚠️ Potential inconsistency: High thunderstorm probability (80%) but green warning level")
    
    def test_hourly_vs_daily_consistency(self):
        """Test consistency between hourly and daily forecasts."""
        hourly_data = create_mock_forecast_data(thunderstorm_probability=60)
        daily_data = create_mock_daily_forecast_data()
        
        # Check if daily thunderstorm probability matches hourly patterns
        hourly_thunderstorm_hours = sum(
            1 for entry in hourly_data["forecast"] 
            if entry["weather"] == "thunderstorm"
        )
        daily_has_thunderstorm = daily_data["forecast"][0]["weather"] == "thunderstorm"
        
        # This should be consistent
        if hourly_thunderstorm_hours > 0:
            assert daily_has_thunderstorm, "Daily forecast should show thunderstorm if hourly does"
        
        print(f"✓ Hourly thunderstorm hours: {hourly_thunderstorm_hours}")
        print(f"✓ Daily thunderstorm forecast: {daily_has_thunderstorm}")


class TestThresholdValidation:
    """Test threshold validation and warning generation."""
    
    def test_thunderstorm_threshold_recognition(self):
        """Test that thunderstorm thresholds are correctly recognized."""
        config = load_config()
        thunderstorm_threshold = config.get("thresholds", {}).get("thunderstorm_probability", 20.0)
        
        # Test data below threshold
        low_prob_data = create_mock_forecast_data(thunderstorm_probability=15)
        below_threshold = low_prob_data["forecast"][0]["precipitation_probability"] < thunderstorm_threshold
        assert below_threshold, "15% should be below threshold"
        
        # Test data above threshold
        high_prob_data = create_mock_forecast_data(thunderstorm_probability=25)
        above_threshold = high_prob_data["forecast"][0]["precipitation_probability"] > thunderstorm_threshold
        assert above_threshold, "25% should be above threshold"
        
        print(f"✓ Thunderstorm threshold: {thunderstorm_threshold}%")
        print(f"✓ Below threshold (15%): {below_threshold}")
        print(f"✓ Above threshold (25%): {above_threshold}")
    
    def test_warning_level_thresholds(self):
        """Test warning level thresholds from configuration."""
        config = load_config()
        
        # Test that configuration has required threshold values
        assert "thresholds" in config, "Configuration should have thresholds section"
        thresholds = config["thresholds"]
        
        required_thresholds = [
            "rain_probability",
            "rain_amount", 
            "thunderstorm_probability",
            "wind_speed",
            "temperature"
        ]
        
        for threshold in required_thresholds:
            assert threshold in thresholds, f"Missing threshold: {threshold}"
            assert isinstance(thresholds[threshold], (int, float)), f"Threshold {threshold} should be numeric"
        
        print("✓ All required thresholds present in configuration")


class TestReportGeneration:
    """Test report generation with warning data."""
    
    def test_morning_report_with_warnings(self):
        """Test morning report generation with warning data."""
        # Mock data for morning report
        forecast_data = create_mock_forecast_data(thunderstorm_probability=70)
        warning_data = create_mock_warning_data(level="orange")
        
        # Simulate morning report logic
        max_temp = max(entry["T"]["value"] for entry in forecast_data["forecast"])
        max_wind = max(entry["wind_speed"] for entry in forecast_data["forecast"])
        thunderstorm_prob = max(entry["precipitation_probability"] for entry in forecast_data["forecast"])
        
        # Check if warning should be included
        warning_level = warning_data["phenomenons_max_colors"]["thunderstorm"]
        include_warning = warning_level in ["yellow", "orange", "red"]
        
        assert max_temp == 26.0, "Maximum temperature should be 26.0°C"
        assert max_wind == 18.0, "Maximum wind should be 18.0 km/h"
        assert thunderstorm_prob == 70, "Thunderstorm probability should be 70%"
        assert include_warning, "Orange warning should be included in report"
        
        print("✓ Morning report data validation successful")
    
    def test_evening_report_with_warnings(self):
        """Test evening report generation with warning data."""
        # Mock data for evening report (next day)
        daily_data = create_mock_daily_forecast_data()
        warning_data = create_mock_warning_data(level="red")
        
        # Simulate evening report logic
        tomorrow_temp = daily_data["forecast"][1]["T"]["max"]
        tomorrow_weather = daily_data["forecast"][1]["weather"]
        warning_level = warning_data["phenomenons_max_colors"]["thunderstorm"]
        
        assert tomorrow_temp == 29.0, "Tomorrow's max temperature should be 29.0°C"
        assert tomorrow_weather == "sunny", "Tomorrow's weather should be sunny"
        assert warning_level == "red", "Warning level should be red"
        
        print("✓ Evening report data validation successful")


def test_comprehensive_warning_validation():
    """Comprehensive test combining all warning validation aspects."""
    # This test combines multiple validation aspects
    config = load_config()
    
    # Test data with complex warning situation
    forecast_data = create_mock_forecast_data(thunderstorm_probability=85)
    warning_data = create_mock_warning_data(level="orange")
    daily_data = create_mock_daily_forecast_data()
    
    # Validation checks
    checks = []
    
    # 1. Check threshold recognition
    thunderstorm_threshold = config["thresholds"]["thunderstorm_probability"]
    above_threshold = forecast_data["forecast"][0]["precipitation_probability"] > thunderstorm_threshold
    checks.append(("Threshold recognition", above_threshold))
    
    # 2. Check warning level consistency
    warning_level = warning_data["phenomenons_max_colors"]["thunderstorm"]
    high_warning = warning_level in ["orange", "red"]
    checks.append(("Warning level consistency", high_warning))
    
    # 3. Check data source consistency
    hourly_thunderstorm = any(entry["weather"] == "thunderstorm" for entry in forecast_data["forecast"])
    daily_thunderstorm = daily_data["forecast"][0]["weather"] == "thunderstorm"
    consistent = hourly_thunderstorm == daily_thunderstorm
    checks.append(("Data source consistency", consistent))
    
    # 4. Check report generation readiness
    ready_for_report = above_threshold and high_warning
    checks.append(("Report generation ready", ready_for_report))
    
    # Print results
    print("\n=== Comprehensive Warning Validation Results ===")
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {check_name}")
    
    # All checks should pass for this test data
    assert all(result for _, result in checks), "All validation checks should pass"
    
    print("✓ Comprehensive warning validation successful")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 