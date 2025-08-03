#!/usr/bin/env python3
"""
Debug script to see what's happening in generate_report method.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def debug_report_generation():
    """Debug the generate_report method."""
    
    print("🔍 DEBUG: GENERATE_REPORT METHOD")
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
    
    # Test generate_report
    print("🧪 TESTING GENERATE_REPORT:")
    print("-" * 30)
    try:
        result_output, debug_output = refactor.generate_report(stage_name, "morning", test_date)
        
        print(f"📧 Result Output: {result_output}")
        print(f"🔍 Debug Output Length: {len(debug_output)}")
        
        # Extract NIGHT section from debug output
        night_start = debug_output.find("####### NIGHT (N) #######")
        if night_start != -1:
            # Find the end of NIGHT section (next section or end)
            next_section = debug_output.find("#######", night_start + 1)
            if next_section != -1:
                night_section = debug_output[night_start:next_section]
            else:
                night_section = debug_output[night_start:]
            
            print("\n📋 NIGHT Section Content:")
            print(night_section)
        else:
            print("\n❌ NIGHT section not found in debug output")
        
        # Check if N11 is in result output
        if "N11" in result_output:
            print("\n✅ N11 found in result output - night data is working!")
        else:
            print("\n❌ N11 not found in result output")
        
    except Exception as e:
        print(f"❌ Generate report failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("🎯 DEBUG COMPLETED!")

if __name__ == "__main__":
    debug_report_generation() 