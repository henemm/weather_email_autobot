#!/usr/bin/env python3
"""
Fix debug output error by adding try-catch blocks
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

def fix_debug_output():
    """Fix debug output error by adding try-catch blocks."""
    
    print("FIXING DEBUG OUTPUT ERROR")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration")
        return
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    target_date = date(2025, 8, 2)
    stage_name = "Test"
    
    print(f"Stage: {stage_name}")
    print(f"Date: {target_date}")
    print()
    
    try:
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        if not weather_data:
            print("No weather data available!")
            return
        
        # Process all weather data
        night_data = refactor.process_night_data(weather_data, stage_name, target_date, "morning")
        day_data = refactor.process_day_data(weather_data, stage_name, target_date, "morning")
        rain_mm_data = refactor.process_rain_mm_data(weather_data, stage_name, target_date, "morning")
        rain_percent_data = refactor.process_rain_percent_data(weather_data, stage_name, target_date, "morning")
        wind_data = refactor.process_wind_data(weather_data, stage_name, target_date, "morning")
        gust_data = refactor.process_gust_data(weather_data, stage_name, target_date, "morning")
        thunderstorm_data = refactor.process_thunderstorm_data(weather_data, stage_name, target_date, "morning")
        thunderstorm_plus_one_data = refactor.process_thunderstorm_plus_one_data(weather_data, stage_name, target_date, "morning")
        risks_data = refactor.process_risks_data(weather_data, stage_name, target_date, "morning")
        risk_zonal_data = refactor.process_risk_zonal_data(weather_data, stage_name, target_date, "morning")
        
        # Create complete report data
        from src.weather.core.morning_evening_refactor import WeatherReportData
        
        report_data = WeatherReportData(
            stage_name=stage_name,
            report_date=target_date,
            report_type="morning",
            night=night_data,
            day=day_data,
            rain_mm=rain_mm_data,
            rain_percent=rain_percent_data,
            wind=wind_data,
            gust=gust_data,
            thunderstorm=thunderstorm_data,
            thunderstorm_plus_one=thunderstorm_plus_one_data,
            risks=risks_data,
            risk_zonal=risk_zonal_data
        )
        
        # Store weather data for debug output
        refactor._last_weather_data = weather_data
        
        print("Weather data processed successfully")
        print(f"Rain(mm) data: threshold={rain_mm_data.threshold_value}, time={rain_mm_data.threshold_time}")
        print()
        
        # Test debug output generation
        print("Testing debug output generation...")
        try:
            debug_output = refactor.generate_debug_output(report_data)
            print("✅ Debug output generated successfully!")
            print(f"Debug output length: {len(debug_output)} characters")
            
            # Check if RAIN(MM) section is present
            if "RAIN(MM)" in debug_output:
                print("✅ RAIN(MM) section found in debug output")
                
                # Extract RAIN(MM) section
                rain_section = ""
                in_rain_section = False
                for line in debug_output.split('\n'):
                    if line.strip() == "RAIN(MM)":
                        in_rain_section = True
                        rain_section += line + '\n'
                    elif in_rain_section and line.strip() == "":
                        in_rain_section = False
                        break
                    elif in_rain_section:
                        rain_section += line + '\n'
                
                print("RAIN(MM) Section:")
                print(rain_section)
            else:
                print("❌ RAIN(MM) section NOT found in debug output")
                print("First 500 characters of debug output:")
                print(debug_output[:500])
            
        except Exception as e:
            print(f"❌ Debug output generation failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_debug_output() 