#!/usr/bin/env python3
"""
Test for debug email append functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from notification.email_client import generate_debug_email_append, _generate_tabular_debug_data


def test_generate_debug_email_append_disabled():
    """Test that debug append returns empty string when debug is disabled."""
    config = {
        "debug": {
            "enabled": False
        }
    }
    
    report_data = {
        "report_type": "morning",
        "weather_data": {}
    }
    
    result = generate_debug_email_append(report_data, config)
    assert result == ""


def test_generate_debug_email_append_enabled():
    """Test that debug append generates output when debug is enabled."""
    config = {
        "debug": {
            "enabled": True
        }
    }
    
    report_data = {
        "report_type": "morning",
        "weather_data": {}
    }
    
    # Mock the dependencies
    with patch('wetter.weather_data_processor.WeatherDataProcessor') as mock_processor, \
         patch('position.etappenlogik.get_current_stage') as mock_get_stage:
        
        # Mock current stage
        mock_get_stage.return_value = {
            "name": "Test Stage",
            "punkte": [
                {"lat": 41.93508, "lon": 9.20595},
                {"lat": 41.94000, "lon": 9.21000}
            ]
        }
        
        # Mock weather data processor
        mock_processor_instance = Mock()
        mock_processor_instance._calculate_weather_data_for_day.return_value = {
            "raw_temperatures": [14.2, 14.0, 15.1, 16.2, 17.3, 18.4, 19.5, 20.6, 21.7, 22.8, 23.9, 24.0, 23.1, 22.2, 21.3, 20.4, 19.5, 18.6, 17.7],
            "raw_rain_probabilities": [5.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0],
            "raw_precipitations": [0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
            "max_wind_speed": 15.0,
            "max_wind_gusts": 25.0,
            "max_thunderstorm_probability": 30.0
        }
        mock_processor.return_value = mock_processor_instance
        
        result = generate_debug_email_append(report_data, config)
        
        # Check that debug output is generated
        assert "--- DEBUG INFO ---" in result
        assert "Test Stage Point 1" in result
        assert "Test Stage Point 2" in result
        assert "heute, Tag" in result


def test_generate_tabular_debug_data():
    """Test tabular debug data generation."""
    weather_data = {
        "raw_temperatures": [14.2, 14.0, 15.1, 16.2, 17.3, 18.4, 19.5, 20.6, 21.7, 22.8, 23.9, 24.0, 23.1, 22.2, 21.3, 20.4, 19.5, 18.6, 17.7],
        "raw_rain_probabilities": [5.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0],
        "raw_precipitations": [0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
        "max_wind_speed": 15.0,
        "max_wind_gusts": 25.0,
        "max_thunderstorm_probability": 30.0
    }
    
    result = _generate_tabular_debug_data(weather_data)
    
    # Check that table structure is correct
    assert "| Hour  |  Temp  | RainW% | Rainmm |  Wind  | Gusts  | Thund% |" in result
    assert "|  04   |" in result
    assert "|  22   |" in result
    assert "|  Min  |" in result
    assert "|  Max  |" in result
    
    # Check that data is formatted correctly (note: actual format uses 6 spaces, not 7)
    assert "|   14.2 |" in result  # Temperature
    assert "|    5.0 |" in result  # Rain probability
    assert "|    0.0 |" in result  # Precipitation
    assert "|   15.0 |" in result  # Wind speed
    assert "|   25.0 |" in result  # Wind gusts
    assert "|   30.0 |" in result  # Thunderstorm


def test_generate_tabular_debug_data_empty():
    """Test tabular debug data generation with empty data."""
    weather_data = {
        "raw_temperatures": [],
        "raw_rain_probabilities": [],
        "raw_precipitations": [],
        "max_wind_speed": 0.0,
        "max_wind_gusts": 0.0,
        "max_thunderstorm_probability": 0.0
    }
    
    result = _generate_tabular_debug_data(weather_data)
    
    # Check that table structure is still correct
    assert "| Hour  |  Temp  | RainW% | Rainmm |  Wind  | Gusts  | Thund% |" in result
    assert "|  04   |" in result
    assert "|  22   |" in result
    assert "|  Min  |" in result
    assert "|  Max  |" in result
    
    # Check that empty data shows dashes (note: actual format uses 6 spaces)
    assert "|      - |" in result


def test_generate_tabular_debug_data_partial():
    """Test tabular debug data generation with partial data."""
    weather_data = {
        "raw_temperatures": [14.2, 14.0, 15.1],  # Only 3 values
        "raw_rain_probabilities": [5.0, 5.0, 10.0],  # Only 3 values
        "raw_precipitations": [0.0, 0.0, 0.1],  # Only 3 values
        "max_wind_speed": 15.0,
        "max_wind_gusts": 25.0,
        "max_thunderstorm_probability": 30.0
    }
    
    result = _generate_tabular_debug_data(weather_data)
    
    # Check that available data is shown
    assert "|   14.2 |" in result
    assert "|   14.0 |" in result
    assert "|   15.1 |" in result
    
    # Check that missing data shows dashes
    assert "|      - |" in result


if __name__ == "__main__":
    pytest.main([__file__]) 