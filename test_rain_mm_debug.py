#!/usr/bin/env python3
"""
Simple test to check Rain(mm) debug output format.
"""

import yaml
from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def main():
    print("🌧️ Testing Rain(mm) Debug Output Format")
    print("=" * 50)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
        stage_name = "Vergio"
        target_date = date.today()
        report_type = "morning"
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Date: {target_date}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Generate report
        print("🔍 Generating report...")
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
        
        # Extract Rain(mm) section
        lines = debug_output.split('\n')
        rain_mm_start = None
        rain_mm_end = None
        
        for i, line in enumerate(lines):
            if "Rain (mm) Data:" in line:
                rain_mm_start = i
            elif rain_mm_start and line.startswith("Rain (%) Data:"):
                rain_mm_end = i
                break
        
        if rain_mm_start is not None:
            if rain_mm_end is None:
                rain_mm_end = len(lines)
            
            rain_mm_section = lines[rain_mm_start:rain_mm_end]
            print("📊 Rain(mm) Debug Output:")
            print("-" * 40)
            for line in rain_mm_section:
                print(line)
        else:
            print("❌ Rain(mm) section not found in debug output")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 