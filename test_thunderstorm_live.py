#!/usr/bin/env python3
"""
Live test for thunderstorm implementation in morning_evening_refactor.py
"""

import yaml
import sys
import os
from datetime import date, datetime, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def main():
    print("🌩️ LIVE TEST: Thunderstorm Implementation")
    print("=" * 50)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
        stage_name = "Test"  # Use Test stage
        report_type = "evening"  # Evening report
        target_date = date.today() + timedelta(days=1)  # Tomorrow
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Date: {target_date}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Generate report
        print("🔍 Generating report...")
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
        
        print("📊 RESULT OUTPUT:")
        print(result_output)
        print()
        
        print("🔍 DEBUG OUTPUT:")
        print(debug_output)
        print()
        
        # Check if thunderstorm data is present
        if "Thunderstorm Data:" in debug_output:
            print("✅ Thunderstorm data found in debug output!")
        else:
            print("❌ No thunderstorm data found in debug output")
        
        # Check result output format
        if "TH:" in result_output:
            print("✅ Thunderstorm format found in result output!")
        else:
            print("❌ No thunderstorm format found in result output")
        
        print()
        print("🎯 Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 