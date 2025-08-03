#!/usr/bin/env python3
"""
Test Rain(%) function implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor, WeatherReportData, WeatherThresholdData
from datetime import date
import yaml
import pytest

def load_config():
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

class TestRainPercentFunction:
    """Test cases for Rain(%) function."""
    
    @pytest.fixture
    def refactor(self):
        """Initialize MorningEveningRefactor with config."""
        config = load_config()
        return MorningEveningRefactor(config)
    
    @pytest.fixture
    def mock_weather_data(self):
        """Mock weather data with probability forecast."""
        # Correct timestamps for 2025-08-02
        return {
            'probability_forecast': [
                {
                    'data': [
                        {'dt': 1754103600, 'rain': {'3h': 10}},  # 2025-08-02 05:00
                        {'dt': 1754114400, 'rain': {'3h': 0}},   # 2025-08-02 08:00
                        {'dt': 1754125200, 'rain': {'3h': 20}},  # 2025-08-02 11:00
                        {'dt': 1754136000, 'rain': {'3h': 30}},  # 2025-08-02 14:00
                        {'dt': 1754146800, 'rain': {'3h': 80}},  # 2025-08-02 17:00
                    ]
                },
                {
                    'data': [
                        {'dt': 1754103600, 'rain': {'3h': 15}},  # 2025-08-02 05:00
                        {'dt': 1754114400, 'rain': {'3h': 0}},   # 2025-08-02 08:00
                        {'dt': 1754125200, 'rain': {'3h': 25}},  # 2025-08-02 11:00
                        {'dt': 1754136000, 'rain': {'3h': 40}},  # 2025-08-02 14:00
                        {'dt': 1754146800, 'rain': {'3h': 100}}, # 2025-08-02 17:00
                    ]
                },
                {
                    'data': [
                        {'dt': 1754103600, 'rain': {'3h': 5}},   # 2025-08-02 05:00
                        {'dt': 1754114400, 'rain': {'3h': 0}},   # 2025-08-02 08:00
                        {'dt': 1754125200, 'rain': {'3h': 20}},  # 2025-08-02 11:00
                        {'dt': 1754136000, 'rain': {'3h': 25}},  # 2025-08-02 14:00
                        {'dt': 1754146800, 'rain': {'3h': 75}},  # 2025-08-02 17:00
                    ]
                }
            ]
        }
    
    def test_rain_percent_function_morning_report(self, refactor, mock_weather_data):
        """Test Rain(%) function for morning report."""
        stage_name = "Test"
        target_date = date(2025, 8, 2)
        
        # Process Rain(%) data for morning
        rain_percent_result = refactor.process_rain_percent_data(
            mock_weather_data, stage_name, target_date, "morning"
        )
        
        # Verify results
        assert rain_percent_result.threshold_value == 20
        assert rain_percent_result.threshold_time == "11"
        assert rain_percent_result.max_value == 100
        assert rain_percent_result.max_time == "17"
        assert len(rain_percent_result.geo_points) == 3
        
        # Check T-G references
        tg_refs = [list(point.keys())[0] for point in rain_percent_result.geo_points]
        assert tg_refs == ['T1G1', 'T1G2', 'T1G3']
    
    def test_rain_percent_function_evening_report(self, refactor, mock_weather_data):
        """Test Rain(%) function for evening report."""
        stage_name = "Test"
        target_date = date(2025, 8, 2)
        
        # Create mock data for tomorrow (2025-08-03) for evening report
        tomorrow_mock_data = {
            'probability_forecast': [
                {
                    'data': [
                        {'dt': 1754190000, 'rain': {'3h': 10}},  # 2025-08-03 05:00
                        {'dt': 1754200800, 'rain': {'3h': 0}},   # 2025-08-03 08:00
                        {'dt': 1754211600, 'rain': {'3h': 20}},  # 2025-08-03 11:00
                        {'dt': 1754222400, 'rain': {'3h': 30}},  # 2025-08-03 14:00
                        {'dt': 1754233200, 'rain': {'3h': 80}},  # 2025-08-03 17:00
                    ]
                },
                {
                    'data': [
                        {'dt': 1754190000, 'rain': {'3h': 15}},  # 2025-08-03 05:00
                        {'dt': 1754200800, 'rain': {'3h': 0}},   # 2025-08-03 08:00
                        {'dt': 1754211600, 'rain': {'3h': 25}},  # 2025-08-03 11:00
                        {'dt': 1754222400, 'rain': {'3h': 40}},  # 2025-08-03 14:00
                        {'dt': 1754233200, 'rain': {'3h': 100}}, # 2025-08-03 17:00
                    ]
                },
                {
                    'data': [
                        {'dt': 1754190000, 'rain': {'3h': 5}},   # 2025-08-03 05:00
                        {'dt': 1754200800, 'rain': {'3h': 0}},   # 2025-08-03 08:00
                        {'dt': 1754211600, 'rain': {'3h': 20}},  # 2025-08-03 11:00
                        {'dt': 1754222400, 'rain': {'3h': 25}},  # 2025-08-03 14:00
                        {'dt': 1754233200, 'rain': {'3h': 75}},  # 2025-08-03 17:00
                    ]
                }
            ]
        }
        
        # Process Rain(%) data for evening
        rain_percent_result = refactor.process_rain_percent_data(
            tomorrow_mock_data, stage_name, target_date, "evening"
        )
        
        # Verify results
        assert rain_percent_result.threshold_value == 20
        assert rain_percent_result.threshold_time == "11"
        assert rain_percent_result.max_value == 100
        assert rain_percent_result.max_time == "17"
        assert len(rain_percent_result.geo_points) == 3
        
        # Check T-G references
        tg_refs = [list(point.keys())[0] for point in rain_percent_result.geo_points]
        assert tg_refs == ['T2G1', 'T2G2', 'T2G3']
    
    def test_rain_percent_function_no_rain(self, refactor):
        """Test Rain(%) function when no rain probability above threshold."""
        mock_data_no_rain = {
            'probability_forecast': [
                {
                    'data': [
                        {'dt': 1754103600, 'rain': {'3h': 5}},   # 2025-08-02 05:00
                        {'dt': 1754114400, 'rain': {'3h': 0}},   # 2025-08-02 08:00
                        {'dt': 1754125200, 'rain': {'3h': 10}},  # 2025-08-02 11:00
                        {'dt': 1754136000, 'rain': {'3h': 5}},   # 2025-08-02 14:00
                        {'dt': 1754146800, 'rain': {'3h': 0}},   # 2025-08-02 17:00
                    ]
                }
            ]
        }
        
        stage_name = "Test"
        target_date = date(2025, 8, 2)
        
        rain_percent_result = refactor.process_rain_percent_data(
            mock_data_no_rain, stage_name, target_date, "morning"
        )
        
        # Should return empty data when no rain probability >= threshold
        assert rain_percent_result.threshold_value is None
        assert rain_percent_result.max_value is None
        assert rain_percent_result.geo_points == []
    
    def test_rain_percent_function_result_output_format(self, refactor, mock_weather_data):
        """Test Rain(%) result output formatting."""
        stage_name = "Test"
        target_date = date(2025, 8, 2)
        
        # Process Rain(%) data
        rain_percent_result = refactor.process_rain_percent_data(
            mock_weather_data, stage_name, target_date, "morning"
        )
        
        # Create report data
        empty_data = WeatherThresholdData()
        report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=empty_data,
            day=empty_data,
            rain_mm=empty_data,
            rain_percent=rain_percent_result,
            wind=empty_data,
            gust=empty_data,
            thunderstorm=empty_data,
            thunderstorm_plus_one=empty_data,
            risks=empty_data,
            risk_zonal=empty_data
        )
        
        # Format result output
        result = refactor.format_result_output(report_data)
        
        # Verify format: PR20%@11(100%@17)
        assert "PR20%@11(100%@17)" in result
    
    def test_rain_percent_function_time_filter(self, refactor):
        """Test Rain(%) function uses correct time filter (05:00, 08:00, 11:00, 14:00, 17:00)."""
        mock_data_with_extra_times = {
            'probability_forecast': [
                {
                    'data': [
                        {'dt': 1754100000, 'rain': {'3h': 50}},  # 2025-08-02 04:00 (should be ignored)
                        {'dt': 1754103600, 'rain': {'3h': 20}},  # 2025-08-02 05:00 (should be included)
                        {'dt': 1754114400, 'rain': {'3h': 30}},  # 2025-08-02 08:00 (should be included)
                        {'dt': 1754125200, 'rain': {'3h': 40}},  # 2025-08-02 11:00 (should be included)
                        {'dt': 1754136000, 'rain': {'3h': 60}},  # 2025-08-02 14:00 (should be included)
                        {'dt': 1754146800, 'rain': {'3h': 80}},  # 2025-08-02 17:00 (should be included)
                        {'dt': 1754150400, 'rain': {'3h': 90}},  # 2025-08-02 18:00 (should be ignored)
                    ]
                }
            ]
        }
        
        stage_name = "Test"
        target_date = date(2025, 8, 2)
        
        rain_percent_result = refactor.process_rain_percent_data(
            mock_data_with_extra_times, stage_name, target_date, "morning"
        )
        
        # Should only include data from 05:00, 08:00, 11:00, 14:00, 17:00
        assert rain_percent_result.threshold_value == 20
        assert rain_percent_result.threshold_time == "5"
        assert rain_percent_result.max_value == 80
        assert rain_percent_result.max_time == "17"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 