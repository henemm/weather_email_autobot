#!/usr/bin/env python3
"""
VALIDATE MORNING REPORT FOR COMMIT
==================================
Validate that morning report is working correctly before committing.
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def validate_morning_report_for_commit():
    """Validate morning report before committing."""
    print("🔍 VALIDATE MORNING REPORT FOR COMMIT")
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
        print("1️⃣ GENERATING MORNING REPORT:")
        print("-" * 30)
        
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date.strftime('%Y-%m-%d'))
        
        print("✅ Morning report generated successfully")
        print(f"Result Output: {result_output}")
        print(f"Result Length: {len(result_output)}")
        print(f"Debug Length: {len(debug_output)}")
        print()
        
        # Validate result output components
        print("2️⃣ VALIDATING RESULT OUTPUT:")
        print("-" * 30)
        
        result_parts = result_output.split()
        
        # Check all required components
        components = {
            'N': next((part for part in result_parts if part.startswith('N')), 'N-'),
            'D': next((part for part in result_parts if part.startswith('D')), 'D-'),
            'R': next((part for part in result_parts if part.startswith('R')), 'R-'),
            'PR': next((part for part in result_parts if part.startswith('PR')), 'PR-'),
            'W': next((part for part in result_parts if part.startswith('W')), 'W-'),
            'G': next((part for part in result_parts if part.startswith('G')), 'G-'),
            'TH': next((part for part in result_parts if part.startswith('TH')), 'TH-'),
            'S+1': next((part for part in result_parts if part.startswith('S+1')), 'S+1-'),
            'HR': next((part for part in result_parts if part.startswith('HR')), 'HR-'),
            'Z': next((part for part in result_parts if part.startswith('Z')), 'Z-')
        }
        
        all_components_present = True
        for component, value in components.items():
            if value == f'{component}-':
                print(f"❌ {component}: {value} (MISSING)")
                all_components_present = False
            else:
                print(f"✅ {component}: {value}")
        
        print()
        
        # Validate debug output
        print("3️⃣ VALIDATING DEBUG OUTPUT:")
        print("-" * 30)
        
        debug_lines = debug_output.split('\n')
        required_sections = [
            '####### NIGHT (N) #######',
            '####### DAY (D) #######', 
            '####### RAIN (R) #######',
            '####### PRAIN (PR) #######',
            '####### WIND (W) #######',
            '####### GUST (G) #######',
            '####### THUNDERSTORM (TH) #######'
        ]
        
        all_sections_present = True
        for section in required_sections:
            if section in debug_lines:
                print(f"✅ {section}")
            else:
                print(f"❌ {section} (MISSING)")
                all_sections_present = False
        
        print()
        
        # Final validation
        print("4️⃣ FINAL VALIDATION:")
        print("-" * 30)
        
        if all_components_present and all_sections_present:
            print("✅ MORNING REPORT READY FOR COMMIT!")
            print("   - All result components present")
            print("   - All debug sections present")
            print("   - No error messages")
        else:
            print("❌ MORNING REPORT NOT READY FOR COMMIT!")
            print("   - Missing components or sections")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    validate_morning_report_for_commit() 