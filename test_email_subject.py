#!/usr/bin/env python3
"""
Test script for the new email subject generation.
Tests the subject format according to the email_format specification.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.notification.email_client import EmailClient

class MockEmailClient:
    """Mock EmailClient for testing subject generation without SMTP config."""
    
    def __init__(self, config):
        self.config = config
    
    def _generate_dynamic_subject(self, report_data):
        """
        Generate email subject according to email_format specification.
        
        Format: {subject} {etappe}: {risk_level} - {highest_risk} ({report_type})
        """
        # Get base subject from config
        base_subject = self.config.get("smtp", {}).get("subject", "GR20 Wetter")
        
        # Get report type
        report_type = report_data.get("report_type", "morning")
        
        # Get stage name
        if report_type == "evening":
            # Use tomorrow's stage for evening reports
            stage = report_data.get("weather_data", {}).get("tomorrow_stage") or report_data.get("location", "Unknown")
        else:
            stage = report_data.get("location", "Unknown")
        
        # Get vigilance warnings
        vigilance_alerts = report_data.get("weather_data", {}).get("vigilance_alerts", [])
        
        if not vigilance_alerts:
            # No vigilance warnings
            risk_level = ""
            highest_risk = ""
        else:
            # Find the highest level alert
            level_priority = {"green": 1, "yellow": 2, "orange": 3, "red": 4}
            highest_alert = max(vigilance_alerts, key=lambda a: level_priority.get(a.get("level", "green"), 1))
            
            level = highest_alert.get("level", "green")
            phenomenon = highest_alert.get("phenomenon", "unknown")
            
            # Only include if level is yellow or higher
            if level_priority.get(level, 1) < 2:
                risk_level = ""
                highest_risk = ""
            else:
                # Translate phenomenon to German
                phenomenon_translation = {
                    "thunderstorm": "Gewitter",
                    "rain": "Regen",
                    "wind": "Wind",
                    "snow": "Schnee",
                    "flood": "Hochwasser",
                    "forest_fire": "Waldbrand",
                    "heat": "Hitze",
                    "cold": "Kälte",
                    "avalanche": "Lawine",
                    "unknown": "Warnung"
                }
                
                german_phenomenon = phenomenon_translation.get(phenomenon.lower(), phenomenon)
                risk_level = level.upper()
                highest_risk = german_phenomenon
        
        # Format: {subject} {etappe}: {risk_level} - {highest_risk} ({report_type})
        if risk_level and highest_risk:
            subject = f"{base_subject} {stage}: {risk_level} - {highest_risk} ({report_type})"
        else:
            subject = f"{base_subject} {stage}:  ({report_type})"
        
        return subject

def test_subject_generation():
    """Test email subject generation with various scenarios."""
    print("=== Testing Email Subject Generation ===")
    
    config = {"smtp": {"subject": "GR20 Wetter"}}
    email_client = MockEmailClient(config)
    
    # Test cases
    test_cases = [
        {
            "name": "Morning report with vigilance warning",
            "report_data": {
                "location": "Vizzavona",
                "report_type": "morning",
                "weather_data": {
                    "vigilance_alerts": [
                        {"phenomenon": "thunderstorm", "level": "orange"}
                    ]
                }
            },
            "expected_contains": ["GR20 Wetter Vizzavona:", "ORANGE", "Gewitter", "(morning)"]
        },
        {
            "name": "Evening report with red vigilance warning",
            "report_data": {
                "location": "Conca",
                "report_type": "evening",
                "weather_data": {
                    "tomorrow_stage": "Vizzavona",
                    "vigilance_alerts": [
                        {"phenomenon": "forest_fire", "level": "red"}
                    ]
                }
            },
            "expected_contains": ["GR20 Wetter Vizzavona:", "RED", "Waldbrand", "(evening)"]
        },
        {
            "name": "Update report without vigilance warning",
            "report_data": {
                "location": "Corte",
                "report_type": "dynamic",
                "weather_data": {
                    "vigilance_alerts": []
                }
            },
            "expected_contains": ["GR20 Wetter Corte:", "(dynamic)"],
            "expected_not_contains": ["ORANGE", "RED", "YELLOW"]
        },
        {
            "name": "Report with green vigilance warning (should be ignored)",
            "report_data": {
                "location": "TestLocation",
                "report_type": "morning",
                "weather_data": {
                    "vigilance_alerts": [
                        {"phenomenon": "rain", "level": "green"}
                    ]
                }
            },
            "expected_contains": ["GR20 Wetter TestLocation:", "(morning)"],
            "expected_not_contains": ["GREEN", "Regen"]
        },
        {
            "name": "Multiple vigilance warnings (should show highest)",
            "report_data": {
                "location": "TestLocation",
                "report_type": "evening",
                "weather_data": {
                    "vigilance_alerts": [
                        {"phenomenon": "rain", "level": "yellow"},
                        {"phenomenon": "thunderstorm", "level": "orange"},
                        {"phenomenon": "heat", "level": "red"}
                    ]
                }
            },
            "expected_contains": ["GR20 Wetter TestLocation:", "RED", "Hitze", "(evening)"],
            "expected_not_contains": ["YELLOW", "ORANGE"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        subject = email_client._generate_dynamic_subject(test_case["report_data"])
        print(f"Generated subject: {subject}")
        
        # Check expected contains
        for expected in test_case["expected_contains"]:
            status = "✅" if expected in subject else "❌"
            print(f"{status} Contains '{expected}': {expected in subject}")
        
        # Check expected not contains
        if "expected_not_contains" in test_case:
            for not_expected in test_case["expected_not_contains"]:
                status = "✅" if not_expected not in subject else "❌"
                print(f"{status} Does NOT contain '{not_expected}': {not_expected not in subject}")
        
        print(f"Subject length: {len(subject)} characters")

def test_subject_with_custom_base():
    """Test subject generation with custom base subject from config."""
    print("\n=== Testing Custom Base Subject ===")
    
    config = {"smtp": {"subject": "Custom Weather Alert"}}
    email_client = MockEmailClient(config)
    
    report_data = {
        "location": "TestLocation",
        "report_type": "morning",
        "weather_data": {
            "vigilance_alerts": [
                {"phenomenon": "thunderstorm", "level": "orange"}
            ]
        }
    }
    
    subject = email_client._generate_dynamic_subject(report_data)
    print(f"Custom base subject: {subject}")
    print(f"Contains 'Custom Weather Alert': {'✅' if 'Custom Weather Alert' in subject else '❌'}")

def test_subject_fallback():
    """Test subject generation with missing config."""
    print("\n=== Testing Subject Fallback ===")
    
    config = {}  # No smtp.subject in config
    email_client = MockEmailClient(config)
    
    report_data = {
        "location": "TestLocation",
        "report_type": "morning",
        "weather_data": {
            "vigilance_alerts": []
        }
    }
    
    subject = email_client._generate_dynamic_subject(report_data)
    print(f"Fallback subject: {subject}")
    print(f"Contains default 'GR20 Wetter': {'✅' if 'GR20 Wetter' in subject else '❌'}")

def main():
    """Run all subject tests."""
    print("🧪 Testing Email Subject Generation")
    print("=" * 50)
    
    test_subject_generation()
    test_subject_with_custom_base()
    test_subject_fallback()
    
    print("\n✅ All subject tests completed!")

if __name__ == "__main__":
    main() 