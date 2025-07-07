#!/usr/bin/env python3
"""
Test script to verify dynamic report triggering.

This script tests the dynamic report logic to ensure it works correctly
with the current configuration.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.logic.report_scheduler import should_send_dynamic_report, ReportScheduler
from src.logic.analyse_weather import compute_risk


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml."""
    import yaml
    
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_dynamic_report_triggering():
    """Test dynamic report triggering logic."""
    print("🧪 Testing Dynamic Report Triggering")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    print(f"✓ Configuration loaded")
    
    # Check if delta_thresholds section exists (used for dynamic reports)
    delta_thresholds = config.get("delta_thresholds", {})
    if not delta_thresholds:
        print("❌ No 'delta_thresholds' section in config.yaml")
        return False
    
    print(f"✓ Delta thresholds configuration found:")
    print(f"  - thunderstorm_probability: {delta_thresholds.get('thunderstorm_probability', 'NOT SET')}")
    print(f"  - rain_probability: {delta_thresholds.get('rain_probability', 'NOT SET')}")
    print(f"  - wind_speed: {delta_thresholds.get('wind_speed', 'NOT SET')}")
    print(f"  - temperature: {delta_thresholds.get('temperature', 'NOT SET')}")
    
    # Test case 1: Significant risk change
    print("\n📊 Test Case 1: Significant Risk Change")
    current_risk = 0.8
    previous_risk = 0.2
    last_report_time = datetime.now() - timedelta(minutes=90)  # 90 minutes ago
    daily_report_count = 0
    
    should_send = should_send_dynamic_report(
        current_risk, previous_risk, last_report_time, daily_report_count, config
    )
    
    risk_change = abs(current_risk - previous_risk)
    print(f"  Current risk: {current_risk:.2f}")
    print(f"  Previous risk: {previous_risk:.2f}")
    print(f"  Risk change: {risk_change:.2f}")
    print(f"  Should send: {'✅ YES' if should_send else '❌ NO'}")
    
    if not should_send:
        print("❌ Expected dynamic report to be triggered for significant risk change")
        return False
    
    # Test case 2: Insufficient risk change
    print("\n📊 Test Case 2: Insufficient Risk Change")
    current_risk = 0.35
    previous_risk = 0.30
    last_report_time = datetime.now() - timedelta(minutes=90)
    daily_report_count = 0
    
    should_send = should_send_dynamic_report(
        current_risk, previous_risk, last_report_time, daily_report_count, config
    )
    
    risk_change = abs(current_risk - previous_risk)
    print(f"  Current risk: {current_risk:.2f}")
    print(f"  Previous risk: {previous_risk:.2f}")
    print(f"  Risk change: {risk_change:.2f}")
    print(f"  Should send: {'✅ YES' if should_send else '❌ NO'}")
    
    if should_send:
        print("❌ Expected no dynamic report for small risk change")
        return False
    
    # Test case 3: Time interval too short
    print("\n📊 Test Case 3: Time Interval Too Short")
    current_risk = 0.8
    previous_risk = 0.2
    last_report_time = datetime.now() - timedelta(minutes=30)  # Only 30 minutes ago
    daily_report_count = 0
    
    should_send = should_send_dynamic_report(
        current_risk, previous_risk, last_report_time, daily_report_count, config
    )
    
    time_since_last = (datetime.now() - last_report_time).total_seconds() / 60
    print(f"  Time since last report: {time_since_last:.1f} minutes")
    print(f"  Should send: {'✅ YES' if should_send else '❌ NO'}")
    
    if should_send:
        print("❌ Expected no dynamic report when time interval too short")
        return False
    
    # Test case 4: Daily limit reached
    print("\n📊 Test Case 4: Daily Limit Reached")
    current_risk = 0.8
    previous_risk = 0.2
    last_report_time = datetime.now() - timedelta(minutes=90)
    daily_report_count = 3  # At maximum
    
    should_send = should_send_dynamic_report(
        current_risk, previous_risk, last_report_time, daily_report_count, config
    )
    
    print(f"  Daily report count: {daily_report_count}")
    print(f"  Should send: {'✅ YES' if should_send else '❌ NO'}")
    
    if should_send:
        print("❌ Expected no dynamic report when daily limit reached")
        return False
    
    print("\n✅ All dynamic report trigger tests passed!")
    return True


def test_scheduler_integration():
    """Test ReportScheduler integration."""
    print("\n🔧 Testing ReportScheduler Integration")
    print("=" * 50)
    
    config = load_config()
    
    # Create scheduler
    scheduler = ReportScheduler("test_state.json", config)
    print(f"✓ ReportScheduler created")
    
    # Test current state
    print(f"  Current state:")
    print(f"    - Last risk value: {scheduler.current_state.last_risk_value:.2f}")
    print(f"    - Daily dynamic count: {scheduler.current_state.daily_dynamic_report_count}")
    print(f"    - Last dynamic report: {scheduler.current_state.last_dynamic_report}")
    
    # Test should_send_report
    current_time = datetime.now()
    current_risk = 0.8
    
    should_send = scheduler.should_send_report(current_time, current_risk)
    report_type = scheduler.get_report_type(current_time, current_risk)
    
    print(f"  Should send report: {'✅ YES' if should_send else '❌ NO'}")
    print(f"  Report type: {report_type}")
    
    return True


def main():
    """Main test function."""
    print("🚀 Dynamic Report Trigger Test")
    print("=" * 60)
    
    success = True
    
    # Test basic triggering logic
    if not test_dynamic_report_triggering():
        success = False
    
    # Test scheduler integration
    if not test_scheduler_integration():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Dynamic reports should work correctly.")
    else:
        print("💥 Some tests failed. Check the configuration and logic.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 