#!/usr/bin/env python3
"""
DEBUG OUTPUT ERROR TEST
=======================
Test the debug output generation to find the exact error.
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def test_debug_output_error():
    """Test debug output generation to find the error."""
    print("🔍 DEBUG OUTPUT ERROR TEST")
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
        
        print("3️⃣ DEBUG OUTPUT:")
        print("-" * 30)
        print(debug_output)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_debug_output_error() 