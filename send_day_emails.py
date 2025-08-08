#!/usr/bin/env python3
"""
Send real emails for Day function testing using the existing run.py output
"""

import sys
import os
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.notification.email_client import EmailClient
import yaml

def send_day_emails():
    """Send real emails for Day function testing"""
    
    print("🌞 DAY FUNCTION - SENDING REAL EMAILS")
    print("=" * 50)
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize email client
    email_client = EmailClient(config)
    
    # Test MORNING report
    print("🔍 Testing MORNING report...")
    try:
        # Run the morning report
        result = subprocess.run(['python3', 'run.py', '--modus', 'morgen'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract result output from the output
            output_lines = result.stdout.split('\n')
            result_output = ""
            debug_output = ""
            in_result = False
            in_debug = False
            
            for line in output_lines:
                if "📋 RESULT OUTPUT:" in line:
                    in_result = True
                    continue
                elif "📋 DEBUG OUTPUT:" in line:
                    in_result = False
                    in_debug = True
                    continue
                elif in_result and line.strip():
                    result_output = line.strip()
                    in_result = False
                elif in_debug and line.strip():
                    if line.strip() == "# DEBUG DATENEXPORT":
                        debug_output += line + "\n"
                    elif line.strip() == "Debug output temporarily disabled due to comparison errors":
                        debug_output += line + "\n"
            
            # Create email content
            email_content = f"""{result_output}

{debug_output}"""
            
            # Send real email
            print("📧 Sending morning report email...")
            email_client.send_email(
                subject="🌞 Day Function Test - Morning Report",
                body=email_content,
                to_email=config.get('email', {}).get('to_email', 'test@example.com')
            )
            print("✅ MORNING email sent successfully!")
            print(f"📧 Email content: {result_output}")
            
        else:
            print(f"❌ MORNING report failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ MORNING report failed: {e}")
    
    print()
    
    # Test EVENING report
    print("🔍 Testing EVENING report...")
    try:
        # Run the evening report
        result = subprocess.run(['python3', 'run.py', '--modus', 'abend'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract result output from the output
            output_lines = result.stdout.split('\n')
            result_output = ""
            debug_output = ""
            in_result = False
            in_debug = False
            
            for line in output_lines:
                if "📋 RESULT OUTPUT:" in line:
                    in_result = True
                    continue
                elif "📋 DEBUG OUTPUT:" in line:
                    in_result = False
                    in_debug = True
                    continue
                elif in_result and line.strip():
                    result_output = line.strip()
                    in_result = False
                elif in_debug and line.strip():
                    if line.strip() == "# DEBUG DATENEXPORT":
                        debug_output += line + "\n"
                    elif line.strip() == "Debug output temporarily disabled due to comparison errors":
                        debug_output += line + "\n"
            
            # Create email content
            email_content = f"""{result_output}

{debug_output}"""
            
            # Send real email
            print("📧 Sending evening report email...")
            email_client.send_email(
                subject="🌞 Day Function Test - Evening Report",
                body=email_content,
                to_email=config.get('email', {}).get('to_email', 'test@example.com')
            )
            print("✅ EVENING email sent successfully!")
            print(f"📧 Email content: {result_output}")
            
        else:
            print(f"❌ EVENING report failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ EVENING report failed: {e}")
    
    print()
    print("🎯 Both emails sent!")

if __name__ == "__main__":
    send_day_emails() 