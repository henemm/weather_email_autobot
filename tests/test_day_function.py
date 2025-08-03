#!/usr/bin/env python3
"""
Unit tests for Day function implementation.
Tests both morning and evening reports according to specification.
"""

import pytest
import sys
import os
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor, WeatherThresholdData


class TestDayFunction:
    """Test class for Day function implementation."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return {
            'startdatum': '2025-07-27',
            'wind_speed': 10,
            'wind_gust_threshold': 20,
            'rain_threshold': 0.2,
            'rain_probability_threshold': 20,
            'thunderstorm_threshold': 'med',
            'debug': {'enabled': True}
        }
    
    @pytest.fixture
    def refactor(self, config):
        """MorningEveningRefactor instance with test config."""
        return MorningEveningRefactor(config)
    
    @pytest.fixture
    def mock_weather_data(self):
        """Mock weather data structure."""
        return {
            'daily_forecast': {
                'daily': [
                    {
                        'dt': datetime(2025, 8, 2, 12, 0).timestamp(),
                        'T': {'max': 24.1, 'min': 8.2}
                    },
                    {
                        'dt': datetime(2025, 8, 3, 12, 0).timestamp(),
                        'T': {'max': 26.3, 'min': 9.1}
                    }
                ]
            },
            'hourly_data': [],
            'probability_forecast': []
        }
    
    def test_day_function_morning_report(self, refactor, mock_weather_data):
        """Test Day function for morning report - should use today's stage for today."""
        target_date = date(2025, 8, 2)
        stage_name = "Vergio"
        report_type = "morning"
        
        # Mock the API calls
        with patch('src.wetter.enhanced_meteofrance_api.EnhancedMeteoFranceAPI') as mock_api:
            mock_instance = Mock()
            mock_api.return_value = mock_instance
            
            # Mock data for 3 points of today's stage
            mock_instance.get_complete_forecast_data.side_effect = [
                {
                    'daily_forecast': {
                        'daily': [{'dt': datetime(2025, 8, 2, 12, 0).timestamp(), 'T': {'max': 22.1}}]
                    }
                },
                {
                    'daily_forecast': {
                        'daily': [{'dt': datetime(2025, 8, 2, 12, 0).timestamp(), 'T': {'max': 24.1}}]
                    }
                },
                {
                    'daily_forecast': {
                        'daily': [{'dt': datetime(2025, 8, 2, 12, 0).timestamp(), 'T': {'max': 18.9}}]
                    }
                }
            ]
            
            result = refactor.process_day_data(mock_weather_data, stage_name, target_date, report_type)
            
            # Verify result structure
            assert isinstance(result, WeatherThresholdData)
            assert result.threshold_value == 24  # Max temp rounded
            assert result.max_value == 24
            assert result.threshold_time is None  # Daily data has no specific time
            assert result.max_time is None
            
            # Verify geo points with correct T-G references
            assert len(result.geo_points) == 3
            expected_tg_refs = ['T1G1', 'T1G2', 'T1G3']
            for i, point in enumerate(result.geo_points):
                assert expected_tg_refs[i] in point
    
    def test_day_function_evening_report(self, refactor, mock_weather_data):
        """Test Day function for evening report - should use tomorrow's stage for tomorrow."""
        target_date = date(2025, 8, 2)
        stage_name = "Vergio"
        report_type = "evening"
        
        # Mock the API calls
        with patch('src.wetter.enhanced_meteofrance_api.EnhancedMeteoFranceAPI') as mock_api:
            mock_instance = Mock()
            mock_api.return_value = mock_instance
            
            # Mock data for 3 points of tomorrow's stage
            mock_instance.get_complete_forecast_data.side_effect = [
                {
                    'daily_forecast': {
                        'daily': [{'dt': datetime(2025, 8, 3, 12, 0).timestamp(), 'T': {'max': 25.1}}]
                    }
                },
                {
                    'daily_forecast': {
                        'daily': [{'dt': datetime(2025, 8, 3, 12, 0).timestamp(), 'T': {'max': 27.3}}]
                    }
                },
                {
                    'daily_forecast': {
                        'daily': [{'dt': datetime(2025, 8, 3, 12, 0).timestamp(), 'T': {'max': 23.9}}]
                    }
                }
            ]
            
            result = refactor.process_day_data(mock_weather_data, stage_name, target_date, report_type)
            
            # Verify result structure
            assert isinstance(result, WeatherThresholdData)
            assert result.threshold_value == 27  # Max temp rounded
            assert result.max_value == 27
            assert result.threshold_time is None
            assert result.max_time is None
            
            # Verify geo points with correct T-G references (T2 for tomorrow)
            assert len(result.geo_points) == 3
            expected_tg_refs = ['T2G1', 'T2G2', 'T2G3']
            for i, point in enumerate(result.geo_points):
                assert expected_tg_refs[i] in point
    
    def test_day_function_no_data(self, refactor, mock_weather_data):
        """Test Day function when no weather data is available."""
        target_date = date(2025, 8, 2)
        stage_name = "Vergio"
        report_type = "morning"
        
        # Mock the API calls to return no data
        with patch('src.wetter.enhanced_meteofrance_api.EnhancedMeteoFranceAPI') as mock_api:
            mock_instance = Mock()
            mock_api.return_value = mock_instance
            mock_instance.get_complete_forecast_data.return_value = {
                'daily_forecast': {'daily': []}
            }
            
            result = refactor.process_day_data(mock_weather_data, stage_name, target_date, report_type)
            
            # Should return empty WeatherThresholdData
            assert isinstance(result, WeatherThresholdData)
            assert result.threshold_value is None
            assert result.max_value is None
            assert result.geo_points == []
    
    def test_day_function_missing_stage(self, refactor, mock_weather_data):
        """Test Day function when stage is not found."""
        target_date = date(2025, 8, 2)
        stage_name = "NonExistentStage"
        report_type = "morning"
        
        # Mock the API calls to return no data
        with patch('src.wetter.enhanced_meteofrance_api.EnhancedMeteoFranceAPI') as mock_api:
            mock_instance = Mock()
            mock_api.return_value = mock_instance
            mock_instance.get_complete_forecast_data.return_value = {
                'daily_forecast': {'daily': []}
            }
            
            result = refactor.process_day_data(mock_weather_data, stage_name, target_date, report_type)
            
            # Should return empty WeatherThresholdData
            assert isinstance(result, WeatherThresholdData)
            assert result.threshold_value is None
            assert result.max_value is None
            assert result.geo_points == []
    
    def test_day_function_debug_output_format(self, refactor):
        """Test that Day debug output follows specification format."""
        # Create test report data
        from src.weather.core.morning_evening_refactor import WeatherReportData
        
        report_data = WeatherReportData(
            stage_name="Vergio",
            report_date=date(2025, 8, 2),
            report_type="morning",
            night=WeatherThresholdData(),
            day=WeatherThresholdData(
                threshold_value=24,
                max_value=24,
                geo_points=[
                    {'T1G1': 22.1},
                    {'T1G2': 24.1},
                    {'T1G3': 18.9}
                ]
            ),
            rain_mm=WeatherThresholdData(),
            rain_percent=WeatherThresholdData(),
            wind=WeatherThresholdData(),
            gust=WeatherThresholdData(),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
        
        debug_output = refactor.generate_debug_output(report_data)
        
        # Check that DAY section is present and formatted correctly
        assert "DAY" in debug_output
        assert "T1G1" in debug_output
        assert "T1G2" in debug_output
        assert "T1G3" in debug_output
        assert "MAX" in debug_output
        assert "24" in debug_output  # Max value
    
    def test_day_function_result_output_format(self, refactor):
        """Test that Day result output follows specification format."""
        # Create test report data
        from src.weather.core.morning_evening_refactor import WeatherReportData
        
        report_data = WeatherReportData(
            stage_name="Vergio",
            report_date=date(2025, 8, 2),
            report_type="morning",
            night=WeatherThresholdData(),
            day=WeatherThresholdData(
                threshold_value=24,
                max_value=24,
                geo_points=[
                    {'T1G1': 22.1},
                    {'T1G2': 24.1},
                    {'T1G3': 18.9}
                ]
            ),
            rain_mm=WeatherThresholdData(),
            rain_percent=WeatherThresholdData(),
            wind=WeatherThresholdData(),
            gust=WeatherThresholdData(),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
        
        result_output = refactor.format_result_output(report_data)
        
        # Check that Day result is in correct format (D24)
        assert "D24" in result_output
    
    def test_day_function_persistence(self, refactor, tmp_path):
        """Test that Day data is correctly persisted."""
        # Mock the persistence directory
        with patch('src.weather.core.morning_evening_refactor.os.makedirs') as mock_makedirs:
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                # Create test report data
                from src.weather.core.morning_evening_refactor import WeatherReportData
                
                report_data = WeatherReportData(
                    stage_name="Vergio",
                    report_date=date(2025, 8, 2),
                    report_type="morning",
                    night=WeatherThresholdData(),
                    day=WeatherThresholdData(
                        threshold_value=24,
                        max_value=24,
                        geo_points=[
                            {'T1G1': 22.1},
                            {'T1G2': 24.1},
                            {'T1G3': 18.9}
                        ]
                    ),
                    rain_mm=WeatherThresholdData(),
                    rain_percent=WeatherThresholdData(),
                    wind=WeatherThresholdData(),
                    gust=WeatherThresholdData(),
                    thunderstorm=WeatherThresholdData(),
                    thunderstorm_plus_one=WeatherThresholdData(),
                    risks=WeatherThresholdData(),
                    risk_zonal=WeatherThresholdData()
                )
                
                # Test persistence
                result = refactor.save_persistence_data(report_data)
                
                # Verify persistence was called
                assert result is True
                mock_makedirs.assert_called()
                mock_open.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 