#!/usr/bin/env python3
"""
Calculate correct timestamps for 2025-08-02
"""

from datetime import datetime
import time

def calculate_timestamps():
    """Calculate correct timestamps for 2025-08-02."""
    
    print("CORRECT TIMESTAMPS FOR 2025-08-02")
    print("=" * 40)
    
    # Base date: 2025-08-02
    base_date = datetime(2025, 8, 2)
    
    # Hours we need: 05:00, 08:00, 11:00, 14:00, 17:00
    hours = [5, 8, 11, 14, 17]
    
    for hour in hours:
        dt = datetime(2025, 8, 2, hour, 0, 0)
        timestamp = int(time.mktime(dt.timetuple()))
        print(f"{hour:02d}:00 -> {timestamp} -> {datetime.fromtimestamp(timestamp)}")

if __name__ == "__main__":
    calculate_timestamps() 