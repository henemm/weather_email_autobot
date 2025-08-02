"""
Simple tests for debug output validator.

These tests validate the debug output validation logic directly,
without needing real weather data or complex setup.
"""

import pytest
from src.weather.core.debug_validator import DebugOutputValidator, validate_debug_output_quick, validate_debug_output_detailed


class TestDebugValidatorSimple:
    """Simple tests for debug output validator."""
    
    def setup_method(self):
        """Set up test validator."""
        self.validator = DebugOutputValidator()
    
    def test_valid_debug_output(self):
        """Test that valid debug output passes validation."""
        valid_debug_output = """
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

T2G2
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

T2G3
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

Rain (%) Data:
T2G1
Time | Rain (%)
4:00 | 0
5:00 | 0
6:00 | 0
7:00 | 0
8:00 | 0
9:00 | 0
10:00 | 0
11:00 | 20
12:00 | 0
13:00 | 0
14:00 | 30
15:00 | 0
16:00 | 0
17:00 | 20
18:00 | 0
19:00 | 0
=========
11:00 | 20% (Threshold)
14:00 | 30% (Max)

Threshold
GEO | Time | %
T2G1 | 11:00 | 20
T2G2 | 11:00 | 20
T2G3 | 11:00 | 20
=========
Threshold | 11:00 | 20

Maximum:
GEO | Time | Max
T2G1 | 14:00 | 30
T2G2 | 14:00 | 30
T2G3 | 14:00 | 30
=========
MAX | 14:00 | 30

Wind Data:
T2G1
Time | Wind (km/h)
4:00 | 2
5:00 | 1
6:00 | 1
7:00 | 1
8:00 | 1
9:00 | 1
10:00 | 1
11:00 | 1
12:00 | 2
13:00 | 3
14:00 | 3
15:00 | 3
16:00 | 3
17:00 | 3
18:00 | 3
19:00 | 3
=========
4:00 | 2 (Threshold)
13:00 | 3 (Max)

Gust Data:
T2G2
Time | Gust (km/h)
4:00 | 13
5:00 | 14
6:00 | 14
7:00 | 14
8:00 | 14
9:00 | 14
10:00 | 14
11:00 | 12
12:00 | 0
13:00 | 11
14:00 | 12
15:00 | 12
16:00 | 13
17:00 | 13
18:00 | 14
19:00 | 15
=========
4:00 | 13 (Threshold)
19:00 | 15 (Max)

Thunderstorm Data:
T2G1
Time | Storm
4:00 | none
5:00 | none
6:00 | none
7:00 | none
8:00 | none
9:00 | none
10:00 | none
11:00 | none
12:00 | none
13:00 | none
14:00 | none
15:00 | none
16:00 | none
17:00 | none
18:00 | none
19:00 | none
=========

Thunderstorm (+1) Data:
T3G1
Time | Storm
05:00 | none
08:00 | none
11:00 | none
14:00 | none
17:00 | none
=========

Risk Zonal Data:
T2G1
Time | Risiko
=========
0:00 | none (Max)
"""
        
        is_valid, errors = self.validator.validate_debug_output(valid_debug_output, 'evening')
        assert is_valid, f"Valid debug output failed validation: {errors}"
    
    def test_missing_sections(self):
        """Test that missing sections are detected."""
        invalid_debug_output = """
# DEBUG DATENEXPORT

Night (N) - temp_min:
T1G3 | 13.2
=========
MIN | 13

Day (D) - temp_max:
T2G1 | 25.4
=========
MAX | 25
"""
        
        is_valid, errors = self.validator.validate_debug_output(invalid_debug_output, 'evening')
        assert not is_valid, "Invalid debug output should fail validation"
        assert any("Missing required section" in error for error in errors)
    
    def test_repeated_hour_sequences(self):
        """Test that repeated hour sequences are detected."""
        invalid_debug_output = """
# DEBUG DATENEXPORT

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
        
        is_valid, errors = self.validator.validate_debug_output(invalid_debug_output, 'evening')
        assert not is_valid, "Debug output with repetitions should fail validation"
        assert any("excessive repetitions" in error for error in errors)
    
    def test_invalid_tg_references(self):
        """Test that invalid T-G references are detected."""
        invalid_debug_output = """
# DEBUG DATENEXPORT

Rain (mm) Data:
T3G1
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
        
        is_valid, errors = self.validator.validate_debug_output(invalid_debug_output, 'evening')
        assert not is_valid, "Debug output with invalid T-G references should fail validation"
        assert any("malformed T-G references" in error for error in errors)
    
    def test_invalid_time_ranges(self):
        """Test that invalid time ranges are detected."""
        invalid_debug_output = """
# DEBUG DATENEXPORT

Rain (mm) Data:
T2G1
Time | Rain (mm)
0:00 | 0
1:00 | 0
2:00 | 0
3:00 | 0
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
20:00 | 0
21:00 | 0
22:00 | 0
23:00 | 0
=========
4:00 | 0 (Max)
"""
        
        is_valid, errors = self.validator.validate_debug_output(invalid_debug_output, 'evening')
        assert not is_valid, "Debug output with invalid time ranges should fail validation"
        assert any("Invalid time found" in error for error in errors)
    
    def test_morning_report_tg_references(self):
        """Test that morning report uses correct T-G references."""
        morning_debug_output = """
# DEBUG DATENEXPORT

Rain (mm) Data:
T1G1
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

T1G2
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

T1G3
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
        
        is_valid, errors = self.validator.validate_debug_output(morning_debug_output, 'morning')
        assert is_valid, f"Morning report debug output failed validation: {errors}"
    
    def test_quick_validation_function(self):
        """Test the quick validation function."""
        valid_debug_output = """
# DEBUG DATENEXPORT

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
        
        is_valid = validate_debug_output_quick(valid_debug_output, 'evening')
        assert is_valid, "Quick validation should pass for valid debug output"
    
    def test_detailed_validation_function(self):
        """Test the detailed validation function."""
        invalid_debug_output = """
# DEBUG DATENEXPORT

Rain (mm) Data:
T2G1
Time | Rain (mm)
0:00 | 0
1:00 | 0
2:00 | 0
3:00 | 0
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
20:00 | 0
21:00 | 0
22:00 | 0
23:00 | 0
=========
4:00 | 0 (Max)
"""
        
        is_valid, errors = validate_debug_output_detailed(invalid_debug_output, 'evening')
        assert not is_valid, "Detailed validation should fail for invalid debug output"
        assert len(errors) > 0, "Detailed validation should return error messages"


if __name__ == "__main__":
    pytest.main([__file__]) 