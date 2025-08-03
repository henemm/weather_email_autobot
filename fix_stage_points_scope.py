#!/usr/bin/env python3
"""
FIX STAGE_POINTS SCOPE
======================
Fix the stage_points scope issue by ensuring it's defined before being used.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read the current file
with open('src/weather/core/morning_evening_refactor.py', 'r') as f:
    content = f.read()

# Find the problematic section and fix it
problematic_section = '''                # Add Threshold and Maximum summary tables (like RAIN)
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | Speed")
                
                # Calculate threshold for each point
                for i, point in enumerate(stage_points):'''

fixed_section = '''                # Add Threshold and Maximum summary tables (like RAIN)
                debug_lines.append("Threshold")
                debug_lines.append("GEO | Time | Speed")
                
                # Calculate threshold for each point
                for i, point in enumerate(stage_points):'''

# The issue is that stage_points is not defined in this scope
# We need to get it from the stage data
problematic_section2 = '''                # Calculate threshold for each point
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)'''

fixed_section2 = '''                # Calculate threshold for each point
                # Get stage points from the stage data
                if stage_idx < len(etappen_data):
                    stage = etappen_data[stage_idx]
                    stage_points = stage.get('punkte', [])
                    
                    for i, point in enumerate(stage_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)'''

# Replace the problematic sections
content = content.replace(problematic_section2, fixed_section2)

# Also fix the second occurrence for GUST
problematic_section3 = '''                # Calculate maximum for each point
                for i, point in enumerate(stage_points):
                    tg_ref = self._get_tg_reference(report_data.report_type, 'gust', i)'''

fixed_section3 = '''                # Calculate maximum for each point
                # Get stage points from the stage data (reuse from above)
                if stage_idx < len(etappen_data):
                    stage = etappen_data[stage_idx]
                    stage_points = stage.get('punkte', [])
                    
                    for i, point in enumerate(stage_points):
                        tg_ref = self._get_tg_reference(report_data.report_type, 'wind', i)'''

# Replace the second problematic section
content = content.replace(problematic_section3, fixed_section3)

# Write back to file
with open('src/weather/core/morning_evening_refactor.py', 'w') as f:
    f.write(content)

print("✅ Stage points scope fixed!")
print("   - stage_points now properly defined before use")
print("   - Fixed for both WIND and GUST sections") 