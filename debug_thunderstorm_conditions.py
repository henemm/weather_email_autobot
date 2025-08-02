#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date, timedelta
import yaml

def debug_thunderstorm_conditions():
    """Debug thunderstorm weather conditions and mapping"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"🔍 Debugging Thunderstorm Conditions for {stage_name} on {target_date}")
    print("=" * 50)
    
    # Calculate +1 day
    plus_one_date = target_date + timedelta(days=1)
    
    # For Evening report: Thunderstorm (+1) = thunderstorm maximum of all points of over-tomorrow's stage for over-tomorrow
    # For Morning report: Thunderstorm (+1) = thunderstorm maximum of all points of tomorrow's stage for tomorrow
    if report_type == 'evening':
        stage_date = plus_one_date + timedelta(days=1)  # Over-tomorrow's date
    else:  # morning
        stage_date = plus_one_date  # Tomorrow's date
    
    print(f"Stage date: {stage_date}")
    
    # Fetch weather data
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    hourly_data = weather_data.get('hourly_data', [])
    
    # Thunderstorm level mapping
    thunderstorm_levels = {
        'Risque d\'orages': 'low',
        'Averses orageuses': 'med', 
        'Orages': 'high'
    }
    
    print(f"\n🔍 Thunderstorm level mapping:")
    for condition, level in thunderstorm_levels.items():
        print(f"  '{condition}' -> '{level}'")
    
    print(f"\n📊 Weather conditions found for {stage_date}:")
    
    # Check all weather conditions for the stage_date
    conditions_found = set()
    thunderstorm_conditions = []
    
    for i, point_data in enumerate(hourly_data):
        if 'data' in point_data:
            for hour_data in point_data['data']:
                if 'dt' in hour_data:
                    from datetime import datetime
                    hour_time = datetime.fromtimestamp(hour_data['dt'])
                    hour_date = hour_time.date()
                    
                    if hour_date == stage_date:
                        # Extract weather condition
                        condition = hour_data.get('condition', '')
                        if not condition and 'weather' in hour_data:
                            weather_data_hour = hour_data['weather']
                            condition = weather_data_hour.get('desc', '')
                        
                        conditions_found.add(condition)
                        
                        # Check if it's a thunderstorm condition
                        thunderstorm_level = thunderstorm_levels.get(condition, 'none')
                        if thunderstorm_level != 'none':
                            thunderstorm_conditions.append({
                                'time': hour_time.strftime('%H:%M'),
                                'condition': condition,
                                'level': thunderstorm_level,
                                'point': f"G{i+1}"
                            })
    
    print(f"All conditions found: {sorted(conditions_found)}")
    
    if thunderstorm_conditions:
        print(f"\n⚡ Thunderstorm conditions found:")
        for tc in thunderstorm_conditions:
            print(f"  {tc['time']} | {tc['point']} | {tc['condition']} -> {tc['level']}")
    else:
        print(f"\n❌ No thunderstorm conditions found!")
    
    # Test the actual process_thunderstorm_plus_one_data function
    print(f"\n🔍 Testing process_thunderstorm_plus_one_data function:")
    thunderstorm_plus_one_result = refactor.process_thunderstorm_plus_one_data(weather_data, stage_name, target_date, report_type)
    
    print(f"Thunderstorm (+1) result:")
    print(f"  Threshold time: {thunderstorm_plus_one_result.threshold_time}")
    print(f"  Threshold value: {thunderstorm_plus_one_result.threshold_value}")
    print(f"  Max time: {thunderstorm_plus_one_result.max_time}")
    print(f"  Max value: {thunderstorm_plus_one_result.max_value}")
    print(f"  Geo points count: {len(thunderstorm_plus_one_result.geo_points)}")

if __name__ == "__main__":
    debug_thunderstorm_conditions() 