"""
Tests for meteofrance-api integration module.

This module tests the new meteofrance-api based weather data fetching,
replacing the previous WCS/AROME/PIAF direct API calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.wetter.fetch_meteofrance import (
    get_forecast,
    get_thunderstorm,
    get_alerts,
    ForecastResult,
    Alert
)


class TestMeteoFranceForecast:
    """Test forecast functionality using meteofrance-api."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        self.department = "65"  # Tarbes department
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_forecast_success(self, mock_client_class):
        """Test successful forecast retrieval."""
        # Mock client and response
        mock_client = Mock()
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                'T': {'value': 25, 'unit': '°C'},
                'weather': 'sunny',
                'precipitation_probability': 10,
                'datetime': '2025-06-24T20:00:00'
            },
            {
                'T': {'value': 18, 'unit': '°C'},
                'weather': 'rain',
                'precipitation_probability': 60,
                'datetime': '2025-06-25T08:00:00'
            }
        ]
        mock_client.get_forecast.return_value = mock_forecast
        mock_client_class.return_value = mock_client
        
        result = get_forecast(self.latitude, self.longitude)
        
        assert isinstance(result, ForecastResult)
        assert result.temperature == 25
        assert result.weather_condition == 'sunny'
        assert result.precipitation_probability == 10
        assert result.timestamp == '2025-06-24T20:00:00'
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_forecast_api_error(self, mock_client_class):
        """Test forecast retrieval with API error."""
        mock_client = Mock()
        mock_client.get_forecast.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        with pytest.raises(RuntimeError, match="Failed to fetch forecast"):
            get_forecast(self.latitude, self.longitude)
            
    def test_get_forecast_invalid_coordinates(self):
        """Test forecast retrieval with invalid coordinates."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            get_forecast(100, self.longitude)
            
        with pytest.raises(ValueError, match="Invalid longitude"):
            get_forecast(self.latitude, 200)


class TestMeteoFranceThunderstorm:
    """Test thunderstorm detection functionality."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_thunderstorm_detected(self, mock_client_class):
        """Test thunderstorm detection when present."""
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
        
        result = get_thunderstorm(self.latitude, self.longitude)
        
        assert result == "Thunderstorm detected with 85% precipitation probability"
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_thunderstorm_not_detected(self, mock_client_class):
        """Test thunderstorm detection when not present."""
        mock_client = Mock()
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                'T': {'value': 22, 'unit': '°C'},
                'weather': 'sunny',
                'precipitation_probability': 10,
                'datetime': '2025-06-24T20:00:00'
            }
        ]
        mock_client.get_forecast.return_value = mock_forecast
        mock_client_class.return_value = mock_client
        
        result = get_thunderstorm(self.latitude, self.longitude)
        
        assert result == "No thunderstorm conditions detected"
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_thunderstorm_api_error(self, mock_client_class):
        """Test thunderstorm detection with API error."""
        mock_client = Mock()
        mock_client.get_forecast.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        with pytest.raises(RuntimeError, match="Failed to fetch thunderstorm data"):
            get_thunderstorm(self.latitude, self.longitude)


class TestMeteoFranceAlerts:
    """Test weather alerts functionality."""
    
    def setup_method(self):
        """Initialize test coordinates."""
        self.latitude = 43.2333
        self.longitude = 0.0833
        self.department = "65"
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_alerts_with_warnings(self, mock_client_class):
        """Test alert retrieval when warnings are present."""
        mock_client = Mock()
        mock_warnings = Mock()
        mock_warnings.phenomenons_max_colors = {
            'Thunderstorms': 'orange',
            'Rain-Flood': 'yellow'
        }
        mock_warnings.domain_id = self.department
        mock_client.get_warning_current_phenomenons.return_value = mock_warnings
        mock_client_class.return_value = mock_client
        
        result = get_alerts(self.latitude, self.longitude)
        
        assert isinstance(result, list)
        assert len(result) == 2
        
        thunderstorm_alert = next(alert for alert in result if alert.phenomenon == 'Thunderstorms')
        assert thunderstorm_alert.level == 'orange'
        
        rain_alert = next(alert for alert in result if alert.phenomenon == 'Rain-Flood')
        assert rain_alert.level == 'yellow'
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_alerts_no_warnings(self, mock_client_class):
        """Test alert retrieval when no warnings are present."""
        mock_client = Mock()
        mock_warnings = Mock()
        mock_warnings.phenomenons_max_colors = {}
        mock_warnings.domain_id = self.department
        mock_client.get_warning_current_phenomenons.return_value = mock_warnings
        mock_client_class.return_value = mock_client
        
        result = get_alerts(self.latitude, self.longitude)
        
        assert isinstance(result, list)
        assert len(result) == 0
        
    @patch('src.wetter.fetch_meteofrance.MeteoFranceClient')
    def test_get_alerts_api_error(self, mock_client_class):
        """Test alert retrieval with API error."""
        mock_client = Mock()
        mock_client.get_warning_current_phenomenons.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        with pytest.raises(RuntimeError, match="Failed to fetch alerts"):
            get_alerts(self.latitude, self.longitude)


class TestForecastResult:
    """Test ForecastResult dataclass."""
    
    def test_forecast_result_creation(self):
        """Test creating ForecastResult instance."""
        result = ForecastResult(
            temperature=25.5,
            weather_condition='sunny',
            precipitation_probability=10,
            timestamp='2025-06-24T20:00:00'
        )
        
        assert result.temperature == 25.5
        assert result.weather_condition == 'sunny'
        assert result.precipitation_probability == 10
        assert result.timestamp == '2025-06-24T20:00:00'


class TestAlert:
    """Test Alert dataclass."""
    
    def test_alert_creation(self):
        """Test creating Alert instance."""
        alert = Alert(
            phenomenon='Thunderstorms',
            level='orange',
            description='Risk of thunderstorms'
        )
        
        assert alert.phenomenon == 'Thunderstorms'
        assert alert.level == 'orange'
        assert alert.description == 'Risk of thunderstorms' 