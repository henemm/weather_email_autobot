"""
Tests for alternative risk email integration module.

This module tests the integration of alternative risk analysis into the email generation pipeline.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.notification.alternative_risk_email_integration import AlternativeRiskEmailIntegration


class TestAlternativeRiskEmailIntegration:
    """Test cases for AlternativeRiskEmailIntegration."""

    def test_generate_alternative_risk_report(self):
        """Test generation of alternative risk report for email integration."""
        # Arrange
        base_time = datetime(2025, 7, 28, 14, 0, 0)
        weather_data_by_point = {
            'point1': {
                'forecast': [
                    {
                        'dt': int(base_time.timestamp()),
                        'T': {'value': 32.5},
                        'rain': {'1h': 2.5},
                        'precipitation_probability': 60,
                        'weather': {'desc': 'Orages'},
                        'wind': {'speed': 35, 'gust': 45}
                    }
                ],
                'stage_name': 'Vizzavona',
                'stage_date': '2025-07-28'
            }
        }
        integration = AlternativeRiskEmailIntegration()

        # Act
        result = integration.generate_alternative_risk_report(
            weather_data_by_point, 'Vizzavona', '2025-07-28'
        )

        # Assert
        assert result is not None
        assert "Alternative Risk Analysis" in result
        assert "32.5°C" in result
        assert "Thunderstorm: Moderate @14" in result
        assert "Wind gusts detected" in result

    def test_integrate_into_email_content(self):
        """Test integration of alternative risk report into email content."""
        # Arrange
        existing_content = "Standard weather report content"
        alternative_report = "---\n\n## 🔍 Alternative Risk Analysis\n\n🔥 **Heat**: Maximum temperature: 32.5°C"
        integration = AlternativeRiskEmailIntegration()

        # Act
        result = integration.integrate_into_email_content(existing_content, alternative_report)

        # Assert
        assert "Standard weather report content" in result
        assert "Alternative Risk Analysis" in result
        assert "32.5°C" in result

    def test_get_night_temperature_info(self):
        """Test getting night temperature information."""
        # Arrange
        base_time = datetime(2025, 7, 28, 22, 0, 0)
        weather_data_by_point = {
            'point1': {
                'forecast': [
                    {
                        'dt': int(base_time.timestamp()),
                        'T': {'value': 15.0}
                    },
                    {
                        'dt': int((base_time.replace(hour=3)).timestamp()),
                        'T': {'value': 8.0}
                    }
                ]
            }
        }
        integration = AlternativeRiskEmailIntegration()

        # Act
        result = integration.get_night_temperature_info(weather_data_by_point)

        # Assert
        assert result is not None
        assert "Night temperature: 8.0°C" in result

    def test_validate_weather_data_with_valid_data(self):
        """Test validation of valid weather data."""
        # Arrange
        weather_data_by_point = {
            'point1': {
                'forecast': [
                    {
                        'dt': int(datetime(2025, 7, 28, 14, 0, 0).timestamp()),
                        'T': {'value': 25.0}
                    }
                ]
            }
        }
        integration = AlternativeRiskEmailIntegration()

        # Act
        result = integration.validate_weather_data(weather_data_by_point)

        # Assert
        assert result is True

    def test_validate_weather_data_with_empty_data(self):
        """Test validation of empty weather data."""
        # Arrange
        weather_data_by_point = {}
        integration = AlternativeRiskEmailIntegration()

        # Act
        result = integration.validate_weather_data(weather_data_by_point)

        # Assert
        assert result is False

    def test_validate_weather_data_with_invalid_data(self):
        """Test validation of invalid weather data."""
        # Arrange
        weather_data_by_point = {
            'point1': {'invalid': 'data'},
            'point2': None
        }
        integration = AlternativeRiskEmailIntegration()

        # Act
        result = integration.validate_weather_data(weather_data_by_point)

        # Assert
        assert result is False

    def test_generate_alternative_risk_report_with_multiple_points(self):
        """Test generation of alternative risk report with multiple GEO-points."""
        # Arrange
        base_time = datetime(2025, 7, 28, 14, 0, 0)
        weather_data_by_point = {
            'point1': {
                'forecast': [
                    {
                        'dt': int(base_time.timestamp()),
                        'T': {'value': 25.0},
                        'rain': {'1h': 1.0},
                        'weather': {'desc': 'Ciel clair'},
                        'wind': {'speed': 10, 'gust': 15}
                    }
                ],
                'stage_name': 'Vizzavona',
                'stage_date': '2025-07-28'
            },
            'point2': {
                'forecast': [
                    {
                        'dt': int((base_time.replace(hour=15)).timestamp()),
                        'T': {'value': 28.0},
                        'rain': {'1h': 2.0},
                        'weather': {'desc': 'Orages'},
                        'wind': {'speed': 20, 'gust': 25}
                    }
                ],
                'stage_name': 'Vizzavona',
                'stage_date': '2025-07-28'
            }
        }
        integration = AlternativeRiskEmailIntegration()

        # Act
        result = integration.generate_alternative_risk_report(
            weather_data_by_point, 'Vizzavona', '2025-07-28'
        )

        # Assert
        assert result is not None
        assert "Alternative Risk Analysis" in result
        assert "28.0°C" in result  # Maximum temperature from both points
        assert "Thunderstorm: Moderate @15" in result 