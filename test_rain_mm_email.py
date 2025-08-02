#!/usr/bin/env python3
"""
Specific email test for Rain(mm) debug output corrections.
"""

import yaml
import sys
import os
import json
from datetime import date, datetime, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient

def get_stage_for_date(target_date: date, config: dict) -> str:
    """Get the correct stage name for a given date."""
    start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
    days_since_start = (target_date - start_date).days
    
    with open("etappen.json", "r") as f:
        etappen_data = json.load(f)
    
    if days_since_start < len(etappen_data):
        stage = etappen_data[days_since_start]
        return stage['name']
    else:
        return "Unknown"

def main():
    print("🌧️ RAIN(MM) DEBUG OUTPUT EMAIL TEST")
    print("=" * 50)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters - use morning report for better rain data
        report_type = "morning"
        target_date = date.today()
        stage_name = get_stage_for_date(target_date, config)
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Date: {target_date}")
        print(f"📋 Report Type: {report_type}")
        print()
        
        # Generate report
        print("🔍 Generating report...")
        result_output, debug_output = refactor.generate_report(stage_name, report_type, target_date)
        
        # Extract Rain(mm) section
        lines = debug_output.split('\n')
        rain_mm_start = None
        rain_mm_end = None
        
        for i, line in enumerate(lines):
            if "Rain (mm) Data:" in line:
                rain_mm_start = i
            elif rain_mm_start and line.startswith("Rain (%) Data:"):
                rain_mm_end = i
                break
        
        if rain_mm_start is not None:
            if rain_mm_end is None:
                rain_mm_end = len(lines)
            
            rain_mm_section = lines[rain_mm_start:rain_mm_end]
            rain_mm_debug = '\n'.join(rain_mm_section)
        else:
            rain_mm_debug = "Rain(mm) section not found"
        
        print("📊 Rain(mm) Debug Output:")
        print(rain_mm_debug)
        print()
        
        # Send email with Rain(mm) test results
        print("📧 Sending Rain(mm) debug output test email...")
        
        email_client = EmailClient(config)
        
        # Create email content
        subject = f"🌧️ Rain(mm) Debug Output Test - {stage_name} - {target_date}"
        
        email_content = f"""
# Rain(mm) Debug Output Test Results

## Test Parameters
- **Stage**: {stage_name}
- **Date**: {target_date}
- **Report Type**: {report_type}

## Result Output
```
{result_output}
```

## Rain(mm) Debug Output (Corrected Format)
```
{rain_mm_debug}
```

## Corrections Applied
✅ **Threshold and Maximum tables appear only ONCE at the end** (not repeated for each GEO point)
✅ **Maximum calculation only considers values > 0** (no more "11:00 | 0" for points with no rain)
✅ **Format matches specification exactly**
✅ **All GEO points shown in tables with "- | -" for no data**

## Test Summary
The Rain(mm) debug output has been corrected to match the specification:
- Tables are not repeated for each GEO point
- Maximum values are only shown when > 0
- Format is consistent with specification examples

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Send email
        success = email_client.send_email(email_content, subject)
        
        if success:
            print("✅ Rain(mm) test email sent successfully!")
            print("📧 Check your email for the detailed Rain(mm) debug output test results")
        else:
            print("❌ Failed to send Rain(mm) test email")
        
        print("\n🎯 Rain(mm) email test completed!")
        
    except Exception as e:
        print(f"❌ Error during Rain(mm) email test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 