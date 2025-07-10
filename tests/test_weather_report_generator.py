"""
Tests for weather report generator.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.report.weather_report_generator import (
    generate_weather_report,
    _format_temperature_data_separate,
    _format_evening_report
)


def test_format_temperature_data_separate_evening_report():
    """Test that evening reports correctly format night and day temperatures separately."""
    # Test data with plausible night and day temperatures
    weather_data = {
        'min_temperature': 15.5,  # Night temperature
        'max_temperature': 33.5   # Day temperature
    }
    
    night_temp, day_temp = _format_temperature_data_separate(weather_data, 'evening')
    
    assert night_temp == "Nacht15.5"
    assert day_temp == "Hitze33.5"


def test_format_temperature_data_separate_morning_report():
    """Test that morning reports only show day temperature."""
    weather_data = {
        'min_temperature': 15.5,
        'max_temperature': 33.5
    }
    
    night_temp, day_temp = _format_temperature_data_separate(weather_data, 'morning')
    
    assert night_temp == ""
    assert day_temp == "Hitze33.5"


def test_format_evening_report_with_temperatures():
    """Test that evening reports include both night and day temperatures."""
    stage_name = "Corte→Vizzavona"
    night_temp = "Nacht15.5"
    day_temp = "Hitze33.5"
    thunderstorm_text = "Gew.40%@14(95%@17)"
    rain_text = "Regen50%@14(70%@17)"
    precipitation_text = "Regen2.0mm@14"
    wind_text = "Wind18 - Böen38"
    thunderstorm_next_text = "Gew+1 90%@15"
    
    report = _format_evening_report(
        stage_name, night_temp, day_temp, thunderstorm_text, rain_text,
        precipitation_text, wind_text, thunderstorm_next_text
    )
    
    # Check that both temperatures are present
    assert "Nacht15.5" in report
    assert "Hitze33.5" in report
    
    # Check the order according to specification
    parts = report.split(" - ")
    assert parts[0] == "Corte→Vizzavona"  # Stage name
    assert parts[1] == "Nacht15.5"      # Night temperature
    assert parts[5] == "Hitze33.5"      # Day temperature


def test_evening_report_temperature_plausibility():
    """Test that evening reports show plausible temperature differences."""
    with patch('src.report.weather_report_generator.load_config') as mock_config, \
         patch('src.report.weather_report_generator.process_weather_data_for_report') as mock_process:
        
        # Mock configuration
        mock_config.return_value = {
            'thresholds': {
                'thunderstorm_probability': 20.0,
                'rain_probability': 25.0,
                'rain_amount': 2.0,
                'wind_speed': 20.0,
                'temperature': 32.0
            }
        }
        
        # Mock weather data with plausible values
        mock_process.return_value = {
            'max_temperature': 33.5,      # Day temperature
            'min_temperature': 15.5,      # Night temperature (18°C difference)
            'max_precipitation': 2.0,
            'max_rain_probability': 70.0,
            'max_thunderstorm_probability': 95.0,
            'max_wind_speed': 38.0,
            'wind_speed': 18.0,
            'thunderstorm_threshold_pct': 40,
            'thunderstorm_threshold_time': '14',
            'thunderstorm_max_time': '17',
            'rain_threshold_pct': 50,
            'rain_threshold_time': '14',
            'rain_max_time': '17',
            'rain_total_time': '14',
            'thunderstorm_next_day': 90,
            'thunderstorm_next_day_threshold_time': '15',
            'fire_risk_warning': ''
        }
        
        # Generate evening report
        result = generate_weather_report('evening')
        
        assert result['success'] is True
        report_text = result['report_text']
        
        # Verify both temperatures are present and plausible
        assert "Nacht15.5" in report_text
        assert "Hitze33.5" in report_text
        
        # Verify temperature difference is reasonable (night should be lower than day)
        night_temp = 15.5
        day_temp = 33.5
        temp_diff = day_temp - night_temp
        assert temp_diff > 5.0, f"Temperature difference too small: {temp_diff}°C"
        assert temp_diff < 25.0, f"Temperature difference too large: {temp_diff}°C"


def test_evening_report_missing_min_temperature():
    """Test evening report when min_temperature is not available."""
    with patch('src.report.weather_report_generator.load_config') as mock_config, \
         patch('src.report.weather_report_generator.process_weather_data_for_report') as mock_process:
        
        mock_config.return_value = {
            'thresholds': {
                'thunderstorm_probability': 20.0,
                'rain_probability': 25.0,
                'rain_amount': 2.0,
                'wind_speed': 20.0,
                'temperature': 32.0
            }
        }
        
        # Mock weather data without min_temperature
        mock_process.return_value = {
            'max_temperature': 33.5,
            'min_temperature': 0.0,  # No night temperature available
            'max_precipitation': 2.0,
            'max_rain_probability': 70.0,
            'max_thunderstorm_probability': 95.0,
            'max_wind_speed': 38.0,
            'wind_speed': 18.0,
            'thunderstorm_threshold_pct': 40,
            'thunderstorm_threshold_time': '14',
            'thunderstorm_max_time': '17',
            'rain_threshold_pct': 50,
            'rain_threshold_time': '14',
            'rain_max_time': '17',
            'rain_total_time': '14',
            'thunderstorm_next_day': 90,
            'thunderstorm_next_day_threshold_time': '15',
            'fire_risk_warning': ''
        }
        
        result = generate_weather_report('evening')
        
        assert result['success'] is True
        report_text = result['report_text']
        
        # Should not show night temperature when not available
        assert "Nacht" not in report_text
        assert "Hitze33.5" in report_text 