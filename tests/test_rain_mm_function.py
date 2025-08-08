#!/usr/bin/env python3
"""
Unit tests for Rain(mm) function implementation.
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


class TestRainMmFunction:
    """Test class for Rain(mm) function implementation."""
    
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
        """Mock weather data structure with hourly rain data."""
        return {
            'daily_forecast': {'daily': []},
            'hourly_data': [
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 2, 4, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 5, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 6, 0).timestamp(),
                            'rain': {'1h': 0.2}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 7, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 16, 0).timestamp(),
                            'rain': {'1h': 1.4}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 17, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 18, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        }
                    ]
                },
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 2, 4, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 5, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 6, 0).timestamp(),
                            'rain': {'1h': 0.2}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 7, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 16, 0).timestamp(),
                            'rain': {'1h': 1.4}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 17, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 18, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        }
                    ]
                },
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 2, 4, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 5, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 6, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 7, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 16, 0).timestamp(),
                            'rain': {'1h': 1.1}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 17, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 18, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        }
                    ]
                }
            ],
            'probability_forecast': []
        }
    
    def test_rain_mm_function_morning_report(self, refactor, mock_weather_data):
        """Test Rain(mm) function for morning report - should use today's stage for today."""
        target_date = date(2025, 8, 2)
        stage_name = "Vergio"
        report_type = "morning"
        
        result = refactor.process_rain_mm_data(mock_weather_data, stage_name, target_date, report_type)
        
        # Verify result structure
        assert isinstance(result, WeatherThresholdData)
        assert result.threshold_value == 0.2  # Threshold value
        assert result.threshold_time == "6"  # Earliest time when rain >= threshold
        assert result.max_value == 1.4  # Maximum rain value
        assert result.max_time == "16"  # Time of maximum rain
        
        # Verify geo points with correct T-G references
        assert len(result.geo_points) == 3
        expected_tg_refs = ['T1G1', 'T1G2', 'T1G3']
        for i, point in enumerate(result.geo_points):
            assert expected_tg_refs[i] in point
    
    def test_rain_mm_function_evening_report(self, refactor):
        """Test Rain(mm) function for evening report - should use tomorrow's stage for tomorrow."""
        target_date = date(2025, 8, 2)
        stage_name = "Vergio"
        report_type = "evening"
        
        # Create mock data for tomorrow (2025-08-03) since evening report uses tomorrow's data
        tomorrow_mock_data = {
            'daily_forecast': {'daily': []},
            'hourly_data': [
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 3, 4, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 5, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 6, 0).timestamp(),
                            'rain': {'1h': 0.2}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 7, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 16, 0).timestamp(),
                            'rain': {'1h': 1.4}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 17, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 18, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        }
                    ]
                },
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 3, 4, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 5, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 6, 0).timestamp(),
                            'rain': {'1h': 0.2}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 7, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 16, 0).timestamp(),
                            'rain': {'1h': 1.4}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 17, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 18, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        }
                    ]
                },
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 3, 4, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 5, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 6, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 7, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 16, 0).timestamp(),
                            'rain': {'1h': 1.1}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 17, 0).timestamp(),
                            'rain': {'1h': 0.8}
                        },
                        {
                            'dt': datetime(2025, 8, 3, 18, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        }
                    ]
                }
            ],
            'probability_forecast': []
        }
        
        result = refactor.process_rain_mm_data(tomorrow_mock_data, stage_name, target_date, report_type)
        
        # Verify result structure
        assert isinstance(result, WeatherThresholdData)
        assert result.threshold_value == 0.2  # Threshold value
        assert result.threshold_time == "6"  # Earliest time when rain >= threshold
        assert result.max_value == 1.4  # Maximum rain value
        assert result.max_time == "16"  # Time of maximum rain
        
        # Verify geo points with correct T-G references (T2 for tomorrow)
        assert len(result.geo_points) == 3
        expected_tg_refs = ['T2G1', 'T2G2', 'T2G3']
        for i, point in enumerate(result.geo_points):
            assert expected_tg_refs[i] in point
    
    def test_rain_mm_function_no_rain(self, refactor):
        """Test Rain(mm) function when no rain above threshold."""
        target_date = date(2025, 8, 2)
        stage_name = "Vergio"
        report_type = "morning"
        
        # Mock weather data with no rain above threshold
        no_rain_data = {
            'daily_forecast': {'daily': []},
            'hourly_data': [
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 2, 4, 0).timestamp(),
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 5, 0).timestamp(),
                            'rain': {'1h': 0.1}
                        }
                    ]
                }
            ],
            'probability_forecast': []
        }
        
        result = refactor.process_rain_mm_data(no_rain_data, stage_name, target_date, report_type)
        
        # Should return empty WeatherThresholdData when no rain above threshold
        assert isinstance(result, WeatherThresholdData)
        assert result.threshold_value is None
        assert result.max_value is None
        assert result.geo_points == []
    
    def test_rain_mm_function_debug_output_format(self, refactor):
        """Test that Rain(mm) debug output follows specification format."""
        # Create test report data
        from src.weather.core.morning_evening_refactor import WeatherReportData
        
        report_data = WeatherReportData(
            stage_name="Vergio",
            report_date=date(2025, 8, 2),
            report_type="morning",
            night=WeatherThresholdData(),
            day=WeatherThresholdData(),
            rain_mm=WeatherThresholdData(
                threshold_value=0.2,
                threshold_time="6",
                max_value=1.4,
                max_time="16",
                geo_points=[
                    {'T1G1': 0.8},
                    {'T1G2': 1.4},
                    {'T1G3': 1.1}
                ]
            ),
            rain_percent=WeatherThresholdData(),
            wind=WeatherThresholdData(),
            gust=WeatherThresholdData(),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
        
        debug_output = refactor.generate_debug_output(report_data)
        
        # Check that RAIN(MM) section is present and formatted correctly
        assert "RAIN(MM)" in debug_output
        assert "T1G1" in debug_output
        assert "T1G2" in debug_output
        assert "T1G3" in debug_output
        assert "Threshold" in debug_output
        assert "Maximum" in debug_output
    
    def test_rain_mm_function_result_output_format(self, refactor):
        """Test that Rain(mm) result output follows specification format."""
        # Create test report data
        from src.weather.core.morning_evening_refactor import WeatherReportData
        
        report_data = WeatherReportData(
            stage_name="Vergio",
            report_date=date(2025, 8, 2),
            report_type="morning",
            night=WeatherThresholdData(),
            day=WeatherThresholdData(),
            rain_mm=WeatherThresholdData(
                threshold_value=0.2,
                threshold_time="6",
                max_value=1.4,
                max_time="16",
                geo_points=[
                    {'T1G1': 0.8},
                    {'T1G2': 1.4},
                    {'T1G3': 1.1}
                ]
            ),
            rain_percent=WeatherThresholdData(),
            wind=WeatherThresholdData(),
            gust=WeatherThresholdData(),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
        
        result_output = refactor.format_result_output(report_data)
        
        # Check that Rain(mm) result is in correct format (R0.2@6(1.4@16))
        assert "R0.2@6(1.4@16)" in result_output
    
    def test_rain_mm_function_time_filter(self, refactor):
        """Test that Rain(mm) function only considers hours 4:00-19:00."""
        target_date = date(2025, 8, 2)
        stage_name = "Vergio"
        report_type = "morning"
        
        # Mock weather data with rain outside the time window
        time_filter_data = {
            'daily_forecast': {'daily': []},
            'hourly_data': [
                {
                    'data': [
                        {
                            'dt': datetime(2025, 8, 2, 3, 0).timestamp(),  # Outside window
                            'rain': {'1h': 2.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 4, 0).timestamp(),  # Inside window
                            'rain': {'1h': 0.0}
                        },
                        {
                            'dt': datetime(2025, 8, 2, 20, 0).timestamp(),  # Outside window
                            'rain': {'1h': 3.0}
                        }
                    ]
                }
            ],
            'probability_forecast': []
        }
        
        result = refactor.process_rain_mm_data(time_filter_data, stage_name, target_date, report_type)
        
        # Should not consider rain outside 4:00-19:00 window
        assert isinstance(result, WeatherThresholdData)
        assert result.threshold_value is None  # No rain above threshold in time window
        assert result.max_value is None
        assert result.geo_points == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 