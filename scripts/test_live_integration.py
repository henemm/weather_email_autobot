#!/usr/bin/env python3
"""
Live test script for enhanced alternative risk analysis integration.
"""

import sys
import os
sys.path.append('src')

from datetime import datetime, timedelta
from wetter.weather_data_processor import WeatherDataProcessor
from notification.email_client import generate_gr20_report_text
from position.etappenlogik import get_stage_info, get_stage_coordinates
from config.config_loader import load_config

def test_live_integration():
    """Test the live integration of enhanced alternative risk analysis."""
    
    print("Live Test: Enhanced Alternative Risk Analysis Integration")
    print("=" * 70)
    
    try:
        # Load configuration
        config = load_config()
        print("Configuration loaded successfully")
        
        # Get current stage information
        current_stage = get_stage_info(config)
        if not current_stage:
            print("ERROR: No current stage found")
            return False
        
        stage_name = current_stage["name"]
        stage_coordinates = current_stage["coordinates"]
        
        print(f"Current stage: {stage_name}")
        print(f"Stage coordinates: {len(stage_coordinates)} points")
        
        # Test the enhanced weather data processor
        processor = WeatherDataProcessor()
        
        # Get stage weather data
        print("\nFetching stage weather data...")
        unified_data = processor.get_stage_weather_data(stage_coordinates, stage_name)
        
        print(f"Successfully fetched data for {len(unified_data.data_points)} points")
        
        # Define time range (04:00-22:00 as per email_format.mdc)
        now = datetime.now()
        start_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        print(f"\nTime range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Get weather summary with enhanced data
        print("\nGenerating weather summary...")
        summary = processor.get_weather_summary(unified_data, start_time, end_time)
        
        print("\nWeather Summary:")
        print(f"  Stage: {summary['stage_name']}")
        print(f"  Date: {summary['stage_date']}")
        print(f"  Data points: {summary['data_points']}")
        
        # Check if enhanced data is available
        enhanced_data = summary.get('enhanced_data', {})
        if enhanced_data:
            print(f"  Enhanced data available:")
            print(f"    Hourly entries: {len(enhanced_data.get('hourly_data', []))}")
            print(f"    Daily entries: {len(enhanced_data.get('daily_data', []))}")
            print(f"    Probability entries: {len(enhanced_data.get('probability_data', []))}")
            print(f"    Thunderstorm entries: {len(enhanced_data.get('thunderstorm_data', []))}")
            
            # Debug: Show the actual structure
            print(f"\n=== DEBUG: Enhanced data structure ===")
            print(f"Keys in enhanced_data: {list(enhanced_data.keys())}")
            print(f"Type of enhanced_data: {type(enhanced_data)}")
            if 'hourly_data' in enhanced_data:
                print(f"First hourly entry: {enhanced_data['hourly_data'][0] if enhanced_data['hourly_data'] else 'None'}")
            if 'thunderstorm_data' in enhanced_data:
                print(f"First thunderstorm entry: {enhanced_data['thunderstorm_data'][0] if enhanced_data['thunderstorm_data'] else 'None'}")
            print(f"==========================================\n")
        else:
            print(f"  Enhanced data: Not available")
        
        # Create report data structure
        report_data = {
            "weather_data": summary,
            "location": stage_name,
            "report_type": "evening",  # Changed from "morning" to "evening"
            "timestamp": datetime.now(),
            "risk_percentage": 25,  # Example risk percentage
            "risk_description": "Moderate risk",
            "report_time": datetime.now(),
            "stage_names": [stage_name]
        }
        
        # Create config with alternative risk analysis enabled
        test_config = {
            "alternative_risk_analysis": {
                "enabled": True
            },
            "debug": {
                "enabled": True
            },
            "smtp": {
                "subject": "GR20 Wetter"
            }
        }
        
        print("\nGenerating email report with enhanced alternative risk analysis...")
        
        # Generate email report text
        email_text = generate_gr20_report_text(report_data, test_config)
        
        print(f"\nEmail report generated successfully!")
        print(f"Total length: {len(email_text)} characters")
        
        # Check for alternative risk analysis in email
        if "Alternative Risikoanalyse" in email_text:
            print("SUCCESS: Alternative Risikoanalyse found in email!")
            
            # Extract alternative risk analysis section
            lines = email_text.split('\n')
            in_ara_section = False
            ara_lines = []
            
            for line in lines:
                if "## Alternative Risikoanalyse" in line:
                    in_ara_section = True
                    ara_lines.append(line)
                elif in_ara_section:
                    if line.startswith('##') and "Alternative Risikoanalyse" not in line:
                        break
                    ara_lines.append(line)
            
            if ara_lines:
                print(f"Alternative Risk Analysis section found with {len(ara_lines)} lines")
                
                # Check for debug information
                debug_lines = [line for line in ara_lines if "DEBUG" in line or "ANALYSIS" in line]
                if debug_lines:
                    print(f"SUCCESS: Debug information found ({len(debug_lines)} debug lines)")
                    
                    # Show first few debug lines
                    print("\nDebug Information Preview:")
                    for i, line in enumerate(debug_lines[:10]):
                        print(f"  {line}")
                    if len(debug_lines) > 10:
                        print(f"  ... ({len(debug_lines) - 10} more debug lines)")
                else:
                    print("WARNING: No debug information found in alternative risk analysis")
                
                # Check for specific risk types
                risk_types = ["Heat:", "Cold:", "Rain:", "Thunderstorm:", "Wind:"]
                found_risks = []
                for risk_type in risk_types:
                    if any(risk_type in line for line in ara_lines):
                        found_risks.append(risk_type)
                
                print(f"Risk types found: {found_risks}")
                
                # Check for time stamps in descriptions
                time_stamp_checks = [
                    "probability @",
                    "max @",
                    "occurrences, @",
                    "gusts @"
                ]
                found_time_stamps = []
                for check in time_stamp_checks:
                    if any(check in line for line in ara_lines):
                        found_time_stamps.append(check)
                
                print(f"Time stamps found: {found_time_stamps}")
                
            else:
                print("WARNING: Alternative Risk Analysis section is empty")
        else:
            print("ERROR: Alternative Risikoanalyse not found in email!")
        
        # Show email preview
        print(f"\nEmail Preview (first 800 characters):")
        print("-" * 60)
        print(email_text[:800])
        if len(email_text) > 800:
            print("...")
        print("-" * 60)
        
        # Show alternative risk analysis section
        if ara_lines:
            print(f"\nAlternative Risk Analysis Section:")
            print("-" * 60)
            for line in ara_lines[:20]:  # Show first 20 lines
                print(line)
            if len(ara_lines) > 20:
                print("...")
            print("-" * 60)
        
        print("\n" + "=" * 70)
        print("Live integration test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error in live integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_live_integration()
    sys.exit(0 if success else 1) 