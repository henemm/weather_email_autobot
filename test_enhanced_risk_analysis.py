#!/usr/bin/env python3
"""
Test script for enhanced alternative risk analysis.
"""

import sys
import os
sys.path.append('src')

from datetime import datetime, timedelta
from wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI
from risiko.enhanced_alternative_risk_analysis import EnhancedAlternativeRiskAnalyzer

def test_enhanced_risk_analysis():
    """Test the enhanced alternative risk analysis with transparent debug output."""
    
    print("Testing Enhanced Alternative Risk Analysis")
    print("=" * 60)
    
    # Test coordinates
    lat = 41.79418
    lon = 9.259567
    location_name = "Conca"
    
    try:
        # Get weather data using enhanced API
        api = EnhancedMeteoFranceAPI()
        weather_data = api.get_complete_forecast_data(lat, lon, location_name)
        
        print(f"Fetched weather data for {location_name}")
        print(f"Hourly entries: {len(weather_data['hourly_data'])}")
        print(f"Daily entries: {len(weather_data['daily_data'])}")
        print(f"Probability entries: {len(weather_data['probability_data'])}")
        print(f"Thunderstorm entries: {len(weather_data['thunderstorm_data'])}")
        print()
        
        # Test enhanced risk analysis
        analyzer = EnhancedAlternativeRiskAnalyzer()
        result = analyzer.analyze_all_risks(weather_data)
        
        print("RISK ANALYSIS RESULTS:")
        print("-" * 25)
        print(f"Heat: {result.heat.description}")
        print(f"Cold: {result.cold.description}")
        print(f"Rain: {result.rain.description}")
        print(f"Thunderstorm: {result.thunderstorm.description}")
        print(f"Wind: {result.wind.description}")
        print()
        
        # Generate report text
        report_text = analyzer.generate_report_text(result)
        
        print("COMPLETE REPORT WITH DEBUG INFORMATION:")
        print("=" * 60)
        print(report_text)
        print("=" * 60)
        
        # Test specific risk analyses
        print("\nDETAILED RISK ANALYSIS BREAKDOWN:")
        print("-" * 40)
        
        # Heat analysis details
        print("HEAT ANALYSIS:")
        print(f"  Max temperature: {result.heat.max_temperature}°C")
        print(f"  Data source: {result.heat.data_source}")
        print(f"  Debug info length: {len(result.heat.debug_info)} characters")
        
        # Cold analysis details
        print("\nCOLD ANALYSIS:")
        print(f"  Min temperature: {result.cold.min_temperature}°C")
        print(f"  Data source: {result.cold.data_source}")
        print(f"  Debug info length: {len(result.cold.debug_info)} characters")
        
        # Rain analysis details
        print("\nRAIN ANALYSIS:")
        print(f"  Has rain: {result.rain.has_rain}")
        print(f"  Max probability: {result.rain.max_probability}%")
        print(f"  Max rain rate: {result.rain.max_rain_rate}mm/h")
        print(f"  First rain time: {result.rain.first_rain_time}")
        print(f"  Data source: {result.rain.data_source}")
        print(f"  Debug info length: {len(result.rain.debug_info)} characters")
        
        # Thunderstorm analysis details
        print("\nTHUNDERSTORM ANALYSIS:")
        print(f"  Has thunderstorm: {result.thunderstorm.has_thunderstorm}")
        print(f"  Thunderstorm count: {result.thunderstorm.thunderstorm_count}")
        print(f"  First thunderstorm time: {result.thunderstorm.first_thunderstorm_time}")
        print(f"  Max probability: {result.thunderstorm.max_probability}%")
        print(f"  Data source: {result.thunderstorm.data_source}")
        print(f"  Debug info length: {len(result.thunderstorm.debug_info)} characters")
        
        # Wind analysis details
        print("\nWIND ANALYSIS:")
        print(f"  Max wind speed: {result.wind.max_wind_speed}km/h")
        print(f"  Max gusts: {result.wind.max_gusts}km/h")
        print(f"  First high wind time: {result.wind.first_high_wind_time}")
        print(f"  Data source: {result.wind.data_source}")
        print(f"  Debug info length: {len(result.wind.debug_info)} characters")
        
        print("\n" + "=" * 60)
        print("Enhanced risk analysis test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error testing enhanced risk analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_risk_analysis()
    sys.exit(0 if success else 1) 