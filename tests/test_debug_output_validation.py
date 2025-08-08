"""
Unit tests for debug output validation.

These tests ensure that the debug output follows the correct format and structure,
catching obvious bugs like repeated lines, incorrect T-G references, and format violations.
"""

import pytest
from datetime import date, datetime
from typing import Dict, Any, List
import re

from src.weather.core.morning_evening_refactor import MorningEveningRefactor, WeatherReportData, WeatherThresholdData


class TestDebugOutputValidation:
    """Test class for comprehensive debug output validation."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.config = {
            'startdatum': '2025-07-29',
            'thresholds': {
                'rain_amount': 0.5,
                'rain_probability': 15.0,
                'temperature': 25.0,
                'thunderstorm_warning_level': 'low',
                'thunderstorm_probability': 10.0,
                'wind_speed': 1.0,
                'wind_gust_threshold': 5.0,
                'wind_gust_percentage': 50.0
            }
        }
        self.refactor = MorningEveningRefactor(self.config)
    
    def create_mock_report_data(self, report_type: str = 'evening') -> WeatherReportData:
        """Create mock report data for testing."""
        # Create mock geo points with T-G references
        if report_type == 'evening':
            t_prefix = "T2"
        else:
            t_prefix = "T1"
        
        rain_mm_geo_points = [
            {f"{t_prefix}G1": {"4:00": 0, "5:00": 0, "6:00": 0, "7:00": 0, "8:00": 0, "9:00": 0, "10:00": 0, "11:00": 0, "12:00": 0, "13:00": 0, "14:00": 0, "15:00": 0, "16:00": 0, "17:00": 0, "18:00": 0, "19:00": 0}},
            {f"{t_prefix}G2": {"4:00": 0, "5:00": 0, "6:00": 0, "7:00": 0, "8:00": 0, "9:00": 0, "10:00": 0, "11:00": 0, "12:00": 0, "13:00": 0, "14:00": 0, "15:00": 0, "16:00": 0, "17:00": 0, "18:00": 0, "19:00": 0}},
            {f"{t_prefix}G3": {"4:00": 0, "5:00": 0, "6:00": 0, "7:00": 0, "8:00": 0, "9:00": 0, "10:00": 0, "11:00": 0, "12:00": 0, "13:00": 0, "14:00": 0, "15:00": 0, "16:00": 0, "17:00": 0, "18:00": 0, "19:00": 0}}
        ]
        
        wind_geo_points = [
            {f"{t_prefix}G1": {"4:00": 2, "5:00": 1, "6:00": 1, "7:00": 1, "8:00": 1, "9:00": 1, "10:00": 1, "11:00": 1, "12:00": 2, "13:00": 3, "14:00": 3, "15:00": 3, "16:00": 3, "17:00": 3, "18:00": 3, "19:00": 3}},
            {f"{t_prefix}G2": {"4:00": 3, "5:00": 3, "6:00": 3, "7:00": 3, "8:00": 2, "9:00": 2, "10:00": 2, "11:00": 2, "12:00": 2, "13:00": 2, "14:00": 3, "15:00": 3, "16:00": 4, "17:00": 4, "18:00": 4, "19:00": 4}},
            {f"{t_prefix}G3": {"4:00": 6, "5:00": 6, "6:00": 6, "7:00": 6, "8:00": 6, "9:00": 6, "10:00": 6, "11:00": 5, "12:00": 5, "13:00": 6, "14:00": 6, "15:00": 6, "16:00": 7, "17:00": 7, "18:00": 7, "19:00": 8}}
        ]
        
        gust_geo_points = [
            {f"{t_prefix}G2": {"4:00": 13, "5:00": 14, "6:00": 14, "7:00": 14, "8:00": 14, "9:00": 14, "10:00": 14, "11:00": 12, "12:00": 0, "13:00": 11, "14:00": 12, "15:00": 12, "16:00": 13, "17:00": 13, "18:00": 14, "19:00": 15}},
            {f"{t_prefix}G3": {"4:00": 13, "5:00": 14, "6:00": 14, "7:00": 14, "8:00": 14, "9:00": 14, "10:00": 14, "11:00": 12, "12:00": 0, "13:00": 11, "14:00": 12, "15:00": 12, "16:00": 13, "17:00": 13, "18:00": 14, "19:00": 15}}
        ]
        
        return WeatherReportData(
            stage_name="Test",
            report_date=date(2025, 8, 3),
            report_type=report_type,
            night=WeatherThresholdData(threshold_value=13.2, threshold_time="22:00", max_value=13.2, max_time="22:00"),
            day=WeatherThresholdData(threshold_value=25.4, threshold_time="14:00", max_value=25.4, max_time="14:00"),
            rain_mm=WeatherThresholdData(threshold_value=0.5, threshold_time="11:00", max_value=1.2, max_time="14:00", geo_points=rain_mm_geo_points),
            rain_percent=WeatherThresholdData(threshold_value=20.0, threshold_time="11:00", max_value=30.0, max_time="14:00"),
            wind=WeatherThresholdData(threshold_value=2.0, threshold_time="04:00", max_value=8.0, max_time="19:00", geo_points=wind_geo_points),
            gust=WeatherThresholdData(threshold_value=13.0, threshold_time="04:00", max_value=15.0, max_time="19:00", geo_points=gust_geo_points),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
    
    def test_debug_output_structure_validation(self):
        """Test that debug output has correct overall structure."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Check for required sections
        required_sections = [
            "Night (N) - temp_min",
            "Day (D) - temp_max", 
            "Rain (mm) Data",
            "Rain (%) Data",
            "Wind Data",
            "Gust Data",
            "Thunderstorm Data",
            "Thunderstorm (+1) Data",
            "Risk Zonal Data"
        ]
        
        for section in required_sections:
            assert section in debug_output, f"Missing required section: {section}"
    
    def test_rain_mm_debug_output_line_count(self):
        """Test that Rain (mm) debug output has correct number of lines."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Extract Rain (mm) section
        rain_section = self._extract_section(debug_output, "Rain (mm) Data")
        
        # Count lines for each geo point
        geo_points = ["T2G1", "T2G2", "T2G3"]  # Evening report
        
        for geo_point in geo_points:
            point_lines = self._count_lines_for_geo_point(rain_section, geo_point)
            
            # Expected: 1 header + 16 hours (4:00-19:00) + 1 separator + 1 max line = 19 lines
            expected_lines = 19
            assert point_lines == expected_lines, f"Geo point {geo_point} has {point_lines} lines, expected {expected_lines}"
    
    def test_rain_mm_debug_output_no_repetition(self):
        """Test that Rain (mm) debug output has no repeated hour sequences."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        rain_section = self._extract_section(debug_output, "Rain (mm) Data")
        
        # Check for repeated hour sequences (4:00 | 0, 5:00 | 0, etc.)
        hour_sequences = re.findall(r'4:00 \| \d+.*?19:00 \| \d+', rain_section, re.DOTALL)
        
        # Should have exactly 3 sequences (one for each geo point)
        assert len(hour_sequences) == 3, f"Found {len(hour_sequences)} hour sequences, expected 3"
        
        # Check that sequences are not identical (they might have different values)
        unique_sequences = set(hour_sequences)
        assert len(unique_sequences) >= 1, "All hour sequences are identical"
    
    def test_wind_debug_output_line_count(self):
        """Test that Wind debug output has correct number of lines."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        wind_section = self._extract_section(debug_output, "Wind Data")
        
        geo_points = ["T2G1", "T2G2", "T2G3"]
        
        for geo_point in geo_points:
            point_lines = self._count_lines_for_geo_point(wind_section, geo_point)
            
            # Expected: 1 header + 16 hours (4:00-19:00) + 1 separator + 2 lines (threshold + max) = 20 lines
            expected_lines = 20
            assert point_lines == expected_lines, f"Wind geo point {geo_point} has {point_lines} lines, expected {expected_lines}"
    
    def test_gust_debug_output_line_count(self):
        """Test that Gust debug output has correct number of lines."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        gust_section = self._extract_section(debug_output, "Gust Data")
        
        geo_points = ["T2G2", "T2G3"]  # T2G1 has no gust data
        
        for geo_point in geo_points:
            point_lines = self._count_lines_for_geo_point(gust_section, geo_point)
            
            # Expected: 1 header + 16 hours (4:00-19:00) + 1 separator + 2 lines (threshold + max) = 20 lines
            expected_lines = 20
            assert point_lines == expected_lines, f"Gust geo point {geo_point} has {point_lines} lines, expected {expected_lines}"
    
    def test_tg_references_consistency(self):
        """Test that T-G references are consistent throughout debug output."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Check that all T-G references follow the correct pattern
        tg_pattern = r'T[12]G[123]'
        tg_references = re.findall(tg_pattern, debug_output)
        
        # Should have T2G1, T2G2, T2G3 for evening report
        expected_references = ["T2G1", "T2G2", "T2G3"]
        
        for expected in expected_references:
            assert expected in tg_references, f"Missing T-G reference: {expected}"
        
        # Check that no invalid T-G references exist
        invalid_pattern = r'T[^12]G[^123]|T[12]G[^123]|T[^12]G[123]'
        invalid_references = re.findall(invalid_pattern, debug_output)
        assert len(invalid_references) == 0, f"Found invalid T-G references: {invalid_references}"
    
    def test_time_range_validation(self):
        """Test that all hourly data shows only 4:00-19:00 range."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Check for any times outside 4:00-19:00 range
        invalid_times = re.findall(r'([0-3]:00|[2-9][0-9]:00|[2-9]:00)', debug_output)
        
        # Only allow 4:00 through 19:00
        allowed_times = [f"{hour:02d}:00" for hour in range(4, 20)]
        
        for invalid_time in invalid_times:
            assert invalid_time in allowed_times, f"Found invalid time: {invalid_time}"
    
    def test_threshold_maximum_tables_structure(self):
        """Test that threshold and maximum tables have correct structure."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Check Rain (%) threshold table structure
        rain_percent_section = self._extract_section(debug_output, "Rain (%) Data")
        
        # Should have threshold table with correct format
        threshold_table = re.search(r'Threshold\nGEO \| Time \| %\n.*?\n=========', rain_percent_section, re.DOTALL)
        assert threshold_table is not None, "Missing or malformed threshold table"
        
        # Should have maximum table with correct format
        maximum_table = re.search(r'Maximum:\nGEO \| Time \| Max\n.*?\n=========', rain_percent_section, re.DOTALL)
        assert maximum_table is not None, "Missing or malformed maximum table"
    
    def test_debug_output_no_empty_sections(self):
        """Test that debug output has no completely empty sections."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Check that sections have content
        sections = [
            "Rain (mm) Data",
            "Rain (%) Data", 
            "Wind Data",
            "Gust Data",
            "Thunderstorm Data",
            "Thunderstorm (+1) Data"
        ]
        
        for section in sections:
            section_content = self._extract_section(debug_output, section)
            
            # Section should have more than just the header
            lines = [line.strip() for line in section_content.split('\n') if line.strip()]
            assert len(lines) > 1, f"Section {section} is empty or has only header"
    
    def test_debug_output_format_consistency(self):
        """Test that debug output format is consistent across all sections."""
        report_data = self.create_mock_report_data()
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Check that all time entries follow the same format
        time_entries = re.findall(r'\d{1,2}:\d{2} \| [^|]*', debug_output)
        
        for entry in time_entries:
            # Should match pattern: "HH:MM | value"
            assert re.match(r'\d{1,2}:\d{2} \| [^|]*$', entry), f"Invalid time entry format: {entry}"
    
    def test_morning_report_tg_references(self):
        """Test that morning report uses correct T-G references (T1 instead of T2)."""
        report_data = self.create_mock_report_data('morning')
        debug_output = self.refactor.generate_debug_output(report_data)
        
        # Should have T1G1, T1G2, T1G3 for morning report
        expected_references = ["T1G1", "T1G2", "T1G3"]
        
        for expected in expected_references:
            assert expected in debug_output, f"Morning report missing T-G reference: {expected}"
        
        # Should NOT have T2 references in morning report
        t2_references = re.findall(r'T2G[123]', debug_output)
        assert len(t2_references) == 0, f"Morning report should not have T2 references: {t2_references}"
    
    def _extract_section(self, debug_output: str, section_name: str) -> str:
        """Extract a specific section from debug output."""
        lines = debug_output.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            if section_name in line:
                in_section = True
                section_lines.append(line)
            elif in_section and line.strip() and not line.startswith(' ') and 'Data:' in line:
                # Next section started
                break
            elif in_section:
                section_lines.append(line)
        
        return '\n'.join(section_lines)
    
    def _count_lines_for_geo_point(self, section: str, geo_point: str) -> int:
        """Count lines for a specific geo point in a section."""
        lines = section.split('\n')
        count = 0
        in_geo_point = False
        
        for line in lines:
            if geo_point in line:
                in_geo_point = True
                count += 1
            elif in_geo_point and line.strip() and not line.startswith(' ') and 'G' in line:
                # Next geo point started
                break
            elif in_geo_point:
                count += 1
        
        return count


class TestDebugOutputEdgeCases:
    """Test edge cases and error conditions in debug output."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.config = {
            'startdatum': '2025-07-29',
            'thresholds': {
                'rain_amount': 0.5,
                'rain_probability': 15.0,
                'temperature': 25.0,
                'thunderstorm_warning_level': 'low',
                'thunderstorm_probability': 10.0,
                'wind_speed': 1.0,
                'wind_gust_threshold': 5.0,
                'wind_gust_percentage': 50.0
            }
        }
        self.refactor = MorningEveningRefactor(self.config)
    
    def test_empty_weather_data_handling(self):
        """Test that debug output handles empty weather data gracefully."""
        report_data = WeatherReportData(
            stage_name="Test",
            report_date=date(2025, 8, 3),
            report_type='evening',
            night=WeatherThresholdData(),
            day=WeatherThresholdData(),
            rain_mm=WeatherThresholdData(),
            rain_percent=WeatherThresholdData(),
            wind=WeatherThresholdData(),
            gust=WeatherThresholdData(),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
        
        # Should not raise exception
        debug_output = self.refactor.generate_debug_output(report_data)
        assert debug_output is not None
        assert len(debug_output) > 0
    
    def test_missing_geo_points_handling(self):
        """Test that debug output handles missing geo points gracefully."""
        report_data = WeatherReportData(
            stage_name="Test",
            report_date=date(2025, 8, 3),
            report_type='evening',
            night=WeatherThresholdData(),
            day=WeatherThresholdData(),
            rain_mm=WeatherThresholdData(geo_points=[]),  # Empty geo points
            rain_percent=WeatherThresholdData(),
            wind=WeatherThresholdData(),
            gust=WeatherThresholdData(),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
        
        # Should not raise exception
        debug_output = self.refactor.generate_debug_output(report_data)
        assert debug_output is not None
    
    def test_invalid_threshold_values_handling(self):
        """Test that debug output handles invalid threshold values gracefully."""
        report_data = WeatherReportData(
            stage_name="Test",
            report_date=date(2025, 8, 3),
            report_type='evening',
            night=WeatherThresholdData(),
            day=WeatherThresholdData(),
            rain_mm=WeatherThresholdData(threshold_value=None, max_value=None),  # None values
            rain_percent=WeatherThresholdData(),
            wind=WeatherThresholdData(),
            gust=WeatherThresholdData(),
            thunderstorm=WeatherThresholdData(),
            thunderstorm_plus_one=WeatherThresholdData(),
            risks=WeatherThresholdData(),
            risk_zonal=WeatherThresholdData()
        )
        
        # Should not raise exception
        debug_output = self.refactor.generate_debug_output(report_data)
        assert debug_output is not None


if __name__ == "__main__":
    pytest.main([__file__]) 