#!/usr/bin/env python3
"""
Test Email Verification - Check actual email content for both reports
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather.core.morning_evening_refactor import MorningEveningRefactor
import yaml

def main():
    print("📧 EMAIL VERIFICATION TEST")
    print("=" * 50)
    
    # Load configuration
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    refactor = MorningEveningRefactor(config)
    
    # Test parameters
    stage_name = "Vergio"
    date_str = "2025-08-02"
    
    print(f"📍 Stage: {stage_name}")
    print(f"📅 Date: {date_str}")
    print()
    
    # Test both report types
    for report_type in ["morning", "evening"]:
        print(f"🔍 Testing {report_type.upper()} report...")
        print("-" * 30)
        
        try:
            # Generate report
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
            
            # Show email content
            print(f"📧 EMAIL CONTENT ({report_type.upper()}):")
            print("=" * 40)
            email_content = f"""{result_output}

# DEBUG DATENEXPORT

{tg_overview}{night_section}"""
            
            print(email_content)
            print("=" * 40)
            
            # Verification checks
            print(f"🔍 VERIFICATION CHECKS ({report_type.upper()}):")
            print("-" * 30)
            
            # Check 1: Result Output contains Night value
            if "N" in result_output:
                print("✅ Result Output contains Night value (N)")
            else:
                print("❌ Result Output missing Night value (N)")
            
            # Check 2: Debug section starts with NIGHT (GROSS)
            if "NIGHT (N) - temp_min:" in night_section:
                print("✅ Debug section starts with NIGHT (GROSS)")
            else:
                print("❌ Debug section does not start with NIGHT (GROSS)")
            
            # Check 3: Contains T-G references
            if "T1G" in night_section or "T2G" in night_section or "T3G" in night_section:
                print("✅ Contains T-G references")
            else:
                print("❌ Missing T-G references")
            
            # Check 4: Contains MIN value
            if "MIN |" in night_section:
                print("✅ Contains MIN value")
            else:
                print("❌ Missing MIN value")
            
            # Check 5: Values are rounded (no decimals)
            import re
            min_match = re.search(r'MIN \| (\d+(?:\.\d+)?)', night_section)
            if min_match:
                min_value = min_match.group(1)
                if '.' not in min_value:
                    print("✅ MIN value is rounded (no decimals)")
                else:
                    print("❌ MIN value has decimals (should be rounded)")
            else:
                print("❌ Could not find MIN value")
            
            # Check 6: T-G reference is correct for report type
            if report_type == "morning":
                if "T1G" in night_section:
                    print("✅ Morning report uses T1G (today's stage)")
                else:
                    print("❌ Morning report should use T1G")
            else:  # evening
                if "T1G" in night_section:
                    print("✅ Evening report uses T1G (today's stage)")
                else:
                    print("❌ Evening report should use T1G")
            
            print()
            
        except Exception as e:
            print(f"❌ Error in {report_type} report: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("🎯 Email verification completed!")

if __name__ == "__main__":
    main() 