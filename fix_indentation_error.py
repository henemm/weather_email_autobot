#!/usr/bin/env python3
"""
FIX INDENTATION ERROR
====================
Fix the indentation error and remove duplicate lines in the debug output.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read the current file
with open('src/weather/core/morning_evening_refactor.py', 'r') as f:
    content = f.read()

# Find and fix the problematic section
problematic_section = '''                debug_lines.append("")
                    debug_lines.append("GEO | Time | Max")
                    for point in report_data.thunderstorm.geo_points:
                        if point['max_time'] is not None:
                            debug_lines.append(f"{point['name']} | {point['max_time']} | {point['max_value']}")
                    debug_lines.append("=========")
                    debug_lines.append(f"MAX | {report_data.thunderstorm.max_time} | {report_data.thunderstorm.max_value}")
                    debug_lines.append("")
                
                # Add Threshold and Maximum summary tables (like RAIN)'''

fixed_section = '''                debug_lines.append("")
                
                # Add Threshold and Maximum summary tables (like RAIN)'''

# Replace the problematic section
content = content.replace(problematic_section, fixed_section)

# Write back to file
with open('src/weather/core/morning_evening_refactor.py', 'w') as f:
    f.write(content)

print("✅ Indentation error fixed!")
print("   - Removed duplicate lines")
print("   - Fixed indentation") 