#!/usr/bin/env python3
"""
VALIDATE CURRENT DEBUG OUTPUT
=============================
Small test to validate the current debug output problem.
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def validate_current_debug_output():
    """Validate the current debug output problem."""
    print("🔍 VALIDATE CURRENT DEBUG OUTPUT")
    print("=" * 50)
    
    try:
        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
        stage_name = "Test"
        target_date = date(2025, 8, 3)
        report_type = "morning"
        
        print(f"📅 Target Date: {target_date}")
        print(f"📍 Stage: {stage_name}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Generate report
        print("1️⃣ GENERATING REPORT:")
        print("-" * 30)
        
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date.strftime('%Y-%m-%d'))
        
        print("✅ Report generated successfully")
        print(f"Result Output Length: {len(result_output)}")
        print(f"Debug Output Length: {len(debug_output)}")
        print()
        
        print("2️⃣ RESULT OUTPUT:")
        print("-" * 30)
        print(result_output)
        print()
        
        print("3️⃣ DEBUG OUTPUT (FIRST 500 CHARS):")
        print("-" * 30)
        print(debug_output[:500])
        print()
        
        print("4️⃣ DEBUG OUTPUT ANALYSIS:")
        print("-" * 30)
        
        # Check for double DEBUG DATENEXPORT
        debug_lines = debug_output.split('\n')
        debug_markers = [i for i, line in enumerate(debug_lines) if '# DEBUG DATENEXPORT' in line]
        
        print(f"DEBUG DATENEXPORT markers found at lines: {debug_markers}")
        
        if len(debug_markers) > 1:
            print("❌ PROBLEM: Multiple DEBUG DATENEXPORT markers found!")
            print(f"   First marker: line {debug_markers[0]}")
            print(f"   Second marker: line {debug_markers[1]}")
            
            # Show context around second marker
            start = max(0, debug_markers[1] - 2)
            end = min(len(debug_lines), debug_markers[1] + 3)
            print(f"\nContext around second marker:")
            for i in range(start, end):
                print(f"   Line {i}: {debug_lines[i]}")
        
        # Check for error message
        if "Error generating debug output" in debug_output:
            print("❌ PROBLEM: Error message found in debug output!")
        
        # Check if debug output is complete
        if len(debug_output) < 1000:
            print("❌ PROBLEM: Debug output seems too short!")
        
        print(f"\nTotal debug lines: {len(debug_lines)}")
        print(f"Debug output ends with: {debug_output[-100:]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    validate_current_debug_output() 