#!/usr/bin/env python3
"""
Detailed MeteoFrance API Analysis Script

This script provides comprehensive analysis of MeteoFrance API usage,
data quality issues, and fallback patterns over the last 14 days.
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

from wetter.fetch_meteofrance import (
    get_forecast_with_fallback,
    get_thunderstorm_with_fallback,
    get_alerts_with_fallback
)


class DetailedMeteoFranceAnalyzer:
    """Detailed analyzer for MeteoFrance API patterns and issues."""
    
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
        """Analyze detailed patterns in log files."""
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
                        
                    # Count MeteoFrance API usage
                    if 'meteofrance' in line.lower():
                        patterns['meteofrance_usage'] += 1
                        daily_patterns[log_date]['meteofrance_success'] += 1
                        
                    # Count OpenMeteo fallbacks
                    if 'falling back to open-meteo' in line:
                        patterns['openmeteo_fallbacks'] += 1
                        daily_patterns[log_date]['openmeteo_fallback'] += 1
                        
                    # Count MeteoFrance errors
                    if 'meteofrance api failed' in line.lower():
                        patterns['meteofrance_errors'] += 1
                        daily_patterns[log_date]['meteofrance_failure'] += 1
                        
                    # Count OpenMeteo errors
                    if 'open-meteo failed' in line.lower():
                        patterns['openmeteo_errors'] += 1
                        
                    # Count temperature issues
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
        
    def analyze_data_quality(self, coordinates: List[Tuple[float, float, str]]) -> Dict[str, Any]:
        """Analyze data quality by testing API endpoints."""
        self.logger.info(f"Analyzing data quality for {len(coordinates)} locations")
        
        quality_results = {
            'total_tests': 0,
            'meteofrance_success': 0,
            'openmeteo_fallback': 0,
            'missing_fields': defaultdict(int),
            'data_completeness': defaultdict(list),
            'response_times': [],
            'error_types': Counter()
        }
        
        for lat, lon, location_name in coordinates:
            quality_results['total_tests'] += 1
            
            try:
                # Test forecast
                start_time = datetime.now()
                forecast_result = get_forecast_with_fallback(lat, lon)
                response_time = (datetime.now() - start_time).total_seconds()
                quality_results['response_times'].append(response_time)
                
                if forecast_result.data_source == 'meteofrance-api':
                    quality_results['meteofrance_success'] += 1
                    
                    # Check data completeness
                    completeness = {
                        'temperature': forecast_result.temperature is not None,
                        'precipitation_probability': forecast_result.precipitation_probability is not None,
                        'wind_speed': forecast_result.wind_speed is not None,
                        'wind_gusts': forecast_result.wind_gusts is not None,
                        'thunderstorm_probability': forecast_result.thunderstorm_probability is not None,
                        'precipitation': forecast_result.precipitation is not None
                    }
                    
                    for field, has_value in completeness.items():
                        if not has_value:
                            quality_results['missing_fields'][field] += 1
                            
                    quality_results['data_completeness'][location_name] = completeness
                    
                else:
                    quality_results['openmeteo_fallback'] += 1
                    
            except Exception as e:
                error_type = type(e).__name__
                quality_results['error_types'][error_type] += 1
                self.logger.error(f"Error testing {location_name}: {e}")
                
        # Calculate averages
        if quality_results['response_times']:
            quality_results['avg_response_time'] = sum(quality_results['response_times']) / len(quality_results['response_times'])
            quality_results['max_response_time'] = max(quality_results['response_times'])
            quality_results['min_response_time'] = min(quality_results['response_times'])
            
        return quality_results
        
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis report."""
        # Get test coordinates
        coordinates = [
            (43.2333, 0.0833, "Tarbes"),
            (48.8566, 2.3522, "Paris"),
            (43.2965, 5.3698, "Marseille"),
            (45.7640, 4.8357, "Lyon"),
            (43.6047, 1.4442, "Toulouse")
        ]
        
        # Analyze log patterns
        log_analysis = self.analyze_log_patterns()
        
        # Analyze data quality
        quality_analysis = self.analyze_data_quality(coordinates)
        
        # Combine results
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'log_analysis': log_analysis,
            'quality_analysis': quality_analysis,
            'summary': {
                'overall_meteofrance_success_rate': (quality_analysis['meteofrance_success'] / quality_analysis['total_tests']) * 100 if quality_analysis['total_tests'] > 0 else 0,
                'overall_fallback_rate': (quality_analysis['openmeteo_fallback'] / quality_analysis['total_tests']) * 100 if quality_analysis['total_tests'] > 0 else 0,
                'most_common_missing_field': max(quality_analysis['missing_fields'].items(), key=lambda x: x[1]) if quality_analysis['missing_fields'] else None,
                'most_common_error': quality_analysis['error_types'].most_common(1)[0] if quality_analysis['error_types'] else None,
                'average_response_time': quality_analysis.get('avg_response_time', 0)
            },
            'recommendations': self._generate_recommendations(log_analysis, quality_analysis)
        }
        
        return report
        
    def _generate_recommendations(self, log_analysis: Dict, quality_analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Check fallback rate
        fallback_rate = log_analysis.get('fallback_rate', 0)
        if fallback_rate > 20:
            recommendations.append(f"High fallback rate ({fallback_rate:.1f}%) - Consider investigating MeteoFrance API reliability")
        elif fallback_rate > 10:
            recommendations.append(f"Moderate fallback rate ({fallback_rate:.1f}%) - Monitor for degradation")
            
        # Check error rate
        error_rate = log_analysis.get('error_rate', 0)
        if error_rate > 15:
            recommendations.append(f"High error rate ({error_rate:.1f}%) - Investigate API stability issues")
            
        # Check missing fields
        missing_fields = quality_analysis.get('missing_fields', {})
        if missing_fields:
            most_missing = max(missing_fields.items(), key=lambda x: x[1])
            if most_missing[1] > quality_analysis['total_tests'] * 0.5:
                recommendations.append(f"Frequent missing field: {most_missing[0]} ({most_missing[1]} times) - Consider data validation")
                
        # Check response times
        avg_response_time = quality_analysis.get('avg_response_time', 0)
        if avg_response_time > 5:
            recommendations.append(f"Slow average response time ({avg_response_time:.2f}s) - Consider performance optimization")
            
        # Check temperature issues
        temp_issues = log_analysis.get('patterns', {}).get('temperature_issues', 0)
        if temp_issues > 100:
            recommendations.append(f"Many temperature validation issues ({temp_issues}) - Review temperature thresholds")
            
        # Check alerts parsing errors
        alerts_errors = log_analysis.get('patterns', {}).get('alerts_parsing_errors', 0)
        if alerts_errors > 10:
            recommendations.append(f"Frequent alerts parsing errors ({alerts_errors}) - Fix alerts data structure handling")
            
        if not recommendations:
            recommendations.append("No significant issues detected - API integration appears healthy")
            
        return recommendations
        
    def export_detailed_report(self, output_file: str = "detailed_meteofrance_analysis.json"):
        """Export detailed analysis report."""
        report = self.generate_comprehensive_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Detailed report exported to {output_file}")
        
    def export_daily_patterns_csv(self, output_file: str = "daily_meteofrance_patterns.csv"):
        """Export daily patterns to CSV."""
        log_analysis = self.analyze_log_patterns()
        daily_patterns = log_analysis.get('daily_patterns', {})
        
        if not daily_patterns:
            self.logger.warning("No daily patterns to export")
            return
            
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'meteofrance_success', 'meteofrance_failure', 'openmeteo_fallback', 'temperature_issues', 'alerts_errors']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for date, patterns in daily_patterns.items():
                row = {'date': date, **patterns}
                writer.writerow(row)
                
        self.logger.info(f"Daily patterns exported to {output_file}")


def main():
    """Main analysis function."""
    print("🔍 Detailed MeteoFrance API Analysis")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = DetailedMeteoFranceAnalyzer()
    
    # Generate comprehensive report
    print("\n📊 Generating comprehensive analysis...")
    report = analyzer.generate_comprehensive_report()
    
    # Display summary
    summary = report['summary']
    print(f"\n📈 Summary:")
    print(f"   MeteoFrance Success Rate: {summary['overall_meteofrance_success_rate']:.1f}%")
    print(f"   Fallback Rate: {summary['overall_fallback_rate']:.1f}%")
    print(f"   Average Response Time: {summary['average_response_time']:.2f}s")
    
    if summary['most_common_missing_field']:
        field, count = summary['most_common_missing_field']
        print(f"   Most Missing Field: {field} ({count} times)")
        
    if summary['most_common_error']:
        error_type, count = summary['most_common_error']
        print(f"   Most Common Error: {error_type} ({count} times)")
    
    # Display recommendations
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    # Export reports
    print(f"\n💾 Exporting reports...")
    analyzer.export_detailed_report()
    analyzer.export_daily_patterns_csv()
    
    print(f"\n✅ Analysis complete!")
    print(f"   - Detailed report: detailed_meteofrance_analysis.json")
    print(f"   - Daily patterns: daily_meteofrance_patterns.csv")


if __name__ == "__main__":
    main() 