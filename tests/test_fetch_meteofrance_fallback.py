"""
Tests for meteofrance-api fallback to open-meteo.

This module tests the fallback mechanism when meteofrance-api is not available
and the system automatically switches to open-meteo for basic weather data.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.wetter.fetch_meteofrance import (
    get_forecast_with_fallback,
    get_thunderstorm_with_fallback,
    get_alerts_with_fallback,
    ForecastResult,
    Alert
)


class TestMeteoFranceFallbackForecast:
    """Test forecast fallback functionality."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_forecast_meteofrance_success(self, mock_client_class):
        """Test successful forecast from meteofrance-api without fallback."""
        mock_client = Mock()
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                'T': {'value': 25, 'unit': '°C'},
                'weather': 'sunny',
                'precipitation_probability': 10,
                'datetime': '2025-06-24T20:00:00'
            }
        ]
        mock_client.get_forecast.return_value = mock_forecast
        mock_client_class.return_value = mock_client
        
        result = get_forecast_with_fallback(self.latitude, self.longitude)
        
        assert isinstance(result, ForecastResult)
        assert result.temperature == 25
        assert result.weather_condition == 'sunny'
        assert result.data_source == 'meteofrance-api'
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    @patch('src.wetter.fetch_meteofrance.fetch_openmeteo_forecast')
    def test_forecast_fallback_to_openmeteo(self, mock_openmeteo, mock_client_class):
        """Test fallback to open-meteo when meteofrance-api fails."""
        # MeteoFrance fails
        mock_client = Mock()
        mock_client.get_forecast.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        # OpenMeteo succeeds
        mock_openmeteo.return_value = {
            'current': {
                'temperature_2m': 22.5,
                'weather_code': 1,
                'precipitation': 0.0,
                'wind_speed_10m': 15.0,
                'time': '2025-06-24T20:00:00'
            },
            'metadata': {
                'data_source': 'Open-Meteo API'
            }
        }
        
        result = get_forecast_with_fallback(self.latitude, self.longitude)
        
        assert isinstance(result, ForecastResult)
        assert result.temperature == 22.5
        assert result.data_source == 'open-meteo'
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    @patch('src.wetter.fetch_meteofrance.fetch_openmeteo_forecast')
    def test_forecast_both_apis_fail(self, mock_openmeteo, mock_client_class):
        """Test behavior when both APIs fail."""
        # MeteoFrance fails
        mock_client = Mock()
        mock_client.get_forecast.side_effect = Exception("MeteoFrance API Error")
        mock_client_class.return_value = mock_client
        
        # OpenMeteo also fails
        mock_openmeteo.side_effect = Exception("OpenMeteo API Error")
        
        with pytest.raises(RuntimeError, match="Both meteofrance-api and open-meteo failed"):
            get_forecast_with_fallback(self.latitude, self.longitude)


class TestMeteoFranceFallbackThunderstorm:
    """Test thunderstorm detection fallback functionality."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_thunderstorm_meteofrance_success(self, mock_client_class):
        """Test successful thunderstorm detection from meteofrance-api."""
        mock_client = Mock()
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                'T': {'value': 28, 'unit': '°C'},
                'weather': 'thunderstorm',
                'precipitation_probability': 85,
                'datetime': '2025-06-24T20:00:00'
            }
        ]
        mock_client.get_forecast.return_value = mock_forecast
        mock_client_class.return_value = mock_client
        
        result = get_thunderstorm_with_fallback(self.latitude, self.longitude)
        
        assert "Thunderstorm detected" in result
        assert "meteofrance-api" in result
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    @patch('src.wetter.fetch_meteofrance.fetch_openmeteo_forecast')
    def test_thunderstorm_fallback_no_cape_data(self, mock_openmeteo, mock_client_class):
        """Test thunderstorm fallback when meteofrance fails - no CAPE data available."""
        # MeteoFrance fails
        mock_client = Mock()
        mock_client.get_forecast.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        # OpenMeteo succeeds but has no thunderstorm data
        mock_openmeteo.return_value = {
            'current': {
                'temperature_2m': 22.5,
                'weather_code': 1,
                'precipitation': 0.0,
                'wind_speed_10m': 15.0,
                'time': '2025-06-24T20:00:00'
            }
        }
        
        result = get_thunderstorm_with_fallback(self.latitude, self.longitude)
        
        assert "No thunderstorm data available" in result
        assert "open-meteo" in result


class TestMeteoFranceFallbackAlerts:
    """Test weather alerts fallback functionality."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        self.department = "65"
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_alerts_meteofrance_success(self, mock_client_class):
        """Test successful alerts from meteofrance-api."""
        mock_client = Mock()
        mock_warnings = Mock()
        mock_warnings.phenomenons_max_colors = {
            'Thunderstorms': 'orange'
        }
        mock_warnings.domain_id = self.department
        mock_client.get_warning_current_phenomenons.return_value = mock_warnings
        mock_client_class.return_value = mock_client
        
        result = get_alerts_with_fallback(self.latitude, self.longitude)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].phenomenon == 'Thunderstorms'
        assert result[0].level == 'orange'
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_alerts_meteofrance_fails_no_fallback(self, mock_client_class):
        """Test alerts when meteofrance fails - no fallback available."""
        mock_client = Mock()
        mock_client.get_warning_current_phenomenons.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        result = get_alerts_with_fallback(self.latitude, self.longitude)
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestFallbackDataSourceTracking:
    """Test that data source is properly tracked in fallback scenarios."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_meteofrance_data_source_tracking(self, mock_client_class):
        """Test data source tracking for meteofrance-api."""
        mock_client = Mock()
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                'T': {'value': 25, 'unit': '°C'},
                'weather': 'sunny',
                'precipitation_probability': 10,
                'datetime': '2025-06-24T20:00:00'
            }
        ]
        mock_client.get_forecast.return_value = mock_forecast
        mock_client_class.return_value = mock_client
        
        result = get_forecast_with_fallback(self.latitude, self.longitude)
        
        assert result.data_source == 'meteofrance-api'
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    @patch('src.wetter.fetch_meteofrance.fetch_openmeteo_forecast')
    def test_openmeteo_data_source_tracking(self, mock_openmeteo, mock_client_class):
        """Test data source tracking for open-meteo fallback."""
        # MeteoFrance fails
        mock_client = Mock()
        mock_client.get_forecast.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        # OpenMeteo succeeds
        mock_openmeteo.return_value = {
            'current': {
                'temperature_2m': 22.5,
                'weather_code': 1,
                'precipitation': 0.0,
                'wind_speed_10m': 15.0,
                'time': '2025-06-24T20:00:00'
            }
        }
        
        result = get_forecast_with_fallback(self.latitude, self.longitude)
        
        assert result.data_source == 'open-meteo'


class TestFallbackErrorHandling:
    """Test error handling in fallback scenarios."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        
    def test_invalid_coordinates_no_fallback(self):
        """Test that invalid coordinates are caught before any API calls."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            get_forecast_with_fallback(100, self.longitude)
            
        with pytest.raises(ValueError, match="Invalid longitude"):
            get_forecast_with_fallback(self.latitude, 200)
            
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    @patch('src.wetter.fetch_meteofrance.fetch_openmeteo_forecast')
    def test_graceful_degradation_forecast(self, mock_openmeteo, mock_client_class):
        """Test graceful degradation when only basic data is available."""
        # MeteoFrance fails
        mock_client = Mock()
        mock_client.get_forecast.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        # OpenMeteo provides minimal data
        mock_openmeteo.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'time': '2025-06-24T20:00:00'
            }
        }
        
        result = get_forecast_with_fallback(self.latitude, self.longitude)
        
        assert result.temperature == 20.0
        assert result.data_source == 'open-meteo'
        # Should handle missing fields gracefully
        assert result.weather_condition is None or result.weather_condition == 'unknown' 