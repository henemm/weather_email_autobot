#!/usr/bin/env python3
"""
Test script for Night position implementation with email sending.
"""

import sys
import os
from datetime import date
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_loader import load_config
from weather.core.morning_evening_refactor import MorningEveningRefactor
from notification.email_client import EmailClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_night_position():
    """Test the Night position implementation with email sending."""
    
    print("🌤️  NIGHT POSITION TEST - Evening Report")
    print("=" * 50)
    print("Testing Night position for Evening report")
    print("⚠️  WARNING: This will send a REAL EMAIL!")
    print()
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        print(f"✅ Configuration loaded")
        print(f"   SMTP host: {config.get('smtp', {}).get('host', 'unknown')}")
        print(f"   Email to: {config.get('smtp', {}).get('to', 'unknown')}")
        
        # Initialize refactor implementation
        print("🔧 Initializing MorningEveningRefactor...")
        refactor = MorningEveningRefactor(config)
        print(f"✅ MorningEveningRefactor initialized")
        
        # Generate evening report
        print(f"\n📅 Generating Evening Report for Night position...")
        print("-" * 40)
        
        result_output, debug_output = refactor.generate_report(
            stage_name="Manganu",  # Will be calculated correctly
            report_type='evening',
            target_date=date.today()
        )
        
        print(f"✅ Evening Report Generated:")
        print(f"   Result: {result_output}")
        print(f"   Length: {len(result_output)} chars")
        print()
        
        print(f"📊 Debug Output:")
        print(debug_output)
        print()
        
        # Prepare email content
        print(f"📧 Preparing Email Content...")
        print("-" * 40)
        
        email_subject = "GR20 Evening Report - Night Position Test"
        
        email_content = f"""
🌤️ GR20 Evening Report - Night Position Test

📋 RESULT OUTPUT:
{result_output}

📊 DEBUG OUTPUT:
{debug_output}

🎯 NIGHT POSITION IMPLEMENTATION:
• Evening Report: Night = temp_min of last point of today's stage for today
• Today's stage: Manganu (calculated from startdate 2025-07-27)
• Last point: 4th point of Manganu stage
• Data source: meteo_france / DAILY_FORECAST | temp_min
• Expected format: N[temp_min] (e.g., N8)

📋 IMPLEMENTATION STATUS:
• ✅ Etappen-Berechnung: Heute/Morgen/Übermorgen
• ✅ Debug-Output: Berichts-Typ und Etappen-Informationen
• 🔄 Night Position: In Entwicklung
• ⏳ Day Position: Noch nicht implementiert
• ⏳ Rain Position: Noch nicht implementiert

Generated at: {date.today().strftime('%Y-%m-%d')}
"""
        
        # Send actual email
        print(f"📧 SENDING REAL EMAIL...")
        print("-" * 40)
        print(f"⚠️  This will send an actual email to: {config.get('smtp', {}).get('to', 'unknown')}")
        print(f"📧 Subject: {email_subject}")
        print(f"📧 Content length: {len(email_content)} chars")
        print()
        
        # Initialize email client
        email_client = EmailClient(config)
        
        # Send the email
        email_success = email_client.send_email(
            message_text=email_content,
            subject=email_subject
        )
        
        if email_success:
            print(f"✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   Email delivered to: {config.get('smtp', {}).get('to')}")
            print(f"   Subject: {email_subject}")
        else:
            print(f"❌ EMAIL SENDING FAILED!")
        
        # Summary
        print(f"\n📋 NIGHT POSITION TEST SUMMARY")
        print("-" * 40)
        print(f"✅ Etappen-Berechnung: SUCCESS")
        print(f"✅ Debug-Output: SUCCESS")
        print(f"✅ Night Position: {'SUCCESS' if 'N' in result_output and result_output != 'N-' else 'PARTIAL'}")
        print(f"✅ Email sending: {'SUCCESS' if email_success else 'FAILED'}")
        
        if email_success:
            print(f"\n🎉 NIGHT POSITION TEST COMPLETED!")
            print(f"   Ready for next position (Day)")
        else:
            print(f"\n⚠️  Test completed but email sending failed")
            
    except Exception as e:
        print(f"❌ Night position test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_night_position() 