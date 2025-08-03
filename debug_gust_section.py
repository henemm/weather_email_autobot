#!/usr/bin/env python3
"""
Debug GUST section to see what's happening.
"""

import yaml
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create refactor instance
refactor = MorningEveningRefactor(config)

# Generate report
result, debug = refactor.generate_report('Test', 'morning', '2025-08-03')

print("GUST SECTION DEBUG:")
print("=" * 50)

# Find GUST section
lines = debug.split('\n')
gust_start = -1
for i, line in enumerate(lines):
    if 'GUST' in line and 'THUNDERSTORM' not in line:
        gust_start = i
        break

if gust_start >= 0:
    print(f"GUST section found at line {gust_start + 1}")
    print()
    
    # Show GUST section content
    for i in range(gust_start, min(gust_start + 30, len(lines))):
        print(f"{i+1:3d}: {lines[i]}")
        
        # Stop if we hit the next section
        if i > gust_start and lines[i].strip() in ['THUNDERSTORM', 'RISKS']:
            break
else:
    print("GUST section not found!")

print()
print("=" * 50)
print("DONE") 