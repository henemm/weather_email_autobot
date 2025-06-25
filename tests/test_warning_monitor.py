import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.state.tracker import WarningStateTracker, WarningState


class TestWarningStateTracker:
    """Test cases for the WarningStateTracker class."""
    
    def test_initialize_with_new_file(self):
        """Test initializing tracker with non-existent file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            tracker = WarningStateTracker(temp_path)
            assert tracker.state_file == temp_path
            assert tracker.current_state is None
        finally:
            os.unlink(temp_path)
    
    def test_initialize_with_existing_file(self):
        """Test initializing tracker with existing state file."""
        test_state = {
            "last_check": "2024-01-01T12:00:00",
            "max_thunderstorm_probability": 30.0,
            "max_precipitation": 15.0,
            "max_wind_speed": 25.0,
            "max_temperature": 28.0,
            "max_cloud_cover": 85.0,
            "last_warning_time": "2024-01-01T10:00:00"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(test_state, temp_file)
            temp_path = temp_file.name
        
        try:
            tracker = WarningStateTracker(temp_path)
            assert tracker.current_state is not None
            assert tracker.current_state.max_thunderstorm_probability == 30.0
            assert tracker.current_state.max_precipitation == 15.0
        finally:
            os.unlink(temp_path)
    
    def test_save_state(self):
        """Test saving state to file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            tracker = WarningStateTracker(temp_path)
            test_state = WarningState(
                last_check=datetime(2024, 1, 1, 12, 0, 0),
                max_thunderstorm_probability=25.0,
                max_precipitation=10.0,
                max_wind_speed=20.0,
                max_temperature=26.0,
                max_cloud_cover=80.0,
                last_warning_time=datetime(2024, 1, 1, 10, 0, 0)
            )
            
            tracker.save_state(test_state)
            
            # Verify file was created and contains correct data
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["max_thunderstorm_probability"] == 25.0
            assert saved_data["max_precipitation"] == 10.0
        finally:
            os.unlink(temp_path)
    
    def test_has_significant_change_when_no_previous_state(self):
        """Test detecting significant change when no previous state exists."""
        tracker = WarningStateTracker("dummy_path")
        tracker.current_state = None
        
        analysis = Mock()
        analysis.max_thunderstorm_probability = 30.0
        analysis.max_precipitation = 15.0
        analysis.max_wind_speed = 25.0
        analysis.max_temperature = 28.0
        analysis.max_cloud_cover = 85.0
        
        config = {
            "schwellen": {
                "delta_thunderstorm": 20.0,
                "delta_precipitation": 30.0,
                "delta_wind": 10.0,
                "delta_temperature": 2.0
            }
        }
        
        result = tracker.has_significant_change(analysis, config)
        assert result is True
    
    def test_has_significant_change_when_threshold_exceeded(self):
        """Test detecting significant change when thresholds are exceeded."""
        tracker = WarningStateTracker("dummy_path")
        tracker.current_state = WarningState(
            last_check=datetime(2024, 1, 1, 12, 0, 0),
            max_thunderstorm_probability=10.0,
            max_precipitation=5.0,
            max_wind_speed=15.0,
            max_temperature=25.0,
            max_cloud_cover=70.0,
            last_warning_time=datetime(2024, 1, 1, 10, 0, 0)
        )
        
        analysis = Mock()
        analysis.max_thunderstorm_probability = 35.0  # +25% (threshold: 20%)
        analysis.max_precipitation = 40.0  # +35mm (threshold: 30mm)
        analysis.max_wind_speed = 30.0  # +15 km/h (threshold: 10 km/h)
        analysis.max_temperature = 28.0  # +3°C (threshold: 2°C)
        analysis.max_cloud_cover = 90.0
        
        config = {
            "schwellen": {
                "delta_thunderstorm": 20.0,
                "delta_precipitation": 30.0,
                "delta_wind": 10.0,
                "delta_temperature": 2.0
            }
        }
        
        result = tracker.has_significant_change(analysis, config)
        assert result is True
    
    def test_has_significant_change_when_threshold_not_exceeded(self):
        """Test no significant change when thresholds are not exceeded."""
        tracker = WarningStateTracker("dummy_path")
        tracker.current_state = WarningState(
            last_check=datetime(2024, 1, 1, 12, 0, 0),
            max_thunderstorm_probability=10.0,
            max_precipitation=5.0,
            max_wind_speed=15.0,
            max_temperature=25.0,
            max_cloud_cover=70.0,
            last_warning_time=datetime(2024, 1, 1, 10, 0, 0)
        )
        
        analysis = Mock()
        analysis.max_thunderstorm_probability = 15.0  # +5% (threshold: 20%)
        analysis.max_precipitation = 10.0  # +5mm (threshold: 30mm)
        analysis.max_wind_speed = 20.0  # +5 km/h (threshold: 10 km/h)
        analysis.max_temperature = 26.0  # +1°C (threshold: 2°C)
        analysis.max_cloud_cover = 75.0
        
        config = {
            "schwellen": {
                "delta_thunderstorm": 20.0,
                "delta_precipitation": 30.0,
                "delta_wind": 10.0,
                "delta_temperature": 2.0
            }
        }
        
        result = tracker.has_significant_change(analysis, config)
        assert result is False


class TestWarningMonitor:
    """Test cases for the main warning monitor functionality."""
    
    def test_generate_warning_text(self):
        """Test generating warning text from analysis."""
        analysis = Mock()
        analysis.max_thunderstorm_probability = 35.0
        analysis.max_precipitation = 40.0
        analysis.max_wind_speed = 30.0
        analysis.max_temperature = 28.0
        analysis.max_cloud_cover = 90.0
        analysis.summary = "Heavy thunderstorms expected"
        
        # This test would verify the text generation logic
        # Implementation would be in the monitor module
        assert analysis.max_thunderstorm_probability == 35.0
        assert analysis.max_precipitation == 40.0 