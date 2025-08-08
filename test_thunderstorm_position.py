#!/usr/bin/env python3
"""
Live test for Thunderstorm position implementation in Evening report.
Sends a real email with thunderstorm results.
"""

import yaml
import sys
import os
from datetime import date, datetime, timedelta
from src.weather.core.morning_evening_refactor import MorningEveningRefactor
from src.notification.email_client import EmailClient

def main():
    print("🌩️ LIVE TEST: Thunderstorm Position Implementation")
    print("=" * 60)
    
    try:
        # Load configuration
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Create refactor instance
        refactor = MorningEveningRefactor(config)
        
        # Test parameters
        stage_name = "Test"  # Use Test stage
        report_type = "evening"  # Evening report
        target_date = date.today() + timedelta(days=1)  # Tomorrow
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Date: {target_date}")
        print(f"📋 Report Type: {report_type}")
        print()
        
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
        if "TH:" in result_output:
            print("✅ Thunderstorm format found in result output!")
        else:
            print("❌ No thunderstorm format found in result output")
        
        # Send email with results
        print("\n📧 Sending email with thunderstorm results...")
        
        email_client = EmailClient(config)
        
        # Create email content
        subject = f"🌩️ Thunderstorm Position Test - {stage_name} - {target_date}"
        
        email_content = f"""
# Thunderstorm Position Implementation Test

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

## Analysis
- Thunderstorm data found: {"✅ Yes" if "Thunderstorm Data:" in debug_output else "❌ No"}
- Thunderstorm format found: {"✅ Yes" if "TH:" in result_output else "❌ No"}

## Expected Behavior
- If no thunderstorms: TH-
- If thunderstorms: TH:level@time(max_level@max_time)

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Send email
        success = email_client.send_email(
            message_text=email_content,
            subject=subject
        )
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email")
        
        print("\n🎯 Live test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 