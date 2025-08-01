#!/usr/bin/env python3
"""
Systematic debug script to identify and fix all issues.
"""

import yaml
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta, datetime

def main():
    print("🔍 SYSTEMATIC DEBUG: Fix all issues")
    print("=" * 60)
    
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
        
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        refactor._last_weather_data = weather_data
        
        # Calculate stage_date
        start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
        days_since_start = (target_date - start_date).days
        
        if report_type == 'evening':
            stage_date = target_date + timedelta(days=1)  # Tomorrow's date
        else:  # morning
            stage_date = target_date  # Today's date
        
        print(f"🌧️ Stage Date: {stage_date}")
        print()
        
        # 1. DEBUG RAIN (mm) - Find threshold issue
        print("1️⃣ DEBUG RAIN (mm):")
        print("-" * 20)
        
        rain_threshold = refactor.thresholds.get('rain_amount', 0.2)
        rain_extractor = lambda h: h.get('rain', {}).get('1h', 0)
        
        result = refactor._process_unified_hourly_data(weather_data, stage_date, rain_extractor, rain_threshold)
        
        print(f"  threshold_value: {result.threshold_value}")
        print(f"  threshold_time: {result.threshold_time}")
        print(f"  max_value: {result.max_value}")
        print(f"  max_time: {result.max_time}")
        
        # Manual threshold calculation
        hourly_data = weather_data.get('hourly_data', [])
        first_threshold_time = None
        first_threshold_value = None
        
        for i, point_data in enumerate(hourly_data):
            if 'data' in point_data:
                for hour_data in point_data['data']:
                    if 'dt' in hour_data:
                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                        hour_date = hour_time.date()
                        if hour_date == stage_date:
                            rain_value = rain_extractor(hour_data)
                            if rain_value >= rain_threshold and first_threshold_time is None:
                                first_threshold_time = hour_time
                                first_threshold_value = rain_value
                                print(f"  FIRST THRESHOLD: {hour_time.strftime('%H:%M')} | {rain_value}")
        
        print()
        
        # 2. DEBUG RAIN (%) - Check if all points are identical
        print("2️⃣ DEBUG RAIN (%):")
        print("-" * 20)
        
        prob_forecast = weather_data.get('probability_forecast', [])
        print(f"  Probability forecast entries: {len(prob_forecast)}")
        
        # Check if all points get the same data
        point_data = {}
        for i in range(3):  # 3 geo points
            point_data[i] = []
            for entry in prob_forecast:
                if 'dt' in entry and 'rain' in entry:
                    entry_time = datetime.fromtimestamp(entry['dt'])
                    entry_date = entry_time.date()
                    if entry_date == stage_date:
                        rain_prob = entry.get('rain', {}).get('3h', 0)
                        point_data[i].append((entry_time, rain_prob))
        
        # Compare data between points
        for i in range(3):
            print(f"  G{i+1}: {len(point_data[i])} entries")
            if point_data[i]:
                print(f"    First: {point_data[i][0]}")
                print(f"    Last: {point_data[i][-1]}")
        
        print()
        
        # 3. DEBUG WIND - Check threshold and timing
        print("3️⃣ DEBUG WIND:")
        print("-" * 20)
        
        wind_threshold = refactor.thresholds.get('wind_speed', 10)
        wind_extractor = lambda h: h.get('wind_speed', 0)
        
        wind_result = refactor._process_unified_hourly_data(weather_data, stage_date, wind_extractor, wind_threshold)
        
        print(f"  threshold_value: {wind_result.threshold_value}")
        print(f"  threshold_time: {wind_result.threshold_time}")
        print(f"  max_value: {wind_result.max_value}")
        print(f"  max_time: {wind_result.max_time}")
        
        # Manual wind threshold calculation
        first_wind_threshold_time = None
        first_wind_threshold_value = None
        
        for i, point_data in enumerate(hourly_data):
            if 'data' in point_data:
                for hour_data in point_data['data']:
                    if 'dt' in hour_data:
                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                        hour_date = hour_time.date()
                        if hour_date == stage_date:
                            wind_value = wind_extractor(hour_data)
                            if wind_value >= wind_threshold and first_wind_threshold_time is None:
                                first_wind_threshold_time = hour_time
                                first_wind_threshold_value = wind_value
                                print(f"  FIRST WIND THRESHOLD: {hour_time.strftime('%H:%M')} | {wind_value}")
        
        print()
        
        # 4. DEBUG GUST - Check if all data is really 0
        print("4️⃣ DEBUG GUST:")
        print("-" * 20)
        
        gust_threshold = refactor.thresholds.get('wind_gust_threshold', 5.0)
        gust_extractor = lambda h: h.get('wind_gusts', 0)
        
        gust_result = refactor._process_unified_hourly_data(weather_data, stage_date, gust_extractor, gust_threshold)
        
        print(f"  threshold_value: {gust_result.threshold_value}")
        print(f"  threshold_time: {gust_result.threshold_time}")
        print(f"  max_value: {gust_result.max_value}")
        print(f"  max_time: {gust_result.max_time}")
        
        # Check raw gust data
        max_gust_found = 0
        for i, point_data in enumerate(hourly_data):
            if 'data' in point_data:
                for hour_data in point_data['data']:
                    if 'dt' in hour_data:
                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                        hour_date = hour_time.date()
                        if hour_date == stage_date:
                            gust_value = gust_extractor(hour_data)
                            if gust_value > max_gust_found:
                                max_gust_found = gust_value
                                print(f"  MAX GUST FOUND: {hour_time.strftime('%H:%M')} | {gust_value}")
        
        if max_gust_found == 0:
            print("  ⚠️  ALL GUST DATA IS 0 - CHECKING RAW DATA STRUCTURE")
            # Check raw data structure
            for i, point_data in enumerate(hourly_data):
                if 'data' in point_data and point_data['data']:
                    sample_hour = point_data['data'][0]
                    print(f"  G{i+1} sample hour keys: {list(sample_hour.keys())}")
                    if 'wind_gusts' in sample_hour:
                        print(f"    wind_gusts: {sample_hour['wind_gusts']}")
                    else:
                        print(f"    No wind_gusts key found")
        
        print()
        
        # 5. DEBUG THUNDERSTORM - Check G2 data
        print("5️⃣ DEBUG THUNDERSTORM:")
        print("-" * 20)
        
        # Check thunderstorm data for each point
        for i, point_data in enumerate(hourly_data):
            if 'data' in point_data:
                print(f"  G{i+1}:")
                thunderstorm_found = False
                for hour_data in point_data['data']:
                    if 'dt' in hour_data:
                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                        hour_date = hour_time.date()
                        if hour_date == stage_date:
                            weather_data = hour_data.get('weather', {})
                            condition = weather_data.get('desc', '')
                            if 'orage' in condition.lower():
                                thunderstorm_found = True
                                print(f"    {hour_time.strftime('%H:%M')}: {condition}")
                
                if not thunderstorm_found:
                    print(f"    No thunderstorm conditions found")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 