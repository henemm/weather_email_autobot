#!/usr/bin/env python3
"""
Comprehensive test for both Morning and Evening reports with corrected T-G reference logic.
"""

import yaml
import sys
import os
import json
from datetime import date, datetime
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.weather.core.debug_validator import validate_debug_output_detailed

def get_stage_for_date(target_date: date, config: dict) -> str:
    """Get the correct stage name for a given date."""
    start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
    days_since_start = (target_date - start_date).days
    
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    if days_since_start < len(etappen_data):
        stage = etappen_data[days_since_start]
        return stage['name']
    else:
        return "Unknown"

def test_report(report_type: str, target_date: date, config: dict):
    """Test a specific report type."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING {report_type.upper()} REPORT")
    print(f"{'='*60}")
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Get correct stage for the date
    stage_name = get_stage_for_date(target_date, config)
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {target_date}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    # Generate report
    print("🔍 Generating complete report...")
    result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
    
    print("📊 RESULT OUTPUT:")
    print(result_output)
    print()
    
    # Validate debug output
    print("🔍 VALIDATING DEBUG OUTPUT:")
    is_valid, validation_errors = validate_debug_output_detailed(debug_output, report_type)
    
    if is_valid:
        print("✅ Debug Output Validation: PASSED")
    else:
        print("❌ Debug Output Validation: FAILED")
        for error in validation_errors:
            print(f"  - {error}")
    print()
    
    # Check weather elements
    weather_elements = {
        "Night": "N" in result_output,
        "Day": "D" in result_output,
        "Rain (mm)": "R" in result_output,
        "Rain (%)": "PR" in result_output,
        "Wind": "W" in result_output,
        "Gust": "G" in result_output,
        "Thunderstorm": "TH:" in result_output,
        "Thunderstorm (+1)": "TH+1:" in result_output,
        "Risks": "HR:" in result_output,
        "Risk Zonal": "Z:" in result_output
    }
    
    print("✅ Weather Elements Check:")
    for element, present in weather_elements.items():
        status = "✅" if present else "❌"
        print(f"  {status} {element}")
    
    # Check T-G references in debug output
    print(f"\n🔍 T-G REFERENCE CHECK for {report_type.upper()} REPORT:")
    if report_type == 'morning':
        expected_t1 = ['T1G1', 'T1G2', 'T1G3']  # Heute
        expected_t2 = ['T2G1', 'T2G2', 'T2G3', 'T2G4']  # Morgen
        expected_t3 = []  # Nicht verwendet
    else:  # evening
        expected_t1 = ['T1G1', 'T1G2', 'T1G3']  # Heute
        expected_t2 = ['T2G1', 'T2G2', 'T2G3', 'T2G4']  # Morgen
        expected_t3 = ['T3G1', 'T3G2', 'T3G3']  # Übermorgen
    
    # Check if expected T-G references are present
    for tg_ref in expected_t1 + expected_t2 + expected_t3:
        if tg_ref in debug_output:
            print(f"  ✅ {tg_ref} found")
        else:
            print(f"  ❌ {tg_ref} missing")
    
    return is_valid, weather_elements

def main():
    print("🌤️ COMPREHENSIVE TEST: Both Morning and Evening Reports")
    print("=" * 70)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Test parameters
        target_date = date.today()
        
        # Test Morning Report
        morning_valid, morning_elements = test_report("morning", target_date, config)
        
        # Test Evening Report
        evening_valid, evening_elements = test_report("evening", target_date, config)
        
        # Summary
        print(f"\n{'='*60}")
        print("📋 TEST SUMMARY")
        print(f"{'='*60}")
        
        print(f"🌅 Morning Report: {'✅ PASSED' if morning_valid else '❌ FAILED'}")
        print(f"🌆 Evening Report: {'✅ PASSED' if evening_valid else '❌ FAILED'}")
        
        print(f"\n📊 Weather Elements Comparison:")
        print("Element          | Morning | Evening")
        print("-" * 40)
        for element in morning_elements.keys():
            morning_status = "✅" if morning_elements[element] else "❌"
            evening_status = "✅" if evening_elements[element] else "❌"
            print(f"{element:<15} | {morning_status:<7} | {evening_status}")
        
        # Overall result
        if morning_valid and evening_valid:
            print(f"\n🎉 OVERALL RESULT: ✅ BOTH REPORTS PASSED")
        else:
            print(f"\n⚠️  OVERALL RESULT: ❌ SOME REPORTS FAILED")
        
    except Exception as e:
        print(f"❌ Error during comprehensive test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 