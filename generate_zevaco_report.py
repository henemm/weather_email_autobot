#!/usr/bin/env python3
"""
Generate weather report for Zevaco (20173).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import yaml
import json
from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def generate_zevaco_report():
    """Generate weather reports for Zevaco."""
    
    print("🌤️ GENERATING ZEVACO WEATHER REPORT")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create weather processor
    weather_processor = MorningEveningRefactor(config)
    
    # Zevaco coordinates (from Météo-France website)
    zevaco_coords = {
        "lat": 41.9167,
        "lon": 8.9000
    }
    
    test_date = date.today()
    
    print(f"📍 Location: Zevaco (20173)")
    print(f"🌍 Coordinates: {zevaco_coords['lat']}, {zevaco_coords['lon']}")
    print(f"📅 Date: {test_date}")
    print()
    
    try:
        # Create temporary stage data for Zevaco
        temp_stage_data = {
            "name": "Zevaco",
            "punkte": [
                {"lat": zevaco_coords["lat"], "lon": zevaco_coords["lon"]},
                {"lat": zevaco_coords["lat"] + 0.01, "lon": zevaco_coords["lon"] + 0.01},
                {"lat": zevaco_coords["lat"] + 0.02, "lon": zevaco_coords["lon"] + 0.02}
            ]
        }
        
        # Generate Morning Report
        print("🌅 Generating Morning Report...")
        morning_result, morning_debug = weather_processor.generate_report("Zevaco", 'morning', str(test_date))
        
        print(f"✅ Morning Report: {len(morning_result)} chars")
        print(f"📊 Morning Result: {morning_result}")
        print()
        
        # Generate Evening Report
        print("🌆 Generating Evening Report...")
        evening_result, evening_debug = weather_processor.generate_report("Zevaco", 'evening', str(test_date))
        
        print(f"✅ Evening Report: {len(evening_result)} chars")
        print(f"📊 Evening Result: {evening_result}")
        print()
        
        # Save detailed report
        report_data = {
            "location": {
                "name": "Zevaco",
                "code": "20173",
                "coordinates": zevaco_coords,
                "meteofrance_url": "https://meteofrance.com/previsions-meteo-france/zevaco/20173"
            },
            "date": str(test_date),
            "reports": {
                "morning": {
                    "result": morning_result,
                    "debug": morning_debug
                },
                "evening": {
                    "result": evening_result,
                    "debug": evening_debug
                }
            }
        }
        
        output_file = f"zevaco_report_{test_date}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print("📋 REPORT SUMMARY:")
        print(f"  🌅 Morning: {morning_result}")
        print(f"  🌆 Evening: {evening_result}")
        print()
        print(f"💾 Detailed report saved to: {output_file}")
        print()
        print("🔗 Météo-France URL:")
        print("https://meteofrance.com/previsions-meteo-france/zevaco/20173")
        
        return report_data
        
    except Exception as e:
        print(f"❌ Error generating Zevaco report: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    generate_zevaco_report() 