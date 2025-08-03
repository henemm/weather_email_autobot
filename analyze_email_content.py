#!/usr/bin/env python3
"""
Analyze email content to validate all sections are present and correctly formatted.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def analyze_email_content():
    """Analyze email content for both Morning and Evening reports."""
    
    print("🔍 E-MAIL CONTENT ANALYSIS")
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
    
    # Analyze Morning Report
    print("🌅 MORNING REPORT ANALYSIS:")
    print("-" * 30)
    try:
        result_output, debug_output = refactor.generate_report(stage_name, "morning", test_date)
        
        print(f"📧 Result Output ({len(result_output)} chars):")
        print(f"'{result_output}'")
        print()
        
        print("🔍 Debug Output Sections:")
        analyze_debug_sections(debug_output, "Morning")
        
    except Exception as e:
        print(f"❌ Morning Report analysis failed: {e}")
    
    print()
    
    # Analyze Evening Report
    print("🌆 EVENING REPORT ANALYSIS:")
    print("-" * 30)
    try:
        result_output, debug_output = refactor.generate_report(stage_name, "evening", test_date)
        
        print(f"📧 Result Output ({len(result_output)} chars):")
        print(f"'{result_output}'")
        print()
        
        print("🔍 Debug Output Sections:")
        analyze_debug_sections(debug_output, "Evening")
        
    except Exception as e:
        print(f"❌ Evening Report analysis failed: {e}")
    
    print()
    print("🎯 ANALYSIS COMPLETED!")

def analyze_debug_sections(debug_output: str, report_type: str):
    """Analyze debug output sections."""
    
    # Expected sections according to specification
    expected_sections = [
        "####### NIGHT (N) #######",
        "####### DAY (D) #######", 
        "####### RAIN (R) #######",
        "####### PRAIN (PR) #######",
        "####### WIND (W) #######",
        "####### GUST (G) #######",
        "####### THUNDERSTORM (TH) #######",
        "####### THUNDERSTORM +1 (TH+1) #######",
        "####### RISKS (HR/TH) #######"
    ]
    
    # Check each expected section
    for section in expected_sections:
        if section in debug_output:
            print(f"✅ {section}")
        else:
            print(f"❌ {section} - MISSING!")
    
    # Check for specific content patterns
    print()
    print("📋 Content Validation:")
    
    # Check for GEO points (T1G1, T1G2, T1G3, etc.)
    geo_points = []
    if "T1G1" in debug_output:
        geo_points.append("T1G1")
    if "T1G2" in debug_output:
        geo_points.append("T1G2") 
    if "T1G3" in debug_output:
        geo_points.append("T1G3")
    if "T2G1" in debug_output:
        geo_points.append("T2G1")
    if "T2G2" in debug_output:
        geo_points.append("T2G2")
    if "T2G3" in debug_output:
        geo_points.append("T2G3")
    
    print(f"📍 GEO Points found: {', '.join(geo_points)}")
    
    # Check for threshold/maximum tables
    if "Threshold" in debug_output and "Maximum" in debug_output:
        print("✅ Threshold/Maximum tables present")
    else:
        print("❌ Threshold/Maximum tables missing")
    
    # Check for time format (4:00, 5:00, etc.)
    if "4:00" in debug_output or "5:00" in debug_output:
        print("✅ Time format correct (no leading zeros)")
    else:
        print("❌ Time format incorrect")
    
    # Check for error messages
    if "Error" in debug_output or "Failed" in debug_output:
        print("❌ Error messages found in debug output")
    else:
        print("✅ No error messages in debug output")

if __name__ == "__main__":
    analyze_email_content() 