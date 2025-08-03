#!/usr/bin/env python3
"""
TEST WIND AND GUST DEBUG OUTPUT
===============================
Test that WIND and GUST debug output matches specification exactly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def test_wind_gust_debug_output():
    """Test WIND and GUST debug output against specification"""
    print("🔍 TEST WIND AND GUST DEBUG OUTPUT")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        config = load_config()
        refactor = MorningEveningRefactor(config)
        
        # Test data
        current_date = date.today()
        stage_name = "Test"
        
        print(f"📅 Test Date: {current_date}")
        print(f"📍 Stage: {stage_name}")
        print()
        
        # Generate report
        print("📊 GENERATING REPORT:")
        print("-" * 30)
        
        result_output, debug_output = refactor.generate_report(stage_name, "morning", str(current_date))
        
        print(f"✅ Report generated")
        print(f"   Result Output: {result_output}")
        print(f"   Debug Output Length: {len(debug_output)} characters")
        print()
        
        # Parse result output
        result_parts = result_output.split()
        if len(result_parts) >= 7:
            wind_part = result_parts[5]
            gust_part = result_parts[6]
            
            print(f"📋 RESULT OUTPUT ANALYSIS:")
            print(f"   Wind: {wind_part}")
            print(f"   Gust: {gust_part}")
            print()
        
        # Analyze debug output
        print("🔍 DEBUG OUTPUT ANALYSIS:")
        print("-" * 30)
        
        debug_lines = debug_output.split('\n')
        
        # Check for WIND section
        wind_section_found = False
        wind_section_start = -1
        wind_section_end = -1
        
        for i, line in enumerate(debug_lines):
            if "WIND" in line and "THUNDERSTORM" not in line:
                wind_section_found = True
                wind_section_start = i
                print(f"✅ WIND section found at line {i+1}: {line.strip()}")
                break
        
        if not wind_section_found:
            print(f"❌ WIND section not found in debug output")
        
        # Check for GUST section
        gust_section_found = False
        gust_section_start = -1
        gust_section_end = -1
        
        for i, line in enumerate(debug_lines):
            if "GUST" in line and "THUNDERSTORM" not in line:
                gust_section_found = True
                gust_section_start = i
                print(f"✅ GUST section found at line {i+1}: {line.strip()}")
                break
        
        if not gust_section_found:
            print(f"❌ GUST section not found in debug output")
        
        print()
        
        # Check WIND section structure
        if wind_section_found:
            print("🌬️ WIND SECTION STRUCTURE CHECK:")
            print("-" * 30)
            
            # Find section boundaries
            section_start = wind_section_start
            section_end = len(debug_lines)
            
            for i in range(wind_section_start + 1, len(debug_lines)):
                if debug_lines[i].strip().startswith('===') or debug_lines[i].strip().startswith('THUNDERSTORM') or debug_lines[i].strip().startswith('GUST'):
                    section_end = i
                    break
            
            print(f"   Section lines: {section_start + 1} to {section_end}")
            
            # Check for required elements
            required_elements = [
                "Time | Wind Speed",
                "T1G1", "T1G2", "T1G3",  # GEO points
                "Threshold", "Maximum"
            ]
            
            section_content = '\n'.join(debug_lines[section_start:section_end])
            
            for element in required_elements:
                if element in section_content:
                    print(f"   ✅ {element} found")
                else:
                    print(f"   ❌ {element} missing")
            
            # Check for hourly data format
            hourly_data_found = False
            for line in debug_lines[section_start:section_end]:
                if "|" in line and ("04:00" in line or "05:00" in line or "06:00" in line):
                    hourly_data_found = True
                    print(f"   ✅ Hourly data format found: {line.strip()}")
                    break
            
            if not hourly_data_found:
                print(f"   ❌ Hourly data format missing")
        
        print()
        
        # Check GUST section structure
        if gust_section_found:
            print("💨 GUST SECTION STRUCTURE CHECK:")
            print("-" * 30)
            
            # Find section boundaries
            section_start = gust_section_start
            section_end = len(debug_lines)
            
            for i in range(gust_section_start + 1, len(debug_lines)):
                if debug_lines[i].strip().startswith('===') or debug_lines[i].strip().startswith('THUNDERSTORM'):
                    section_end = i
                    break
            
            print(f"   Section lines: {section_start + 1} to {section_end}")
            
            # Check for required elements
            required_elements = [
                "Time | Gust Speed",
                "T1G1", "T1G2", "T1G3",  # GEO points
                "Threshold", "Maximum"
            ]
            
            section_content = '\n'.join(debug_lines[section_start:section_end])
            
            for element in required_elements:
                if element in section_content:
                    print(f"   ✅ {element} found")
                else:
                    print(f"   ❌ {element} missing")
            
            # Check for hourly data format
            hourly_data_found = False
            for line in debug_lines[section_start:section_end]:
                if "|" in line and ("04:00" in line or "05:00" in line or "06:00" in line):
                    hourly_data_found = True
                    print(f"   ✅ Hourly data format found: {line.strip()}")
                    break
            
            if not hourly_data_found:
                print(f"   ❌ Hourly data format missing")
        
        print()
        
        # Specification compliance check
        print("📋 SPECIFICATION COMPLIANCE CHECK:")
        print("-" * 40)
        
        # Expected format from specification
        expected_wind_format = """
WIND
T1G1
Time | Wind Speed
04:00 | 5.2
05:00 | 7.8
...
=========
05:00 | 7.8 (Threshold)
17:00 | 15.3 (Max)

T1G2
Time | Wind Speed
...
=========
...

Threshold
GEO | Time | Speed
T1G1 | 5 | 7.8
T1G2 | 6 | 8.2
T1G3 | 5 | 7.8
=========
Threshold | 5 | 7.8

Maximum
GEO | Time | Max
T1G1 | 17 | 15.3
T1G2 | 16 | 12.1
T1G3 | 17 | 14.8
=========
MAX | 17 | 15.3
"""
        
        expected_gust_format = """
GUST
T1G1
Time | Gust Speed
04:00 | 8.1
05:00 | 12.3
...
=========
05:00 | 12.3 (Threshold)
17:00 | 25.7 (Max)

T1G2
Time | Gust Speed
...
=========
...

Threshold
GEO | Time | Speed
T1G1 | 5 | 12.3
T1G2 | 6 | 13.8
T1G3 | 5 | 12.3
=========
Threshold | 5 | 12.3

Maximum
GEO | Time | Max
T1G1 | 17 | 25.7
T1G2 | 16 | 22.4
T1G3 | 17 | 24.1
=========
MAX | 17 | 25.7
"""
        
        print("Expected WIND format:")
        print("   - WIND section header")
        print("   - Individual GEO point tables (T1G1, T1G2, T1G3)")
        print("   - Hourly data format: Time | Wind Speed")
        print("   - Threshold and Maximum summary tables")
        print("   - Proper T-G references")
        print()
        
        print("Expected GUST format:")
        print("   - GUST section header")
        print("   - Individual GEO point tables (T1G1, T1G2, T1G3)")
        print("   - Hourly data format: Time | Gust Speed")
        print("   - Threshold and Maximum summary tables")
        print("   - Proper T-G references")
        print()
        
        # Final assessment
        print("🎯 FINAL ASSESSMENT:")
        print("-" * 20)
        
        if wind_section_found and gust_section_found:
            print("✅ WIND and GUST sections exist")
        else:
            print("❌ WIND and GUST sections missing")
        
        if wind_part != "W-" and gust_part != "G-":
            print("✅ WIND and GUST data extraction working")
        else:
            print("❌ WIND and GUST data extraction failing")
        
        print()
        print("📊 CONCLUSION:")
        print("WIND and GUST debug output does NOT match specification!")
        print("Need to implement proper debug output format.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wind_gust_debug_output() 