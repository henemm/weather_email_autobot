#!/usr/bin/env python3
"""
Verification script for Rain(mm) function - analyzes output to understand issues
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

def verify_rain_mm_function():
    """Verify Rain(mm) function output and debug issues."""
    
    print("Rain(mm) FUNCTION - VERIFICATION")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    target_date = date(2025, 8, 2)
    stage_name = "Vergio"
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print(f"Rain threshold: {config.get('thresholds', {}).get('rain_amount', 0.2)}")
    print()
    
    # Test MORNING report
    print("Verifying MORNING report...")
    try:
        # Generate morning report
        morning_result, morning_debug = refactor.generate_report(stage_name, "morning", target_date.strftime('%Y-%m-%d'))
        
        print(f"Result Output: {morning_result}")
        
        # Check if Rain(mm) is present in result
        if "R" in morning_result:
            rain_part = morning_result.split("R")[1].split()[0]  # Extract R{value}
            print(f"Rain(mm) Result: R{rain_part}")
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
            print("Available sections in debug output:")
            for line in morning_debug.split('\n'):
                if line.strip() in ["NIGHT", "DAY", "RAIN(MM)", "RAIN(%)", "WIND", "GUST", "THUNDERSTORM"]:
                    print(f"  - {line.strip()}")
        
    except Exception as e:
        print(f"MORNING report verification failed: {e}")
    
    print()
    
    # Test EVENING report
    print("Verifying EVENING report...")
    try:
        # Generate evening report
        evening_result, evening_debug = refactor.generate_report(stage_name, "evening", target_date.strftime('%Y-%m-%d'))
        
        print(f"Result Output: {evening_result}")
        
        # Check if Rain(mm) is present in result
        if "R" in evening_result:
            rain_part = evening_result.split("R")[1].split()[0]  # Extract R{value}
            print(f"Rain(mm) Result: R{rain_part}")
        else:
            print("No 'R' found in Result Output")
        
        # Check debug output for Rain(mm) section
        if "RAIN(MM)" in evening_debug:
            print("Rain(mm) section found in debug output")
            
            # Extract Rain(mm) section
            rain_section = ""
            in_rain_section = False
            for line in evening_debug.split('\n'):
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
            print("Available sections in debug output:")
            for line in evening_debug.split('\n'):
                if line.strip() in ["NIGHT", "DAY", "RAIN(MM)", "RAIN(%)", "WIND", "GUST", "THUNDERSTORM"]:
                    print(f"  - {line.strip()}")
        
    except Exception as e:
        print(f"EVENING report verification failed: {e}")
    
    print()
    print("Verification Summary:")
    print("If Rain(mm) shows 'R-', it means no rain above threshold was found")
    print("If Rain(mm) section is missing from debug output, it means no rain data was processed")
    print("Check that:")
    print("   - Weather data contains rain values above threshold (0.2mm)")
    print("   - Rain(mm) function is being called correctly")
    print("   - Debug output includes Rain(mm) section when data is available")

if __name__ == "__main__":
    verify_rain_mm_function() 