#!/usr/bin/env python3
"""
Demo script for debug email append functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from notification.email_client import generate_debug_email_append, generate_gr20_report_text
from config.config_loader import load_config
from report.weather_report_generator import generate_weather_report


def demo_debug_email_append():
    """Demonstrate debug email append functionality."""
    print("🔍 DEBUG EMAIL APPEND DEMO")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config()
        
        # Enable debug mode
        config["debug"]["enabled"] = True
        
        print("✅ Configuration loaded with debug enabled")
        
        # Generate a weather report
        print("\n📊 Generating weather report...")
        result = generate_weather_report('morning', config)
        
        if result["success"]:
            print("✅ Weather report generated successfully")
            
            # Get the report data
            report_data = result
            
            # Generate email text with debug info
            print("\n📧 Generating email text with debug info...")
            email_text = generate_gr20_report_text(report_data, config)
            
            print("\n📄 EMAIL CONTENT:")
            print("=" * 60)
            print(email_text)
            print("=" * 60)
            print(f"📏 Total length: {len(email_text)} characters")
            
            # Check if debug info is present
            if "--- DEBUG INFO ---" in email_text:
                print("\n✅ Debug information found in email!")
                
                # Extract debug section
                debug_start = email_text.find("--- DEBUG INFO ---")
                debug_section = email_text[debug_start:]
                
                print("\n🔍 DEBUG SECTION:")
                print("-" * 40)
                print(debug_section)
                print("-" * 40)
            else:
                print("\n❌ No debug information found in email")
                
        else:
            print(f"❌ Failed to generate weather report: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


def demo_debug_disabled():
    """Demonstrate that debug is disabled by default."""
    print("\n🔍 DEBUG DISABLED DEMO")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config()
        
        # Ensure debug is disabled
        config["debug"]["enabled"] = False
        
        print("✅ Configuration loaded with debug disabled")
        
        # Generate a weather report
        print("\n📊 Generating weather report...")
        result = generate_weather_report('morning', config)
        
        if result["success"]:
            print("✅ Weather report generated successfully")
            
            # Get the report data
            report_data = result
            
            # Generate email text without debug info
            print("\n📧 Generating email text without debug info...")
            email_text = generate_gr20_report_text(report_data, config)
            
            print("\n📄 EMAIL CONTENT:")
            print("=" * 60)
            print(email_text)
            print("=" * 60)
            print(f"📏 Total length: {len(email_text)} characters")
            
            # Check that debug info is NOT present
            if "--- DEBUG INFO ---" not in email_text:
                print("\n✅ Debug information correctly NOT found in email!")
            else:
                print("\n❌ Debug information incorrectly found in email")
                
        else:
            print(f"❌ Failed to generate weather report: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo function."""
    print("🚀 DEBUG EMAIL APPEND FUNCTIONALITY DEMO")
    print("=" * 60)
    
    # Demo with debug enabled
    demo_debug_email_append()
    
    # Demo with debug disabled
    demo_debug_disabled()
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main() 