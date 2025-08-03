#!/usr/bin/env python3
"""
Verification script for Day function - analyzes email content against specification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
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

def verify_day_function_specification():
    """Verify that Day function output matches specification exactly."""
    
    print("🔍 DAY FUNCTION - SPECIFICATION VERIFICATION")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    target_date = date(2025, 8, 2)
    stage_name = "Vergio"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {target_date}")
    print()
    
    # Test MORNING report
    print("🔍 Verifying MORNING report...")
    try:
        # Generate morning report
        morning_result, morning_debug = refactor.generate_report(stage_name, "morning", target_date.strftime('%Y-%m-%d'))
        
        print(f"📊 Result Output: {morning_result}")
        
        # Verify Result Output format
        if "D" in morning_result:
            day_part = morning_result.split("D")[1].split()[0]  # Extract D{value}
            print(f"✅ Day Result: D{day_part}")
            
            # Verify it's a number
            try:
                day_value = int(day_part)
                print(f"✅ Day Value: {day_value}°C (rounded)")
            except ValueError:
                print(f"❌ Day Value is not a number: {day_part}")
        else:
            print("❌ No 'D' found in Result Output")
        
        # Extract and verify Day section from debug output
        day_section = ""
        in_day_section = False
        for line in morning_debug.split('\n'):
            if line.strip() == "DAY":
                in_day_section = True
                day_section += line + '\n'
            elif in_day_section and line.strip() == "":
                in_day_section = False
                break
            elif in_day_section:
                day_section += line + '\n'
        
        print(f"\n🔍 Day Debug Section:")
        print(day_section)
        
        # Verify T-G references for morning (should be T1G1, T1G2, T1G3)
        expected_tg_refs = ["T1G1", "T1G2", "T1G3"]
        for tg_ref in expected_tg_refs:
            if tg_ref in day_section:
                print(f"✅ Found {tg_ref}")
            else:
                print(f"❌ Missing {tg_ref}")
        
        # Verify MAX line
        if "MAX |" in day_section:
            print("✅ Found MAX line")
        else:
            print("❌ Missing MAX line")
        
    except Exception as e:
        print(f"❌ MORNING report verification failed: {e}")
    
    print()
    
    # Test EVENING report
    print("🔍 Verifying EVENING report...")
    try:
        # Generate evening report
        evening_result, evening_debug = refactor.generate_report(stage_name, "evening", target_date.strftime('%Y-%m-%d'))
        
        print(f"📊 Result Output: {evening_result}")
        
        # Verify Result Output format
        if "D" in evening_result:
            day_part = evening_result.split("D")[1].split()[0]  # Extract D{value}
            print(f"✅ Day Result: D{day_part}")
            
            # Verify it's a number
            try:
                day_value = int(day_part)
                print(f"✅ Day Value: {day_value}°C (rounded)")
            except ValueError:
                print(f"❌ Day Value is not a number: {day_part}")
        else:
            print("❌ No 'D' found in Result Output")
        
        # Extract and verify Day section from debug output
        day_section = ""
        in_day_section = False
        for line in evening_debug.split('\n'):
            if line.strip() == "DAY":
                in_day_section = True
                day_section += line + '\n'
            elif in_day_section and line.strip() == "":
                in_day_section = False
                break
            elif in_day_section:
                day_section += line + '\n'
        
        print(f"\n🔍 Day Debug Section:")
        print(day_section)
        
        # Verify T-G references for evening (should be T2G1, T2G2, T2G3)
        expected_tg_refs = ["T2G1", "T2G2", "T2G3"]
        for tg_ref in expected_tg_refs:
            if tg_ref in day_section:
                print(f"✅ Found {tg_ref}")
            else:
                print(f"❌ Missing {tg_ref}")
        
        # Verify MAX line
        if "MAX |" in day_section:
            print("✅ Found MAX line")
        else:
            print("❌ Missing MAX line")
        
    except Exception as e:
        print(f"❌ EVENING report verification failed: {e}")
    
    print()
    print("🎯 Specification Verification Summary:")
    print("📋 According to specification:")
    print("   - Morning: Day = temp_max of all points of today's stage for today (T1G1, T1G2, T1G3)")
    print("   - Evening: Day = temp_max of all points of tomorrow's stage for tomorrow (T2G1, T2G2, T2G3)")
    print("   - Result Output: D{max_temp_rounded}")
    print("   - Debug Output: DAY section with T-G references and MAX line")
    print("   - Temperature values should be rounded to integers")

if __name__ == "__main__":
    verify_day_function_specification() 