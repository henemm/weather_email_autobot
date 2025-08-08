#!/usr/bin/env python3
"""
Demo script for alternative risk analysis.

This script demonstrates the alternative risk analysis functionality
with sample MeteoFrance API data, focusing on thunderstorm timing for hikers.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.risiko.alternative_risk_analysis import AlternativeRiskAnalyzer


def main():
    """Demonstrate alternative risk analysis with sample MeteoFrance data."""
    print("🌤️ Alternative Risk Analysis Demo (MeteoFrance API)")
    print("🎯 Focus: Thunderstorm Timing for Hikers")
    print("=" * 70)
    
    # Sample MeteoFrance API data structure with timing
    sample_weather_data = {
        'forecast': [
            {
                'dt': 1751857200,  # 14:00
                'T': {'value': 25.5},
                'rain': {'1h': 1.5},
                'precipitation_probability': 30,
                'weather': {'desc': 'Ciel clair'},
                'wind': {'speed': 15, 'gust': 20}
            },
            {
                'dt': 1751860800,  # 15:00
                'T': {'value': 28.0},
                'rain': {'1h': 2.5},
                'precipitation_probability': 60,
                'weather': {'desc': 'Risque d\'orages'},
                'wind': {'speed': 25, 'gust': 35}
            },
            {
                'dt': 1751864400,  # 16:00
                'T': {'value': 32.5},
                'rain': {'1h': 1.0},
                'precipitation_probability': 45,
                'weather': {'desc': 'Orages'},
                'wind': {'speed': 35, 'gust': 45}
            },
            {
                'dt': 1751868000,  # 17:00
                'T': {'value': 29.0},
                'rain': {'1h': 3.0},
                'precipitation_probability': 70,
                'weather': {'desc': 'Orages lourds'},
                'wind': {'speed': 20, 'gust': 30}
            }
        ]
    }
    
    # Create analyzer
    analyzer = AlternativeRiskAnalyzer()
    
    try:
        # Perform complete analysis
        print("📊 Analyzing MeteoFrance weather data...")
        result = analyzer.analyze_all_risks(sample_weather_data)
        
        # Generate report
        print("\n📋 Generated Report:")
        report_text = analyzer.generate_report_text(result)
        print(report_text)
        
        # Show individual results
        print("\n🔍 Detailed Analysis:")
        print(f"🔥 Heat: {result.heat_risk.description}")
        print(f"❄️ Cold: {result.cold_risk.description}")
        print(f"🌧️ Rain: {result.rain_risk.description}")
        print(f"⛈️ Thunderstorm: {result.thunderstorm_risk.description}")
        print(f"🌬️ Wind: {result.wind_risk.description}")
        
        # Show thunderstorm timing details (most important for hikers)
        print("\n⛈️ THUNDERSTORM TIMING ANALYSIS:")
        print("-" * 40)
        if result.thunderstorm_risk.has_risk:
            print("🚨 THUNDERSTORM RISK DETECTED!")
            for thunderstorm in result.thunderstorm_risk.thunderstorm_times:
                intensity_icon = "🔴" if thunderstorm.intensity == "heavy" else "🟡" if thunderstorm.intensity == "risk" else "🟠"
                print(f"  {intensity_icon} {thunderstorm.hour:02d}:00 - {thunderstorm.description}")
                print(f"     Intensity: {thunderstorm.intensity}")
        else:
            print("✅ No thunderstorm conditions detected")
            
        # Show risk summary
        print("\n⚠️ Risk Summary:")
        risks_detected = []
        if result.rain_risk.has_risk:
            risks_detected.append("Rain")
        if result.thunderstorm_risk.has_risk:
            risks_detected.append("Thunderstorm")
        if result.wind_risk.has_risk:
            risks_detected.append("Wind")
        
        if risks_detected:
            print(f"Risks detected: {', '.join(risks_detected)}")
        else:
            print("No significant risks detected")
            
        # Show MeteoFrance API structure
        print("\n📡 MeteoFrance API Data Structure:")
        print("✅ Temperature: T.value")
        print("✅ Rain: rain.1h")
        print("✅ Wind: wind.speed, wind.gust")
        print("✅ Weather: weather.desc")
        print("✅ Timing: dt (Unix timestamp)")
        print("❌ precipitation_probability: Estimated from weather description")
        print("❌ WMO codes: Mapped from French weather descriptions")
        
        # Show hiker-specific recommendations
        print("\n🥾 HIKER RECOMMENDATIONS:")
        print("-" * 40)
        if result.thunderstorm_risk.has_risk:
            print("🚨 CRITICAL: Thunderstorm risk detected!")
            print("   • Plan your hike to avoid thunderstorm hours")
            print("   • Seek shelter before thunderstorms arrive")
            print("   • Avoid exposed ridges and summits during storms")
            print("   • Monitor weather conditions closely")
        else:
            print("✅ No thunderstorm risk - safe hiking conditions")
            
        if result.wind_risk.has_risk:
            print("🌬️ WIND: High gusts detected")
            print("   • Be cautious on exposed sections")
            print("   • Secure loose items")
            
        if result.rain_risk.has_risk:
            print("🌧️ RAIN: Significant precipitation expected")
            print("   • Bring waterproof gear")
            print("   • Consider trail conditions")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 