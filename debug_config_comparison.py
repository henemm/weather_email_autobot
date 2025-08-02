#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from datetime import date
import yaml

def debug_config_comparison():
    """Debug config comparison between config file and self.thresholds"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create refactor instance
    refactor = MorningEveningRefactor(config)
    
    print(f"🔍 Config Comparison Debug")
    print("=" * 50)
    
    print(f"📊 Config file thresholds:")
    print(f"  wind_speed: {config['thresholds']['wind_speed']}")
    print(f"  rain_amount: {config['thresholds']['rain_amount']}")
    print(f"  rain_probability: {config['thresholds']['rain_probability']}")
    print(f"  temperature: {config['thresholds']['temperature']}")
    print(f"  thunderstorm_probability: {config['thresholds']['thunderstorm_probability']}")
    print(f"  wind_gust_threshold: {config['thresholds']['wind_gust_threshold']}")
    print(f"  wind_gust_percentage: {config['thresholds']['wind_gust_percentage']}")
    
    print(f"\n📊 Self.thresholds:")
    print(f"  wind_speed: {refactor.thresholds.get('wind_speed')}")
    print(f"  rain_amount: {refactor.thresholds.get('rain_amount')}")
    print(f"  rain_probability: {refactor.thresholds.get('rain_probability')}")
    print(f"  temperature: {refactor.thresholds.get('temperature')}")
    print(f"  thunderstorm_probability: {refactor.thresholds.get('thunderstorm_probability')}")
    print(f"  wind_gust_threshold: {refactor.thresholds.get('wind_gust_threshold')}")
    print(f"  wind_gust_percentage: {refactor.thresholds.get('wind_gust_percentage')}")
    
    print(f"\n🔍 Comparison:")
    print(f"  wind_speed: {config['thresholds']['wind_speed']} == {refactor.thresholds.get('wind_speed')} -> {config['thresholds']['wind_speed'] == refactor.thresholds.get('wind_speed')}")
    
    # Test with evening report for tomorrow
    stage_name = "Petra"
    target_date = date(2025, 8, 3)  # Tomorrow
    report_type = "evening"
    
    print(f"\n🔍 Testing with actual data:")
    
    # Fetch weather data directly
    weather_data = refactor.fetch_weather_data(stage_name, target_date)
    
    # Test wind processing with config thresholds
    wind_threshold_config = config['thresholds']['wind_speed']
    wind_extractor = lambda h: h.get('wind', {}).get('speed', 0)
    
    print(f"Using config threshold: {wind_threshold_config}")
    result_config = refactor._process_unified_hourly_data(weather_data, target_date, wind_extractor, wind_threshold_config, report_type, 'wind')
    print(f"Config result: threshold_time={result_config.threshold_time}, threshold_value={result_config.threshold_value}")
    
    # Test wind processing with self.thresholds
    wind_threshold_self = refactor.thresholds.get('wind_speed', 1.0)
    print(f"Using self.thresholds: {wind_threshold_self}")
    result_self = refactor._process_unified_hourly_data(weather_data, target_date, wind_extractor, wind_threshold_self, report_type, 'wind')
    print(f"Self result: threshold_time={result_self.threshold_time}, threshold_value={result_self.threshold_value}")
    
    # Test the actual process_wind_data function
    print(f"\n🔍 Testing process_wind_data function:")
    wind_result = refactor.process_wind_data(weather_data, stage_name, target_date, report_type)
    print(f"Process wind data result: threshold_time={wind_result.threshold_time}, threshold_value={wind_result.threshold_value}")

if __name__ == "__main__":
    debug_config_comparison() 