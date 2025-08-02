#!/usr/bin/env python3
"""
Live test for complete Morning/Evening Refactor implementation.
Sends a real email with all weather elements results.
"""

import yaml
import sys
import os
import json
from datetime import date, datetime, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.weather.core.debug_validator import validate_debug_output_quick, validate_debug_output_detailed
from src.notification.email_client import EmailClient

def get_stage_for_date(target_date: date, config: dict) -> str:
    """
    Get the correct stage name for a given date.
    
    Args:
        target_date: Target date
        config: Configuration with startdatum
        
    Returns:
        Stage name for the given date
    """
    start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
    days_since_start = (target_date - start_date).days
    
    # Load etappen.json
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    if days_since_start < len(etappen_data):
        stage = etappen_data[days_since_start]
        return stage['name']
    else:
        return "Unknown"

def main():
    print("🌤️ LIVE TEST: Complete Morning/Evening Refactor Implementation")
    print("=" * 70)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
        report_type = "evening"  # Evening report
        target_date = date.today()  # Today
        
        # Get correct stage for the date
        stage_name = get_stage_for_date(target_date, config)
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Date: {target_date}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Generate report
        print("🔍 Generating complete report...")
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
        
        print("📊 RESULT OUTPUT:")
        print(result_output)
        print()
        
        print("🔍 DEBUG OUTPUT:")
        print(debug_output)
        print()
        
        # Validate debug output
        print("🔍 VALIDATING DEBUG OUTPUT:")
        is_valid, validation_errors = validate_debug_output_detailed(debug_output, report_type)
        
        if is_valid:
            print("✅ Debug Output Validation: PASSED")
        else:
            print("❌ Debug Output Validation: FAILED")
            for error in validation_errors:
                print(f"  - {error}")
        print()
        
        # Check if all weather elements are present
        weather_elements = {
            "Night": "N" in result_output,
            "Day": "D" in result_output,
            "Rain (mm)": "R" in result_output,
            "Rain (%)": "PR" in result_output,
            "Wind": "W" in result_output,
            "Gust": "G" in result_output,
            "Thunderstorm": "TH:" in result_output,
            "Thunderstorm (+1)": "TH+1:" in result_output,
            "Risks": "HR:" in result_output,
            "Risk Zonal": "Z:" in result_output
        }
        
        print("✅ Weather Elements Check:")
        for element, present in weather_elements.items():
            status = "✅" if present else "❌"
            print(f"  {status} {element}")
        
        # Send email with results
        print("\n📧 Sending email with complete implementation results...")
        
        email_client = EmailClient(config)
        
        # Create email content
        subject = f"🌤️ Complete Implementation Test - {stage_name} - {target_date}"
        
        email_content = f"""
# Complete Morning/Evening Refactor Implementation Test

## Test Parameters
- **Stage**: {stage_name}
- **Date**: {target_date}
- **Report Type**: {report_type}

## Result Output
```
{result_output}
```

## Debug Output
```
{debug_output}
```

## Validation Results
- **Debug Output Valid**: {'✅ PASSED' if is_valid else '❌ FAILED'}
- **Validation Errors**: {len(validation_errors) if validation_errors else 0}

## Weather Elements Status
"""
        
        for element, present in weather_elements.items():
            status = "✅ Present" if present else "❌ Missing"
            email_content += f"- **{element}**: {status}\n"
        
        email_content += f"""

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Send email
        success = email_client.send_email(email_content, subject)
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email")
        
        print("\n🎯 Live test completed!")
        
    except Exception as e:
        print(f"❌ Error during live test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 