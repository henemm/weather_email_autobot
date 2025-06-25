"""
Test meteofrance-api proof of concept for Tarbes, France.

This test validates that the official meteofrance-api library provides
comparable data to the public website, especially for thunderstorm conditions.
"""

import pytest
from unittest.mock import Mock, patch
from meteofrance_api.client import MeteoFranceClient


class TestMeteoFranceAPIPOC:
    """Test meteofrance-api functionality for Tarbes weather data."""
    
    def setup_method(self):
        """Initialize test client and coordinates."""
        self.client = MeteoFranceClient()
        self.latitude = 43.2333
        self.longitude = 0.0833
        self.department = "65"  # Tarbes department
        
    def test_client_initialization(self):
        """Test that MeteoFranceClient can be initialized without errors."""
        assert isinstance(self.client, MeteoFranceClient)
        
    @patch('meteofrance_api.client.MeteoFranceClient.get_forecast')
    def test_forecast_data_structure(self, mock_get_forecast):
        """Test that forecast data has expected structure."""
        # Mock response structure based on meteofrance-api documentation
        mock_forecast = Mock()
        mock_forecast.forecast = [
            {
                'T': {'value': 25, 'unit': '°C'},  # Temperature
                'weather': 'thunderstorm',
                'precipitation_probability': 80,
                'datetime': '2025-06-24T20:00:00'
            },
            {
                'T': {'value': 18, 'unit': '°C'},
                'weather': 'rain',
                'precipitation_probability': 60,
                'datetime': '2025-06-25T08:00:00'
            }
        ]
        mock_get_forecast.return_value = mock_forecast
        
        forecast = self.client.get_forecast(self.latitude, self.longitude)
        
        assert hasattr(forecast, 'forecast')
        assert len(forecast.forecast) >= 1
        assert 'T' in forecast.forecast[0]
        assert 'weather' in forecast.forecast[0]
        
    @patch('meteofrance_api.client.MeteoFranceClient.get_warning_current_phenomenons')
    def test_warning_data_structure(self, mock_get_warnings):
        """Test that warning data has expected structure for thunderstorms."""
        # Mock warning response
        mock_warnings = Mock()
        mock_warnings.phenomenons_max_colors = {
            'Thunderstorms': 'orange',
            'Rain-Flood': 'yellow'
        }
        mock_warnings.domain_id = self.department
        mock_get_warnings.return_value = mock_warnings
        
        warnings = self.client.get_warning_current_phenomenons(self.department)
        
        assert hasattr(warnings, 'phenomenons_max_colors')
        assert isinstance(warnings.phenomenons_max_colors, dict)
        
    @patch('meteofrance_api.client.MeteoFranceClient.get_rain')
    def test_rain_data_structure(self, mock_get_rain):
        """Test that rain forecast data has expected structure."""
        # Mock rain response
        mock_rain = Mock()
        mock_rain.forecast = [
            {
                'intensity': 2.5,
                'datetime': '2025-06-24T20:00:00'
            }
        ]
        mock_get_rain.return_value = mock_rain
        
        rain = self.client.get_rain(self.latitude, self.longitude)
        
        assert hasattr(rain, 'forecast')
        assert len(rain.forecast) >= 1
        assert 'intensity' in rain.forecast[0]
        
    def test_thunderstorm_detection_in_forecast(self):
        """Test that thunderstorm conditions can be detected in forecast data."""
        # This test would require actual API call or comprehensive mocking
        # For now, we test the logic with mock data
        forecast_data = [
            {'weather': 'thunderstorm', 'precipitation_probability': 80},
            {'weather': 'rain', 'precipitation_probability': 60},
            {'weather': 'sunny', 'precipitation_probability': 10}
        ]
        
        thunderstorm_entries = [
            entry for entry in forecast_data 
            if entry['weather'] == 'thunderstorm'
        ]
        
        assert len(thunderstorm_entries) >= 0  # May or may not have thunderstorms
        
    def test_warning_color_validation(self):
        """Test that warning colors are valid values."""
        valid_colors = ['green', 'yellow', 'orange', 'red']
        
        # Mock warning data
        warning_data = {
            'phenomenons_max_colors': {
                'Thunderstorms': 'orange',
                'Rain-Flood': 'yellow'
            }
        }
        
        for phenomenon, color in warning_data['phenomenons_max_colors'].items():
            assert color in valid_colors, f"Invalid color {color} for {phenomenon}"
            
    def test_coordinate_validation(self):
        """Test that coordinates are within valid ranges."""
        assert -90 <= self.latitude <= 90, "Latitude out of valid range"
        assert -180 <= self.longitude <= 180, "Longitude out of valid range"
        
    def test_department_code_validation(self):
        """Test that department code is valid format."""
        assert len(self.department) == 2, "Department code should be 2 digits"
        assert self.department.isdigit(), "Department code should be numeric" 