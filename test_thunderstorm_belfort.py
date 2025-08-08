#!/usr/bin/env python3
"""
Test thunderstorm processing for Belfort with real data.
"""

import yaml
import sys
import os
from datetime import date, datetime, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

def main():
    print("🌩️ TEST: Thunderstorm Processing for Belfort")
    print("=" * 50)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Temporarily modify start date so Belfort becomes first stage
        original_start_date = config.get('startdatum', '2025-07-27')
        config['startdatum'] = date.today().strftime('%Y-%m-%d')  # Set to today
        
        # Test parameters - use Belfort coordinates directly
        stage_name = "Belfort"  # We'll create a temporary stage
        report_type = "evening"
        target_date = date.today() + timedelta(days=1)  # Tomorrow
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Date: {target_date}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Temporarily add Belfort to etappen.json for testing
        import json
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
        
        # Add Belfort as first stage for testing
        belfort_stage = {
            "name": "Belfort",
            "punkte": [
                {"lat": 47.6386, "lon": 6.8631}
            ]
        }
        
        # Temporarily modify etappen_data
        test_etappen = [belfort_stage] + etappen_data[:2]  # Belfort + first 2 stages
        
        # Save temporary etappen for testing
        with open("etappen_test.json", "w") as f:
            json.dump(test_etappen, f, indent=2)
        
        # Temporarily replace etappen.json
        import shutil
        shutil.copy("etappen.json", "etappen_backup.json")
        shutil.copy("etappen_test.json", "etappen.json")
        
        try:
            # Generate report
            print("🔍 Generating report...")
            result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
            
            print("📊 RESULT OUTPUT:")
            print(result_output)
            print()
            
            print("🔍 DEBUG OUTPUT:")
            print(debug_output)
            print()
            
            # Check if thunderstorm data is present
            if "Thunderstorm Data:" in debug_output:
                print("✅ Thunderstorm data found in debug output!")
            else:
                print("❌ No thunderstorm data found in debug output")
            
            # Check result output format
            if "TH:" in result_output and "TH-" not in result_output:
                print("✅ Thunderstorm format found in result output!")
            else:
                print("❌ No thunderstorm format found in result output")
            
        finally:
            # Restore original etappen.json
            shutil.copy("etappen_backup.json", "etappen.json")
            os.remove("etappen_backup.json")
            os.remove("etappen_test.json")
        
        print("\n🎯 Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 