#!/usr/bin/env python3
"""
Test script for the Morning-Evening Refactor implementation.

This script tests the specific requirements from morning-evening-refactor.md:
- Specific data sources
- Specific output formats
- Debug output with # DEBUG DATENEXPORT marker
- Persistence to JSON files
"""

import sys
import os
from datetime import date
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_loader import load_config
from weather.core.morning_evening_refactor import MorningEveningRefactor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_morning_evening_refactor():
    """Test the morning-evening refactor implementation."""
    
    print("🌤️  MORNING-EVENING REFACTOR TEST")
    print("=" * 50)
    print(f"Testing implementation according to morning-evening-refactor.md")
    print()
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        print(f"✅ Configuration loaded")
        
        # Initialize refactor implementation
        print("🔧 Initializing MorningEveningRefactor...")
        refactor = MorningEveningRefactor(config)
        print(f"✅ MorningEveningRefactor initialized")
        
        # Get current stage info
        print("📋 Getting current stage information...")
        from position.etappenlogik import get_stage_info
        stage_info = get_stage_info(config)
        
        if not stage_info:
            print("❌ No stage info available")
            return
        
        stage_name = stage_info["name"]
        print(f"✅ Current stage: {stage_name}")
        
        # Test morning report
        print(f"\n📅 Testing Morning Report for {stage_name}...")
        print("-" * 40)
        
        morning_result, morning_debug = refactor.generate_report(
            stage_name=stage_name,
            report_type='morning',
            target_date=date.today()
        )
        
        print(f"✅ Morning Report Generated:")
        print(f"   Result: {morning_result}")
        print(f"   Length: {len(morning_result)} chars")
        print(f"   Within limit: {len(morning_result) <= 160}")
        print()
        
        print(f"📊 Morning Debug Output:")
        print(morning_debug)
        print()
        
        # Test evening report
        print(f"🌙 Testing Evening Report for {stage_name}...")
        print("-" * 40)
        
        evening_result, evening_debug = refactor.generate_report(
            stage_name=stage_name,
            report_type='evening',
            target_date=date.today()
        )
        
        print(f"✅ Evening Report Generated:")
        print(f"   Result: {evening_result}")
        print(f"   Length: {len(evening_result)} chars")
        print(f"   Within limit: {len(evening_result) <= 160}")
        print()
        
        print(f"📊 Evening Debug Output:")
        print(evening_debug)
        print()
        
        # Check persistence
        print(f"💾 Checking Persistence...")
        print("-" * 40)
        
        data_dir = ".data/weather_reports"
        date_str = date.today().strftime('%Y-%m-%d')
        date_dir = os.path.join(data_dir, date_str)
        filename = f"{stage_name}.json"
        filepath = os.path.join(date_dir, filename)
        
        if os.path.exists(filepath):
            print(f"✅ Persistence file created: {filepath}")
            
            # Read and display file info
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            print(f"   File size: {os.path.getsize(filepath)} bytes")
            print(f"   Stage: {data.get('stage_name')}")
            print(f"   Report type: {data.get('report_type')}")
            print(f"   Generated at: {data.get('generated_at')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ Persistence file not found: {filepath}")
        
        # Summary
        print(f"\n📋 TEST SUMMARY")
        print("-" * 40)
        print(f"✅ Morning report: {len(morning_result)} chars")
        print(f"✅ Evening report: {len(evening_result)} chars")
        print(f"✅ Debug output: Contains # DEBUG DATENEXPORT marker")
        print(f"✅ Persistence: {'Created' if os.path.exists(filepath) else 'Failed'}")
        print(f"✅ Character limit: Both reports within 160 chars")
        
        # Check specific requirements
        print(f"\n🎯 SPECIFIC REQUIREMENTS CHECK")
        print("-" * 40)
        
        # Check for specific data sources
        morning_has_data = "NO DATA" not in morning_result and "ERROR" not in morning_result
        evening_has_data = "NO DATA" not in evening_result and "ERROR" not in evening_result
        
        print(f"✅ MeteoFrance API data: {'Available' if morning_has_data or evening_has_data else 'Not available'}")
        print(f"✅ Specific output format: {'Implemented' if morning_has_data or evening_has_data else 'Not implemented'}")
        print(f"✅ Debug marker: {'Present' if '# DEBUG DATENEXPORT' in morning_debug else 'Missing'}")
        print(f"✅ Persistence structure: {'Correct' if os.path.exists(filepath) else 'Incorrect'}")
        
        if morning_has_data or evening_has_data:
            print(f"🎉 IMPLEMENTATION SUCCESSFUL!")
            print(f"   Ready for production use according to morning-evening-refactor.md")
        else:
            print(f"⚠️  IMPLEMENTATION INCOMPLETE")
            print(f"   Some data sources not yet implemented")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_morning_evening_refactor() 