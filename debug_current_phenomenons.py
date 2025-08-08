#!/usr/bin/env python3

import sys
import os
sys.path.append('/opt/weather_email_autobot')

from src.wetter.department_mapper import DepartmentMapper

def debug_current_phenomenons():
    """Debug the CurrentPhenomenons object structure"""
    
    mapper = DepartmentMapper()
    
    # Test coordinates for FONT-ROMEU-ODEILLO-VIA
    lat, lon = 42.471359, 2.029742
    
    print(f"Testing coordinates: {lat}, {lon}")
    
    try:
        warnings = mapper.get_warning_data_for_coordinates(lat, lon)
        
        if warnings is None:
            print("No warning data returned")
            return
            
        print(f"Type of warnings: {type(warnings)}")
        print(f"Warnings object: {warnings}")
        
        # Try to inspect the object's attributes
        print("\n=== Object Attributes ===")
        for attr in dir(warnings):
            if not attr.startswith('_'):
                try:
                    value = getattr(warnings, attr)
                    print(f"{attr}: {value}")
                except Exception as e:
                    print(f"{attr}: Error accessing - {e}")
        
        # Try to call methods if they exist
        print("\n=== Method Calls ===")
        if hasattr(warnings, 'phenomenons'):
            try:
                phenomenons = warnings.phenomenons
                print(f"phenomenons: {phenomenons}")
                if phenomenons:
                    for i, phenom in enumerate(phenomenons):
                        print(f"  Phenomenon {i}: {phenom}")
                        if hasattr(phenom, '__dict__'):
                            print(f"    Attributes: {phenom.__dict__}")
            except Exception as e:
                print(f"Error accessing phenomenons: {e}")
        
        if hasattr(warnings, 'get_phenomenons'):
            try:
                phenomenons = warnings.get_phenomenons()
                print(f"get_phenomenons(): {phenomenons}")
            except Exception as e:
                print(f"Error calling get_phenomenons(): {e}")
        
        # Try to convert to dict if possible
        print("\n=== Dict Conversion ===")
        try:
            warnings_dict = warnings.__dict__
            print(f"__dict__: {warnings_dict}")
        except Exception as e:
            print(f"Error converting to dict: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_current_phenomenons()
