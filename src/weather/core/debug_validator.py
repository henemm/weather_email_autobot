"""
Automatic debug output validator.

This module provides functions to validate debug output and catch obvious bugs
before they reach production. It should be run before any commit.
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import date


class DebugOutputValidator:
    """Validator for debug output to catch obvious bugs."""
    
    def __init__(self):
        """Initialize the validator."""
        self.errors = []
        self.warnings = []
    
    def validate_debug_output(self, debug_output: str, report_type: str = 'evening') -> Tuple[bool, List[str]]:
        """
        Validate debug output and return validation result.
        
        Args:
            debug_output: The debug output string to validate
            report_type: 'morning' or 'evening'
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors = []
        self.warnings = []
        
        # Run all validation checks
        self._validate_structure(debug_output)
        self._validate_line_counts(debug_output)
        self._validate_no_repetitions(debug_output)
        self._validate_tg_references(debug_output, report_type)
        self._validate_time_ranges(debug_output)
        self._validate_format_consistency(debug_output)
        self._validate_threshold_tables(debug_output)
        
        return len(self.errors) == 0, self.errors + self.warnings
    
    def _validate_structure(self, debug_output: str):
        """Validate that debug output has correct overall structure."""
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
            if section not in debug_output:
                self.errors.append(f"Missing required section: {section}")
    
    def _validate_line_counts(self, debug_output: str):
        """Validate that each section has correct number of lines."""
        sections_to_check = [
            ("Rain (mm) Data", ["T2G1", "T2G2", "T2G3"], 19),  # 1 header + 16 hours + 1 separator + 1 max
            ("Wind Data", ["T2G1", "T2G2", "T2G3"], 20),       # 1 header + 16 hours + 1 separator + 2 lines (threshold + max)
            ("Gust Data", ["T2G2", "T2G3"], 20),               # T2G1 has no gust data
        ]
        
        for section_name, geo_points, expected_lines in sections_to_check:
            section = self._extract_section(debug_output, section_name)
            if not section:
                continue
                
            for geo_point in geo_points:
                point_lines = self._count_lines_for_geo_point(section, geo_point)
                if point_lines != expected_lines:
                    self.errors.append(
                        f"Section {section_name} geo point {geo_point} has {point_lines} lines, expected {expected_lines}"
                    )
    
    def _validate_no_repetitions(self, debug_output: str):
        """Validate that there are no repeated hour sequences."""
        # Check Rain (mm) for repeated sequences
        rain_section = self._extract_section(debug_output, "Rain (mm) Data")
        if rain_section:
            hour_sequences = re.findall(r'4:00 \| \d+.*?19:00 \| \d+', rain_section, re.DOTALL)
            
            # Should have exactly 3 sequences (one for each geo point)
            if len(hour_sequences) != 3:
                self.errors.append(
                    f"Rain (mm) section has {len(hour_sequences)} hour sequences, expected 3"
                )
            
            # Check for excessive repetitions (more than 3 sequences)
            if len(hour_sequences) > 3:
                self.errors.append(
                    f"Rain (mm) section has excessive repetitions: {len(hour_sequences)} sequences found"
                )
    
    def _validate_tg_references(self, debug_output: str, report_type: str):
        """Validate that T-G references are correct for the report type."""
        if report_type == 'evening':
            expected_references = ["T2G1", "T2G2", "T2G3"]
            invalid_references = ["T1G1", "T1G2", "T1G3"]
        else:  # morning
            expected_references = ["T1G1", "T1G2", "T1G3"]
            invalid_references = ["T2G1", "T2G2", "T2G3"]
        
        # Check for missing expected references
        for expected in expected_references:
            if expected not in debug_output:
                self.errors.append(f"Missing T-G reference: {expected}")
        
        # Check for invalid references
        for invalid in invalid_references:
            if invalid in debug_output:
                self.errors.append(f"Invalid T-G reference for {report_type} report: {invalid}")
        
        # Check for malformed T-G references
        invalid_pattern = r'T[^12]G[^123]|T[12]G[^123]|T[^12]G[123]'
        malformed_references = re.findall(invalid_pattern, debug_output)
        if malformed_references:
            self.errors.append(f"Found malformed T-G references: {malformed_references}")
    
    def _validate_time_ranges(self, debug_output: str):
        """Validate that all times are within 4:00-19:00 range."""
        # Find all time entries
        time_entries = re.findall(r'(\d{1,2}):00 \|', debug_output)
        
        allowed_hours = set(range(4, 20))  # 4:00 to 19:00
        
        for time_str in time_entries:
            try:
                hour = int(time_str)
                if hour not in allowed_hours:
                    self.errors.append(f"Invalid time found: {hour}:00 (must be 4:00-19:00)")
            except ValueError:
                self.errors.append(f"Malformed time entry: {time_str}")
    
    def _validate_format_consistency(self, debug_output: str):
        """Validate that all time entries follow consistent format."""
        time_entries = re.findall(r'\d{1,2}:\d{2} \| [^|]*', debug_output)
        
        for entry in time_entries:
            if not re.match(r'\d{1,2}:\d{2} \| [^|]*$', entry):
                self.errors.append(f"Invalid time entry format: {entry}")
    
    def _validate_threshold_tables(self, debug_output: str):
        """Validate that threshold and maximum tables have correct structure."""
        # Check Rain (%) threshold table
        rain_percent_section = self._extract_section(debug_output, "Rain (%) Data")
        if rain_percent_section:
            threshold_table = re.search(r'Threshold\nGEO \| Time \| %\n.*?\n=========', rain_percent_section, re.DOTALL)
            if not threshold_table:
                self.errors.append("Missing or malformed Rain (%) threshold table")
            
            maximum_table = re.search(r'Maximum:\nGEO \| Time \| Max\n.*?\n=========', rain_percent_section, re.DOTALL)
            if not maximum_table:
                self.errors.append("Missing or malformed Rain (%) maximum table")
    
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


def validate_debug_output_quick(debug_output: str, report_type: str = 'evening') -> bool:
    """
    Quick validation function for immediate use.
    
    Args:
        debug_output: The debug output string to validate
        report_type: 'morning' or 'evening'
        
    Returns:
        True if valid, False if errors found
    """
    validator = DebugOutputValidator()
    is_valid, errors = validator.validate_debug_output(debug_output, report_type)
    
    if not is_valid:
        print("❌ Debug Output Validation Failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Debug Output Validation Passed")
    return True


def validate_debug_output_detailed(debug_output: str, report_type: str = 'evening') -> Tuple[bool, List[str]]:
    """
    Detailed validation function with full error reporting.
    
    Args:
        debug_output: The debug output string to validate
        report_type: 'morning' or 'evening'
        
    Returns:
        Tuple of (is_valid, list_of_all_issues)
    """
    validator = DebugOutputValidator()
    return validator.validate_debug_output(debug_output, report_type)


if __name__ == "__main__":
    # Example usage
    sample_debug_output = """
# DEBUG DATENEXPORT

Night (N) - temp_min:
T1G3 | 13.2
=========
MIN | 13

Day (D) - temp_max:
T2G1 | 25.4
T2G2 | 25.4
T2G3 | 22.7
=========
MAX | 25

Rain (mm) Data:
T2G1
Time | Rain (mm)
4:00 | 0
5:00 | 0
6:00 | 0
7:00 | 0
8:00 | 0
9:00 | 0
10:00 | 0
11:00 | 0
12:00 | 0
13:00 | 0
14:00 | 0
15:00 | 0
16:00 | 0
17:00 | 0
18:00 | 0
19:00 | 0
=========
4:00 | 0 (Max)
"""
    
    is_valid, errors = validate_debug_output_detailed(sample_debug_output, 'evening')
    print(f"Validation result: {is_valid}")
    if errors:
        print("Errors found:")
        for error in errors:
            print(f"  - {error}") 