#!/usr/bin/env python3
"""
Test Night Function Verification - Check if output matches expectations
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def main():
    print("🌙 NIGHT FUNCTION VERIFICATION TEST")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "Vergio"
    date_str = "2025-08-02"
    report_type = "evening"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {date_str}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    try:
        # Generate report
        print("🔍 Generating report...")
        result_output, debug_output = refactor.generate_report(stage_name, report_type, date_str)
        
        # Extract Night section from debug output
        lines = debug_output.split('\n')
        night_section = ""
        in_night_section = False
        
        for line in lines:
            if "NIGHT (N) - temp_min:" in line:
                in_night_section = True
                night_section += line + "\n"
            elif in_night_section and line.startswith("DAY (D) - temp_max:"):
                break
            elif in_night_section:
                night_section += line + "\n"
        
        print("📊 ACTUAL OUTPUT:")
        print("=" * 30)
        print(f"Result Output: {result_output}")
        print()
        print("Night Debug Section:")
        print(night_section)
        print("=" * 30)
        
        # Check expectations
        print("\n🔍 VERIFICATION CHECKS:")
        print("=" * 30)
        
        # Check 1: Result Output contains Night value
        if "N" in result_output:
            print("✅ Result Output contains Night value (N)")
        else:
            print("❌ Result Output missing Night value (N)")
        
        # Check 2: Debug section starts with NIGHT (GROSS)
        if "NIGHT (N) - temp_min:" in night_section:
            print("✅ Debug section starts with NIGHT (GROSS)")
        else:
            print("❌ Debug section does not start with NIGHT (GROSS)")
        
        # Check 3: Contains T-G references
        if "T1G" in night_section or "T2G" in night_section or "T3G" in night_section:
            print("✅ Contains T-G references")
        else:
            print("❌ Missing T-G references")
        
        # Check 4: Contains MIN value
        if "MIN |" in night_section:
            print("✅ Contains MIN value")
        else:
            print("❌ Missing MIN value")
        
        # Check 5: Values are rounded (no decimals)
        import re
        min_match = re.search(r'MIN \| (\d+(?:\.\d+)?)', night_section)
        if min_match:
            min_value = min_match.group(1)
            if '.' not in min_value:
                print("✅ MIN value is rounded (no decimals)")
            else:
                print("❌ MIN value has decimals (should be rounded)")
        else:
            print("❌ Could not find MIN value")
        
        # Check 6: Unified Processing - should have multiple geo points
        tg_refs = re.findall(r'T\d+G\d+', night_section)
        if len(tg_refs) > 0:
            print(f"✅ Found {len(tg_refs)} T-G references: {tg_refs}")
        else:
            print("❌ No T-G references found")
        
        print("\n📋 SUMMARY:")
        print("=" * 30)
        print("Night function should:")
        print("- Use DAILY_FORECAST | temp_min")
        print("- Show T-G references (T1G1, T1G2, etc.)")
        print("- Display MIN value (rounded)")
        print("- Work for both Morning and Evening reports")
        print("- Use Unified Processing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 