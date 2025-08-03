#!/usr/bin/env python3
"""
Debug why T1G2 and T1G3 are not showing in WIND and GUST sections.
"""

import yaml
import json
from src.weather.core.morning_evening_refactor import MorningEveningRefactor

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Load etappen data
with open('etappen.json', 'r') as f:
    etappen_data = json.load(f)

print("🔍 DEBUG ALL GEO POINTS")
print("=" * 50)

# Check Test stage
test_stage = etappen_data[0]  # First stage
print(f"Test Stage: {test_stage.get('name', 'Unknown')}")
print(f"Number of points: {len(test_stage.get('punkte', []))}")

for i, point in enumerate(test_stage.get('punkte', [])):
    print(f"  T1G{i+1}: lat={point.get('lat')}, lon={point.get('lon')}")

print()

# Create refactor instance
refactor = MorningEveningRefactor(config)

# Generate report
result, debug = refactor.generate_report('Test', 'morning', '2025-08-03')

print("📊 DEBUG OUTPUT ANALYSIS:")
print("=" * 50)

# Find WIND section
lines = debug.split('\n')
wind_start = -1
wind_end = -1

for i, line in enumerate(lines):
    if 'WIND' in line and 'THUNDERSTORM' not in line:
        wind_start = i
        print(f"WIND section starts at line {i+1}")
        break

if wind_start >= 0:
    # Find end of WIND section
    for i in range(wind_start + 1, len(lines)):
        if lines[i].strip() in ['GUST', 'THUNDERSTORM', 'RISKS']:
            wind_end = i
            break
    
    if wind_end == -1:
        wind_end = len(lines)
    
    print(f"WIND section ends at line {wind_end}")
    print()
    
    # Count T1G references in WIND section
    t1g_count = 0
    for i in range(wind_start, wind_end):
        line = lines[i].strip()
        if line.startswith('T1G'):
            t1g_count += 1
            print(f"  Found: {line}")
    
    print(f"Total T1G references in WIND: {t1g_count}")

print()

# Find GUST section
gust_start = -1
gust_end = -1

for i, line in enumerate(lines):
    if 'GUST' in line and 'THUNDERSTORM' not in line:
        gust_start = i
        print(f"GUST section starts at line {i+1}")
        break

if gust_start >= 0:
    # Find end of GUST section
    for i in range(gust_start + 1, len(lines)):
        if lines[i].strip() in ['THUNDERSTORM', 'RISKS']:
            gust_end = i
            break
    
    if gust_end == -1:
        gust_end = len(lines)
    
    print(f"GUST section ends at line {gust_end}")
    print()
    
    # Count T1G references in GUST section
    t1g_count = 0
    for i in range(gust_start, gust_end):
        line = lines[i].strip()
        if line.startswith('T1G'):
            t1g_count += 1
            print(f"  Found: {line}")
    
    print(f"Total T1G references in GUST: {t1g_count}")

print()
print("=" * 50)
print("DONE") 