#!/usr/bin/env python3
"""
VALIDATE METHOD USAGE
=====================
Test to validate which methods are used for morning vs evening reports.
"""

import yaml
from datetime import datetime, date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def validate_method_usage():
    """Validate which methods are used for morning vs evening reports."""
    print("🔍 VALIDATE METHOD USAGE")
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
        
        print(f"📅 Target Date: {target_date}")
        print(f"📍 Stage: {stage_name}")
        print()
        
        # Test both report types
        for report_type in ["morning", "evening"]:
            print(f"📋 TESTING {report_type.upper()} REPORT:")
            print("-" * 30)
            
            try:
                # Generate report
                result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date.strftime('%Y-%m-%d'))
                
                print(f"✅ {report_type.capitalize()} report generated successfully")
                print(f"Result Output: {result_output}")
                print(f"Result Length: {len(result_output)}")
                print(f"Debug Length: {len(debug_output)}")
                
                # Analyze result output components
                result_parts = result_output.split()
                print(f"Result parts: {result_parts}")
                
                # Check for specific components
                day_component = next((part for part in result_parts if part.startswith('D')), 'D-')
                rain_component = next((part for part in result_parts if part.startswith('R')), 'R-')
                pr_component = next((part for part in result_parts if part.startswith('PR')), 'PR-')
                
                print(f"Day component: {day_component}")
                print(f"Rain component: {rain_component}")
                print(f"PR component: {pr_component}")
                
                # Check debug output sections
                debug_lines = debug_output.split('\n')
                sections = [line for line in debug_lines if '#######' in line]
                print(f"Debug sections: {sections}")
                
            except Exception as e:
                print(f"❌ {report_type.capitalize()} report failed: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
            
            print()
        
        print("🔍 ANALYSIS:")
        print("-" * 30)
        print("The reports should use EXACTLY the same methods!")
        print("If they don't, the refactoring was incomplete.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    validate_method_usage() 