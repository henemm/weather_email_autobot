"""
Tests for report debug integration functionality.

This module tests the integration of debug functionality into the regular
report workflow, including configuration handling and debug output generation.
"""

import pytest
import os
import tempfile
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from src.wetter.report_debug import (
    ReportDebugger,
    ReportDebugInfo,
    create_report_debugger
)
from src.model.datatypes import WeatherData, WeatherPoint


class TestReportDebuggerConfiguration:
    """Test ReportDebugger configuration handling."""
    
    def test_debugger_disabled_by_default(self):
        """Test that debugger is disabled when no debug config is provided."""
        config = {}
        debugger = ReportDebugger(config)
        
        assert not debugger.should_debug()
        assert debugger.enabled is False
    
    def test_debugger_enabled_with_config(self):
        """Test that debugger is enabled when debug.enabled is True."""
        config = {
            "debug": {
                "enabled": True,
                "output_directory": "test_debug"
            }
        }
        debugger = ReportDebugger(config)
        
        assert debugger.should_debug()
        assert debugger.enabled is True
        assert debugger.output_directory == "test_debug"
    
    def test_debugger_default_output_directory(self):
        """Test that debugger uses default output directory when not specified."""
        config = {
            "debug": {
                "enabled": True
            }
        }
        debugger = ReportDebugger(config)
        
        assert debugger.output_directory == "output/debug"
    
    def test_debugger_custom_output_directory(self):
        """Test that debugger uses custom output directory."""
        config = {
            "debug": {
                "enabled": True,
                "output_directory": "custom/debug/path"
            }
        }
        debugger = ReportDebugger(config)
        
        assert debugger.output_directory == "custom/debug/path"


class TestReportDebuggerFunctionality:
    """Test ReportDebugger functionality."""
    
    def setup_method(self):
        """Initialize test configuration."""
        self.config = {
            "debug": {
                "enabled": True,
                "raw_data_output": True,
                "threshold_validation": True,
                "comparison_with_report": True,
                "save_debug_files": True,
                "output_directory": "test_debug_output"
            },
            "thresholds": {
                "rain_probability": 25.0,
                "rain_amount": 2.0,
                "thunderstorm_probability": 20.0,
                "wind_speed": 40.0
            }
        }
        self.debugger = ReportDebugger(self.config)
    
    @patch('src.wetter.report_debug.get_raw_weather_data')
    @patch('src.wetter.report_debug.save_debug_output')
    def test_debug_weather_data_collection_enabled(self, mock_save_output, mock_get_raw_data):
        """Test weather data collection when debugging is enabled."""
        # Arrange
        mock_raw_data = Mock()
        mock_raw_data.time_points = []  # Add required attribute
        mock_get_raw_data.return_value = mock_raw_data
        mock_save_output.return_value = None  # Mock save function
        
        # Act
        result = self.debugger.debug_weather_data_collection(42.15, 9.15, "Corte")
        
        # Assert
        assert result == mock_raw_data
        mock_get_raw_data.assert_called_once_with(42.15, 9.15, "Corte", 24)
    
    def test_debug_weather_data_collection_disabled(self):
        """Test weather data collection when debugging is disabled."""
        # Arrange
        self.debugger.enabled = False
        
        # Act
        result = self.debugger.debug_weather_data_collection(42.15, 9.15, "Corte")
        
        # Assert
        assert result is None
    
    @patch('src.wetter.report_debug.analyze_weather_data')
    def test_debug_weather_analysis_enabled(self, mock_analyze):
        """Test weather analysis when debugging is enabled."""
        # Arrange
        mock_analysis = Mock()
        mock_analysis.max_rain_probability = 30.0
        mock_analysis.max_thunderstorm_probability = 25.0
        mock_analysis.max_precipitation = 5.0
        mock_analysis.max_wind_speed = 35.0
        mock_analysis.max_wind_gusts = 45.0
        mock_analysis.max_cloud_cover = 70.0
        mock_analysis.risk = 0.6
        mock_analysis.summary = "Test summary"
        mock_analysis.risks = []
        mock_analyze.return_value = mock_analysis
        
        weather_data = WeatherData(points=[
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=datetime.now(),
                temperature=25.0,
                feels_like=25.0,
                precipitation=3.0,
                wind_speed=30.0,
                cloud_cover=60.0,
                rain_probability=30.0,
                thunderstorm_probability=25.0
            )
        ])
        
        # Act
        result = self.debugger.debug_weather_analysis(weather_data, "Corte")
        
        # Assert
        assert result == mock_analysis
        mock_analyze.assert_called_once_with(weather_data, self.config)
    
    def test_debug_weather_analysis_disabled(self):
        """Test weather analysis when debugging is disabled."""
        # Arrange
        self.debugger.enabled = False
        weather_data = WeatherData(points=[])
        
        # Act
        result = self.debugger.debug_weather_analysis(weather_data, "Corte")
        
        # Assert
        assert result is None
    
    @patch('src.wetter.report_debug.compare_raw_data_with_report')
    def test_debug_report_comparison_enabled(self, mock_compare):
        """Test report comparison when debugging is enabled."""
        # Arrange
        mock_raw_data = Mock()
        mock_comparison = {"matches": 5, "issues": []}
        mock_compare.return_value = mock_comparison
        
        report_values = {
            "temperature": 25.0,
            "precipitation_probability": 30.0
        }
        
        # Act
        result = self.debugger.debug_report_comparison(
            mock_raw_data, report_values, "Corte"
        )
        
        # Assert
        assert result == mock_comparison
        mock_compare.assert_called_once_with(mock_raw_data, report_values, self.config)
    
    def test_debug_report_comparison_disabled(self):
        """Test report comparison when debugging is disabled."""
        # Arrange
        self.debugger.enabled = False
        mock_raw_data = Mock()
        report_values = {}
        
        # Act
        result = self.debugger.debug_report_comparison(
            mock_raw_data, report_values, "Corte"
        )
        
        # Assert
        assert result is None
    
    def test_debug_threshold_validation_enabled(self):
        """Test threshold validation when debugging is enabled."""
        # Arrange
        weather_data = WeatherData(points=[
            WeatherPoint(
                latitude=42.15,
                longitude=9.15,
                elevation=0.0,
                time=datetime.now(),
                temperature=25.0,
                feels_like=25.0,
                precipitation=3.0,  # Above threshold
                wind_speed=45.0,  # Above threshold
                cloud_cover=60.0,
                rain_probability=30.0,  # Above threshold
                thunderstorm_probability=25.0  # Above threshold
            )
        ])
        
        # Act
        result = self.debugger.debug_threshold_validation(weather_data, "Corte")
        
        # Assert
        assert result is not None
        assert result["location"] == "Corte"
        assert "thresholds" in result
        assert "crossings" in result
        assert len(result["crossings"]) > 0
        
        # Check that threshold crossings are detected
        crossings = result["crossings"][0]["crossings"]
        assert any("Rain probability 30.0%" in crossing for crossing in crossings)
        assert any("Thunderstorm probability 25.0%" in crossing for crossing in crossings)
        assert any("Precipitation amount 3.0mm" in crossing for crossing in crossings)
        assert any("Wind speed 45.0km/h" in crossing for crossing in crossings)
    
    def test_debug_threshold_validation_disabled(self):
        """Test threshold validation when debugging is disabled."""
        # Arrange
        self.debugger.enabled = False
        weather_data = WeatherData(points=[])
        
        # Act
        result = self.debugger.debug_threshold_validation(weather_data, "Corte")
        
        # Assert
        assert result is None


class TestReportDebugInfo:
    """Test ReportDebugInfo dataclass."""
    
    def test_report_debug_info_creation(self):
        """Test ReportDebugInfo creation with all fields."""
        # Arrange
        timestamp = datetime.now()
        raw_data = Mock()
        weather_analysis = Mock()
        report_values = {"temperature": 25.0}
        comparison_results = {"matches": 5}
        debug_files = ["file1.txt", "file2.json"]
        
        # Act
        debug_info = ReportDebugInfo(
            timestamp=timestamp,
            location_name="Corte",
            latitude=42.15,
            longitude=9.15,
            raw_data=raw_data,
            weather_analysis=weather_analysis,
            report_values=report_values,
            comparison_results=comparison_results,
            debug_files=debug_files
        )
        
        # Assert
        assert debug_info.timestamp == timestamp
        assert debug_info.location_name == "Corte"
        assert debug_info.latitude == 42.15
        assert debug_info.longitude == 9.15
        assert debug_info.raw_data == raw_data
        assert debug_info.weather_analysis == weather_analysis
        assert debug_info.report_values == report_values
        assert debug_info.comparison_results == comparison_results
        assert debug_info.debug_files == debug_files


class TestDebugSummaryGeneration:
    """Test debug summary generation."""
    
    def setup_method(self):
        """Initialize test debugger."""
        self.config = {
            "debug": {
                "enabled": True,
                "output_directory": "test_debug"
            }
        }
        self.debugger = ReportDebugger(self.config)
    
    def test_generate_debug_summary_with_all_data(self):
        """Test debug summary generation with complete data."""
        # Arrange
        raw_data = Mock()
        raw_data.time_points = [Mock(), Mock(), Mock()]  # 3 time points
        
        weather_analysis = Mock()
        weather_analysis.max_rain_probability = 30.0
        weather_analysis.max_thunderstorm_probability = 25.0
        
        comparison_results = {
            "issues": ["Issue 1", "Issue 2"]
        }
        
        debug_info = ReportDebugInfo(
            timestamp=datetime(2025, 7, 5, 14, 0, 0),
            location_name="Corte",
            latitude=42.15,
            longitude=9.15,
            raw_data=raw_data,
            weather_analysis=weather_analysis,
            report_values={"temperature": 25.0},
            comparison_results=comparison_results,
            debug_files=["file1.txt", "file2.json"]
        )
        
        # Act
        summary = self.debugger.generate_debug_summary(debug_info)
        
        # Assert
        assert "DEBUG SUMMARY" in summary
        assert "Location: Corte" in summary
        assert "Coordinates: 42.15, 9.15" in summary
        assert "Raw data points: 3" in summary
        assert "Analysis completed: Yes" in summary
        assert "Max rain probability: 30.0%" in summary
        assert "Max thunderstorm probability: 25.0%" in summary
        assert "Comparison issues: 2" in summary
        assert "Debug files generated: 2" in summary
    
    def test_generate_debug_summary_with_minimal_data(self):
        """Test debug summary generation with minimal data."""
        # Arrange
        debug_info = ReportDebugInfo(
            timestamp=datetime(2025, 7, 5, 14, 0, 0),
            location_name="Corte",
            latitude=42.15,
            longitude=9.15,
            raw_data=None,
            weather_analysis=None,
            report_values={},
            comparison_results=None,
            debug_files=[]
        )
        
        # Act
        summary = self.debugger.generate_debug_summary(debug_info)
        
        # Assert
        assert "DEBUG SUMMARY" in summary
        assert "Location: Corte" in summary
        assert "Coordinates: 42.15, 9.15" in summary
        # Debug: Print the actual summary to see what's in it
        print(f"Actual summary:\n{summary}")
        # The summary should contain basic location info
        assert "Timestamp: 2025-07-05 14:00:00" in summary
    
    def test_generate_debug_summary_disabled(self):
        """Test debug summary generation when debugging is disabled."""
        # Arrange
        self.debugger.enabled = False
        debug_info = ReportDebugInfo(
            timestamp=datetime.now(),
            location_name="Corte",
            latitude=42.15,
            longitude=9.15,
            raw_data=None,
            weather_analysis=None,
            report_values={},
            comparison_results=None,
            debug_files=[]
        )
        
        # Act
        summary = self.debugger.generate_debug_summary(debug_info)
        
        # Assert
        assert summary == ""


class TestCreateReportDebugger:
    """Test create_report_debugger function."""
    
    def test_create_report_debugger(self):
        """Test create_report_debugger function."""
        # Arrange
        config = {
            "debug": {
                "enabled": True,
                "output_directory": "test_debug"
            }
        }
        
        # Act
        debugger = create_report_debugger(config)
        
        # Assert
        assert isinstance(debugger, ReportDebugger)
        assert debugger.enabled is True
        assert debugger.output_directory == "test_debug" 