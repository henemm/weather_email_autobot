#!/usr/bin/env python3
"""
Generate comparison data for Météo-France manual comparison.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import yaml
import json
from datetime import date
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def generate_comparison_data():
    """Generate our system's output for comparison with Météo-France website."""
    
    print("🌤️ GENERATING COMPARISON DATA")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create weather processor
    weather_processor = MorningEveningRefactor(config)
    
    # Test stage name
    stage_name = "Test-Corsica"
    test_date = date.today()
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {test_date}")
    print()
    
    comparison_data = {
        "comparison_date": str(test_date),
        "stage_name": stage_name,
        "our_system_output": {
            "morning_report": {},
            "evening_report": {}
        }
    }
    
    try:
        # Generate Morning Report
        print("🌅 Generating Morning Report...")
        morning_result, morning_debug = weather_processor.generate_report(stage_name, 'morning', str(test_date))
        
        comparison_data["our_system_output"]["morning_report"] = {
            "result_output": morning_result,
            "debug_output": morning_debug
        }
        
        print(f"✅ Morning Report: {len(morning_result)} chars")
        
        # Generate Evening Report
        print("🌆 Generating Evening Report...")
        evening_result, evening_debug = weather_processor.generate_report(stage_name, 'evening', str(test_date))
        
        comparison_data["our_system_output"]["evening_report"] = {
            "result_output": evening_result,
            "debug_output": evening_debug
        }
        
        print(f"✅ Evening Report: {len(evening_result)} chars")
        
        # Save comparison data
        output_file = f"comparison_data_{test_date}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, indent=2, ensure_ascii=False)
        
        print()
        print("📊 COMPARISON DATA SUMMARY:")
        print(f"  🌅 Morning Report: {morning_result}")
        print(f"  🌆 Evening Report: {evening_result}")
        print()
        print(f"💾 Data saved to: {output_file}")
        print()
        print("📋 NEXT STEPS:")
        print("1. Öffne die Météo-France Website: https://meteofrance.com/previsions-meteo-france/prunelli-di-fiumorbo/20243")
        print("2. Trage die Website-Daten in meteofrance_manual_comparison_template.json ein")
        print("3. Kopiere die Result Outputs aus diesem Skript in die Template")
        print("4. Vergleiche die Daten und identifiziere Abweichungen")
        
        return comparison_data
        
    except Exception as e:
        print(f"❌ Error generating comparison data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    generate_comparison_data() 