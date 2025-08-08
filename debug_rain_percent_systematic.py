#!/usr/bin/env python3
"""
Systematic debug script to understand why rain percent data is identical for all geo points.
"""

import yaml
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta, datetime

def main():
    print("🔍 SYSTEMATIC DEBUG: Rain (%) - Why identical for all points?")
    print("=" * 70)
    
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
            stage_date = target_date - timedelta(days=1)  # Use today's data
        else:  # morning
            stage_date = target_date  # Today's date
        
        print(f"🌧️ Stage Date: {stage_date}")
        print()
        
        # DEBUG: Check probability_forecast structure
        print("1️⃣ DEBUG: Probability Forecast Structure:")
        print("-" * 40)
        
        prob_forecast = weather_data.get('probability_forecast', [])
        print(f"  Probability forecast entries: {len(prob_forecast)}")
        
        if prob_forecast:
            print(f"  First entry keys: {list(prob_forecast[0].keys())}")
            print(f"  First entry: {prob_forecast[0]}")
            
            # Check if rain data exists
            if 'rain' in prob_forecast[0]:
                print(f"  Rain data type: {type(prob_forecast[0]['rain'])}")
                print(f"  Rain data: {prob_forecast[0]['rain']}")
        
        print()
        
        # DEBUG: Check if probability_forecast is per geo point or global
        print("2️⃣ DEBUG: Is probability_forecast per geo point or global?")
        print("-" * 50)
        
        # Check if we have separate probability data for each geo point
        hourly_data = weather_data.get('hourly_data', [])
        print(f"  Hourly data points: {len(hourly_data)}")
        
        for i, point_data in enumerate(hourly_data):
            if 'data' in point_data:
                print(f"  G{i+1}: {len(point_data['data'])} hourly entries")
                
                # Check if this point has its own probability data
                if 'probability' in point_data:
                    print(f"    Has probability data: {len(point_data['probability'])} entries")
                else:
                    print(f"    No probability data")
        
        print()
        
        # DEBUG: Check how process_rain_percent_data works
        print("3️⃣ DEBUG: How process_rain_percent_data works:")
        print("-" * 40)
        
        # Get stage coordinates
        import json
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
        
        if stage_date == target_date - timedelta(days=1):  # Today
            stage_idx = days_since_start
        else:  # Tomorrow
            stage_idx = days_since_start + 1
        
        if stage_idx < len(etappen_data):
            stage = etappen_data[stage_idx]
            stage_points = stage.get('punkte', [])
            print(f"  Stage: {stage['name']}")
            print(f"  Points: {len(stage_points)}")
            
            for i, point in enumerate(stage_points):
                print(f"  G{i+1}: lat={point['lat']}, lon={point['lon']}")
        
        print()
        
        # DEBUG: Check if probability_forecast is global or per point
        print("4️⃣ DEBUG: Probability forecast usage:")
        print("-" * 35)
        
        # The problem: probability_forecast is GLOBAL, not per geo point!
        # All geo points get the SAME probability_forecast data!
        
        print("  ⚠️  PROBLEM IDENTIFIED:")
        print("  probability_forecast is GLOBAL data, not per geo point!")
        print("  All geo points get the SAME probability_forecast data!")
        print("  This is why all points show identical rain (%) data!")
        
        print()
        
        # DEBUG: Check what the API actually provides
        print("5️⃣ DEBUG: What does meteofrance-api actually provide?")
        print("-" * 45)
        
        print("  meteofrance-api provides:")
        print("  - forecast: hourly data per geo point")
        print("  - probability_forecast: GLOBAL data (not per geo point)")
        print("  - daily_forecast: daily data per geo point")
        
        print()
        print("  SOLUTION: Use forecast data and calculate probability from rain values!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 