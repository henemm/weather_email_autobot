#!/usr/bin/env python3
"""
Test script to verify vigilance warnings integration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wetter.fetch_meteofrance import get_alerts
from notification.email_client import _format_vigilance_warning

def test_vigilance_integration():
    """Test vigilance warnings integration."""
    print("=== VIGILANCE INTEGRATION TEST ===")
    
    # Test coordinates for Conca
    lat, lon = 41.79418, 9.259567
    
    print(f"Testing coordinates: {lat}, {lon}")
    print()
    
    # Get alerts
    alerts = get_alerts(lat, lon)
    print("Raw alerts:")
    for alert in alerts:
        print(f"  {alert.phenomenon}: {alert.level}")
    print()
    
    # Convert to format expected by email client
    alert_dicts = [
        {
            'phenomenon': alert.phenomenon,
            'level': alert.level
        }
        for alert in alerts
    ]
    
    print("Alert dictionaries:")
    for alert_dict in alert_dicts:
        print(f"  {alert_dict}")
    print()
    
    # Test vigilance warning formatting
    vigilance_text = _format_vigilance_warning(alert_dicts)
    print(f"Formatted vigilance warning: '{vigilance_text}'")
    print()
    
    # Test with only high-level alerts (yellow and above)
    high_level_alerts = [
        alert_dict for alert_dict in alert_dicts
        if alert_dict['level'] in ['yellow', 'orange', 'red']
    ]
    
    print("High-level alerts (yellow and above):")
    for alert_dict in high_level_alerts:
        print(f"  {alert_dict}")
    print()
    
    high_level_text = _format_vigilance_warning(high_level_alerts)
    print(f"High-level vigilance warning: '{high_level_text}'")

if __name__ == "__main__":
    test_vigilance_integration() 