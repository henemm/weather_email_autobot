"""
Unit tests for Open-Meteo weather data fetching module.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import requests
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_openmeteo import (
    fetch_openmeteo_forecast,
    _parse_openmeteo_response,
    get_weather_summary
)


class TestOpenMeteoFetch:
    """Test cases for Open-Meteo weather data fetching functionality"""

    def setup_method(self):
        """Setup test data"""
        self.latitude = 41.7481
        self.longitude = 9.2972
        
        # Sample Open-Meteo API response
        self.sample_api_response = {
            "latitude": 41.7481,
            "longitude": 9.2972,
            "generationtime_ms": 0.123,
            "utc_offset_seconds": 3600,
            "timezone": "Europe/Paris",
            "timezone_abbreviation": "CEST",
            "elevation": 150.0,
            "current_units": {
                "time": "iso8601",
                "temperature_2m": "°C",
                "relative_humidity_2m": "%",
                "apparent_temperature": "°C",
                "precipitation": "mm",
                "weather_code": "wmo code",
                "wind_speed_10m": "km/h",
                "wind_direction_10m": "°",
                "pressure_msl": "hPa",
                "cloud_cover": "%"
            },
            "current": {
                "time": "2025-01-15T12:00",
                "temperature_2m": 22.5,
                "relative_humidity_2m": 65,
                "apparent_temperature": 24.2,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 15.2,
                "wind_direction_10m": 180,
                "pressure_msl": 1013.2,
                "cloud_cover": 25
            },
            "hourly_units": {
                "time": "iso8601",
                "temperature_2m": "°C",
                "relative_humidity_2m": "%",
                "apparent_temperature": "°C",
                "precipitation_probability": "%",
                "precipitation": "mm",
                "weather_code": "wmo code",
                "wind_speed_10m": "km/h",
                "wind_direction_10m": "°",
                "pressure_msl": "hPa",
                "cloud_cover": "%"
            },
            "hourly": {
                "time": ["2025-01-15T12:00", "2025-01-15T13:00"],
                "temperature_2m": [22.5, 23.1],
                "relative_humidity_2m": [65, 62],
                "apparent_temperature": [24.2, 24.8],
                "precipitation_probability": [10, 15],
                "precipitation": [0.0, 0.2],
                "weather_code": [1, 2],
                "wind_speed_10m": [15.2, 16.8],
                "wind_direction_10m": [180, 185],
                "pressure_msl": [1013.2, 1012.8],
                "cloud_cover": [25, 30]
            }
        }

    def test_fetch_openmeteo_forecast_success(self):
        """Test successful Open-Meteo forecast fetching"""
        with patch('wetter.fetch_openmeteo.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_api_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = fetch_openmeteo_forecast(self.latitude, self.longitude)
            
            assert isinstance(result, dict)
            assert "location" in result
            assert "current" in result
            assert "hourly" in result
            assert "metadata" in result
            
            # Verify location data
            assert result["location"]["latitude"] == self.latitude
            assert result["location"]["longitude"] == self.longitude
            assert result["location"]["timezone"] == "Europe/Paris"
            
            # Verify current data
            current = result["current"]
            assert current["temperature_2m"] == 22.5
            assert current["wind_speed_10m"] == 15.2
            assert current["precipitation"] == 0.0
            
            # Verify API call parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "api.open-meteo.com" in call_args[0][0]
            assert call_args[1]["params"]["latitude"] == self.latitude
            assert call_args[1]["params"]["longitude"] == self.longitude

    def test_fetch_openmeteo_forecast_invalid_coordinates(self):
        """Test Open-Meteo forecast fetching with invalid coordinates"""
        # Test invalid latitude
        with pytest.raises(ValueError, match="Invalid latitude"):
            fetch_openmeteo_forecast(100.0, self.longitude)
        
        # Test invalid longitude
        with pytest.raises(ValueError, match="Invalid longitude"):
            fetch_openmeteo_forecast(self.latitude, 200.0)

    def test_fetch_openmeteo_forecast_http_error(self):
        """Test Open-Meteo forecast fetching with HTTP error"""
        with patch('wetter.fetch_openmeteo.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
            mock_get.return_value = mock_response
            
            with pytest.raises(RuntimeError, match="HTTP error 500"):
                fetch_openmeteo_forecast(self.latitude, self.longitude)

    def test_fetch_openmeteo_forecast_network_error(self):
        """Test Open-Meteo forecast fetching with network error"""
        with patch('wetter.fetch_openmeteo.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Network error")
            
            with pytest.raises(RuntimeError, match="Network error"):
                fetch_openmeteo_forecast(self.latitude, self.longitude)

    def test_parse_openmeteo_response_success(self):
        """Test successful parsing of Open-Meteo API response"""
        result = _parse_openmeteo_response(self.sample_api_response, self.latitude, self.longitude)
        
        assert isinstance(result, dict)
        assert "location" in result
        assert "current" in result
        assert "hourly" in result
        assert "metadata" in result
        
        # Verify location parsing
        location = result["location"]
        assert location["latitude"] == self.latitude
        assert location["longitude"] == self.longitude
        assert location["timezone"] == "Europe/Paris"
        assert location["timezone_abbreviation"] == "CEST"
        assert location["utc_offset_seconds"] == 3600
        
        # Verify current weather parsing
        current = result["current"]
        assert current["time"] == "2025-01-15T12:00"
        assert current["temperature_2m"] == 22.5
        assert current["relative_humidity_2m"] == 65
        assert current["apparent_temperature"] == 24.2
        assert current["precipitation"] == 0.0
        assert current["weather_code"] == 1
        assert current["wind_speed_10m"] == 15.2
        assert current["wind_direction_10m"] == 180
        assert current["pressure_msl"] == 1013.2
        assert current["cloud_cover"] == 25
        
        # Verify hourly forecast parsing
        hourly = result["hourly"]
        assert len(hourly["time"]) == 2
        assert len(hourly["temperature_2m"]) == 2
        assert hourly["time"][0] == "2025-01-15T12:00"
        assert hourly["temperature_2m"][0] == 22.5

    def test_parse_openmeteo_response_empty_data(self):
        """Test parsing of Open-Meteo response with empty data"""
        empty_response = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": "auto"
        }
        
        result = _parse_openmeteo_response(empty_response, self.latitude, self.longitude)
        
        assert isinstance(result, dict)
        assert result["location"]["latitude"] == self.latitude
        assert result["location"]["longitude"] == self.longitude
        assert result["current"] == {}
        assert result["hourly"] == {}

    def test_get_weather_summary_success(self):
        """Test successful weather summary generation"""
        # Create forecast data with current weather
        forecast_data = {
            "current": {
                "time": "2025-01-15T12:00",
                "temperature_2m": 22.5,
                "relative_humidity_2m": 65,
                "apparent_temperature": 24.2,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 15.2,
                "wind_direction_10m": 180,
                "pressure_msl": 1013.2,
                "cloud_cover": 25
            }
        }
        
        summary = get_weather_summary(forecast_data)
        
        assert isinstance(summary, dict)
        assert "temperature" in summary
        assert "wind" in summary
        assert "precipitation" in summary
        assert "conditions" in summary
        assert "timestamp" in summary
        
        # Verify temperature data
        temp = summary["temperature"]
        assert temp["current"] == 22.5
        assert temp["feels_like"] == 24.2
        assert temp["unit"] == "°C"
        
        # Verify wind data
        wind = summary["wind"]
        assert wind["speed"] == 15.2
        assert wind["direction"] == 180
        assert wind["speed_unit"] == "km/h"
        assert wind["direction_unit"] == "degrees"
        
        # Verify precipitation data
        precip = summary["precipitation"]
        assert precip["current"] == 0.0
        assert precip["unit"] == "mm"
        
        # Verify conditions data
        conditions = summary["conditions"]
        assert conditions["weather_code"] == 1
        assert conditions["cloud_cover"] == 25
        assert conditions["relative_humidity"] == 65
        assert conditions["pressure"] == 1013.2

    def test_get_weather_summary_no_current_data(self):
        """Test weather summary generation with no current data"""
        forecast_data = {}
        
        summary = get_weather_summary(forecast_data)
        
        assert summary == {"error": "No current weather data available"}

    def test_get_weather_summary_empty_current(self):
        """Test weather summary generation with empty current data"""
        forecast_data = {"current": {}}
        
        summary = get_weather_summary(forecast_data)
        
        assert summary == {"error": "No current weather data available"}

    def test_fetch_openmeteo_forecast_api_parameters(self):
        """Test that API parameters are correctly set"""
        with patch('wetter.fetch_openmeteo.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self.sample_api_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            fetch_openmeteo_forecast(self.latitude, self.longitude)
            
            # Verify API call parameters
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            
            assert params["latitude"] == self.latitude
            assert params["longitude"] == self.longitude
            assert "temperature_2m" in params["current"]
            assert "wind_speed_10m" in params["current"]
            assert "precipitation" in params["current"]
            assert params["timezone"] == "auto"
            assert params["forecast_days"] == 3 