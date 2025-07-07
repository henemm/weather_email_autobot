"""
Tests for the central weather formatter.

These tests verify that the new central formatter produces correct output
according to the email_format.mdc specification for all report types.
"""

import pytest
from datetime import datetime, date
from src.weather.core.models import (
    AggregatedWeatherData, ReportType, VigilanceData, VigilanceLevel, ReportConfig
)
from src.weather.core.formatter import WeatherFormatter


class TestCentralFormatter:
    """Test the central weather formatter."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = ReportConfig()
        self.formatter = WeatherFormatter(self.config)
        
        # Sample weather data for testing
        self.sample_weather_data = AggregatedWeatherData(
            location_name="TestLocation",
            latitude=42.0,
            longitude=9.0,
            max_temperature=25.5,
            min_temperature=12.3,
            max_temperature_time="15:00",
            min_temperature_time="05:00",
            max_rain_probability=45.0,
            max_precipitation=2.1,
            rain_threshold_pct=25.0,
            rain_threshold_time="15:00",
            rain_max_time="16:00",
            precipitation_max_time="16:00",
            max_wind_speed=18.0,
            max_wind_gusts=32.0,
            wind_threshold_kmh=20.0,
            wind_threshold_time="13:00",
            wind_max_time="14:00",
            wind_gusts_max_time="14:00",
            max_thunderstorm_probability=65.0,
            thunderstorm_threshold_pct=35.0,
            thunderstorm_threshold_time="14:00",
            thunderstorm_max_time="15:00",
            tomorrow_max_thunderstorm_probability=75.0,
            tomorrow_thunderstorm_threshold_time="14:00",
            tomorrow_thunderstorm_max_time="15:00",
            day_after_tomorrow_max_thunderstorm_probability=80.0,
            day_after_tomorrow_thunderstorm_threshold_time="15:00",
            day_after_tomorrow_thunderstorm_max_time="16:00",
            target_date=date(2025, 7, 7),
            time_window="05:00-17:00",
            data_source="test",
            processed_at=datetime.now()
        )
        
        self.stage_names = {
            'today': 'SanPetru',
            'tomorrow': 'Vizzavona',
            'day_after_tomorrow': 'Corte'
        }
    
    def test_morning_report_format(self):
        """Test morning report formatting."""
        report_text = self.formatter.format_report_text(
            self.sample_weather_data,
            ReportType.MORNING,
            self.stage_names
        )
        
        # Verify all required components are present
        assert "SanPetru" in report_text
        assert "Gew." in report_text
        assert "Regen" in report_text
        assert "Hitze" in report_text
        assert "Wind" in report_text
        assert "Windböen" in report_text
        assert "Gew.+1" in report_text
        
        # Verify character limit
        assert len(report_text) <= 160
        
        # Verify format structure
        parts = report_text.split(" | ")
        assert len(parts) == 8  # 8 components for morning report
        
        # Verify specific formatting
        assert "Gew.35%@14(65%@15)" in report_text  # Thunderstorm with threshold and max
        assert "Regen25%@15(45%@16)" in report_text  # Rain with threshold and max
        assert "Regen2.1mm@16" in report_text  # Precipitation
        assert "Hitze25.5°C" in report_text  # Temperature
        assert "Wind18km/h" in report_text  # Wind
        assert "Windböen32km/h" in report_text  # Wind gusts
        assert "Gew.+1 75%@14" in report_text  # Thunderstorm next day
    
    def test_evening_report_format(self):
        """Test evening report formatting."""
        report_text = self.formatter.format_report_text(
            self.sample_weather_data,
            ReportType.EVENING,
            self.stage_names
        )
        
        # Verify all required components are present
        assert "Vizzavona→Corte" in report_text
        assert "Nacht" in report_text
        assert "Gew." in report_text
        assert "Regen" in report_text
        assert "Hitze" in report_text
        assert "Wind" in report_text
        assert "Windböen" in report_text
        assert "Gew.+1" in report_text
        
        # Verify character limit
        assert len(report_text) <= 160
        
        # Verify format structure
        parts = report_text.split(" | ")
        assert len(parts) == 9  # 9 components for evening report (includes night temp)
        
        # Verify specific formatting
        assert "Nacht12.3°C" in report_text  # Night temperature
        assert "Gew.35%@14(65%@15)" in report_text  # Thunderstorm
        assert "Regen25%@15(45%@16)" in report_text  # Rain
        assert "Regen2.1mm@16" in report_text  # Precipitation
        assert "Hitze25.5°C" in report_text  # Temperature
        assert "Wind18km/h" in report_text  # Wind
        assert "Windböen32km/h" in report_text  # Wind gusts
        assert "Gew.+1 80%@15" in report_text  # Thunderstorm day after tomorrow
    
    def test_update_report_format(self):
        """Test update report formatting."""
        report_text = self.formatter.format_report_text(
            self.sample_weather_data,
            ReportType.UPDATE,
            self.stage_names
        )
        
        # Verify all required components are present
        assert "SanPetru" in report_text
        assert "Update:" in report_text
        assert "Gew." in report_text
        assert "Regen" in report_text
        assert "Hitze" in report_text
        assert "Wind" in report_text
        assert "Windböen" in report_text
        assert "Gew.+1" in report_text
        
        # Verify character limit
        assert len(report_text) <= 160
        
        # Verify format structure
        parts = report_text.split(" | ")
        assert len(parts) == 9  # 9 components for update report (includes "Update:")
        
        # Verify "Update:" prefix is present
        assert "Update:" in parts
    
    def test_null_value_handling(self):
        """Test handling of null values."""
        null_weather_data = AggregatedWeatherData(
            location_name="TestLocation",
            latitude=42.0,
            longitude=9.0,
            max_temperature=None,
            min_temperature=None,
            max_rain_probability=None,
            max_precipitation=None,
            max_wind_speed=None,
            max_wind_gusts=None,
            max_thunderstorm_probability=None,
            target_date=date(2025, 7, 7),
            data_source="test"
        )
        
        report_text = self.formatter.format_report_text(
            null_weather_data,
            ReportType.MORNING,
            self.stage_names
        )
        
        # Verify null values are handled correctly
        assert "Hitze -" in report_text
        assert "Regen -" in report_text
        assert "Regen -mm" in report_text
        assert "Wind -" in report_text
        assert "Windböen -" in report_text
        assert "Gew. -" in report_text
        assert "Gew.+1 -" in report_text
        
        # Verify character limit
        assert len(report_text) <= 160
    
    def test_stage_name_shortening(self):
        """Test stage name shortening to 10 characters."""
        long_stage_names = {
            'today': 'VeryLongStageNameThatExceedsTenCharacters',
            'tomorrow': 'AnotherVeryLongStageName',
            'day_after_tomorrow': 'ThirdVeryLongStageName'
        }
        
        report_text = self.formatter.format_report_text(
            self.sample_weather_data,
            ReportType.MORNING,
            long_stage_names
        )
        
        # Verify stage name is shortened
        parts = report_text.split(" | ")
        stage_name = parts[0]
        assert len(stage_name) <= 10
        
        # Test evening report with long names
        evening_text = self.formatter.format_report_text(
            self.sample_weather_data,
            ReportType.EVENING,
            long_stage_names
        )
        
        evening_parts = evening_text.split(" | ")
        stage_names_part = evening_parts[0]  # "Start→End"
        assert "→" in stage_names_part
        # Each part should be <= 10 characters
        start_end = stage_names_part.split("→")
        assert len(start_end[0]) <= 10
        assert len(start_end[1]) <= 10
    
    def test_email_subject_format(self):
        """Test email subject formatting."""
        # Test without vigilance data
        subject = self.formatter.format_email_subject(
            ReportType.MORNING,
            "SanPetru"
        )
        assert subject == "GR20 Wetter SanPetru: (morning)"
        
        # Test with vigilance data
        vigilance_data = VigilanceData(
            level=VigilanceLevel.ORANGE,
            phenomenon="thunderstorm",
            description="Gewitter"
        )
        
        subject_with_vigilance = self.formatter.format_email_subject(
            ReportType.EVENING,
            "Vizzavona",
            vigilance_data
        )
        assert subject_with_vigilance == "GR20 Wetter Vizzavona: HIGH - Gewitter (evening)"
        
        # Test with different vigilance levels
        red_vigilance = VigilanceData(
            level=VigilanceLevel.RED,
            phenomenon="forest_fire",
            description="Waldbrand"
        )
        
        subject_red = self.formatter.format_email_subject(
            ReportType.UPDATE,
            "Corte",
            red_vigilance
        )
        assert subject_red == "GR20 Wetter Corte: MAX - Waldbrand (update)"
    
    def test_character_limit_compliance(self):
        """Test that reports comply with 160 character limit."""
        # Create data that would generate a very long report
        long_weather_data = AggregatedWeatherData(
            location_name="VeryLongLocationName",
            latitude=42.0,
            longitude=9.0,
            max_temperature=99.9,
            min_temperature=0.1,
            max_temperature_time="15:00",
            min_temperature_time="05:00",
            max_rain_probability=99.9,
            max_precipitation=99.9,
            rain_threshold_pct=99.9,
            rain_threshold_time="15:00",
            rain_max_time="16:00",
            precipitation_max_time="16:00",
            max_wind_speed=999.0,
            max_wind_gusts=999.0,
            wind_threshold_kmh=999.0,
            wind_threshold_time="13:00",
            wind_max_time="14:00",
            wind_gusts_max_time="14:00",
            max_thunderstorm_probability=99.9,
            thunderstorm_threshold_pct=99.9,
            thunderstorm_threshold_time="14:00",
            thunderstorm_max_time="15:00",
            tomorrow_max_thunderstorm_probability=99.9,
            tomorrow_thunderstorm_threshold_time="14:00",
            tomorrow_thunderstorm_max_time="15:00",
            day_after_tomorrow_max_thunderstorm_probability=99.9,
            day_after_tomorrow_thunderstorm_threshold_time="15:00",
            day_after_tomorrow_thunderstorm_max_time="16:00",
            target_date=date(2025, 7, 7),
            data_source="test"
        )
        
        long_stage_names = {
            'today': 'VeryLongStageName',
            'tomorrow': 'AnotherVeryLongStageName',
            'day_after_tomorrow': 'ThirdVeryLongStageName'
        }
        
        # Test all report types
        for report_type in [ReportType.MORNING, ReportType.EVENING, ReportType.UPDATE]:
            report_text = self.formatter.format_report_text(
                long_weather_data,
                report_type,
                long_stage_names
            )
            
            assert len(report_text) <= 160, f"Report type {report_type.value} exceeds 160 characters: {len(report_text)}"
    
    def test_formatting_consistency(self):
        """Test that formatting is consistent across report types."""
        # Test that the same weather data produces consistent formatting for similar components
        morning_text = self.formatter.format_report_text(
            self.sample_weather_data,
            ReportType.MORNING,
            self.stage_names
        )
        
        update_text = self.formatter.format_report_text(
            self.sample_weather_data,
            ReportType.UPDATE,
            self.stage_names
        )
        
        # Extract weather components (excluding stage name and "Update:" prefix)
        morning_parts = morning_text.split(" | ")[1:]  # Skip stage name
        update_parts = update_text.split(" | ")[2:]  # Skip stage name and "Update:"
        
        # Weather components should be identical
        assert morning_parts == update_parts
    
    def test_threshold_vs_max_formatting(self):
        """Test threshold vs maximum value formatting."""
        # Test case where threshold equals maximum
        equal_data = AggregatedWeatherData(
            location_name="TestLocation",
            latitude=42.0,
            longitude=9.0,
            max_rain_probability=50.0,
            rain_threshold_pct=50.0,
            rain_threshold_time="15:00",
            rain_max_time="15:00",
            target_date=date(2025, 7, 7),
            data_source="test"
        )
        
        report_text = self.formatter.format_report_text(
            equal_data,
            ReportType.MORNING,
            self.stage_names
        )
        
        # When threshold equals maximum, should show only maximum
        assert "Regen50%@15" in report_text
        assert "Regen50%@15(50%@15)" not in report_text  # Should not show both
        
        # Test case where threshold is different from maximum
        different_data = AggregatedWeatherData(
            location_name="TestLocation",
            latitude=42.0,
            longitude=9.0,
            max_rain_probability=80.0,
            rain_threshold_pct=25.0,
            rain_threshold_time="15:00",
            rain_max_time="16:00",
            target_date=date(2025, 7, 7),
            data_source="test"
        )
        
        report_text = self.formatter.format_report_text(
            different_data,
            ReportType.MORNING,
            self.stage_names
        )
        
        # When threshold differs from maximum, should show both
        assert "Regen25%@15(80%@16)" in report_text 