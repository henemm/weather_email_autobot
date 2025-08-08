#!/usr/bin/env python3
"""
Corrected MeteoFrance API Analysis Script

This script provides a corrected analysis of MeteoFrance API usage,
properly identifying fallback patterns and data quality issues.
"""

import os
import sys
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import csv
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class CorrectedMeteoFranceAnalyzer:
    """Corrected analyzer for MeteoFrance API patterns and issues."""
    
    def __init__(self, log_file: str = "logs/warning_monitor.log"):
        """Initialize the analyzer."""
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_log_patterns(self) -> Dict[str, Any]:
        """Analyze detailed patterns in log files with correct fallback detection."""
        if not os.path.exists(self.log_file):
            self.logger.warning(f"Log file not found: {self.log_file}")
            return {}
            
        self.logger.info(f"Analyzing detailed patterns in: {self.log_file}")
        
        # Initialize counters
        patterns = {
            'meteofrance_usage': 0,
            'openmeteo_fallbacks': 0,
            'meteofrance_errors': 0,
            'openmeteo_errors': 0,
            'temperature_issues': 0,
            'alerts_parsing_errors': 0,
            'api_timeouts': 0,
            'authentication_errors': 0,
            'data_quality_issues': 0
        }
        
        # Track daily patterns
        daily_patterns = defaultdict(lambda: {
            'meteofrance_success': 0,
            'meteofrance_failure': 0,
            'openmeteo_fallback': 0,
            'temperature_issues': 0,
            'alerts_errors': 0
        })
        
        # Track error messages
        error_messages = Counter()
        
        # Track API response patterns
        api_responses = {
            'successful_forecasts': 0,
            'failed_forecasts': 0,
            'successful_thunderstorm': 0,
            'failed_thunderstorm': 0,
            'successful_alerts': 0,
            'failed_alerts': 0
        }
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Extract date from log line
                    date_match = re.search(r'\[(\d{4}-\d{2}-\d{2})', line)
                    if date_match:
                        log_date = date_match.group(1)
                    else:
                        continue
                        
                    # Count MeteoFrance API usage (corrected)
                    if 'meteofrance' in line.lower() and 'api' in line.lower():
                        patterns['meteofrance_usage'] += 1
                        daily_patterns[log_date]['meteofrance_success'] += 1
                        
                    # Count OpenMeteo fallbacks (corrected - case sensitive)
                    if 'Falling back to open-meteo' in line:
                        patterns['openmeteo_fallbacks'] += 1
                        daily_patterns[log_date]['openmeteo_fallback'] += 1
                        
                    # Count MeteoFrance errors
                    if 'meteofrance api failed' in line.lower():
                        patterns['meteofrance_errors'] += 1
                        daily_patterns[log_date]['meteofrance_failure'] += 1
                        
                    # Count OpenMeteo errors
                    if 'open-meteo failed' in line.lower():
                        patterns['openmeteo_errors'] += 1
                        
                    # Count temperature issues (corrected)
                    if 'temperatures too low for summer' in line.lower():
                        patterns['temperature_issues'] += 1
                        daily_patterns[log_date]['temperature_issues'] += 1
                        
                    # Count alerts parsing errors
                    if "'list' object has no attribute 'items'" in line:
                        patterns['alerts_parsing_errors'] += 1
                        daily_patterns[log_date]['alerts_errors'] += 1
                        
                    # Count API timeouts
                    if 'timeout' in line.lower():
                        patterns['api_timeouts'] += 1
                        
                    # Count authentication errors
                    if '401' in line or 'unauthorized' in line.lower():
                        patterns['authentication_errors'] += 1
                        
                    # Track specific error messages
                    if 'error' in line.lower() or 'exception' in line.lower():
                        # Extract error message
                        error_match = re.search(r'error[:\s]+(.+)', line, re.IGNORECASE)
                        if error_match:
                            error_msg = error_match.group(1).strip()
                            error_messages[error_msg[:100]] += 1
                            
                    # Track API response patterns
                    if 'successfully fetched' in line.lower():
                        if 'forecast' in line.lower():
                            api_responses['successful_forecasts'] += 1
                        elif 'thunderstorm' in line.lower():
                            api_responses['successful_thunderstorm'] += 1
                        elif 'alerts' in line.lower():
                            api_responses['successful_alerts'] += 1
                            
                    if 'failed to fetch' in line.lower():
                        if 'forecast' in line.lower():
                            api_responses['failed_forecasts'] += 1
                        elif 'thunderstorm' in line.lower():
                            api_responses['failed_thunderstorm'] += 1
                        elif 'alerts' in line.lower():
                            api_responses['failed_alerts'] += 1
                            
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            
        return {
            'patterns': patterns,
            'daily_patterns': dict(daily_patterns),
            'error_messages': dict(error_messages.most_common(20)),
            'api_responses': api_responses,
            'fallback_rate': (patterns['openmeteo_fallbacks'] / max(patterns['meteofrance_usage'], 1)) * 100,
            'error_rate': (patterns['meteofrance_errors'] / max(patterns['meteofrance_usage'], 1)) * 100
        }
        
    def analyze_temperature_validation_issues(self) -> Dict[str, Any]:
        """Analyze temperature validation issues in detail."""
        self.logger.info("Analyzing temperature validation issues")
        
        temperature_issues = {
            'total_issues': 0,
            'temperature_values': [],
            'dates': defaultdict(int),
            'locations': defaultdict(int),
            'hourly_patterns': defaultdict(int)
        }
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'temperatures too low for summer' in line.lower():
                        temperature_issues['total_issues'] += 1
                        
                        # Extract temperature value
                        temp_match = re.search(r'\(([\d.]+)°C\)', line)
                        if temp_match:
                            temp_value = float(temp_match.group(1))
                            temperature_issues['temperature_values'].append(temp_value)
                            
                        # Extract date
                        date_match = re.search(r'\[(\d{4}-\d{2}-\d{2})', line)
                        if date_match:
                            date = date_match.group(1)
                            temperature_issues['dates'][date] += 1
                            
                        # Extract location
                        location_match = re.search(r'for (\w+) on', line)
                        if location_match:
                            location = location_match.group(1)
                            temperature_issues['locations'][location] += 1
                            
                        # Extract hour
                        hour_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}):', line)
                        if hour_match:
                            hour = hour_match.group(1)
                            temperature_issues['hourly_patterns'][hour] += 1
                            
        except Exception as e:
            self.logger.error(f"Error analyzing temperature issues: {e}")
            
        return temperature_issues
        
    def generate_corrected_report(self) -> Dict[str, Any]:
        """Generate a corrected analysis report."""
        # Analyze log patterns
        log_analysis = self.analyze_log_patterns()
        
        # Analyze temperature validation issues
        temperature_analysis = self.analyze_temperature_validation_issues()
        
        # Calculate corrected statistics
        total_meteofrance_attempts = log_analysis['patterns']['meteofrance_usage']
        total_fallbacks = log_analysis['patterns']['openmeteo_fallbacks']
        total_temperature_issues = log_analysis['patterns']['temperature_issues']
        
        # Estimate actual fallback rate (including temperature-triggered fallbacks)
        estimated_total_fallbacks = total_fallbacks + total_temperature_issues
        actual_fallback_rate = (estimated_total_fallbacks / max(total_meteofrance_attempts, 1)) * 100
        
        # Combine results
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'log_analysis': log_analysis,
            'temperature_analysis': temperature_analysis,
            'corrected_summary': {
                'total_meteofrance_attempts': total_meteofrance_attempts,
                'explicit_fallbacks': total_fallbacks,
                'temperature_triggered_fallbacks': total_temperature_issues,
                'estimated_total_fallbacks': estimated_total_fallbacks,
                'actual_fallback_rate': actual_fallback_rate,
                'temperature_validation_issues': total_temperature_issues,
                'most_common_temperature': max(temperature_analysis['temperature_values']) if temperature_analysis['temperature_values'] else None,
                'most_affected_location': max(temperature_analysis['locations'].items(), key=lambda x: x[1]) if temperature_analysis['locations'] else None,
                'most_affected_date': max(temperature_analysis['dates'].items(), key=lambda x: x[1]) if temperature_analysis['dates'] else None
            },
            'recommendations': self._generate_corrected_recommendations(log_analysis, temperature_analysis)
        }
        
        return report
        
    def _generate_corrected_recommendations(self, log_analysis: Dict, temperature_analysis: Dict) -> List[str]:
        """Generate corrected recommendations based on analysis results."""
        recommendations = []
        
        # Check actual fallback rate
        actual_fallback_rate = log_analysis.get('fallback_rate', 0)
        temperature_issues = log_analysis.get('patterns', {}).get('temperature_issues', 0)
        total_attempts = log_analysis.get('patterns', {}).get('meteofrance_usage', 0)
        
        estimated_total_fallbacks = actual_fallback_rate + (temperature_issues / max(total_attempts, 1)) * 100
        
        if estimated_total_fallbacks > 50:
            recommendations.append(f"CRITICAL: Very high fallback rate ({estimated_total_fallbacks:.1f}%) - MeteoFrance API is effectively not being used")
        elif estimated_total_fallbacks > 20:
            recommendations.append(f"HIGH: High fallback rate ({estimated_total_fallbacks:.1f}%) - Significant reliance on Open-Meteo")
        elif estimated_total_fallbacks > 10:
            recommendations.append(f"MODERATE: Moderate fallback rate ({estimated_total_fallbacks:.1f}%) - Monitor for degradation")
            
        # Check temperature validation issues
        if temperature_analysis['total_issues'] > 100:
            recommendations.append(f"CRITICAL: {temperature_analysis['total_issues']} temperature validation issues - MeteoFrance data being rejected unnecessarily")
            
        # Check for 0°C temperatures (likely data quality issue)
        zero_temp_count = sum(1 for temp in temperature_analysis['temperature_values'] if temp == 0.0)
        if zero_temp_count > 50:
            recommendations.append(f"HIGH: {zero_temp_count} instances of 0°C temperatures - Likely MeteoFrance data quality issue")
            
        # Check alerts parsing errors
        alerts_errors = log_analysis.get('patterns', {}).get('alerts_parsing_errors', 0)
        if alerts_errors > 10:
            recommendations.append(f"MODERATE: {alerts_errors} alerts parsing errors - Fix alerts data structure handling")
            
        if not recommendations:
            recommendations.append("No significant issues detected - API integration appears healthy")
            
        return recommendations
        
    def export_corrected_report(self, output_file: str = "corrected_meteofrance_analysis.json"):
        """Export corrected analysis report."""
        report = self.generate_corrected_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Corrected report exported to {output_file}")
        
    def export_temperature_analysis_csv(self, output_file: str = "temperature_validation_analysis.csv"):
        """Export temperature validation analysis to CSV."""
        temperature_analysis = self.analyze_temperature_validation_issues()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'temperature_issues', 'most_common_temp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for date, count in temperature_analysis['dates'].items():
                # Find most common temperature for this date
                writer.writerow({
                    'date': date,
                    'temperature_issues': count,
                    'most_common_temp': 'N/A'  # Would need more detailed analysis
                })
                
        self.logger.info(f"Temperature analysis exported to {output_file}")


def main():
    """Main analysis function."""
    print("🔍 Corrected MeteoFrance API Analysis")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = CorrectedMeteoFranceAnalyzer()
    
    # Generate corrected report
    print("\n📊 Generating corrected analysis...")
    report = analyzer.generate_corrected_report()
    
    # Display corrected summary
    summary = report['corrected_summary']
    print(f"\n📈 Corrected Summary:")
    print(f"   Total MeteoFrance Attempts: {summary['total_meteofrance_attempts']}")
    print(f"   Explicit Fallbacks: {summary['explicit_fallbacks']}")
    print(f"   Temperature-Triggered Fallbacks: {summary['temperature_triggered_fallbacks']}")
    print(f"   Estimated Total Fallbacks: {summary['estimated_total_fallbacks']}")
    print(f"   Actual Fallback Rate: {summary['actual_fallback_rate']:.1f}%")
    print(f"   Temperature Validation Issues: {summary['temperature_validation_issues']}")
    
    if summary['most_common_temperature'] is not None:
        print(f"   Most Common Temperature Issue: {summary['most_common_temperature']}°C")
        
    if summary['most_affected_location']:
        location, count = summary['most_affected_location']
        print(f"   Most Affected Location: {location} ({count} issues)")
        
    if summary['most_affected_date']:
        date, count = summary['most_affected_date']
        print(f"   Most Affected Date: {date} ({count} issues)")
    
    # Display recommendations
    print(f"\n💡 Corrected Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    # Export reports
    print(f"\n💾 Exporting corrected reports...")
    analyzer.export_corrected_report()
    analyzer.export_temperature_analysis_csv()
    
    print(f"\n✅ Corrected analysis complete!")
    print(f"   - Corrected report: corrected_meteofrance_analysis.json")
    print(f"   - Temperature analysis: temperature_validation_analysis.csv")


if __name__ == "__main__":
    main() 