#!/usr/bin/env python3
"""
Debug script to understand why the unified function is not working correctly.
"""

import yaml
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta, datetime

def main():
    print("🔍 DEBUG: Unified Function Problem")
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
        
        # Fetch weather data
        weather_data = refactor.fetch_weather_data(stage_name, target_date)
        
        # Calculate stage_date
        start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
        days_since_start = (target_date - start_date).days
        
        if report_type == 'evening':
            stage_date = target_date + timedelta(days=1)  # Tomorrow's date
        else:  # morning
            stage_date = target_date  # Today's date
        
        print(f"🌧️ Stage Date: {stage_date}")
        print(f"🌧️ Rain threshold: {refactor.thresholds.get('rain_amount', 'NOT SET')}")
        print()
        
        # Test unified function directly
        rain_threshold = refactor.thresholds.get('rain_amount', 0.2)
        rain_extractor = lambda h: h.get('rain', {}).get('1h', 0)
        
        print("🔧 Testing unified function directly:")
        print("-" * 40)
        
        result = refactor._process_unified_hourly_data(weather_data, stage_date, rain_extractor, rain_threshold)
        
        print(f"Result from unified function:")
        print(f"  threshold_value: {result.threshold_value}")
        print(f"  threshold_time: {result.threshold_time}")
        print(f"  max_value: {result.max_value}")
        print(f"  max_time: {result.max_time}")
        print(f"  geo_points: {len(result.geo_points) if result.geo_points else 0}")
        
        if result.geo_points:
            for i, point in enumerate(result.geo_points):
                print(f"  G{i+1}: {point}")
        
        print()
        
        # Debug the unified function step by step
        print("🔧 Step-by-step debug of unified function:")
        print("-" * 45)
        
        hourly_data = weather_data.get('hourly_data', [])
        print(f"Hourly data points: {len(hourly_data)}")
        
        for i, point_data in enumerate(hourly_data):
            if 'data' in point_data:
                print(f"\nPoint {i+1} (G{i+1}):")
                print(f"  Data entries: {len(point_data['data'])}")
                
                # Count entries for target date
                target_date_count = 0
                for hour_data in point_data['data']:
                    if 'dt' in hour_data:
                        hour_time = datetime.fromtimestamp(hour_data['dt'])
                        hour_date = hour_time.date()
                        
                        if hour_date == stage_date:
                            target_date_count += 1
                            value = rain_extractor(hour_data)
                            print(f"    {hour_time.strftime('%H:%M')}: {value}")
                
                print(f"  Entries for target date: {target_date_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 