#!/usr/bin/env python3
"""
Simple test script for Rain(mm) function with Test stage (Belfort)
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

def test_rain_mm_test_stage():
    """Test Rain(mm) function with Test stage."""
    
    print("Rain(mm) FUNCTION - TEST STAGE (Belfort)")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"  # Use "Test" stage which should include Belfort
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print(f"Rain threshold: {config.get('thresholds', {}).get('rain_amount', 0.5)}")
    print()
    
    # Test MORNING report
    print("Testing MORNING report...")
    try:
        # Generate morning report
        morning_result, morning_debug = refactor.generate_report(stage_name, "morning", target_date.strftime('%Y-%m-%d'))
        
        print(f"Result Output: {morning_result}")
        
        # Check if Rain(mm) is present in result
        if "R" in morning_result:
            rain_part = morning_result.split("R")[1].split()[0]  # Extract R{value}
            print(f"Rain(mm) Result: R{rain_part}")
            
            if rain_part != "-":
                print("SUCCESS: Rain(mm) detected!")
            else:
                print("FAILURE: No rain detected")
        else:
            print("No 'R' found in Result Output")
        
        # Check debug output for Rain(mm) section
        if "RAIN(MM)" in morning_debug:
            print("Rain(mm) section found in debug output")
            
            # Extract Rain(mm) section
            rain_section = ""
            in_rain_section = False
            for line in morning_debug.split('\n'):
                if line.strip() == "RAIN(MM)":
                    in_rain_section = True
                    rain_section += line + '\n'
                elif in_rain_section and line.strip() == "":
                    in_rain_section = False
                    break
                elif in_rain_section:
                    rain_section += line + '\n'
            
            print("Rain(mm) Debug Section:")
            print(rain_section)
        else:
            print("Rain(mm) section NOT found in debug output")
            print("Debug output length:", len(morning_debug))
            print("First 500 characters of debug output:")
            print(morning_debug[:500])
        
    except Exception as e:
        print(f"MORNING report failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rain_mm_test_stage() 