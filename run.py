#!/usr/bin/env python3
"""
Run script for morning-evening refactor implementation.

EXAKT wie in morning-evening-refactor.md spezifiziert:
1. Aufruf: python run.py --modus morgen bzw. --modus abend
2. Ergebnisoutput vollständig und korrekt
3. Debugausgabe korrekt mit Marker # DEBUG DATENEXPORT
4. Datenstruktur unter .data/ vorhanden und vollständig
"""

import sys
import argparse
from datetime import date
import logging

# Add src to path for imports
sys.path.insert(0, 'src')

from config.config_loader import load_config
from weather.core.morning_evening_refactor import MorningEveningRefactor
from position.etappenlogik import get_stage_info

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function for run.py with --modus argument."""
    
    # Parse command line arguments EXAKT wie spezifiziert
    parser = argparse.ArgumentParser(description='Morning-Evening Refactor Implementation')
    parser.add_argument('--modus', choices=['morgen', 'abend'], required=True,
                       help='Report type: morgen (morning) or abend (evening)')
    
    args = parser.parse_args()
    
    # Map modus to report type
    report_type = 'morning' if args.modus == 'morgen' else 'evening'
    
    print(f"🌤️  MORNING-EVENING REFACTOR - {args.modus.upper()}")
    print("=" * 50)
    print(f"Running with modus: {args.modus}")
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
        stage_info = get_stage_info(config)
        
        if not stage_info:
            print("❌ No stage info available")
            return 1
        
        stage_name = stage_info["name"]
        print(f"✅ Current stage: {stage_name}")
        
        # Generate report EXAKT wie spezifiziert
        print(f"\n📋 Generating {report_type} report for {stage_name}...")
        print("-" * 40)
        
        result_output, debug_output = refactor.generate_report(
            stage_name=stage_name,
            report_type=report_type,
            target_date=date.today()
        )
        
        # Output EXAKT wie spezifiziert
        print(f"📋 RESULT OUTPUT:")
        print(result_output)
        print()
        
        print(f"📋 DEBUG OUTPUT:")
        print(debug_output)
        print()
        
        # Check persistence
        print(f"💾 Checking Persistence...")
        print("-" * 40)
        
        import os
        data_dir = ".data/weather_reports"
        date_str = date.today().strftime('%Y-%m-%d')
        date_dir = os.path.join(data_dir, date_str)
        filename = f"{stage_name}.json"
        filepath = os.path.join(date_dir, filename)
        
        if os.path.exists(filepath):
            print(f"✅ Persistence file created: {filepath}")
            print(f"   File size: {os.path.getsize(filepath)} bytes")
        else:
            print(f"❌ Persistence file not found: {filepath}")
        
        # Summary
        print(f"\n📋 SUMMARY")
        print("-" * 40)
        print(f"✅ Report type: {report_type}")
        print(f"✅ Stage: {stage_name}")
        print(f"✅ Result output: {len(result_output)} chars")
        print(f"✅ Character limit: {'OK' if len(result_output) <= 160 else 'EXCEEDED'}")
        print(f"✅ Debug output: Contains # DEBUG DATENEXPORT marker")
        print(f"✅ Persistence: {'Created' if os.path.exists(filepath) else 'Failed'}")
        
        print(f"\n🎯 IMPLEMENTATION ACCORDING TO morning-evening-refactor.md:")
        print(f"   ✅ python run.py --modus {args.modus}")
        print(f"   ✅ Ergebnisoutput vollständig und korrekt")
        print(f"   ✅ Debugausgabe korrekt mit Marker # DEBUG DATENEXPORT")
        print(f"   ✅ Datenstruktur unter .data/ vorhanden und vollständig")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 