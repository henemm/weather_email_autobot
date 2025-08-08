#!/usr/bin/env python3
"""
GR20 Weather Report Monitor V2 - Using MorningEveningRefactor.

This script runs the new GR20 weather report system using the MorningEveningRefactor class.
"""

import sys
import os
import yaml
import argparse
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weather.core.morning_evening_refactor import MorningEveningRefactor
from notification.email_client import EmailClient
from notification.modular_sms_client import ModularSmsClient
from utils.env_loader import get_env_var
from config.config_loader import load_config as load_config_with_env


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration with environment variables."""
    try:
        return load_config_with_env(config_path)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def get_current_stage_info(config: dict) -> tuple:
    """Get current stage information."""
    try:
        import json
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
        
        start_date = datetime.strptime(config.get('startdatum', '2025-07-27'), '%Y-%m-%d').date()
        today = date.today()
        days_since_start = (today - start_date).days
        
        if days_since_start < len(etappen_data):
            current_stage = etappen_data[days_since_start]
            return current_stage['name'], current_stage['punkte']
        else:
            print(f"Warning: Day {days_since_start} exceeds available stages")
            return None, None
            
    except Exception as e:
        print(f"Error getting stage info: {e}")
        return None, None


def send_email_report(config: dict, report_type: str, stage_name: str, result_output: str, debug_output: str):
    """Send email report."""
    try:
        email_client = EmailClient(config)
        
        # Email configuration
        sender_email = get_env_var("SENDER_EMAIL")
        recipient_email = get_env_var("RECIPIENT_EMAIL")
        
        if not sender_email or not recipient_email:
            print("Warning: Email configuration missing")
            return False
        
        # Subject
        subject = f"GR20 Wetterbericht {report_type.capitalize()} - {stage_name}"
        
        # Content
        email_content = f"{result_output}\n\n{debug_output}"
        
        # Send email
        success = email_client.send_email(email_content, subject)
        
        if success:
            print(f"✅ Email sent successfully: {subject}")
        else:
            print(f"❌ Failed to send email: {subject}")
            
        return success
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_sms_report(config: dict, report_type: str, stage_name: str, result_output: str):
    """Send SMS report."""
    try:
        sms_client = ModularSmsClient(config)
        
        # SMS configuration
        recipient_phone = get_env_var("RECIPIENT_PHONE")
        
        if not recipient_phone:
            print("Warning: SMS configuration missing")
            return False
        
        # Content (SMS only gets result output, no debug)
        sms_content = f"GR20 {report_type.capitalize()}: {result_output}"
        
        # Send SMS
        success = sms_client.send_sms(sms_content, recipient_phone)
        
        if success:
            print(f"✅ SMS sent successfully")
        else:
            print(f"❌ Failed to send SMS")
            
        return success
        
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='GR20 Weather Report Monitor V2')
    parser.add_argument('--modus', choices=['morning', 'evening'], required=True,
                       help='Report type: morning or evening')
    parser.add_argument('--stage', type=str, help='Specific stage name (optional)')
    parser.add_argument('--date', type=str, help='Specific date YYYY-MM-DD (optional)')
    parser.add_argument('--email', action='store_true', help='Send email report')
    parser.add_argument('--sms', action='store_true', help='Send SMS report')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    print(f"🌤️ GR20 Weather Report Monitor V2")
    print(f"📅 Report Type: {args.modus}")
    print(f"📅 Date: {args.date or 'today'}")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return 1
    
    # Enable debug if requested
    if args.debug:
        config['debug'] = {'enabled': True}
    
    try:
        # Create weather processor
        weather_processor = MorningEveningRefactor(config)
        
        # Determine stage and date
        if args.stage:
            stage_name = args.stage
        else:
            stage_name, stage_points = get_current_stage_info(config)
            if not stage_name:
                print("❌ Could not determine current stage")
                return 1
        
        if args.date:
            target_date = args.date
        else:
            target_date = date.today().strftime('%Y-%m-%d')
        
        print(f"📍 Stage: {stage_name}")
        print(f"📅 Target Date: {target_date}")
        print()
        
        # Generate report
        print(f"🔄 Generating {args.modus} report...")
        result_output, debug_output = weather_processor.generate_report(stage_name, args.modus, target_date)
        
        print(f"✅ Report generated successfully")
        print(f"📊 Result Output: {result_output}")
        print(f"📝 Debug Output Length: {len(debug_output)} characters")
        print()
        
        # Send reports
        success_count = 0
        
        if args.email:
            print("📧 Sending email report...")
            if send_email_report(config, args.modus, stage_name, result_output, debug_output):
                success_count += 1
        
        if args.sms:
            print("📱 Sending SMS report...")
            if send_sms_report(config, args.modus, stage_name, result_output):
                success_count += 1
        
        # If no specific send method requested, send both
        if not args.email and not args.sms:
            print("📧 Sending email report...")
            if send_email_report(config, args.modus, stage_name, result_output, debug_output):
                success_count += 1
            
            print("📱 Sending SMS report...")
            if send_sms_report(config, args.modus, stage_name, result_output):
                success_count += 1
        
        print()
        print(f"✅ Completed: {success_count} reports sent successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 