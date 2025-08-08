#!/usr/bin/env python3
"""
Debug WIND section to see what's happening.
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

print("WIND SECTION DEBUG:")
print("=" * 50)

# Find WIND section
lines = debug.split('\n')
wind_start = -1
for i, line in enumerate(lines):
    if 'WIND' in line and 'THUNDERSTORM' not in line:
        wind_start = i
        break

if wind_start >= 0:
    print(f"WIND section found at line {wind_start + 1}")
    print()
    
    # Show WIND section content
    for i in range(wind_start, min(wind_start + 30, len(lines))):
        print(f"{i+1:3d}: {lines[i]}")
        
        # Stop if we hit the next section
        if i > wind_start and lines[i].strip() in ['GUST', 'THUNDERSTORM', 'RISKS']:
            break
else:
    print("WIND section not found!")

print()
print("=" * 50)
print("DONE") 