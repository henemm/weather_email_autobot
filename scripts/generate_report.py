#!/usr/bin/env python3
"""
Simple Weather Report Generator.

This script allows you to generate weather reports in different modes:
- morning: Morning report (04:30 format)
- evening: Evening report (19:00 format) 
- dynamic: Dynamic update report

Usage:
    python scripts/generate_report.py --mode morning
    python scripts/generate_report.py --mode evening
    python scripts/generate_report.py --mode dynamic
"""

import argparse
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report.weather_report_generator import generate_weather_report
from config.config_loader import load_config


def main():
    """Main function to generate weather reports."""
    parser = argparse.ArgumentParser(
        description="Generate GR20 weather reports in different modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_report.py --mode morning    # Generate morning report
  python scripts/generate_report.py --mode evening    # Generate evening report  
  python scripts/generate_report.py --mode dynamic    # Generate dynamic report
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["morning", "evening", "dynamic"],
        required=True,
        help="Report mode: morning, evening, or dynamic"
    )
    
    parser.add_argument(
        "--send", 
        action="store_true",
        help="Send the report via email and SMS (if configured)"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    print(f"🌤️  Generating {args.mode} weather report...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Load configuration
        if args.verbose:
            print("📋 Loading configuration...")
        config = load_config()
        
        # Generate the report
        if args.verbose:
            print(f"🔍 Generating {args.mode} report...")
        
        result = generate_weather_report(args.mode, config)
        
        if result["success"]:
            print("✅ Report generated successfully!")
            print()
            
            # Display the report
            print("📄 WEATHER REPORT:")
            print("=" * 60)
            print(result["report_text"])
            print("=" * 60)
            print(f"📏 Length: {len(result['report_text'])} characters")
            print()
            
            # Send the report if requested
            if args.send:
                print("📧 Sending report...")
                
                # Import here to avoid circular imports
                from notification.email_client import EmailClient
                from notification.sms_client import ModularSmsClient
                
                # Send email
                email_client = EmailClient(config)
                email_success = email_client.send_gr20_report(result)
                
                if email_success:
                    print("✅ Email sent successfully")
                else:
                    print("❌ Failed to send email")
                
                # Send SMS if configured
                try:
                    sms_client = ModularSmsClient(config)
                    sms_success = sms_client.send_gr20_report(result)
                    
                    if sms_success:
                        print("✅ SMS sent successfully")
                    else:
                        print("❌ Failed to send SMS")
                        
                except Exception as e:
                    print(f"⚠️  SMS not available: {e}")
                
                print()
            
            # Show additional info if verbose
            if args.verbose:
                print("📊 REPORT DETAILS:")
                print(f"   Location: {result.get('location', 'Unknown')}")
                print(f"   Risk Score: {result.get('risk_percentage', 0):.1f}%")
                print(f"   Report Type: {result.get('report_type', 'Unknown')}")
                print()
            
            print("🎉 Done!")
            
        else:
            print("❌ Failed to generate report:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 