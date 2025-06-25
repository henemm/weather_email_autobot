"""
Tests for the GR20 weather report scheduler functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.logic.report_scheduler import (
    ReportScheduler,
    should_send_scheduled_report,
    should_send_dynamic_report,
    get_nearest_stage_location,
    get_weather_model_for_report
)


class TestReportScheduler:
    """Test cases for ReportScheduler class."""
    
    def test_should_send_scheduled_report_morning_time(self):
        """Test morning report scheduling."""
        config = {
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            }
        }
        
        # Test morning time
        morning_time = datetime.now().replace(hour=4, minute=30, second=0, microsecond=0)
        assert should_send_scheduled_report(morning_time, config) is True
        
        # Test non-morning time
        other_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        assert should_send_scheduled_report(other_time, config) is False
    
    def test_should_send_scheduled_report_evening_time(self):
        """Test evening report scheduling."""
        config = {
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            }
        }
        
        # Test evening time
        evening_time = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        assert should_send_scheduled_report(evening_time, config) is True
        
        # Test non-evening time
        other_time = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
        assert should_send_scheduled_report(other_time, config) is False
    
    def test_should_send_dynamic_report_threshold_exceeded(self):
        """Test dynamic report when risk threshold is exceeded."""
        config = {
            "dynamic_send": {
                "threshold": 0.4,
                "delta_pct": 15.0,
                "min_interval_min": 30,
                "max_daily_reports": 3
            }
        }
        
        current_risk = 0.6
        previous_risk = 0.3
        last_report_time = datetime.now() - timedelta(minutes=45)
        daily_report_count = 1
        
        result = should_send_dynamic_report(
            current_risk, previous_risk, last_report_time, daily_report_count, config
        )
        
        assert result is True
    
    def test_should_send_dynamic_report_insufficient_change(self):
        """Test dynamic report when risk change is insufficient."""
        config = {
            "dynamic_send": {
                "threshold": 0.4,
                "delta_pct": 15.0,
                "min_interval_min": 30,
                "max_daily_reports": 3
            }
        }
        
        current_risk = 0.5
        previous_risk = 0.45  # Only 5% change, below 15% threshold
        last_report_time = datetime.now() - timedelta(minutes=45)
        daily_report_count = 1
        
        result = should_send_dynamic_report(
            current_risk, previous_risk, last_report_time, daily_report_count, config
        )
        
        assert result is False
    
    def test_should_send_dynamic_report_interval_too_short(self):
        """Test dynamic report when minimum interval is not met."""
        config = {
            "dynamic_send": {
                "threshold": 0.4,
                "delta_pct": 15.0,
                "min_interval_min": 30,
                "max_daily_reports": 3
            }
        }
        
        current_risk = 0.6
        previous_risk = 0.3
        last_report_time = datetime.now() - timedelta(minutes=15)  # Too recent
        daily_report_count = 1
        
        result = should_send_dynamic_report(
            current_risk, previous_risk, last_report_time, daily_report_count, config
        )
        
        assert result is False
    
    def test_should_send_dynamic_report_max_daily_reached(self):
        """Test dynamic report when maximum daily reports reached."""
        config = {
            "dynamic_send": {
                "threshold": 0.4,
                "delta_pct": 15.0,
                "min_interval_min": 30,
                "max_daily_reports": 3
            }
        }
        
        current_risk = 0.6
        previous_risk = 0.3
        last_report_time = datetime.now() - timedelta(minutes=45)
        daily_report_count = 3  # Maximum reached
        
        result = should_send_dynamic_report(
            current_risk, previous_risk, last_report_time, daily_report_count, config
        )
        
        assert result is False
    
    def test_get_nearest_stage_location(self):
        """Test finding nearest GR20 stage location."""
        config = {
            "gr20_stages": [
                {"name": "Calenzana", "coordinates": [42.5083, 8.8556]},
                {"name": "Haut Asco", "coordinates": [42.4500, 9.0333]},
                {"name": "Vizzavona", "coordinates": [42.1167, 9.1333]},
                {"name": "Conca", "coordinates": [41.7333, 9.3500]}
            ]
        }
        
        # Test position near Vizzavona
        test_lat, test_lon = 42.12, 9.14
        nearest = get_nearest_stage_location(test_lat, test_lon, config)
        
        assert nearest["name"] == "Vizzavona"
        assert nearest["coordinates"] == [42.1167, 9.1333]
    
    def test_get_nearest_stage_location_no_stages(self):
        """Test nearest stage location when no stages configured."""
        config = {"gr20_stages": []}
        
        nearest = get_nearest_stage_location(42.0, 9.0, config)
        
        assert nearest is None


class TestWeatherModelSelection:
    """Test weather model selection based on report type."""
    
    def test_get_weather_model_for_morning_report(self):
        """Test weather model selection for morning reports."""
        config = {
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            }
        }
        
        # Test morning time
        morning_time = datetime.now().replace(hour=4, minute=30, second=0, microsecond=0)
        model = get_weather_model_for_report(morning_time, config)
        
        assert model == "AROME_HR"
    
    def test_get_weather_model_for_evening_report(self):
        """Test weather model selection for evening reports."""
        config = {
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            }
        }
        
        # Test evening time
        evening_time = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        model = get_weather_model_for_report(evening_time, config)
        
        assert model == "AROME_HR"
    
    def test_get_weather_model_for_dynamic_report(self):
        """Test weather model selection for dynamic reports."""
        config = {
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            }
        }
        
        # Test non-scheduled time (should be dynamic)
        dynamic_time = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        model = get_weather_model_for_report(dynamic_time, config)
        
        assert model == "AROME_HR_NOWCAST"
    
    def test_get_weather_model_fallback(self):
        """Test weather model selection fallback behavior."""
        config = {
            "send_schedule": {
                "morning_time": "04:30",
                "evening_time": "19:00"
            }
        }
        
        # Test with invalid config (should fallback to AROME_HR)
        morning_time = datetime.now().replace(hour=4, minute=30, second=0, microsecond=0)
        model = get_weather_model_for_report(morning_time, {})
        
        assert model == "AROME_HR"


class TestReportSchedulerIntegration:
    """Integration tests for ReportScheduler."""
    
    @patch('src.logic.report_scheduler.ReportScheduler._load_state')
    def test_scheduler_initialization(self, mock_load_state):
        """Test ReportScheduler initialization."""
        mock_load_state.return_value = None
        
        config = {
            "send_schedule": {"morning_time": "04:30", "evening_time": "19:00"},
            "dynamic_send": {"threshold": 0.4, "delta_pct": 15.0}
        }
        
        scheduler = ReportScheduler("test_state.json", config)
        
        assert scheduler.state_file == "test_state.json"
        assert scheduler.config == config
        assert scheduler.current_state is None
    
    @patch('src.logic.report_scheduler.ReportScheduler._save_state')
    def test_scheduler_save_state(self, mock_save_state):
        """Test saving scheduler state."""
        config = {
            "send_schedule": {"morning_time": "04:30", "evening_time": "19:00"},
            "dynamic_send": {"threshold": 0.4, "delta_pct": 15.0}
        }
        
        scheduler = ReportScheduler("test_state.json", config)
        scheduler.current_state = Mock()
        
        scheduler._save_state()
        
        mock_save_state.assert_called_once() 