"""
Unit tests for forecast data conversion.

This module tests the conversion from ForecastResult to WeatherData
to ensure compatibility with the weather analysis system.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from wetter.fetch_meteofrance import ForecastResult
from model.datatypes import WeatherData, WeatherPoint


def test_forecast_result_to_weather_data_conversion():
    """Test conversion from ForecastResult to WeatherData."""
    # Create a mock ForecastResult
    forecast = ForecastResult(
        temperature=25.5,
        weather_condition="sunny",
        precipitation_probability=15,
        timestamp="2025-06-25T19:00:00",
        data_source="meteofrance-api"
    )
    
    lat, lon = 42.510501, 8.851262
    
    # Import the conversion function from the main script
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    
    from run_gr20_weather_monitor import forecast_result_to_weather_data
    
    # Convert
    weather_data = forecast_result_to_weather_data(forecast, lat, lon)
    
    # Assertions
    assert isinstance(weather_data, WeatherData)
    assert len(weather_data.points) == 1
    
    point = weather_data.points[0]
    assert isinstance(point, WeatherPoint)
    assert point.latitude == lat
    assert point.longitude == lon
    assert point.temperature == 25.5
    assert point.thunderstorm_probability == 15
    assert point.elevation == 0.0  # Default value
    assert point.wind_speed == 0.0  # Not available in ForecastResult
    assert point.wind_direction == 0.0  # Not available in ForecastResult
    assert point.cloud_cover == 0.0  # Not available in ForecastResult


def test_forecast_result_to_weather_data_with_missing_timestamp():
    """Test conversion when timestamp is missing."""
    forecast = ForecastResult(
        temperature=20.0,
        weather_condition="cloudy",
        precipitation_probability=30,
        timestamp="",  # Empty timestamp
        data_source="meteofrance-api"
    )
    
    lat, lon = 42.510501, 8.851262
    
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    
    from run_gr20_weather_monitor import forecast_result_to_weather_data
    
    # Convert
    weather_data = forecast_result_to_weather_data(forecast, lat, lon)
    
    # Should use current time when timestamp is empty
    point = weather_data.points[0]
    assert isinstance(point.time, datetime)
    assert point.temperature == 20.0
    assert point.thunderstorm_probability == 30


def test_forecast_result_to_weather_data_with_none_values():
    """Test conversion with None values in ForecastResult."""
    forecast = ForecastResult(
        temperature=18.5,
        weather_condition=None,
        precipitation_probability=None,
        timestamp="2025-06-25T19:00:00",
        data_source="meteofrance-api"
    )
    
    lat, lon = 42.510501, 8.851262
    
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    
    from run_gr20_weather_monitor import forecast_result_to_weather_data
    
    # Convert
    weather_data = forecast_result_to_weather_data(forecast, lat, lon)
    
    # Should handle None values gracefully
    point = weather_data.points[0]
    assert point.temperature == 18.5
    assert point.thunderstorm_probability is None 