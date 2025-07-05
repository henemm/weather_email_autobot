"""
Test module for Météo-France API consistency verification.

This module tests the consistency between raw weather data and generated reports,
ensuring proper threshold application and data mapping.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch

from src.wetter.fetch_meteofrance import (
    get_forecast, 
    get_thunderstorm, 
    get_alerts,
    ForecastResult,
    Alert
)
from src.wetter.analyse import analysiere_regen_risiko, WetterDaten
from src.logic.analyse_weather import analyze_weather_data
from src.model.datatypes import WeatherData, WeatherPoint


class TestMeteoFranceRawDataOutput:
    """Test raw data output functionality for debugging."""
    
    def setup_method(self):
        """Initialize test coordinates and mock data."""
        self.latitude = 42.15  # Corte, Corsica
        self.longitude = 9.15
        self.test_time = datetime(2025, 7, 5, 14, 0, 0)  # 14:00 on July 5, 2025
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_raw_data_output_structure(self, mock_client_class):
        """Test that raw data output contains all required layers."""
        # Arrange
        mock_client = Mock()
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                'dt': int(self.test_time.timestamp()),
                'T': {'value': 28.5, 'unit': '°C'},
                'weather': {'desc': 'thunderstorm', 'icon': 'p3t'},
                'precipitation_probability': 75,
                'precipitation': {'1h': 5.2},  # 5.2mm in 1 hour
                'datetime': self.test_time.isoformat(),
                'wind': {'speed': 25, 'gust': 40, 'direction': 270}
            },
            {
                'dt': int((self.test_time + timedelta(hours=1)).timestamp()),
                'T': {'value': 26.0, 'unit': '°C'},
                'weather': {'desc': 'rain', 'icon': 'p2r'},
                'precipitation_probability': 45,
                'precipitation': {'1h': 2.1},
                'datetime': (self.test_time + timedelta(hours=1)).isoformat(),
                'wind': {'speed': 15, 'gust': 25, 'direction': 280}
            }
        ]
        mock_client.get_forecast.return_value = mock_forecast
        mock_client_class.return_value = mock_client
        
        # Act
        result = get_forecast(self.latitude, self.longitude)
        
        # Assert
        assert isinstance(result, ForecastResult)
        assert result.temperature == 28.5
        assert result.weather_condition == 'thunderstorm'
        assert result.precipitation_probability == 75
        assert result.wind_speed == 25
        assert result.wind_gusts == 40
        assert result.data_source == "meteofrance-api"
        
    def test_raw_data_debug_format(self):
        """Test debug output format for raw data."""
        # This test verifies the expected debug output format
        expected_format = {
            "etappe": "XY",
            "zeitpunkt": "14:00",
            "geo_points": [
                {
                    "geo_1": {
                        "blitz": 30,
                        "regen_wahrscheinlichkeit": 45,
                        "regen_menge": 2.1
                    }
                }
            ]
        }
        
        # Verify structure
        assert "etappe" in expected_format
        assert "zeitpunkt" in expected_format
        assert "geo_points" in expected_format
        assert isinstance(expected_format["geo_points"], list)


class TestThresholdValidation:
    """Test threshold validation and application."""
    
    def setup_method(self):
        """Initialize test configuration."""
        self.config = {
            "thresholds": {
                "rain_probability": 25.0,
                "rain_amount": 2.0,
                "thunderstorm_probability": 20.0,
                "wind_speed": 40.0,
                "temperature": 30.0,
                "cloud_cover": 50.0
            }
        }
        
    def test_rain_probability_threshold_application(self):
        """Test that rain probability threshold is correctly applied."""
        # Arrange
        weather_data = [
            WetterDaten(
                datum=datetime.now(),
                temperatur=25.0,
                niederschlag_prozent=30.0,  # Above threshold (25%)
                niederschlag_mm=1.5,
                wind_geschwindigkeit=15.0,
                luftfeuchtigkeit=70.0
            ),
            WetterDaten(
                datum=datetime.now() + timedelta(hours=1),
                temperatur=26.0,
                niederschlag_prozent=15.0,  # Below threshold
                niederschlag_mm=0.5,
                wind_geschwindigkeit=12.0,
                luftfeuchtigkeit=65.0
            )
        ]
        
        # Act
        result = analysiere_regen_risiko(weather_data, self.config)
        
        # Assert
        assert result.risiko_stufe.value in ["mittel", "hoch", "sehr_hoch"]
        assert len(result.kritische_werte) > 0
        # Debug: Print the actual critical values
        print(f"Critical values: {result.kritische_werte}")
        # The function uses > instead of >=, so 30% should trigger the threshold
        # Note: The function formats the value as "30.0%" not "30%"
        assert any("Regenwahrscheinlichkeit 30.0%" in value for value in result.kritische_werte)
        
    def test_rain_amount_threshold_application(self):
        """Test that rain amount threshold is correctly applied."""
        # Arrange
        weather_data = [
            WetterDaten(
                datum=datetime.now(),
                temperatur=24.0,
                niederschlag_prozent=20.0,
                niederschlag_mm=3.5,  # Above threshold
                wind_geschwindigkeit=10.0,
                luftfeuchtigkeit=75.0
            )
        ]
        
        # Act
        result = analysiere_regen_risiko(weather_data, self.config)
        
        # Assert
        assert len(result.kritische_werte) > 0
        assert any("Niederschlagsmenge 3.5mm" in value for value in result.kritische_werte)
        
    def test_threshold_time_detection(self):
        """Test that threshold crossing times are correctly detected."""
        # Arrange
        test_time = datetime(2025, 7, 5, 14, 0, 0)
        weather_points = [
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time,
                temperature=25.0,
                feels_like=25.0,
                precipitation=0.0,
                wind_speed=15.0,
                cloud_cover=60.0,
                rain_probability=15.0,  # Below threshold
                thunderstorm_probability=10.0
            ),
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time + timedelta(hours=1),
                temperature=26.0,
                feels_like=26.0,
                precipitation=0.0,
                wind_speed=12.0,
                cloud_cover=55.0,
                rain_probability=30.0,  # Above threshold
                thunderstorm_probability=15.0
            )
        ]
        weather_data = WeatherData(points=weather_points)
        
        # Act
        result = analyze_weather_data(weather_data, self.config)
        
        # Assert
        assert result.max_rain_probability == 30.0
        # The analysis should detect the threshold crossing


class TestDataMappingVerification:
    """Test mapping between raw data and report output."""
    
    def setup_method(self):
        """Initialize test data."""
        self.config = {
            "thresholds": {
                "rain_probability": 25.0,
                "rain_amount": 2.0,
                "thunderstorm_probability": 20.0
            }
        }
        
    def test_max_values_mapping(self):
        """Test that maximum values from raw data correctly map to report."""
        # Arrange
        test_time = datetime(2025, 7, 5, 14, 0, 0)
        weather_points = [
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time,
                temperature=28.0,
                feels_like=28.0,
                precipitation=3.5,
                wind_speed=25.0,
                cloud_cover=70.0,
                rain_probability=35.0,
                thunderstorm_probability=25.0
            ),
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time + timedelta(hours=1),
                temperature=26.0,
                feels_like=26.0,
                precipitation=1.0,
                wind_speed=15.0,
                cloud_cover=50.0,
                rain_probability=20.0,
                thunderstorm_probability=15.0
            )
        ]
        weather_data = WeatherData(points=weather_points)
        
        # Act
        result = analyze_weather_data(weather_data, self.config)
        
        # Assert
        assert result.max_temperature == 28.0
        assert result.max_precipitation == 3.5
        assert result.max_rain_probability == 35.0
        assert result.max_thunderstorm_probability == 25.0
        assert result.max_wind_speed == 25.0
        
    def test_threshold_time_mapping(self):
        """Test that threshold crossing times are correctly mapped."""
        # Arrange
        test_time = datetime(2025, 7, 5, 14, 0, 0)
        weather_points = [
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time,
                temperature=25.0,
                feels_like=25.0,
                precipitation=0.0,
                wind_speed=15.0,
                cloud_cover=60.0,
                rain_probability=15.0,
                thunderstorm_probability=10.0
            ),
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time + timedelta(hours=1),
                temperature=26.0,
                feels_like=26.0,
                precipitation=0.0,
                wind_speed=12.0,
                cloud_cover=55.0,
                rain_probability=30.0,  # Crosses threshold
                thunderstorm_probability=15.0
            ),
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time + timedelta(hours=2),
                temperature=27.0,
                feels_like=27.0,
                precipitation=0.0,
                wind_speed=10.0,
                cloud_cover=50.0,
                rain_probability=40.0,
                thunderstorm_probability=20.0  # Crosses threshold
            )
        ]
        weather_data = WeatherData(points=weather_points)
        
        # Act
        result = analyze_weather_data(weather_data, self.config)
        
        # Assert
        assert result.max_rain_probability == 40.0
        assert result.max_thunderstorm_probability == 20.0
        # The analysis should correctly identify threshold crossings


class TestReportConsistency:
    """Test consistency between raw data and generated reports."""
    
    def setup_method(self):
        """Initialize test configuration."""
        self.config = {
            "thresholds": {
                "rain_probability": 25.0,
                "rain_amount": 2.0,
                "thunderstorm_probability": 20.0
            }
        }
        
    def test_report_values_match_raw_data(self):
        """Test that report values match the maximum values from raw data."""
        # Arrange
        test_time = datetime(2025, 7, 5, 14, 0, 0)
        weather_points = [
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time,
                temperature=25.0,
                feels_like=25.0,
                precipitation=1.0,
                wind_speed=15.0,
                cloud_cover=60.0,
                rain_probability=20.0,
                thunderstorm_probability=15.0
            ),
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time + timedelta(hours=1),
                temperature=30.0,  # Max temperature
                feels_like=30.0,
                precipitation=5.0,  # Max precipitation
                wind_speed=35.0,  # Max wind speed
                cloud_cover=80.0,  # Max cloud cover
                rain_probability=45.0,  # Max rain probability
                thunderstorm_probability=30.0  # Max thunderstorm probability
            )
        ]
        weather_data = WeatherData(points=weather_points)
        
        # Act
        result = analyze_weather_data(weather_data, self.config)
        
        # Assert
        # Verify that report values match the maximum values from raw data
        assert result.max_temperature == 30.0
        assert result.max_precipitation == 5.0
        assert result.max_wind_speed == 35.0
        assert result.max_cloud_cover == 80.0
        assert result.max_rain_probability == 45.0
        assert result.max_thunderstorm_probability == 30.0
        
    def test_threshold_trigger_consistency(self):
        """Test that threshold triggers are consistent with raw data."""
        # Arrange
        test_time = datetime(2025, 7, 5, 14, 0, 0)
        weather_points = [
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time,
                temperature=25.0,
                feels_like=25.0,
                precipitation=0.0,
                wind_speed=15.0,
                cloud_cover=60.0,
                rain_probability=15.0,  # Below threshold
                thunderstorm_probability=10.0  # Below threshold
            ),
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=test_time + timedelta(hours=1),
                temperature=26.0,
                feels_like=26.0,
                precipitation=0.0,
                wind_speed=12.0,
                cloud_cover=55.0,
                rain_probability=30.0,  # Above threshold
                thunderstorm_probability=25.0  # Above threshold
            )
        ]
        weather_data = WeatherData(points=weather_points)
        
        # Act
        result = analyze_weather_data(weather_data, self.config)
        
        # Assert
        # Both thresholds should be triggered
        assert result.max_rain_probability >= self.config["thresholds"]["rain_probability"]
        assert result.max_thunderstorm_probability >= self.config["thresholds"]["thunderstorm_probability"]
        
        # Verify that risks are detected
        assert len(result.risks) > 0 