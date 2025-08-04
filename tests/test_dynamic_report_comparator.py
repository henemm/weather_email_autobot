"""
Unit tests for DynamicReportComparator

Tests the comparison logic for dynamic weather reports.
"""

import pytest
import json
import os
from datetime import date, datetime
from unittest.mock import patch, MagicMock
from src.logic.dynamic_report_comparator import DynamicReportComparator


class TestDynamicReportComparator:
    """Test cases for DynamicReportComparator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'delta_thresholds': {
                'rain_probability': 1.0,
                'rain_amount': 1.5,
                'temperature': 1.0,
                'thunderstorm': 1,
                'wind_speed': 1.0
            }
        }
        self.comparator = DynamicReportComparator(self.config)
        
    def test_init_with_config(self):
        """Test initialization with configuration."""
        assert self.comparator.config == self.config
        assert self.comparator.delta_thresholds == self.config['delta_thresholds']
        assert self.comparator.data_dir == ".data/weather_reports"
    
    def test_load_last_report_file_not_found(self):
        """Test loading last report when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            result = self.comparator.load_last_report("TestStage", date(2025, 8, 4))
            assert result is None
    
    def test_load_last_report_file_exists(self):
        """Test loading last report when file exists."""
        mock_data = {
            'stage_name': 'TestStage',
            'report_date': '2025-08-04',
            'rain_mm': {'max_value': 5.0, 'threshold_time': '14:00'}
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
            
            result = self.comparator.load_last_report("TestStage", date(2025, 8, 4))
            assert result == mock_data
    
    def test_compare_reports_no_previous_report(self):
        """Test comparison when no previous report exists."""
        current_report = {'rain_mm': {'max_value': 5.0}}
        
        should_send, change_details = self.comparator.compare_reports(current_report, None)
        
        assert should_send is True
        assert change_details['reason'] == 'first_report'
    
    def test_compare_reports_no_significant_changes(self):
        """Test comparison when no significant changes detected."""
        current_report = {
            'rain_mm': {'max_value': 5.0, 'threshold_time': '14:00'},
            'wind': {'max_value': 10.0, 'threshold_time': '15:00'}
        }
        previous_report = {
            'rain_mm': {'max_value': 5.0, 'threshold_time': '14:00'},
            'wind': {'max_value': 10.0, 'threshold_time': '15:00'}
        }
        
        should_send, change_details = self.comparator.compare_reports(current_report, previous_report)
        
        assert should_send is False
        assert change_details['reason'] == 'no_significant_changes'
        assert len(change_details['changes']) == 0
    
    def test_compare_reports_significant_rain_change(self):
        """Test comparison when significant rain change detected."""
        current_report = {
            'rain_mm': {'max_value': 7.0, 'threshold_time': '14:00'}
        }
        previous_report = {
            'rain_mm': {'max_value': 5.0, 'threshold_time': '14:00'}
        }
        
        should_send, change_details = self.comparator.compare_reports(current_report, previous_report)
        
        assert should_send is True
        assert change_details['reason'] == 'significant_changes_detected'
        assert len(change_details['changes']) == 1
        assert change_details['changes'][0]['element'] == 'rain_mm'
    
    def test_compare_reports_time_change(self):
        """Test comparison when threshold time changes significantly."""
        current_report = {
            'rain_mm': {'max_value': 5.0, 'threshold_time': '16:00'}
        }
        previous_report = {
            'rain_mm': {'max_value': 5.0, 'threshold_time': '14:00'}
        }
        
        should_send, change_details = self.comparator.compare_reports(current_report, previous_report)
        
        assert should_send is True
        assert change_details['reason'] == 'significant_changes_detected'
        assert len(change_details['changes']) == 1
    
    def test_compare_element_max_value_change(self):
        """Test element comparison with max value change."""
        current = {'rain_mm': {'max_value': 7.0}}
        previous = {'rain_mm': {'max_value': 5.0}}
        
        result = self.comparator._compare_element(current, previous, 'rain_mm', 'rain_amount')
        assert result is True
    
    def test_compare_element_no_change(self):
        """Test element comparison with no significant change."""
        current = {'rain_mm': {'max_value': 5.0}}
        previous = {'rain_mm': {'max_value': 5.0}}
        
        result = self.comparator._compare_element(current, previous, 'rain_mm', 'rain_amount')
        assert result is False
    
    def test_compare_element_missing_data(self):
        """Test element comparison with missing data."""
        current = {'rain_mm': {'max_value': 5.0}}
        previous = {}
        
        result = self.comparator._compare_element(current, previous, 'rain_mm', 'rain_amount')
        assert result is False
    
    def test_save_comparison_result(self):
        """Test saving comparison result."""
        with patch('os.makedirs') as mock_makedirs, \
             patch('builtins.open', create=True) as mock_open:
            
            self.comparator.save_comparison_result(
                "TestStage", 
                date(2025, 8, 4), 
                True, 
                {'reason': 'test'}
            )
            
            mock_makedirs.assert_called_once()
            mock_open.assert_called_once()


class TestDynamicReportIntegration:
    """Integration tests for dynamic report functionality."""
    
    def test_dynamic_report_conditions_check(self):
        """Test the dynamic report conditions check."""
        from src.weather.core.morning_evening_refactor import MorningEveningRefactor
        
        config = {
            'delta_thresholds': {
                'rain_probability': 1.0,
                'rain_amount': 1.5,
                'wind_speed': 1.0
            }
        }
        
        refactor = MorningEveningRefactor(config)
        
        # Test with no previous report (should return True)
        with patch.object(refactor, '_generate_report_data_only', return_value={}):
            result = refactor._check_dynamic_report_conditions("TestStage", date(2025, 8, 4))
            assert result is True
    
    def test_rain_2h_data_processing(self):
        """Test RAIN 2H data processing."""
        from src.weather.core.morning_evening_refactor import MorningEveningRefactor
        
        config = {}
        refactor = MorningEveningRefactor(config)
        
        # Mock weather data with rain forecast
        weather_data = {
            'rain_forecast': [
                {'time': '13:00', 'amount': 1.0},
                {'time': '14:00', 'amount': 1.0}
            ]
        }
        
        result = refactor.process_rain_2h_data(
            weather_data, 
            "TestStage", 
            date(2025, 8, 4), 
            'dynamic'
        )
        
        assert hasattr(result, 'geo_points')
        assert hasattr(result, 'max_value')
        assert hasattr(result, 'threshold_value')


if __name__ == '__main__':
    pytest.main([__file__]) 