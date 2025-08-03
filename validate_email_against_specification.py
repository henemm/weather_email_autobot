#!/usr/bin/env python3
"""
Comprehensive email validation against specification
Systematically checks if actual email content matches exact specification requirements
"""

import json
import re
from datetime import date, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
# from src.email.email_client import EmailClient  # Not needed for validation
from src.config.config_loader import load_config

def create_expected_email_content(report_type: str):
    """Create the exact expected email content according to specification"""
    
    if report_type == "morning":
        expected_content = """Test: N21 D30 R0.2@6(1.40@16) PR20%@11(100%@17) W10@11(15@17) G20@11(30@17) TH:M@16(H@18) S+1:M@14(H@17) HR:M@17TH:H@17 Z:H208,217M:16,24

# DEBUG DATENEXPORT

Berichts-Typ: morning

heute: 2025-08-02, Test, 3 Punkte
  T1G1 "lat": 47.638699, "lon": 6.846891
  T1G2 "lat": 47.246166, "lon": -1.652276
  T1G3 "lat": 43.283255, "lon": 5.370061
morgen: 2025-08-03, Petra, 3 Punkte
  T2G1 "lat": 42.219882, "lon": 8.980494
  T2G2 "lat": 42.210865, "lon": 9.006806
  T2G3 "lat": 42.198058, "lon": 9.051533

NIGHT (N) - temp_min:
T1G3 | 20.7
=========
MIN | 21

DAY
T1G1 | 20.9
T1G2 | 26.1
T1G3 | 29.9
=========
MAX | 30

RAIN(MM)
T1G1
Time | Rain (mm)
04:00 | 0.00
05:00 | 0.00
06:00 | 0.20
07:00 | 0.80
08:00 | 0.00
09:00 | 0.00
10:00 | 0.00
11:00 | 0.00
12:00 | 0.00
13:00 | 0.00
14:00 | 0.00
15:00 | 0.00
16:00 | 1.40
17:00 | 0.80
18:00 | 0.00
19:00 | 0.00
=========
06:00 | 0.20 (Threshold)
16:00 | 1.40 (Max)

T1G2
Time | Rain (mm)
04:00 | 0.00
05:00 | 0.00
06:00 | 0.00
07:00 | 0.80
08:00 | 0.00
09:00 | 0.00
10:00 | 0.00
11:00 | 0.00
12:00 | 0.00
13:00 | 0.00
14:00 | 0.00
15:00 | 0.00
16:00 | 1.20
17:00 | 0.80
18:00 | 0.00
19:00 | 0.00
=========
07:00 | 0.80 (Threshold)
16:00 | 1.20 (Max)

T1G3
Time | Rain (mm)
04:00 | 0.00
05:00 | 0.00
06:00 | 0.00
07:00 | 0.80
08:00 | 0.00
09:00 | 0.00
10:00 | 0.00
11:00 | 0.00
12:00 | 0.00
13:00 | 0.00
14:00 | 0.00
15:00 | 0.00
16:00 | 1.10
17:00 | 0.80
18:00 | 0.00
19:00 | 0.00
=========
07:00 | 0.80 (Threshold)
16:00 | 1.10 (Max)

Theshold
GEO | Time | mm
G1 | 06:00 | 0.20
G2 | 07:00 | 0.80
G3 | 07:00 | 0.80
=========
Threshold | 06:00 | 0.20

Maximum:
GEO | Time | Max
G1 | 16:00 | 1.40
G2 | 16:00 | 1.20
G3 | 16:00 | 1.10
=========
MAX | 16:00 | 1.40

RAIN(%)
T1G1
Time | Rain (%)
05:00 | 10
08:00 | 0
11:00 | 20
14:00 | 20
17:00 | 100
=========
11:00 | 20 (Threshold)
17:00 | 100 (Max)

T1G2
Time | Rain (%)
05:00 | 10
08:00 | 0
11:00 | 10
14:00 | 30
17:00 | 100
=========
14:00 | 30 (Threshold)
17:00 | 100 (Max)

T1G3
Time | Rain (%)
05:00 | 10
08:00 | 0
11:00 | 20
14:00 | 20
17:00 | 80
=========
11:00 | 20 (Threshold)
17:00 | 80 (Max)

Theshold
GEO | Time | mm
G1 | 11:00 | 20
G2 | 14:00 | 30
G3 | 11:00 | 20
=========
Threshold | 11:00 | 20

Maximum:
GEO | Time | Max
G1 | 17:00 | 100
G2 | 17:00 | 100
G3 | 17:00 | 80
=========
MAX | 17:00 | 100"""
    
    else:  # evening
        expected_content = """Test: N21 D25 R0.2@6(1.40@16) PR20%@11(100%@17) W10@11(15@17) G20@11(30@17) TH:M@16(H@18) S+1:M@14(H@17) HR:M@17TH:H@17 Z:H208,217M:16,24

# DEBUG DATENEXPORT

Berichts-Typ: evening

heute: 2025-08-02, Test, 3 Punkte
  T1G1 "lat": 47.638699, "lon": 6.846891
  T1G2 "lat": 47.246166, "lon": -1.652276
  T1G3 "lat": 43.283255, "lon": 5.370061
morgen: 2025-08-03, Petra, 3 Punkte
  T2G1 "lat": 42.219882, "lon": 8.980494
  T2G2 "lat": 42.210865, "lon": 9.006806
  T2G3 "lat": 42.198058, "lon": 9.051533
übermorgen: 2025-08-04, Onda, 3 Punkte
  T3G1 "lat": 42.134736, "lon": 8.873431
  T3G2 "lat": 42.034736, "lon": 8.873431
  T3G3 "lat": 42.434736, "lon": 8.873431

NIGHT (N) - temp_min:
T1G3 | 20.7
=========
MIN | 21

DAY
T2G1 | 18.9
T2G2 | 24.1
T2G3 | 18.1
=========
MAX | 24

RAIN(MM)
T2G1
Time | Rain (mm)
04:00 | 0.00
05:00 | 0.00
06:00 | 0.20
07:00 | 0.80
08:00 | 0.00
09:00 | 0.00
10:00 | 0.00
11:00 | 0.00
12:00 | 0.00
13:00 | 0.00
14:00 | 0.00
15:00 | 0.00
16:00 | 1.40
17:00 | 0.80
18:00 | 0.00
19:00 | 0.00
=========
06:00 | 0.20 (Threshold)
16:00 | 1.40 (Max)

T2G2
Time | Rain (mm)
04:00 | 0.00
05:00 | 0.00
06:00 | 0.00
07:00 | 0.80
08:00 | 0.00
09:00 | 0.00
10:00 | 0.00
11:00 | 0.00
12:00 | 0.00
13:00 | 0.00
14:00 | 0.00
15:00 | 0.00
16:00 | 1.20
17:00 | 0.80
18:00 | 0.00
19:00 | 0.00
=========
07:00 | 0.80 (Threshold)
16:00 | 1.20 (Max)

T2G3
Time | Rain (mm)
04:00 | 0.00
05:00 | 0.00
06:00 | 0.00
07:00 | 0.80
08:00 | 0.00
09:00 | 0.00
10:00 | 0.00
11:00 | 0.00
12:00 | 0.00
13:00 | 0.00
14:00 | 0.00
15:00 | 0.00
16:00 | 1.10
17:00 | 0.80
18:00 | 0.00
19:00 | 0.00
=========
07:00 | 0.80 (Threshold)
16:00 | 1.10 (Max)

Theshold
GEO | Time | mm
G1 | 06:00 | 0.20
G2 | 07:00 | 0.80
G3 | 07:00 | 0.80
=========
Threshold | 06:00 | 0.20

Maximum:
GEO | Time | Max
G1 | 16:00 | 1.40
G2 | 16:00 | 1.20
G3 | 16:00 | 1.10
=========
MAX | 16:00 | 1.40

RAIN(%)
T2G1
Time | Rain (%)
05:00 | 10
08:00 | 0
11:00 | 20
14:00 | 20
17:00 | 100
=========
11:00 | 20 (Threshold)
17:00 | 100 (Max)

T2G2
Time | Rain (%)
05:00 | 10
08:00 | 0
11:00 | 10
14:00 | 30
17:00 | 100
=========
14:00 | 30 (Threshold)
17:00 | 100 (Max)

T2G3
Time | Rain (%)
05:00 | 10
08:00 | 0
11:00 | 20
14:00 | 20
17:00 | 80
=========
11:00 | 20 (Threshold)
17:00 | 80 (Max)

Theshold
GEO | Time | mm
G1 | 11:00 | 20
G2 | 14:00 | 30
G3 | 11:00 | 20
=========
Threshold | 11:00 | 20

Maximum:
GEO | Time | Max
G1 | 17:00 | 100
G2 | 17:00 | 100
G3 | 17:00 | 80
=========
MAX | 17:00 | 100"""
    
    return expected_content

def validate_email_content(actual_content: str, expected_content: str, report_type: str):
    """Validate actual email content against expected specification"""
    
    print("=" * 80)
    print(f"EMAIL VALIDATION FOR {report_type.upper()} REPORT")
    print("=" * 80)
    
    # Split content into lines for comparison
    actual_lines = actual_content.strip().split('\n')
    expected_lines = expected_content.strip().split('\n')
    
    print(f"Actual content length: {len(actual_lines)} lines")
    print(f"Expected content length: {len(expected_lines)} lines")
    
    # 1. Check Result-Output format
    print("\n" + "="*60)
    print("1. RESULT-OUTPUT VALIDATION")
    print("="*60)
    
    actual_result = actual_lines[0] if actual_lines else ""
    expected_result = expected_lines[0] if expected_lines else ""
    
    print(f"Expected: {expected_result}")
    print(f"Actual:   {actual_result}")
    
    result_valid = actual_result == expected_result
    print(f"Result-Output valid: {'✅' if result_valid else '❌'}")
    
    # 2. Check Debug-Output structure
    print("\n" + "="*60)
    print("2. DEBUG-OUTPUT STRUCTURE VALIDATION")
    print("="*60)
    
    # Check for required sections
    required_sections = [
        "# DEBUG DATENEXPORT",
        "Berichts-Typ:",
        "heute:",
        "morgen:",
        "NIGHT (N) - temp_min:",
        "DAY",
        "RAIN(MM)",
        "RAIN(%)"
    ]
    
    if report_type == "evening":
        required_sections.append("übermorgen:")
    
    actual_content_text = "\n".join(actual_lines)
    missing_sections = []
    
    for section in required_sections:
        if section not in actual_content_text:
            missing_sections.append(section)
        else:
            print(f"✅ Found: {section}")
    
    if missing_sections:
        print(f"❌ Missing sections: {missing_sections}")
    
    # 3. Check coordinates format
    print("\n" + "="*60)
    print("3. COORDINATES VALIDATION")
    print("="*60)
    
    coordinate_pattern = r'T\d+G\d+\s+"lat":\s*[\d.-]+,\s*"lon":\s*[\d.-]+'
    coordinates_found = re.findall(coordinate_pattern, actual_content_text)
    
    expected_coordinates = 6 if report_type == "morning" else 9  # evening has übermorgen
    
    print(f"Expected coordinates: {expected_coordinates}")
    print(f"Found coordinates: {len(coordinates_found)}")
    
    if len(coordinates_found) == expected_coordinates:
        print("✅ Coordinates count correct")
        for coord in coordinates_found:
            print(f"  ✅ {coord}")
    else:
        print("❌ Coordinates count incorrect")
        for coord in coordinates_found:
            print(f"  Found: {coord}")
    
    # 4. Check time format (no leading zeros)
    print("\n" + "="*60)
    print("4. TIME FORMAT VALIDATION")
    print("="*60)
    
    # Check for incorrect time formats (with leading zeros)
    incorrect_time_patterns = [
        r'0\d:\d\d',  # 04:00, 05:00, etc.
        r'\d\d:\d\d'  # Any time with leading zero
    ]
    
    time_format_errors = []
    for pattern in incorrect_time_patterns:
        matches = re.findall(pattern, actual_content_text)
        for match in matches:
            if match not in time_format_errors:
                time_format_errors.append(match)
    
    if time_format_errors:
        print("❌ Time format errors (should not have leading zeros):")
        for error in time_format_errors:
            print(f"  ❌ {error}")
    else:
        print("✅ Time format correct (no leading zeros)")
    
    # 5. Check RAIN(MM) section structure
    print("\n" + "="*60)
    print("5. RAIN(MM) SECTION VALIDATION")
    print("="*60)
    
    rain_mm_section = ""
    if "RAIN(MM)" in actual_content_text:
        start_idx = actual_content_text.find("RAIN(MM)")
        end_marker = "RAIN(%)" if "RAIN(%)" in actual_content_text else "Theshold"
        end_idx = actual_content_text.find(end_marker, start_idx)
        
        if end_idx != -1:
            rain_mm_section = actual_content_text[start_idx:end_idx]
        else:
            rain_mm_section = actual_content_text[start_idx:]
    
    if rain_mm_section:
        print("✅ RAIN(MM) section found")
        
        # Check for required elements
        required_rain_elements = [
            "Time | Rain (mm)",
            "=========",
            "(Threshold)",
            "(Max)"
        ]
        
        for element in required_rain_elements:
            if element in rain_mm_section:
                print(f"  ✅ {element}")
            else:
                print(f"  ❌ Missing: {element}")
    else:
        print("❌ RAIN(MM) section not found")
    
    # 6. Check RAIN(%) section structure
    print("\n" + "="*60)
    print("6. RAIN(%) SECTION VALIDATION")
    print("="*60)
    
    rain_percent_section = ""
    if "RAIN(%)" in actual_content_text:
        start_idx = actual_content_text.find("RAIN(%)")
        end_marker = "Theshold"
        end_idx = actual_content_text.find(end_marker, start_idx)
        
        if end_idx != -1:
            rain_percent_section = actual_content_text[start_idx:end_idx]
        else:
            rain_percent_section = actual_content_text[start_idx:]
    
    if rain_percent_section:
        print("✅ RAIN(%) section found")
        
        # Check for required elements
        required_percent_elements = [
            "Time | Rain (%)",
            "=========",
            "(Threshold)",
            "(Max)"
        ]
        
        for element in required_percent_elements:
            if element in rain_percent_section:
                print(f"  ✅ {element}")
            else:
                print(f"  ❌ Missing: {element}")
    else:
        print("❌ RAIN(%) section not found")
    
    # 7. Line-by-line comparison for critical sections
    print("\n" + "="*60)
    print("7. DETAILED LINE-BY-LINE COMPARISON")
    print("="*60)
    
    max_lines = max(len(actual_lines), len(expected_lines))
    differences_found = 0
    
    for i in range(min(max_lines, 50)):  # Compare first 50 lines
        actual_line = actual_lines[i] if i < len(actual_lines) else "MISSING"
        expected_line = expected_lines[i] if i < len(expected_lines) else "MISSING"
        
        if actual_line != expected_line:
            differences_found += 1
            print(f"❌ Line {i+1:3d}:")
            print(f"   Expected: '{expected_line}'")
            print(f"   Actual:   '{actual_line}'")
            print()
    
    if differences_found == 0:
        print("✅ No differences found in first 50 lines")
    else:
        print(f"❌ {differences_found} differences found in first 50 lines")
    
    # 8. Overall validation summary
    print("\n" + "="*80)
    print("OVERALL VALIDATION SUMMARY")
    print("="*80)
    
    validation_results = {
        "Result-Output": result_valid,
        "Debug-Structure": len(missing_sections) == 0,
        "Coordinates": len(coordinates_found) == expected_coordinates,
        "Time-Format": len(time_format_errors) == 0,
        "RAIN(MM)-Section": "RAIN(MM)" in actual_content_text,
        "RAIN(%)-Section": "RAIN(%)" in actual_content_text,
        "Line-Comparison": differences_found == 0
    }
    
    all_valid = all(validation_results.values())
    
    for test, result in validation_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test:20} {status}")
    
    print(f"\nOverall validation: {'✅ PASS' if all_valid else '❌ FAIL'}")
    
    if not all_valid:
        print("\n❌ EMAIL DOES NOT MEET SPECIFICATION REQUIREMENTS!")
        print("Key issues to fix:")
        if not result_valid:
            print("- Result-Output format incorrect")
        if len(missing_sections) > 0:
            print(f"- Missing sections: {missing_sections}")
        if len(coordinates_found) != expected_coordinates:
            print(f"- Coordinate count incorrect: {len(coordinates_found)} vs {expected_coordinates}")
        if len(time_format_errors) > 0:
            print(f"- Time format errors: {time_format_errors}")
        if differences_found > 0:
            print(f"- {differences_found} line differences found")
    else:
        print("\n🎉 EMAIL FULLY COMPLIES WITH SPECIFICATION!")
    
    return all_valid

def send_and_validate_email(report_type: str):
    """Send email and validate it against specification"""
    
    print("=" * 80)
    print(f"SENDING AND VALIDATING {report_type.upper()} REPORT EMAIL")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    # email_client = EmailClient(config)  # Not needed for validation
    
    # Generate report
    print("Generating report...")
    result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date.strftime('%Y-%m-%d'))
    
    # Combine into email content
    email_content = f"{result_output}\n\n{debug_output}"
    
    print(f"Generated email content length: {len(email_content)} characters")
    
    # Get expected content
    expected_content = create_expected_email_content(report_type)
    
    # Validate content
    is_valid = validate_email_content(email_content, expected_content, report_type)
    
    # Show validation results
    if is_valid:
        print("\n" + "="*60)
        print("VALIDATION PASSED")
        print("="*60)
        print("✅ Email content would be sent successfully")
    else:
        print("\n❌ Email validation failed - NOT sending email")
        print("Please fix the issues above before sending")
    
    return is_valid

if __name__ == "__main__":
    # Test both morning and evening reports
    print("TESTING MORNING REPORT")
    morning_valid = send_and_validate_email("morning")
    
    print("\n" + "="*80)
    print("TESTING EVENING REPORT")
    evening_valid = send_and_validate_email("evening")
    
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Morning Report: {'✅ VALID' if morning_valid else '❌ INVALID'}")
    print(f"Evening Report: {'✅ VALID' if evening_valid else '❌ INVALID'}")
    
    if morning_valid and evening_valid:
        print("\n🎉 ALL REPORTS COMPLY WITH SPECIFICATION!")
    else:
        print("\n❌ SOME REPORTS DO NOT COMPLY WITH SPECIFICATION!")
        print("Please fix the issues above.") 