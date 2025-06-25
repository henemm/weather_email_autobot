"""
Unit tests for weather model comparison module.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch
from datetime import datetime
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.compare_models import (
    compare_meteofrance_openmeteo_conca,
    compare_arome_openmeteo_conca,  # Backward compatibility
    _fetch_meteofrance_data,
    _fetch_openmeteo_data,
    save_comparison_to_file,
    get_comparison_summary,
    CONCA_LATITUDE,
    CONCA_LONGITUDE
)


class TestCompareModels:
    """Test cases for weather model comparison functionality"""

    def setup_method(self):
        """Setup test data"""
        self.sample_meteofrance_data = {
            "forecast": {
                "temperature": 22.5,
                "weather_condition": "sunny",
                "precipitation_probability": 10,
                "timestamp": "2025-01-15T12:00:00",
                "data_source": "meteofrance-api"
            },
            "thunderstorm": {
                "status": "No thunderstorm conditions detected",
                "data_source": "meteofrance-api"
            },
            "alerts": {
                "count": 0,
                "alerts": []
            },
            "metadata": {
                "data_source": "Météo-France API",
                "timestamp": "2025-01-15T12:00:00Z"
            }
        }
        # The Open-Meteo mock must have a 'hourly' key for the real function
        self.sample_openmeteo_data = {
            "current": {
                "temperature": {
                    "current": 22.5,
                    "feels_like": 24.2,
                    "unit": "°C"
                },
                "wind": {
                    "speed": 15.2,
                    "direction": 180,
                    "speed_unit": "km/h",
                    "direction_unit": "degrees"
                },
                "precipitation": {
                    "current": 0.0,
                    "unit": "mm"
                },
                "conditions": {
                    "weather_code": 1,
                    "cloud_cover": 25,
                    "relative_humidity": 65,
                    "pressure": 1013.2
                },
                "timestamp": "2025-01-15T12:00"
            },
            "hourly": {
                "time": ["2025-01-15T12:00", "2025-01-15T13:00"],
                "temperature_2m": [22.5, 23.1]
            },
            "metadata": {
                "data_source": "Open-Meteo API",
                "timestamp": "2025-01-15T12:00:00Z"
            }
        }

    @patch('wetter.compare_models._fetch_meteofrance_data')
    @patch('wetter.compare_models._fetch_openmeteo_data')
    def test_compare_meteofrance_openmeteo_conca_success(self, mock_fetch_openmeteo, mock_fetch_meteofrance):
        """Test successful weather model comparison"""
        # Arrange
        mock_fetch_meteofrance.return_value = self.sample_meteofrance_data
        mock_fetch_openmeteo.return_value = self.sample_openmeteo_data
        
        # Act
        result = compare_meteofrance_openmeteo_conca()
        
        # Assert
        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "location" in result
        assert "meteofrance" in result
        assert "open_meteo" in result
        assert "errors" in result
        
        # Verify location
        location = result["location"]
        assert location["name"] == "Conca, Corsica"
        assert location["latitude"] == CONCA_LATITUDE
        assert location["longitude"] == CONCA_LONGITUDE
        
        # Verify Météo-France data
        assert result["meteofrance"] == self.sample_meteofrance_data
        
        # Verify Open-Meteo data
        assert result["open_meteo"] == self.sample_openmeteo_data
        
        # Verify no errors
        assert result["errors"] == []

    @patch('wetter.compare_models._fetch_meteofrance_data')
    @patch('wetter.compare_models._fetch_openmeteo_data')
    def test_compare_meteofrance_openmeteo_conca_meteofrance_error(self, mock_fetch_openmeteo, mock_fetch_meteofrance):
        """Test comparison when Météo-France data fetch fails"""
        # Arrange
        mock_fetch_meteofrance.side_effect = RuntimeError("Météo-France API error")
        mock_fetch_openmeteo.return_value = self.sample_openmeteo_data
        
        # Act
        result = compare_meteofrance_openmeteo_conca()
        
        # Assert
        assert "errors" in result
        assert len(result["errors"]) == 1
        assert "Météo-France data fetch failed" in result["errors"][0]
        assert result["meteofrance"]["error"] == "Météo-France data fetch failed: Météo-France API error"
        assert result["open_meteo"] == self.sample_openmeteo_data

    @patch('wetter.compare_models._fetch_meteofrance_data')
    @patch('wetter.compare_models._fetch_openmeteo_data')
    def test_compare_meteofrance_openmeteo_conca_openmeteo_error(self, mock_fetch_openmeteo, mock_fetch_meteofrance):
        """Test comparison when Open-Meteo data fetch fails"""
        # Arrange
        mock_fetch_meteofrance.return_value = self.sample_meteofrance_data
        mock_fetch_openmeteo.side_effect = RuntimeError("Open-Meteo API error")
        
        # Act
        result = compare_meteofrance_openmeteo_conca()
        
        # Assert
        assert "errors" in result
        assert len(result["errors"]) == 1
        assert "Open-Meteo data fetch failed" in result["errors"][0]
        assert result["meteofrance"] == self.sample_meteofrance_data
        assert result["open_meteo"]["error"] == "Open-Meteo data fetch failed: Open-Meteo API error"

    @patch('wetter.compare_models.get_forecast_with_fallback')
    @patch('wetter.compare_models.get_thunderstorm_with_fallback')
    @patch('wetter.compare_models.get_alerts_with_fallback')
    def test_fetch_meteofrance_data_success(self, mock_get_alerts, mock_get_thunderstorm, mock_get_forecast):
        """Test successful Météo-France data fetching"""
        # Arrange
        mock_forecast = Mock()
        mock_forecast.temperature = 22.5
        mock_forecast.weather_condition = "sunny"
        mock_forecast.precipitation_probability = 10
        mock_forecast.timestamp = "2025-01-15T12:00:00"
        mock_forecast.data_source = "meteofrance-api"
        mock_get_forecast.return_value = mock_forecast
        
        mock_get_thunderstorm.return_value = "No thunderstorm conditions detected (meteofrance-api)"
        
        mock_alerts = []
        mock_get_alerts.return_value = mock_alerts
        
        # Act
        result = _fetch_meteofrance_data()
        
        # Assert
        assert isinstance(result, dict)
        assert "forecast" in result
        assert "thunderstorm" in result
        assert "alerts" in result
        assert "metadata" in result
        
        # Verify metadata
        assert result["metadata"]["data_source"] == "Météo-France API"
        
        # Verify forecast data
        forecast = result["forecast"]
        assert forecast["temperature"] == 22.5
        assert forecast["weather_condition"] == "sunny"
        assert forecast["precipitation_probability"] == 10
        assert forecast["data_source"] == "meteofrance-api"
        
        # Verify thunderstorm data
        thunderstorm = result["thunderstorm"]
        assert "No thunderstorm conditions detected" in thunderstorm["status"]
        assert thunderstorm["data_source"] == "meteofrance-api"
        
        # Verify alerts data
        alerts = result["alerts"]
        assert alerts["count"] == 0
        assert alerts["alerts"] == []

    @patch('wetter.compare_models.get_forecast_with_fallback')
    def test_fetch_meteofrance_data_forecast_error(self, mock_get_forecast):
        """Test Météo-France data fetching with forecast error"""
        # Arrange
        mock_get_forecast.side_effect = RuntimeError("Forecast API error")
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to fetch Météo-France data"):
            _fetch_meteofrance_data()

    @patch('wetter.compare_models.fetch_openmeteo_forecast')
    @patch('wetter.compare_models.get_weather_summary')
    def test_fetch_openmeteo_data_success(self, mock_get_summary, mock_fetch_forecast):
        """Test successful Open-Meteo data fetching"""
        # Arrange
        mock_fetch_forecast.return_value = self.sample_openmeteo_data
        mock_get_summary.return_value = self.sample_openmeteo_data["current"]
        
        # Act
        result = _fetch_openmeteo_data()
        
        # Assert
        assert isinstance(result, dict)
        assert "current" in result
        assert "forecast" in result
        assert "metadata" in result
        
        # Verify metadata
        assert result["metadata"]["data_source"] == "Open-Meteo API"
        
        # Verify current data
        assert result["current"] == self.sample_openmeteo_data["current"]
        
        # Verify forecast data
        assert result["forecast"] == self.sample_openmeteo_data["hourly"]

    @patch('wetter.compare_models.fetch_openmeteo_forecast')
    def test_fetch_openmeteo_data_error(self, mock_fetch_forecast):
        """Test Open-Meteo data fetching with error"""
        # Arrange
        mock_fetch_forecast.side_effect = RuntimeError("Open-Meteo API error")
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Open-Meteo API error"):
            _fetch_openmeteo_data()

    def test_save_comparison_to_file_success(self, tmp_path):
        """Test successful comparison data saving"""
        # Arrange
        comparison_data = {
            "timestamp": "2025-01-15T12:00:00Z",
            "location": {"name": "Test Location"},
            "meteofrance": self.sample_meteofrance_data,
            "open_meteo": self.sample_openmeteo_data,
            "errors": []
        }
        
        # Change to tmp_path for testing
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Act
            filepath = save_comparison_to_file(comparison_data)
            
            # Assert
            assert os.path.exists(filepath)
            assert filepath.endswith('.json')
            
            # Verify file content
            with open(filepath, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data["timestamp"] == comparison_data["timestamp"]
            assert saved_data["location"]["name"] == comparison_data["location"]["name"]
            
        finally:
            os.chdir(original_cwd)

    def test_save_comparison_to_file_custom_filename(self, tmp_path):
        """Test comparison data saving with custom filename"""
        # Arrange
        comparison_data = {
            "timestamp": "2025-01-15T12:00:00Z",
            "location": {"name": "Test Location"},
            "meteofrance": self.sample_meteofrance_data,
            "open_meteo": self.sample_openmeteo_data,
            "errors": []
        }
        
        custom_filename = "custom_comparison.json"
        
        # Change to tmp_path for testing
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Act
            filepath = save_comparison_to_file(comparison_data, custom_filename)
            
            # Assert
            assert filepath.endswith(custom_filename)
            assert os.path.exists(filepath)
            
        finally:
            os.chdir(original_cwd)

    def test_save_comparison_to_file_creates_directory(self, tmp_path):
        """Test that save_comparison_to_file creates data directory if it doesn't exist"""
        # Arrange
        comparison_data = {
            "timestamp": "2025-01-15T12:00:00Z",
            "location": {"name": "Test Location"},
            "meteofrance": self.sample_meteofrance_data,
            "open_meteo": self.sample_openmeteo_data,
            "errors": []
        }
        
        # Change to tmp_path for testing
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Act
            filepath = save_comparison_to_file(comparison_data)
            
            # Assert
            data_dir = os.path.dirname(filepath)
            assert os.path.exists(data_dir)
            assert os.path.isdir(data_dir)
            
        finally:
            os.chdir(original_cwd)

    def test_get_comparison_summary_success(self):
        """Test successful comparison summary generation"""
        # Arrange
        comparison_data = {
            "timestamp": "2025-01-15T12:00:00Z",
            "location": {"name": "Conca, Corsica"},
            "meteofrance": self.sample_meteofrance_data,
            "open_meteo": self.sample_openmeteo_data,
            "errors": []
        }
        
        # Act
        summary = get_comparison_summary(comparison_data)
        
        # Assert
        assert isinstance(summary, dict)
        assert summary["timestamp"] == comparison_data["timestamp"]
        assert summary["location"]["name"] == comparison_data["location"]["name"]
        
        # Verify data sources
        assert summary["data_sources"]["meteofrance"] == "available"
        assert summary["data_sources"]["open_meteo"] == "available"
        
        # Verify Météo-France summary
        meteofrance_summary = summary["summary"]["meteofrance"]
        assert meteofrance_summary["temperature"] == 22.5
        assert meteofrance_summary["weather_condition"] == "sunny"
        assert meteofrance_summary["data_available"] is True
        
        # Verify Open-Meteo summary
        openmeteo_summary = summary["summary"]["open_meteo"]
        assert openmeteo_summary["temperature"] == 22.5
        assert openmeteo_summary["data_available"] is True

    def test_get_comparison_summary_with_errors(self):
        """Test comparison summary generation with errors"""
        # Arrange
        comparison_data = {
            "timestamp": "2025-01-15T12:00:00Z",
            "location": {"name": "Conca, Corsica"},
            "meteofrance": {"error": "API error"},
            "open_meteo": {"error": "Network error"},
            "errors": ["Météo-France data fetch failed", "Open-Meteo data fetch failed"]
        }
        
        # Act
        summary = get_comparison_summary(comparison_data)
        
        # Assert
        assert summary["data_sources"]["meteofrance"] == "error"
        assert summary["data_sources"]["open_meteo"] == "error"
        assert len(summary["errors"]) == 2
        assert summary["summary"]["meteofrance"]["error"] == "API error"
        assert summary["summary"]["open_meteo"]["error"] == "Network error"

    def test_get_comparison_summary_partial_failure(self):
        """Test comparison summary generation with partial failure"""
        # Arrange
        comparison_data = {
            "timestamp": "2025-01-15T12:00:00Z",
            "location": {"name": "Conca, Corsica"},
            "meteofrance": self.sample_meteofrance_data,
            "open_meteo": {"error": "Network error"},
            "errors": ["Open-Meteo data fetch failed"]
        }
        
        # Act
        summary = get_comparison_summary(comparison_data)
        
        # Assert
        assert summary["data_sources"]["meteofrance"] == "available"
        assert summary["data_sources"]["open_meteo"] == "error"
        assert len(summary["errors"]) == 1
        assert summary["summary"]["meteofrance"]["data_available"] is True
        assert summary["summary"]["open_meteo"]["error"] == "Network error"

    def test_backward_compatibility_compare_arome_openmeteo_conca(self):
        """Test backward compatibility function"""
        # Arrange
        with patch('wetter.compare_models.compare_meteofrance_openmeteo_conca') as mock_compare:
            mock_compare.return_value = {"test": "data"}
            
            # Act
            result = compare_arome_openmeteo_conca()
            
            # Assert
            assert result == {"test": "data"}
            mock_compare.assert_called_once() 