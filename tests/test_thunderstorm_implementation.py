#!/usr/bin/env python3
"""
Test for thunderstorm implementation in morning_evening_refactor.py
"""

import pytest
from datetime import date, datetime
from src.weather.core.morning_evening_refactor import MorningEveningRefactor, WeatherThresholdData

class TestThunderstormImplementation:
    """Test cases for thunderstorm processing."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.config = {
            'rain_amount_threshold': 0.2,
            'rain_probability_threshold': 20.0,
            'wind_speed_threshold': 10.0,
            'wind_gust_threshold': 20.0,
            'thunderstorm_threshold': 'med'  # Threshold for thunderstorm level
        }
        self.refactor = MorningEveningRefactor(self.config)
    
    def test_process_thunderstorm_data_with_risk_dorages(self):
        """Test thunderstorm processing with 'Risque d'orages' condition."""
        # Set threshold to 'low' for this test
        self.refactor.thresholds['thunderstorm'] = 'low'
        
        # Mock weather data with 'Risque d'orages'
        weather_data = {
            'hourly_data': [
                {
                    'data': [
                        {
                            'time': '2025-08-02T17:00:00',
                            'condition': 'Risque d\'orages'
                        }
                    ]
                }
            ]
        }
        
        result = self.refactor.process_thunderstorm_data(
            weather_data, 'Test', date(2025, 8, 2), 'evening'
        )
        
        assert result.threshold_value == 'low'
        assert result.threshold_time == '17'
        assert result.max_value == 'low'
        assert result.max_time == '17'
    
    def test_process_thunderstorm_data_with_averses_orageuses(self):
        """Test thunderstorm processing with 'Averses orageuses' condition."""
        weather_data = {
            'hourly_data': [
                {
                    'data': [
                        {
                            'time': '2025-08-02T16:00:00',
                            'condition': 'Averses orageuses'
                        }
                    ]
                }
            ]
        }
        
        result = self.refactor.process_thunderstorm_data(
            weather_data, 'Test', date(2025, 8, 2), 'evening'
        )
        
        assert result.threshold_value == 'med'
        assert result.threshold_time == '16'
        assert result.max_value == 'med'
        assert result.max_time == '16'
    
    def test_process_thunderstorm_data_with_orages(self):
        """Test thunderstorm processing with 'Orages' condition."""
        weather_data = {
            'hourly_data': [
                {
                    'data': [
                        {
                            'time': '2025-08-02T18:00:00',
                            'condition': 'Orages'
                        }
                    ]
                }
            ]
        }
        
        result = self.refactor.process_thunderstorm_data(
            weather_data, 'Test', date(2025, 8, 2), 'evening'
        )
        
        assert result.threshold_value == 'high'
        assert result.threshold_time == '18'
        assert result.max_value == 'high'
        assert result.max_time == '18'
    
    def test_process_thunderstorm_data_with_no_thunderstorm(self):
        """Test thunderstorm processing with no thunderstorm condition."""
        weather_data = {
            'hourly_data': [
                {
                    'data': [
                        {
                            'time': '2025-08-02T17:00:00',
                            'condition': 'Ciel clair'
                        }
                    ]
                }
            ]
        }
        
        result = self.refactor.process_thunderstorm_data(
            weather_data, 'Test', date(2025, 8, 2), 'evening'
        )
        
        assert result.threshold_value is None
        assert result.threshold_time is None
        assert result.max_value is None
        assert result.max_time is None
    
    def test_process_thunderstorm_data_with_multiple_conditions(self):
        """Test thunderstorm processing with multiple conditions."""
        weather_data = {
            'hourly_data': [
                {
                    'data': [
                        {
                            'time': '2025-08-02T17:00:00',
                            'condition': 'Averses orageuses'
                        },
                        {
                            'time': '2025-08-02T18:00:00',
                            'condition': 'Orages'
                        }
                    ]
                }
            ]
        }
        
        result = self.refactor.process_thunderstorm_data(
            weather_data, 'Test', date(2025, 8, 2), 'evening'
        )
        
        # Should find threshold at first occurrence (17:00, med)
        assert result.threshold_value == 'med'
        assert result.threshold_time == '17'
        # Should find maximum at highest level (18:00, high)
        assert result.max_value == 'high'
        assert result.max_time == '18'
    
    def test_thunderstorm_threshold_logic(self):
        """Test that thunderstorm threshold logic works correctly."""
        # Test with threshold set to 'med'
        self.refactor.thresholds['thunderstorm'] = 'med'
        
        weather_data = {
            'hourly_data': [
                {
                    'data': [
                        {
                            'time': '2025-08-02T17:00:00',
                            'condition': 'Risque d\'orages'  # low level
                        }
                    ]
                }
            ]
        }
        
        result = self.refactor.process_thunderstorm_data(
            weather_data, 'Test', date(2025, 8, 2), 'evening'
        )
        
        # Should not meet 'med' threshold
        assert result.threshold_value is None
        assert result.threshold_time is None
        assert result.max_value == 'low'
        assert result.max_time == '17'

if __name__ == "__main__":
    pytest.main([__file__]) 