#!/usr/bin/env python3
"""
FIX WIND AND GUST LOGIC
=======================
Fix the threshold and maximum calculation logic in WIND and GUST methods.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read the current file
with open('src/weather/core/morning_evening_refactor.py', 'r') as f:
    content = f.read()

# Fix WIND method - replace the global threshold/max logic
wind_old_logic = '''                    # Track global threshold and max
                    if point_threshold_value is not None:
                        if global_threshold_value is None or point_threshold_value < global_threshold_value:
                            global_threshold_value = point_threshold_value
                            global_threshold_time = point_threshold_time
                    
                    if point_max_value is not None:
                        if global_max_value is None or point_max_value > global_max_value:
                            global_max_value = point_max_value
                            global_max_time = point_max_time'''

wind_new_logic = '''                    # Track global threshold and max
                    if point_threshold_value is not None:
                        # Threshold: earliest time when threshold was first exceeded
                        if global_threshold_time is None:
                            global_threshold_value = point_threshold_value
                            global_threshold_time = point_threshold_time
                        else:
                            # Take the earliest time
                            if int(point_threshold_time) < int(global_threshold_time):
                                global_threshold_value = point_threshold_value
                                global_threshold_time = point_threshold_time
                    
                    if point_max_value is not None and point_max_value > 0:
                        # Maximum: highest value, if equal take earliest time
                        if global_max_value is None:
                            global_max_value = point_max_value
                            global_max_time = point_max_time
                        else:
                            if point_max_value > global_max_value:
                                global_max_value = point_max_value
                                global_max_time = point_max_time
                            elif point_max_value == global_max_value:
                                # If equal values, take earliest time
                                if int(point_max_time) < int(global_max_time):
                                    global_max_time = point_max_time'''

# Replace in content
content = content.replace(wind_old_logic, wind_new_logic)

# Fix GUST method - replace the global threshold/max logic (same replacement)
content = content.replace(wind_old_logic, wind_new_logic)

# Write back to file
with open('src/weather/core/morning_evening_refactor.py', 'w') as f:
    f.write(content)

print("✅ WIND and GUST logic fixed!")
print("   - Threshold: earliest time when threshold was first exceeded")
print("   - Maximum: highest value, if equal take earliest time")
print("   - 0 values are not considered as maximum") 