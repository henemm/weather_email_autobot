#!/usr/bin/env python3
"""
Test for debug output consistency issues in MorningEveningRefactor.
Tests the specific problems identified by the user.
"""

import pytest
import re
from datetime import datetime
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.config.config_loader import load_config


class TestDebugOutputConsistency:
    """Test class for debug output consistency issues."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = load_config()
        self.processor = MorningEveningRefactor(self.config)
        
    def test_rain_mm_missing_threshold_summary(self):
        """Test that Rain (mm) section has threshold summary at end of each GEO point."""
        stage_name = "Test-Corsica"
        report_type = "morning"
        target_date = datetime.now().strftime('%Y-%m-%d')
        
        result_output, debug_output = self.processor.generate_report(stage_name, report_type, target_date)
        
        # Check for Rain (mm) section
        rain_section = self._extract_section(debug_output, "RAIN (R)")
        assert rain_section, "Rain (R) section not found"
        
        # Check each GEO point has threshold summary
        geo_points = self._extract_geo_points(rain_section)
        for geo_point in geo_points:
            # Should have threshold summary like "17:00 | 2.5 (Threshold)"
            threshold_pattern = r'\d{1,2}:\d{2} \| \d+\.?\d* \(Threshold\)'
            assert re.search(threshold_pattern, geo_point), f"Missing threshold summary in {geo_point[:50]}..."
            
    def test_rain_mm_missing_global_summary_table(self):
        """Test that Rain (mm) section has global summary table for threshold and maximum."""
        stage_name = "Test-Corsica"
        report_type = "morning"
        target_date = datetime.now().strftime('%Y-%m-%d')
        
        result_output, debug_output = self.processor.generate_report(stage_name, report_type, target_date)
        
        rain_section = self._extract_section(debug_output, "RAIN (R)")
        assert rain_section, "Rain (R) section not found"
        
        # Should have global summary tables
        assert "Threshold" in rain_section, "Missing global threshold table"
        assert "Maximum:" in rain_section, "Missing global maximum table"
        
        # Check threshold table format
        threshold_table = self._extract_table(rain_section, "Threshold")
        assert threshold_table, "Threshold table not found"
        assert "GEO | Time | mm" in threshold_table, "Threshold table missing header"
        
        # Check maximum table format
        maximum_table = self._extract_table(rain_section, "Maximum:")
        assert maximum_table, "Maximum table not found"
        assert "GEO | Time | Max" in maximum_table, "Maximum table missing header"
        
    def test_rain_percent_missing_threshold_summary(self):
        """Test that Rain (%) section has threshold summary (not just maximum)."""
        stage_name = "Test-Corsica"
        report_type = "morning"
        target_date = datetime.now().strftime('%Y-%m-%d')
        
        result_output, debug_output = self.processor.generate_report(stage_name, report_type, target_date)
        
        rain_percent_section = self._extract_section(debug_output, "PRAIN (PR)")
        assert rain_percent_section, "PRAIN (PR) section not found"
        
        # Check each GEO point has both threshold and maximum
        geo_points = self._extract_geo_points(rain_percent_section)
        for geo_point in geo_points:
            # Should have both threshold and maximum
            threshold_pattern = r'\d{1,2}:\d{2} \| \d+\.?\d*% \(Threshold\)'
            maximum_pattern = r'\d{1,2}:\d{2} \| \d+\.?\d*% \(Max\)'
            
            assert re.search(threshold_pattern, geo_point), f"Missing threshold in {geo_point[:50]}..."
            assert re.search(maximum_pattern, geo_point), f"Missing maximum in {geo_point[:50]}..."
            
    def test_rain_percent_global_threshold_table(self):
        """Test that Rain (%) section has global threshold table."""
        stage_name = "Test-Corsica"
        report_type = "morning"
        target_date = datetime.now().strftime('%Y-%m-%d')
        
        result_output, debug_output = self.processor.generate_report(stage_name, report_type, target_date)
        
        rain_percent_section = self._extract_section(debug_output, "PRAIN (PR)")
        assert rain_percent_section, "PRAIN (PR) section not found"
        
        # Should have global threshold table
        threshold_table = self._extract_table(rain_percent_section, "Threshold")
        assert threshold_table, "Global threshold table missing"
        assert "GEO | Time | %" in threshold_table, "Threshold table missing correct header"
        
    def test_risks_section_missing_summaries(self):
        """Test that Risks section has summaries for each GEO point and global summary."""
        stage_name = "Test-Corsica"
        report_type = "morning"
        target_date = datetime.now().strftime('%Y-%m-%d')
        
        result_output, debug_output = self.processor.generate_report(stage_name, report_type, target_date)
        
        risks_section = self._extract_section(debug_output, "RISKS (HR/TH)")
        assert risks_section, "RISKS (HR/TH) section not found"
        
        # Check each GEO point has summary
        geo_points = self._extract_geo_points(risks_section)
        for geo_point in geo_points:
            # Should have summary line with maximum values
            summary_pattern = r'=========\n.*\(Max\)'
            assert re.search(summary_pattern, geo_point), f"Missing summary in {geo_point[:50]}..."
            
        # Should have global summary table
        assert "Maximum HRain:" in risks_section, "Missing global HRain summary"
        assert "Maximum Thunder:" in risks_section, "Missing global Thunder summary"
        
    def test_wind_calculation_not_sum(self):
        """Test that Wind values are not sums but actual wind speeds."""
        stage_name = "Test-Corsica"
        report_type = "morning"
        target_date = datetime.now().strftime('%Y-%m-%d')
        
        result_output, debug_output = self.processor.generate_report(stage_name, report_type, target_date)
        
        # Extract wind values from result output
        wind_match = re.search(r'W(\d+\.?\d*)@(\d+)\((\d+\.?\d*)@(\d+)\)', result_output)
        assert wind_match, "Wind pattern not found in result output"
        
        threshold_value = float(wind_match.group(1))
        max_value = float(wind_match.group(3))
        
        # Values should be reasonable wind speeds (not sums)
        assert threshold_value <= 50, f"Wind threshold {threshold_value} seems too high (sum?)"
        assert max_value <= 50, f"Wind maximum {max_value} seems too high (sum?)"
        
        # Check debug output for individual wind values
        wind_section = self._extract_section(debug_output, "WIND (W)")
        assert wind_section, "WIND (W) section not found"
        
        # Extract individual wind values
        wind_values = re.findall(r'\d{1,2}:\d{2} \| (\d+)', wind_section)
        wind_values = [int(v) for v in wind_values if v.isdigit()]
        
        # Individual values should be reasonable
        for value in wind_values:
            assert value <= 30, f"Individual wind value {value} seems too high"
            
    def test_consistency_between_runs(self):
        """Test that multiple runs produce consistent output."""
        stage_name = "Test-Corsica"
        report_type = "morning"
        target_date = datetime.now().strftime('%Y-%m-%d')
        
        # Run twice
        result1, debug1 = self.processor.generate_report(stage_name, report_type, target_date)
        result2, debug2 = self.processor.generate_report(stage_name, report_type, target_date)
        
        # Results should be identical
        assert result1 == result2, "Result output inconsistent between runs"
        assert debug1 == debug2, "Debug output inconsistent between runs"
        
    def _extract_section(self, debug_output, section_name):
        """Extract a specific section from debug output."""
        pattern = rf'####### {section_name} #######\n(.*?)(?=#######|$)'
        match = re.search(pattern, debug_output, re.DOTALL)
        return match.group(1) if match else None
        
    def _extract_geo_points(self, section):
        """Extract individual GEO point data from a section."""
        pattern = r'(T\d+G\d+\n.*?=========\n.*?)(?=T\d+G\d+\n|$)'
        matches = re.findall(pattern, section, re.DOTALL)
        return matches
        
    def _extract_table(self, section, table_name):
        """Extract a specific table from a section."""
        pattern = rf'{table_name}\n(.*?)(?=\n\n|\n[A-Z]|$)'
        match = re.search(pattern, section, re.DOTALL)
        return match.group(1) if match else None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 