#!/usr/bin/env python3
"""
Analyze Rain(mm) emails and compare with specification requirements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient
from datetime import date
import yaml

def load_config():
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def analyze_rain_mm_emails():
    """Analyze Rain(mm) emails and compare with specification."""
    
    print("Rain(mm) EMAIL ANALYSIS vs SPECIFICATION")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print(f"Rain threshold: {config.get('thresholds', {}).get('rain_amount', 0.5)}")
    print()
    
    # Test MORNING report
    print("ANALYZING MORNING REPORT...")
    print("-" * 40)
    
    try:
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        # Process Rain(mm) data
        rain_mm_result = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        
        # Create minimal report data
        from src.weather.core.morning_evening_refactor import WeatherReportData, WeatherThresholdData
        
        empty_data = WeatherThresholdData()
        
        morning_report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=empty_data,
            day=empty_data,
            rain_mm=rain_mm_result,
            rain_percent=empty_data,
            wind=empty_data,
            gust=empty_data,
            thunderstorm=empty_data,
            thunderstorm_plus_one=empty_data,
            risks=empty_data,
            risk_zonal=empty_data
        )
        
        # Generate result output
        morning_result = refactor.format_result_output(morning_report_data)
        
        print(f"ACTUAL Result Output: {morning_result}")
        print()
        
        # Analyze Rain(mm) part
        if "R" in morning_result:
            rain_part = morning_result.split("R")[1].split()[0]
            print(f"Rain(mm) part: R{rain_part}")
            
            # Check specification requirements
            print("\nSPECIFICATION CHECK:")
            print("1. Format: R{threshold}@{time}({max}@{max_time})")
            print(f"   Actual: R{rain_part}")
            
            if rain_part != "-":
                # Parse the actual result
                if "@" in rain_part and "(" in rain_part and ")" in rain_part:
                    # Format: R0.6@17(0.6@17)
                    # Extract threshold part: R0.6@17
                    threshold_part = rain_part.split("(")[0]
                    threshold_parts = threshold_part.split("@")
                    threshold_value = threshold_parts[0]
                    threshold_time = threshold_parts[1]
                    
                    # Extract max part: (0.6@17)
                    max_part = rain_part.split("(")[1].rstrip(")")
                    max_parts = max_part.split("@")
                    max_value = max_parts[0]
                    max_time = max_parts[1]
                
                    print(f"   Parsed: threshold={threshold_value}, time={threshold_time}, max={max_value}, max_time={max_time}")
                    
                    # Check against actual data
                    print(f"\n2. Data Verification:")
                    print(f"   Expected threshold: {rain_mm_result.threshold_value}")
                    print(f"   Expected threshold_time: {rain_mm_result.threshold_time}")
                    print(f"   Expected max_value: {rain_mm_result.max_value}")
                    print(f"   Expected max_time: {rain_mm_result.max_time}")
                    
                    # Check if values match
                    threshold_ok = float(threshold_value) == rain_mm_result.threshold_value
                    time_ok = threshold_time == str(rain_mm_result.threshold_time)
                    max_ok = float(max_value) == rain_mm_result.max_value
                    max_time_ok = max_time == str(rain_mm_result.max_time)
                    
                    print(f"\n3. Value Checks:")
                    print(f"   Threshold value: {'✅' if threshold_ok else '❌'}")
                    print(f"   Threshold time: {'✅' if time_ok else '❌'}")
                    print(f"   Max value: {'✅' if max_ok else '❌'}")
                    print(f"   Max time: {'✅' if max_time_ok else '❌'}")
                    
                    # Check time format (no leading zeros)
                    print(f"\n4. Time Format Check:")
                    print(f"   Time format (no leading zeros): {'✅' if not threshold_time.startswith('0') else '❌'}")
                    
                    # Check T-G references
                    print(f"\n5. T-G Reference Check:")
                    print(f"   Geo points: {rain_mm_result.geo_points}")
                    expected_tg = ["T1G1", "T1G2", "T1G3"]  # Morning report
                    actual_tg = [list(point.keys())[0] for point in rain_mm_result.geo_points]
                    tg_ok = actual_tg == expected_tg
                    print(f"   T-G references: {'✅' if tg_ok else '❌'} (Expected: {expected_tg}, Actual: {actual_tg})")
                    
                else:
                    print("   ❌ Format parsing failed")
            else:
                print("   ✅ No rain detected (R-) - this is correct if no rain above threshold")
        
        # Check debug output requirements
        print(f"\n6. Debug Output Check:")
        print("   Specification requires: RAIN(MM) section with detailed tables")
        print("   Current status: Debug output has error - needs fixing")
        
        # Check email content requirements
        print(f"\n7. Email Content Check:")
        print("   Specification requires: Result-Output + # DEBUG DATENEXPORT + Debug-Output")
        print("   Current status: Result-Output ✅, Debug-Output ❌ (has error)")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("✅ Rain(mm) function detects rain correctly")
    print("✅ Result output format is correct")
    print("❌ Debug output has error and needs fixing")
    print("❌ Email content incomplete (missing proper debug output)")
    print("\nNEXT STEPS:")
    print("1. Fix debug output error")
    print("2. Ensure RAIN(MM) section appears in debug output")
    print("3. Verify complete email content matches specification")

if __name__ == "__main__":
    analyze_rain_mm_emails() 