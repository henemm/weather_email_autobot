#!/usr/bin/env python3
"""
Analyze worst-case SMS length for GR20 weather reports.
"""

def analyze_worst_case_sms_length():
    """Analyze the worst-case SMS length with maximum values."""
    
    # Worst case scenario with maximum values
    stage_name = "LängsterEt"  # 10 chars (truncated)
    min_temp = -99.9  # 5 chars
    thunderstorm_max = 99  # 2 chars
    thunderstorm_threshold_time = "23"  # 2 chars (HH format)
    thunderstorm_max_time = "23"  # 2 chars (HH format)
    thunderstorm_next_day = 99  # 2 chars
    rain_total = 999.9  # 5 chars
    rain_threshold_time = "23"  # 2 chars (HH format)
    rain_max_time = "23"  # 2 chars (HH format)
    temp_max = 99.9  # 4 chars
    wind_max = 999  # 3 chars (Windgeschwindigkeit)
    wind_gusts = 999  # 3 chars (Böhen)
    vigilance_warning = "ROT Gewitter"  # 12 chars
    
    # Morning report format
    morning_parts = [
        stage_name,
        f"Gew. {thunderstorm_max}%",
        f"Regen {rain_total}mm",
        f"Hitze {temp_max}°C",
        f"Wind {wind_max} (max {wind_gusts})",
        f"Gew. +1 {thunderstorm_next_day}%",
        vigilance_warning
    ]
    
    # Evening report format (worst case)
    evening_parts = [
        stage_name,
        f"Nacht {min_temp}°C",
        f"Gew. {thunderstorm_max}%@{thunderstorm_threshold_time} (max {thunderstorm_max}%@{thunderstorm_max_time})",
        f"Regen {rain_total}mm@{rain_threshold_time} (max {rain_total}mm@{rain_max_time})",
        f"Hitze {temp_max}°C",
        f"Wind {wind_max} (max {wind_gusts})",
        vigilance_warning,
        f"Gew. +1 {thunderstorm_next_day}%"
    ]
    
    # Dynamic report format
    dynamic_parts = [
        stage_name,
        f"Update: Gew. {thunderstorm_max}%@{thunderstorm_threshold_time}",
        f"Regen {rain_total}mm@{rain_threshold_time}",
        f"Hitze {temp_max}°C",
        f"Wind {wind_max} (max {wind_gusts})",
        vigilance_warning
    ]
    
    # Calculate lengths
    morning_text = " | ".join(morning_parts)
    evening_text = " | ".join(evening_parts)
    dynamic_text = " | ".join(dynamic_parts)
    
    print("=== SMS LENGTH ANALYSIS ===")
    print(f"Morning Report: {len(morning_text)} chars")
    print(f"Evening Report: {len(evening_text)} chars")
    print(f"Dynamic Report: {len(dynamic_text)} chars")
    print()
    
    print("=== MORNING REPORT BREAKDOWN ===")
    for i, part in enumerate(morning_parts):
        print(f"{i+1:2d}. {part} ({len(part)} chars)")
    print(f"Total: {len(morning_text)} chars")
    print(f"Available: {160 - len(morning_text)} chars")
    print()
    
    print("=== EVENING REPORT BREAKDOWN ===")
    for i, part in enumerate(evening_parts):
        print(f"{i+1:2d}. {part} ({len(part)} chars)")
    print(f"Total: {len(evening_text)} chars")
    print(f"Available: {160 - len(evening_text)} chars")
    print()
    
    print("=== DYNAMIC REPORT BREAKDOWN ===")
    for i, part in enumerate(dynamic_parts):
        print(f"{i+1:2d}. {part} ({len(part)} chars)")
    print(f"Total: {len(dynamic_text)} chars")
    print(f"Available: {160 - len(dynamic_text)} chars")
    print()
    
    # Check if any exceed 160 chars
    if len(morning_text) > 160:
        print(f"❌ Morning report exceeds limit by {len(morning_text) - 160} chars")
    else:
        print(f"✅ Morning report: {160 - len(morning_text)} chars available")
        
    if len(evening_text) > 160:
        print(f"❌ Evening report exceeds limit by {len(evening_text) - 160} chars")
    else:
        print(f"✅ Evening report: {160 - len(evening_text)} chars available")
        
    if len(dynamic_text) > 160:
        print(f"❌ Dynamic report exceeds limit by {len(dynamic_text) - 160} chars")
    else:
        print(f"✅ Dynamic report: {160 - len(dynamic_text)} chars available")

if __name__ == "__main__":
    analyze_worst_case_sms_length() 