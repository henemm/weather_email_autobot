#!/usr/bin/env python3
"""
Debug script to understand why rain_mm threshold_value is not being set correctly.
"""

import yaml
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta

def main():
    print("🔍 DEBUG: Rain (mm) Threshold Problem")
    print("=" * 50)
    
    try:
        # Load config
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Generate report
        stage_name = "Test"
        report_type = "evening"
        target_date = date.today() + timedelta(days=1)
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Date: {target_date}")
        print(f"📋 Report Type: {report_type}")
        print(f"🌧️ Rain threshold: {refactor.thresholds.get('rain_amount', 'NOT SET')}")
        print()
        
        # Generate report
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
        
        print("📊 RESULT OUTPUT:")
        print(result_output)
        print()
        
        # Check rain_mm data structure
        print("🌧️ Rain (mm) Data Structure Analysis:")
        print("-" * 40)
        
        if hasattr(refactor, '_last_weather_data') and refactor._last_weather_data:
            hourly_data = refactor._last_weather_data.get('hourly_data', [])
            print(f"Hourly data points: {len(hourly_data)}")
            
            # Analyze each point
            for i, point_data in enumerate(hourly_data):
                if 'data' in point_data:
                    print(f"\nPoint {i+1} (G{i+1}):")
                    
                    # Find maximum rain value for this point
                    point_max_rain = None
                    point_max_rain_time = None
                    point_threshold_rain = None
                    point_threshold_time = None
                    
                    for hour_data in point_data['data']:
                        if 'dt' in hour_data:
                            from datetime import datetime
                            hour_time = datetime.fromtimestamp(hour_data['dt'])
                            hour_date = hour_time.date()
                            
                            if hour_date == target_date:
                                rain_value = hour_data.get('rain', {}).get('1h', 0)
                                
                                # Track maximum
                                if point_max_rain is None or rain_value > point_max_rain:
                                    point_max_rain = rain_value
                                    point_max_rain_time = hour_time
                                
                                # Track threshold (earliest time when rain >= threshold)
                                if rain_value >= refactor.thresholds.get('rain_amount', 0) and point_threshold_time is None:
                                    point_threshold_rain = rain_value
                                    point_threshold_time = hour_time
                    
                    print(f"  Max rain: {point_max_rain} at {point_max_rain_time.strftime('%H:%M') if point_max_rain_time else 'None'}")
                    print(f"  Threshold rain: {point_threshold_rain} at {point_threshold_time.strftime('%H:%M') if point_threshold_time else 'None'}")
                    print(f"  Threshold reached: {point_threshold_time is not None}")
        
        # Check the actual report_data structure
        print("\n📋 Report Data Structure:")
        print("-" * 30)
        
        # Recreate the report to get access to report_data
        report_data = refactor.generate_report(stage_name, report_type, target_date)
        
        # Since generate_report returns (result, debug), we need to access the internal data differently
        # Let's check the config thresholds
        print(f"Config rain_amount threshold: {config.get('rain_amount', 'NOT SET')}")
        print(f"Refactor rain_amount threshold: {refactor.thresholds.get('rain_amount', 'NOT SET')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 