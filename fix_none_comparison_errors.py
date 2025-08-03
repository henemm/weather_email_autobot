#!/usr/bin/env python3
"""
FIX NONE COMPARISON ERRORS
==========================
Fix all None comparison errors in the generate_debug_output function.
"""

import re

def fix_none_comparisons():
    """Fix all None comparison errors in the morning_evening_refactor.py file."""
    
    # Read the file
    with open('src/weather/core/morning_evening_refactor.py', 'r') as f:
        content = f.read()
    
    # Fix patterns for >= comparisons that might involve None values
    patterns_to_fix = [
        # Pattern 1: value >= threshold
        (r'(\w+)\s*>=\s*(\w+\.get\([^)]+\)|\w+\.get\([^)]+,\s*\d+\.?\d*\))', r'\1 is not None and \1 >= \2'),
        # Pattern 2: value >= self.thresholds.get(...)
        (r'(\w+)\s*>=\s*self\.thresholds\.get\([^)]+\)', r'\1 is not None and \1 >= self.thresholds.get(...)'),
        # Pattern 3: rain_value >= self.thresholds['rain_amount']
        (r'(\w+)\s*>=\s*self\.thresholds\[[^\]]+\]', r'\1 is not None and \1 >= self.thresholds[...]'),
        # Pattern 4: thunderstorm_level >= self.thresholds['thunderstorm']
        (r'thunderstorm_level\s*>=\s*self\.thresholds\[[^\]]+\]', r'thunderstorm_level is not None and thunderstorm_level >= self.thresholds[...]'),
    ]
    
    # Apply fixes
    modified_content = content
    for pattern, replacement in patterns_to_fix:
        modified_content = re.sub(pattern, replacement, modified_content)
    
    # Write back
    with open('src/weather/core/morning_evening_refactor.py', 'w') as f:
        f.write(modified_content)
    
    print("✅ Fixed None comparison errors")

if __name__ == "__main__":
    fix_none_comparisons() 