#!/usr/bin/env python3
"""
COMPREHENSIVE SPECIFICATION TEST
================================
Test ALL specification requirements including:
- Section headers format
- All sections completeness
- Correct geo points (NIGHT = last point)
- Real weather data validation
"""

import yaml
import json
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def test_specification_compliance(report_type: str, target_date: str):
    """Test complete specification compliance."""
    print(f"🔍 SPECIFICATION TEST - {report_type.upper()} REPORT")
    print("=" * 60)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Generate report
    result, debug = refactor.generate_report('Test', report_type, target_date)
    
    print(f"📅 Test Date: {target_date}")
    print(f"📍 Report Type: {report_type}")
    print()
    
    # Show result output
    print("📋 RESULT OUTPUT:")
    print("-" * 40)
    print(result)
    print()
    
    # Parse debug output
    lines = debug.split('\n')
    
    print("🔍 SPECIFICATION COMPLIANCE CHECK:")
    print("-" * 40)
    
    # 1. Check Section Headers Format
    print("1️⃣ SECTION HEADERS FORMAT:")
    print("-" * 30)
    
    required_sections = [
        "####### NIGHT (N) #######",
        "####### DAY (D) #######", 
        "####### RAIN (R) #######",
        "####### PRAIN (PR) #######",
        "####### WIND (W) #######",
        "####### GUST (G) #######",
        "####### THUNDERSTORM (TH) #######",
        "####### THUNDERSTORM +1 (TH+1) #######",
        "####### RISKS (HR/TH) #######"
    ]
    
    found_sections = []
    missing_sections = []
    
    for section in required_sections:
        if section in debug:
            found_sections.append(section)
            print(f"   ✅ {section}")
        else:
            missing_sections.append(section)
            print(f"   ❌ {section}")
    
    print()
    
    # 2. Check NIGHT section - should use LAST geo point
    print("2️⃣ NIGHT SECTION - LAST GEO POINT:")
    print("-" * 30)
    
    night_section_found = False
    night_uses_last_point = False
    
    for i, line in enumerate(lines):
        if "####### NIGHT (N) #######" in line:
            night_section_found = True
            print(f"   ✅ NIGHT section found at line {i+1}")
            
            # Check next few lines for geo point
            for j in range(i+1, min(i+10, len(lines))):
                line_content = lines[j].strip()
                if line_content.startswith('T1G'):
                    if 'T1G3' in line_content:  # Should be last point
                        night_uses_last_point = True
                        print(f"   ✅ Uses T1G3 (last point): {line_content}")
                    else:
                        print(f"   ❌ Uses wrong point: {line_content} (should be T1G3)")
                    break
            break
    
    if not night_section_found:
        print("   ❌ NIGHT section not found!")
    
    print()
    
    # 3. Check all sections have proper structure
    print("3️⃣ SECTION STRUCTURE CHECK:")
    print("-" * 30)
    
    section_structures = {
        "NIGHT": ["Time | temp_min", "=========", "MIN |"],
        "DAY": ["GEO | temp_max", "=========", "MAX |"],
        "RAIN": ["Time | Rain (mm)", "=========", "Threshold", "Maximum"],
        "PRAIN": ["Time | Rain (%)", "=========", "Threshold", "Maximum"],
        "WIND": ["Time | Wind", "=========", "Threshold", "Maximum"],
        "GUST": ["Time | Gust", "=========", "Threshold", "Maximum"],
        "THUNDERSTORM": ["Time | Storm", "=========", "Threshold", "Maximum"],
        "RISKS": ["Time | HRain | Storm", "=========", "Maximum HRain", "Maximum Storm"]
    }
    
    for section_name, required_elements in section_structures.items():
        section_header = f"####### {section_name} ("
        section_found = any(section_header in line for line in lines)
        
        if section_found:
            print(f"   ✅ {section_name} section found")
            
            # Check structure elements
            missing_elements = []
            for element in required_elements:
                if element not in debug:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"      ❌ Missing elements: {missing_elements}")
            else:
                print(f"      ✅ Structure complete")
        else:
            print(f"   ❌ {section_name} section missing")
    
    print()
    
    # 4. Check geo points completeness
    print("4️⃣ GEO POINTS COMPLETENESS:")
    print("-" * 30)
    
    # Count T1G/T2G references in each section
    sections_to_check = ["WIND", "GUST", "RAIN", "PRAIN", "THUNDERSTORM"]
    
    for section in sections_to_check:
        section_header = f"####### {section} ("
        section_start = -1
        
        # Find section start
        for i, line in enumerate(lines):
            if section_header in line:
                section_start = i
                break
        
        if section_start >= 0:
            # Count T1G/T2G references in this section
            tg_count = 0
            for i in range(section_start, len(lines)):
                line = lines[i].strip()
                if line.startswith('T1G') or line.startswith('T2G'):
                    tg_count += 1
                elif line.startswith('#######') and i > section_start:
                    break
            
            expected_count = 3  # Should have 3 geo points
            if tg_count >= expected_count:
                print(f"   ✅ {section}: {tg_count} geo points")
            else:
                print(f"   ❌ {section}: only {tg_count}/{expected_count} geo points")
        else:
            print(f"   ❌ {section}: section not found")
    
    print()
    
    # 5. Check result output format
    print("5️⃣ RESULT OUTPUT FORMAT:")
    print("-" * 30)
    
    result_parts = result.split()
    if len(result_parts) >= 2:
        stage_name = result_parts[0].rstrip(':')
        weather_data = result_parts[1]
        
        print(f"   Stage: {stage_name}")
        print(f"   Weather data: {weather_data}")
        print(f"   Length: {len(weather_data)} characters")
        
        # Check for required elements
        required_elements = ['N', 'D', 'R', 'PR', 'W', 'G', 'TH', 'S+1', 'HR', 'Z']
        missing_elements = []
        
        for element in required_elements:
            if element not in weather_data:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"   ❌ Missing elements: {missing_elements}")
        else:
            print(f"   ✅ All required elements present")
        
        # Check length limit
        if len(weather_data) <= 160:
            print(f"   ✅ Within 160 character limit")
        else:
            print(f"   ❌ Exceeds 160 character limit ({len(weather_data)} chars)")
    else:
        print(f"   ❌ Invalid result format: {result}")
    
    print()
    
    # 6. Check for real weather data (specific coordinates)
    print("6️⃣ REAL WEATHER DATA CHECK:")
    print("-" * 30)
    
    # Check if we have any non-zero weather values
    has_real_data = False
    
    # Look for non-zero values in debug output
    for line in lines:
        if any(pattern in line for pattern in ['| 0.00', '| 0', '| none']):
            continue
        if any(pattern in line for pattern in ['| 1.', '| 2.', '| 3.', '| 4.', '| 5.', '| 6.', '| 7.', '| 8.', '| 9.']):
            has_real_data = True
            break
        if any(pattern in line for pattern in ['| low', '| med', '| high', '| L', '| M', '| H']):
            has_real_data = True
            break
    
    if has_real_data:
        print(f"   ✅ Real weather data detected")
    else:
        print(f"   ❌ No real weather data found (all zeros/none)")
    
    print()
    
    # Summary
    print("📋 SPECIFICATION COMPLIANCE SUMMARY:")
    print("-" * 40)
    
    total_sections = len(required_sections)
    found_sections_count = len(found_sections)
    missing_sections_count = len(missing_sections)
    
    print(f"   Sections: {found_sections_count}/{total_sections} found")
    print(f"   NIGHT uses last point: {'✅' if night_uses_last_point else '❌'}")
    print(f"   Real weather data: {'✅' if has_real_data else '❌'}")
    
    if missing_sections_count == 0 and night_uses_last_point and has_real_data:
        print(f"   🎯 OVERALL: ✅ SPECIFICATION COMPLIANT")
    else:
        print(f"   🎯 OVERALL: ❌ SPECIFICATION VIOLATIONS DETECTED")
    
    print()
    print("=" * 60)
    print()

def main():
    """Test both morning and evening reports for specification compliance."""
    print("🔍 COMPREHENSIVE SPECIFICATION TEST")
    print("=" * 60)
    print()
    
    # Test date
    test_date = "2025-08-03"
    
    # Test morning report
    test_specification_compliance("morning", test_date)
    
    # Test evening report
    test_specification_compliance("evening", test_date)
    
    print("🎯 SPECIFICATION TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    main() 