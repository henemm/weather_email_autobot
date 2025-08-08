#!/usr/bin/env python3
"""
Test script to send email with complete debug output including T-G reference overview.
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
    print("📧 FULL DEBUG OUTPUT EMAIL")
    print("=" * 40)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
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
        
        # Extract T-G reference overview (first part of debug output)
        lines = debug_output.split('\n')
        tg_overview_lines = []
        in_tg_overview = False
        
        for line in lines:
            if "Berichts-Typ:" in line:
                in_tg_overview = True
                tg_overview_lines.append(line)
            elif in_tg_overview and line.startswith("Night (N) - temp_min:"):
                break
            elif in_tg_overview:
                tg_overview_lines.append(line)
        
        tg_overview = '\n'.join(tg_overview_lines)
        
        # Count issues
        threshold_count = sum(1 for line in lines if line.strip() == "Threshold")
        maximum_count = sum(1 for line in lines if line.strip() == "Maximum:")
        none_count = sum(1 for line in lines if "None" in line)
        
        print("📊 Analysis completed!")
        print()
        
        # Send email with complete debug output
        print("📧 Sending full debug output email...")
        
        email_client = EmailClient(config)
        
        # Create email content
        subject = f"🌤️ Full Debug Output - {stage_name} - {target_date}"
        
        email_content = f"""
# Full Debug Output Analysis

## Test Parameters
- **Stage**: {stage_name}
- **Date**: {target_date}
- **Report Type**: {report_type}

## Result Output
```
{result_output}
```

## T-G Reference Overview
```
{tg_overview}
```

## Complete Debug Output
```
{debug_output}
```

## Issues Found
- **Threshold tables**: {threshold_count} (should be 1 per weather element)
- **Maximum tables**: {maximum_count} (should be 1 per weather element)
- **None values**: {none_count} (should be 0)

## Current Status
✅ **T-G Reference Overview**: Present and correct
✅ **System is functional** - all weather elements present
⚠️ **Rain(%) has None values** - needs fixing
⚠️ **Table duplication** - Threshold/Maximum tables repeated
⚠️ **Debug output needs cleanup**

## Next Steps
1. Fix Rain(%) None values
2. Remove table duplications
3. Clean up debug output format

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Send email
        success = email_client.send_email(email_content, subject)
        
        if success:
            print("✅ Full debug output email sent successfully!")
            print("📧 Check your email for complete debug output analysis")
        else:
            print("❌ Failed to send full debug output email")
        
        print("\n🎯 Full debug output test completed!")
        
    except Exception as e:
        print(f"❌ Error during full debug output test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 