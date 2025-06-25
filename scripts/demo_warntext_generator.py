#!/usr/bin/env python3
"""
Demo script for the warntext generator functionality.

This script demonstrates how the generate_warntext function works with different
risk values and configuration settings.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.warntext_generator import generate_warntext


def demo_warntext_generator():
    """Demonstrate the warntext generator with various risk values."""
    
    # Configuration with different threshold levels
    config = {
        "warn_thresholds": {
            "info": 0.3,
            "warning": 0.6,
            "critical": 0.9
        }
    }
    
    print("=== Warntext Generator Demo ===\n")
    print("Configuration:")
    print(f"  Info threshold: {config['warn_thresholds']['info']}")
    print(f"  Warning threshold: {config['warn_thresholds']['warning']}")
    print(f"  Critical threshold: {config['warn_thresholds']['critical']}")
    print()
    
    # Test different risk values
    test_risks = [
        0.0,    # No risk
        0.2,    # Below info threshold
        0.3,    # At info threshold
        0.4,    # Between info and warning
        0.6,    # At warning threshold
        0.7,    # Between warning and critical
        0.9,    # At critical threshold
        0.95,   # Above critical
        1.0     # Maximum risk
    ]
    
    print("Risk Value Tests:")
    print("-" * 50)
    
    for risk in test_risks:
        try:
            result = generate_warntext(risk, config)
            status = "Generated" if result else "No warning"
            print(f"Risk: {risk:.2f} → {status}")
            if result:
                print(f"  Text: {result}")
            print()
        except Exception as e:
            print(f"Risk: {risk:.2f} → Error: {e}")
            print()
    
    # Test error cases
    print("Error Case Tests:")
    print("-" * 50)
    
    # Invalid risk values
    invalid_risks = [-0.1, 1.1, float('nan'), float('inf')]
    for risk in invalid_risks:
        try:
            result = generate_warntext(risk, config)
            print(f"Risk: {risk} → {result}")
        except ValueError as e:
            print(f"Risk: {risk} → Error: {e}")
    
    # Invalid configurations
    invalid_configs = [
        {},  # Empty config
        {"other_key": "value"},  # Missing warn_thresholds
        {"warn_thresholds": {"info": 0.3}},  # Incomplete thresholds
        {"warn_thresholds": {"info": 0.3, "warning": 0.6, "critical": 0.5}},  # Invalid order
    ]
    
    print("\nInvalid Configuration Tests:")
    print("-" * 50)
    
    for i, invalid_config in enumerate(invalid_configs, 1):
        try:
            result = generate_warntext(0.5, invalid_config)
            print(f"Config {i}: {invalid_config} → {result}")
        except ValueError as e:
            print(f"Config {i}: {invalid_config} → Error: {e}")


if __name__ == "__main__":
    demo_warntext_generator() 