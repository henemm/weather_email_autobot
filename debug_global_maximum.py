#!/usr/bin/env python3
"""
Debug script to understand why global maximum calculation is not working.
"""

import yaml
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta

def main():
    print("🔍 DEBUG: Global Maximum Calculation")
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
        print()
        
        # Generate report
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
        
        print("📊 RESULT OUTPUT:")
        print(result_output)
        print()
        
        # Check rain_mm data
        print("🌧️ Rain (mm) Data Analysis:")
        print("-" * 30)
        
        if hasattr(refactor, '_last_weather_data') and refactor._last_weather_data:
            hourly_data = refactor._last_weather_data.get('hourly_data', [])
            print(f"Hourly data points: {len(hourly_data)}")
            
            # Find maximum rain value across all points
            global_max_rain = None
            global_max_rain_time = None
            
            for i, point_data in enumerate(hourly_data):
                if 'data' in point_data:
                    print(f"Point {i+1} has {len(point_data['data'])} entries")
                    
                    for hour_data in point_data['data']:
                        if 'dt' in hour_data:
                            from datetime import datetime
                            hour_time = datetime.fromtimestamp(hour_data['dt'])
                            hour_date = hour_time.date()
                            
                            if hour_date == target_date:
                                rain_value = hour_data.get('rain', {}).get('1h', 0)
                                if global_max_rain is None or rain_value > global_max_rain:
                                    global_max_rain = rain_value
                                    global_max_rain_time = hour_time
                                    print(f"  New max: {rain_value} at {hour_time.strftime('%H:%M')}")
            
            print(f"Calculated global max rain: {global_max_rain} at {global_max_rain_time.strftime('%H:%M') if global_max_rain_time else 'None'}")
        
        # Check rain_percent data
        print("\n🌧️ Rain (%) Data Analysis:")
        print("-" * 30)
        
        if hasattr(refactor, '_last_weather_data') and refactor._last_weather_data:
            prob_forecast = refactor._last_weather_data.get('probability_forecast', [])
            print(f"Probability forecast entries: {len(prob_forecast)}")
            
            # Find maximum rain probability
            global_max_prob = None
            global_max_prob_time = None
            
            for entry in prob_forecast:
                if 'dt' in entry and 'rain' in entry:
                    from datetime import datetime
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    
                    if entry_date == target_date:
                        rain_prob = entry.get('rain', {}).get('3h', 0)
                        if global_max_prob is None or rain_prob > global_max_prob:
                            global_max_prob = rain_prob
                            global_max_prob_time = entry_time
                            print(f"  New max prob: {rain_prob}% at {entry_time.strftime('%H:%M')}")
            
            print(f"Calculated global max probability: {global_max_prob}% at {global_max_prob_time.strftime('%H:%M') if global_max_prob_time else 'None'}")
        
        # Check wind data
        print("\n🌬️ Wind Data Analysis:")
        print("-" * 30)
        
        if hasattr(refactor, '_last_weather_data') and refactor._last_weather_data:
            hourly_data = refactor._last_weather_data.get('hourly_data', [])
            
            # Find maximum wind speed across all points
            global_max_wind = None
            global_max_wind_time = None
            
            for i, point_data in enumerate(hourly_data):
                if 'data' in point_data:
                    for hour_data in point_data['data']:
                        if 'dt' in hour_data:
                            from datetime import datetime
                            hour_time = datetime.fromtimestamp(hour_data['dt'])
                            hour_date = hour_time.date()
                            
                            if hour_date == target_date:
                                wind_speed = hour_data.get('wind', {}).get('speed', 0)
                                if global_max_wind is None or wind_speed > global_max_wind:
                                    global_max_wind = wind_speed
                                    global_max_wind_time = hour_time
                                    print(f"  New max wind: {wind_speed} km/h at {hour_time.strftime('%H:%M')}")
            
            print(f"Calculated global max wind: {global_max_wind} km/h at {global_max_wind_time.strftime('%H:%M') if global_max_wind_time else 'None'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 