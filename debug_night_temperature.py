#!/usr/bin/env python3
"""
Debug script to check why we're not getting temperature data from the API.
"""

import sys
import os
from datetime import date
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config_loader import load_config
from wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_night_temperature():
    """Debug why we're not getting temperature data."""
    
    print("🔍 DEBUG NIGHT TEMPERATURE")
    print("=" * 40)
    
    try:
        # Load configuration
        config = load_config()
        start_date = config.get('startdatum', '2025-07-27')
        print(f"Start date: {start_date}")
        
        # Calculate today's stage
        from datetime import datetime, timedelta
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        today = date.today()
        days_since_start = (today - start_date_obj).days
        print(f"Days since start: {days_since_start}")
        
        # Get stage information
        import json
        with open("etappen.json", "r") as f:
            etappen_data = json.load(f)
        
        if days_since_start >= len(etappen_data):
            print(f"❌ Stage index {days_since_start} out of range (max: {len(etappen_data)-1})")
            return
        
        stage = etappen_data[days_since_start]
        print(f"Today's stage: {stage['name']}")
        print(f"Stage points: {len(stage['punkte'])}")
        
        # Get the last point
        last_point = stage['punkte'][-1]
        lat, lon = last_point['lat'], last_point['lon']
        print(f"Last point: {lat}, {lon}")
        
        # Fetch weather data
        print(f"\n🌤️ Fetching weather data...")
        api = EnhancedMeteoFranceAPI()
        point_data = api.get_complete_forecast_data(lat, lon, f"{stage['name']}_last_point")
        
        # Check daily data
        daily_data = point_data.get('daily_data', [])
        print(f"Daily data entries: {len(daily_data)}")
        
        if daily_data:
            print(f"\n📊 Daily data structure:")
            for i, entry in enumerate(daily_data[:3]):  # Show first 3 entries
                print(f"Entry {i}: {entry}")
            
            # Look for today's entry
            today_str = today.strftime('%Y-%m-%d')
            print(f"\n🔍 Looking for date: {today_str}")
            
            today_entry = None
            for entry in daily_data:
                entry_date = entry.get('date')
                print(f"Entry date: {entry_date}")
                if entry_date == today_str:
                    today_entry = entry
                    break
            
            if today_entry:
                print(f"\n✅ Found today's entry:")
                print(f"   Entry: {today_entry}")
                temp_min = today_entry.get('temp_min')
                temp_max = today_entry.get('temp_max')
                print(f"   temp_min: {temp_min}")
                print(f"   temp_max: {temp_max}")
                
                if temp_min is not None:
                    print(f"   ✅ temp_min found: {temp_min}")
                else:
                    print(f"   ❌ temp_min is None")
            else:
                print(f"\n❌ No entry found for today ({today_str})")
        else:
            print(f"\n❌ No daily data available")
        
        # Check if debug is enabled
        debug_enabled = config.get('debug', {}).get('enabled', False)
        print(f"\n🔧 Debug enabled: {debug_enabled}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_night_temperature() 