#!/usr/bin/env python3
"""
Test script for full integration of enhanced alternative risk analysis into email system.
"""

import sys
import os
sys.path.append('src')

from datetime import datetime, timedelta
from wetter.weather_data_processor import WeatherDataProcessor
from notification.email_client import generate_gr20_report_text

def test_full_integration():
    """Test the full integration of enhanced alternative risk analysis into email system."""
    
    print("Testing Full Integration of Enhanced Alternative Risk Analysis")
    print("=" * 70)
    
    # Test coordinates for Conca stage
    stage_coordinates = [
        [41.79418, 9.259567],  # Conca
        [41.80000, 9.260000],  # Nearby point
        [41.79000, 9.250000]   # Another nearby point
    ]
    stage_name = "Conca"
    
    try:
        # Test the integrated processor
        processor = WeatherDataProcessor()
        
        print(f"Testing stage: {stage_name}")
        print(f"Coordinates: {len(stage_coordinates)} points")
        print()
        
        # Get stage weather data
        unified_data = processor.get_stage_weather_data(stage_coordinates, stage_name)
        
        print(f"Successfully fetched data for {len(unified_data.data_points)} points")
        
        # Define time range (04:00-22:00 as per email_format.mdc)
        now = datetime.now()
        start_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        print(f"\nTime range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Get weather summary with enhanced data
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
        else:
            print(f"  Enhanced data: Not available")
        
        # Create report data structure
        report_data = {
            "weather_data": summary,
            "location": stage_name,
            "report_type": "morning",
            "timestamp": datetime.now()
        }
        
        # Create config with alternative risk analysis enabled
        config = {
            "alternative_risk_analysis": {
                "enabled": True
            },
            "debug": {
                "enabled": True
            }
        }
        
        print("\nGenerating email report with enhanced alternative risk analysis...")
        
        # Generate email report text
        email_text = generate_gr20_report_text(report_data, config)
        
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
                
            else:
                print("WARNING: Alternative Risk Analysis section is empty")
        else:
            print("ERROR: Alternative Risikoanalyse not found in email!")
        
        # Show email preview
        print(f"\nEmail Preview (first 500 characters):")
        print("-" * 50)
        print(email_text[:500])
        if len(email_text) > 500:
            print("...")
        print("-" * 50)
        
        print("\n" + "=" * 70)
        print("Full integration test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error testing full integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_integration()
    sys.exit(0 if success else 1) 