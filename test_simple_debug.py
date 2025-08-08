#!/usr/bin/env python3
"""
Simple test to check what's broken in debug output.
"""

import yaml
from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def main():
    print("🔍 SIMPLE DEBUG TEST")
    print("=" * 30)
    
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
        
        print("📊 RESULT OUTPUT:")
        print(result_output)
        print()
        
        # Check for specific issues
        lines = debug_output.split('\n')
        
        # Count Threshold tables
        threshold_count = sum(1 for line in lines if line.strip() == "Threshold")
        print(f"🔍 Found {threshold_count} 'Threshold' lines")
        
        # Count Maximum tables
        maximum_count = sum(1 for line in lines if line.strip() == "Maximum:")
        print(f"🔍 Found {maximum_count} 'Maximum:' lines")
        
        # Check for Rain(%) issues
        rain_percent_sections = []
        in_rain_percent = False
        current_section = []
        
        for line in lines:
            if "Rain (%) Data:" in line:
                if current_section:
                    rain_percent_sections.append(current_section)
                current_section = [line]
                in_rain_percent = True
            elif in_rain_percent and line.startswith("Wind Data:"):
                rain_percent_sections.append(current_section)
                in_rain_percent = False
                break
            elif in_rain_percent:
                current_section.append(line)
        
        if current_section:
            rain_percent_sections.append(current_section)
        
        print(f"🔍 Found {len(rain_percent_sections)} Rain(%) sections")
        
        # Show first Rain(%) section
        if rain_percent_sections:
            print("\n📊 FIRST RAIN(%) SECTION:")
            print("-" * 40)
            for line in rain_percent_sections[0]:
                print(line)
        
        print("\n✅ Simple debug test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 