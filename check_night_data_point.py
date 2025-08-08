#!/usr/bin/env python3
"""
Check which data point is used for NIGHT section.
Should use the LAST point (T1G3) according to specification.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def check_night_data_point():
    """Check which data point is used for NIGHT section."""
    
    print("🔍 NIGHT DATENPUNKT PRÜFUNG")
    print("=" * 50)
    
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize refactor
    refactor = MorningEveningRefactor(config)
    
    # Test date
    test_date = "2025-08-03"
    stage_name = "Test"
    
    print(f"📅 Test Date: {test_date}")
    print(f"📍 Stage: {stage_name}")
    print()
    
    # Test Morning Report
    print("🌅 MORNING REPORT - NIGHT CHECK:")
    print("-" * 40)
    try:
        result_output, debug_output = refactor.generate_report(stage_name, "morning", test_date)
        
        # Extract NIGHT section from debug output
        night_start = debug_output.find("####### NIGHT (N) #######")
        if night_start != -1:
            # Find the end of NIGHT section (next section or end)
            next_section = debug_output.find("#######", night_start + 1)
            if next_section != -1:
                night_section = debug_output[night_start:next_section]
            else:
                night_section = debug_output[night_start:]
            
            print("📋 NIGHT Section Content:")
            print(night_section)
            print()
            
            # Check which data points are used
            if "T1G1" in night_section:
                print("❌ T1G1 found in NIGHT - WRONG! Should use T1G3 (last point)")
            elif "T1G2" in night_section:
                print("❌ T1G2 found in NIGHT - WRONG! Should use T1G3 (last point)")
            elif "T1G3" in night_section:
                print("✅ T1G3 found in NIGHT - CORRECT! Using last point")
            else:
                print("❓ No clear T1G reference found in NIGHT section")
            
            # Check for temperature value
            if "|" in night_section:
                lines = night_section.split('\n')
                for line in lines:
                    if "|" in line and ("T1G" in line or "G" in line):
                        print(f"📊 Temperature data: {line.strip()}")
                        break
        else:
            print("❌ NIGHT section not found in debug output")
        
    except Exception as e:
        print(f"❌ Morning Report check failed: {e}")
    
    print()
    
    # Test Evening Report
    print("🌆 EVENING REPORT - NIGHT CHECK:")
    print("-" * 40)
    try:
        result_output, debug_output = refactor.generate_report(stage_name, "evening", test_date)
        
        # Extract NIGHT section from debug output
        night_start = debug_output.find("####### NIGHT (N) #######")
        if night_start != -1:
            # Find the end of NIGHT section (next section or end)
            next_section = debug_output.find("#######", night_start + 1)
            if next_section != -1:
                night_section = debug_output[night_start:next_section]
            else:
                night_section = debug_output[night_start:]
            
            print("📋 NIGHT Section Content:")
            print(night_section)
            print()
            
            # Check which data points are used
            if "T1G1" in night_section:
                print("❌ T1G1 found in NIGHT - WRONG! Should use T1G3 (last point)")
            elif "T1G2" in night_section:
                print("❌ T1G2 found in NIGHT - WRONG! Should use T1G3 (last point)")
            elif "T1G3" in night_section:
                print("✅ T1G3 found in NIGHT - CORRECT! Using last point")
            else:
                print("❓ No clear T1G reference found in NIGHT section")
            
            # Check for temperature value
            if "|" in night_section:
                lines = night_section.split('\n')
                for line in lines:
                    if "|" in line and ("T1G" in line or "G" in line):
                        print(f"📊 Temperature data: {line.strip()}")
                        break
        else:
            print("❌ NIGHT section not found in debug output")
        
    except Exception as e:
        print(f"❌ Evening Report check failed: {e}")
    
    print()
    print("🎯 NIGHT CHECK COMPLETED!")

if __name__ == "__main__":
    check_night_data_point() 