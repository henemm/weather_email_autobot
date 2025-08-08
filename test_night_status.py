#!/usr/bin/env python3
"""
Test Night Function Status - Before Refactoring (Evening Report)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
from notification.email_client import EmailClient
import yaml

def main():
    print("🌙 NIGHT FUNCTION STATUS TEST (EVENING REPORT)")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    email_client = EmailClient(config)
    
    # Test parameters - EVENING REPORT
    stage_name = "Vergio"
    date_str = "2025-08-02"
    report_type = "evening"  # Changed to evening
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {date_str}")
    print(f"📋 Report Type: {report_type}")
    print()
    
    try:
        # Generate report
        print("🔍 Generating report...")
        result_output, debug_output = refactor.generate_report(stage_name, report_type, date_str)
        
        # Extract T-G reference overview and Night section from debug output
        lines = debug_output.split('\n')
        tg_overview = ""
        night_section = ""
        in_tg_overview = False
        in_night_section = False
        
        for line in lines:
            # Extract T-G reference overview
            if "Berichts-Typ:" in line:
                in_tg_overview = True
                tg_overview += line + "\n"
            elif in_tg_overview and line.startswith("NIGHT (N) - temp_min:"):
                in_tg_overview = False
                in_night_section = True
                night_section += line + "\n"
            elif in_tg_overview:
                tg_overview += line + "\n"
            # Extract Night section
            elif in_night_section and line.startswith("DAY (D) - temp_max:"):
                break
            elif in_night_section:
                night_section += line + "\n"
        
        # Send status email
        print("📧 Sending Night function status email...")
        email_content = f"""{result_output}

# DEBUG DATENEXPORT

{tg_overview}{night_section}"""
        
        success = email_client.send_email(email_content, f"🌙 Night Function Status - {stage_name} - {date_str} - {report_type}")
        
        if success:
            print("✅ Status email sent successfully!")
            print("📧 Please check your email and approve the Night function refactoring")
        else:
            print("❌ Failed to send status email")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 