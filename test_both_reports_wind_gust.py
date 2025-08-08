#!/usr/bin/env python3
"""
COMPREHENSIVE TEST - BOTH REPORTS (MORNING AND EVENING)
=======================================================
Test WIND and GUST implementation for both morning and evening reports.
"""

import yaml
import json
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def test_report(report_type: str, target_date: str):
    """Test a specific report type (morning or evening)."""
    print(f"🔍 TESTING {report_type.upper()} REPORT")
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
    
    # Analyze result output
    print("📋 RESULT OUTPUT ANALYSIS:")
    print("-" * 40)
    result_parts = result.split()
    if len(result_parts) >= 2:
        stage_name = result_parts[0].rstrip(':')
        weather_data = result_parts[1]
        
        # Extract WIND and GUST parts
        parts = weather_data.split()
        wind_part = None
        gust_part = None
        
        for part in parts:
            if part.startswith('W'):
                wind_part = part
            elif part.startswith('G'):
                gust_part = part
        
        print(f"   Stage: {stage_name}")
        print(f"   Wind: {wind_part}")
        print(f"   Gust: {gust_part}")
        print(f"   Full Result: {weather_data}")
        print(f"   Length: {len(weather_data)} characters")
    
    print()
    
    # Analyze debug output
    print("🔍 DEBUG OUTPUT ANALYSIS:")
    print("-" * 40)
    
    lines = debug.split('\n')
    
    # Find WIND section
    wind_section_found = False
    wind_section_start = -1
    wind_t1g_count = 0
    
    for i, line in enumerate(lines):
        if "####### WIND (W) #######" in line:
            wind_section_found = True
            wind_section_start = i
            print(f"✅ WIND section found at line {i+1}")
            break
    
    if not wind_section_found:
        print("❌ WIND section not found!")
    else:
        # Count T1G/T2G references in WIND section
        for i in range(wind_section_start, len(lines)):
            line = lines[i].strip()
            if line.startswith('T1G') or line.startswith('T2G'):
                wind_t1g_count += 1
            elif line.startswith('####### GUST') or line.startswith('####### THUNDERSTORM'):
                break
        
        print(f"   T1G references in WIND: {wind_t1g_count}")
    
    # Find GUST section
    gust_section_found = False
    gust_section_start = -1
    gust_t1g_count = 0
    
    for i, line in enumerate(lines):
        if "####### GUST (G) #######" in line:
            gust_section_found = True
            gust_section_start = i
            print(f"✅ GUST section found at line {i+1}")
            break
    
    if not gust_section_found:
        print("❌ GUST section not found!")
    else:
        # Count T1G/T2G references in GUST section
        for i in range(gust_section_start, len(lines)):
            line = lines[i].strip()
            if line.startswith('T1G') or line.startswith('T2G'):
                gust_t1g_count += 1
            elif line.startswith('####### THUNDERSTORM'):
                break
        
        print(f"   T1G references in GUST: {gust_t1g_count}")
    
    print()
    
    # Show section content
    if wind_section_found:
        print("🌬️ WIND SECTION CONTENT:")
        print("-" * 30)
        for i in range(wind_section_start, min(wind_section_start + 20, len(lines))):
            line = lines[i].strip()
            if line.startswith('####### GUST') or line.startswith('####### THUNDERSTORM'):
                break
            if line:  # Only show non-empty lines
                print(f"   {i+1:3d}: {line}")
    
    print()
    
    if gust_section_found:
        print("💨 GUST SECTION CONTENT:")
        print("-" * 30)
        for i in range(gust_section_start, min(gust_section_start + 20, len(lines))):
            line = lines[i].strip()
            if line.startswith('####### THUNDERSTORM'):
                break
            if line:  # Only show non-empty lines
                print(f"   {i+1:3d}: {line}")
    
    print()
    
    # Specification compliance check
    print("📋 SPECIFICATION COMPLIANCE CHECK:")
    print("-" * 40)
    
    # Check if all required elements are present
    required_elements = [
        "####### WIND (W) #######",
        "####### GUST (G) #######",
        "Time | Wind",
        "Time | Gust",
        "Threshold",
        "Maximum"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in debug:
            missing_elements.append(element)
    
    if missing_elements:
        print("❌ Missing elements:")
        for element in missing_elements:
            print(f"   - {element}")
    else:
        print("✅ All required elements present")
    
    # Check T1G count
    expected_t1g_count = 3  # Based on etappen.json
    if wind_t1g_count >= expected_t1g_count:
        print(f"✅ WIND shows all {expected_t1g_count} GEO points")
    else:
        print(f"❌ WIND shows only {wind_t1g_count}/{expected_t1g_count} GEO points")
    
    if gust_t1g_count >= expected_t1g_count:
        print(f"✅ GUST shows all {expected_t1g_count} GEO points")
    else:
        print(f"❌ GUST shows only {gust_t1g_count}/{expected_t1g_count} GEO points")
    
    print()
    print("=" * 60)
    print()

def main():
    """Test both morning and evening reports."""
    print("🌬️ COMPREHENSIVE WIND/GUST TEST - BOTH REPORTS")
    print("=" * 60)
    print()
    
    # Test date
    test_date = "2025-08-03"
    
    # Test morning report
    test_report("morning", test_date)
    
    # Test evening report
    test_report("evening", test_date)
    
    print("🎯 COMPREHENSIVE TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    main() 