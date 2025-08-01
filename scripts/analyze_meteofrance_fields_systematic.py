#!/usr/bin/env python3
"""
Systematic analysis of MeteoFrance API field availability and data quality.

This script performs a comprehensive analysis of the MeteoFrance API integration
to identify systematic weaknesses and non-functional aspects as requested in
requests/analyse_meteofrance_fields.md.
"""

import sys
import os
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meteofrance_api.client import MeteoFranceClient
from src.wetter.fetch_meteofrance import get_forecast, get_forecast_with_fallback
from src.wetter.fetch_openmeteo import fetch_openmeteo_forecast


class MeteoFranceFieldAnalyzer:
    """Systematic analyzer for MeteoFrance API field availability and quality."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.client = MeteoFranceClient()
        self.results = {
            'field_matrix': [],
            'fallback_reasons': [],
            'alerts_parsing_issues': [],
            'api_usage_breakdown': {}
        }
        
    def analyze_api_response_structure(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        """
        Analyze the complete API response structure for field availability.
        
        Args:
            lat: Latitude
            lon: Longitude
            location_name: Name of the location
            
        Returns:
            Dictionary with field availability analysis
        """
        print(f"🔍 Analyzing API response structure for {location_name} ({lat}, {lon})")
        
        try:
            # Get raw forecast data
            forecast = self.client.get_forecast(lat, lon)
            
            if not forecast or not forecast.forecast:
                return {
                    'location': location_name,
                    'coordinates': f"{lat}, {lon}",
                    'timestamp': datetime.now().isoformat(),
                    'status': 'no_data',
                    'entries_analyzed': 0,
                    'field_availability': {},
                    'data_quality_issues': []
                }
            
            # Analyze first 6 entries (24 hours)
            entries_to_analyze = forecast.forecast[:6]
            field_availability = {}
            data_quality_issues = []
            
            # Track field presence across all entries
            all_fields = set()
            field_values = {}
            
            for i, entry in enumerate(entries_to_analyze):
                # Collect all field names
                all_fields.update(entry.keys())
                
                # Analyze specific weather-related fields
                for field_name in entry.keys():
                    if field_name not in field_values:
                        field_values[field_name] = []
                    field_values[field_name].append(entry[field_name])
            
            # Analyze field availability
            for field in all_fields:
                values = field_values.get(field, [])
                non_null_count = sum(1 for v in values if v is not None and v != "")
                availability_pct = (non_null_count / len(values)) * 100 if values else 0
                
                field_availability[field] = {
                    'available': non_null_count > 0,
                    'availability_percentage': availability_pct,
                    'total_entries': len(values),
                    'non_null_entries': non_null_count,
                    'sample_values': values[:3]  # First 3 values as sample
                }
                
                # Check for data quality issues
                if field in ['T', 'temperature', 'temp']:
                    temp_values = [v for v in values if v is not None]
                    if temp_values:
                        # Check for 0°C temperatures in summer
                        zero_temp_count = sum(1 for v in temp_values if v == 0)
                        if zero_temp_count > 0:
                            data_quality_issues.append({
                                'field': field,
                                'issue': 'zero_temperature_summer',
                                'count': zero_temp_count,
                                'total': len(temp_values)
                            })
                
                # Check for null/empty values
                null_count = sum(1 for v in values if v is None or v == "")
                if null_count > 0:
                    data_quality_issues.append({
                        'field': field,
                        'issue': 'null_or_empty_values',
                        'count': null_count,
                        'total': len(values)
                    })
            
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'entries_analyzed': len(entries_to_analyze),
                'field_availability': field_availability,
                'data_quality_issues': data_quality_issues,
                'total_fields_found': len(all_fields)
            }
            
        except Exception as e:
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error_message': str(e),
                'entries_analyzed': 0,
                'field_availability': {},
                'data_quality_issues': []
            }
    
    def analyze_fallback_patterns(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        """
        Analyze fallback patterns and reasons.
        
        Args:
            lat: Latitude
            lon: Longitude
            location_name: Name of the location
            
        Returns:
            Dictionary with fallback analysis
        """
        print(f"🔄 Analyzing fallback patterns for {location_name}")
        
        try:
            # Test MeteoFrance API directly
            meteofrance_result = None
            meteofrance_error = None
            
            try:
                meteofrance_result = get_forecast(lat, lon)
            except Exception as e:
                meteofrance_error = str(e)
            
            # Test with fallback
            fallback_result = None
            fallback_error = None
            
            try:
                fallback_result = get_forecast_with_fallback(lat, lon)
            except Exception as e:
                fallback_error = str(e)
            
            # Determine fallback reason
            fallback_reason = None
            if meteofrance_error and fallback_result:
                if "temperature" in meteofrance_error.lower():
                    fallback_reason = "temperature_validation_failed"
                elif "api" in meteofrance_error.lower():
                    fallback_reason = "api_error"
                else:
                    fallback_reason = "unknown_error"
            
            # Compare data sources
            data_source_comparison = {
                'meteofrance_available': meteofrance_result is not None,
                'meteofrance_error': meteofrance_error,
                'fallback_used': fallback_result and fallback_result.data_source == "open-meteo",
                'fallback_reason': fallback_reason,
                'final_data_source': fallback_result.data_source if fallback_result else None
            }
            
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'fallback_analysis': data_source_comparison
            }
            
        except Exception as e:
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error_message': str(e)
            }
    
    def analyze_alerts_parsing(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        """
        Analyze alerts parsing and structure.
        
        Args:
            lat: Latitude
            lon: Longitude
            location_name: Name of the location
            
        Returns:
            Dictionary with alerts analysis
        """
        print(f"⚠️ Analyzing alerts parsing for {location_name}")
        
        try:
            from src.wetter.fetch_meteofrance import get_alerts
            
            alerts_result = None
            alerts_error = None
            
            try:
                alerts_result = get_alerts(lat, lon)
            except Exception as e:
                alerts_error = str(e)
            
            alerts_analysis = {
                'alerts_available': alerts_result is not None and len(alerts_result) > 0,
                'alerts_count': len(alerts_result) if alerts_result else 0,
                'alerts_error': alerts_error,
                'alerts_structure': []
            }
            
            if alerts_result:
                for alert in alerts_result:
                    alert_structure = {
                        'phenomenon': getattr(alert, 'phenomenon', None),
                        'level': getattr(alert, 'level', None),
                        'description': getattr(alert, 'description', None)
                    }
                    alerts_analysis['alerts_structure'].append(alert_structure)
            
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'alerts_analysis': alerts_analysis
            }
            
        except Exception as e:
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error_message': str(e)
            }
    
    def compare_with_openmeteo(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        """
        Compare MeteoFrance data with OpenMeteo fallback.
        
        Args:
            lat: Latitude
            lon: Longitude
            location_name: Name of the location
            
        Returns:
            Dictionary with comparison analysis
        """
        print(f"📊 Comparing MeteoFrance with OpenMeteo for {location_name}")
        
        try:
            # Get MeteoFrance data
            meteofrance_data = None
            try:
                meteofrance_data = get_forecast(lat, lon)
            except Exception:
                pass
            
            # Get OpenMeteo data
            openmeteo_data = None
            try:
                openmeteo_data = fetch_openmeteo_forecast(lat, lon)
            except Exception:
                pass
            
            comparison = {
                'meteofrance_available': meteofrance_data is not None,
                'openmeteo_available': openmeteo_data is not None,
                'field_comparison': {}
            }
            
            if meteofrance_data and openmeteo_data:
                # Compare temperature
                mf_temp = meteofrance_data.temperature
                om_temp = openmeteo_data.get('current', {}).get('temperature_2m')
                
                comparison['field_comparison']['temperature'] = {
                    'meteofrance': mf_temp,
                    'openmeteo': om_temp,
                    'difference': mf_temp - om_temp if mf_temp and om_temp else None
                }
                
                # Compare wind speed
                mf_wind = meteofrance_data.wind_speed
                om_wind = openmeteo_data.get('current', {}).get('wind_speed_10m')
                
                comparison['field_comparison']['wind_speed'] = {
                    'meteofrance': mf_wind,
                    'openmeteo': om_wind,
                    'difference': mf_wind - om_wind if mf_wind and om_wind else None
                }
            
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'comparison': comparison
            }
            
        except Exception as e:
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error_message': str(e)
            }
    
    def run_comprehensive_analysis(self):
        """Run comprehensive analysis on multiple test locations."""
        print("🚀 Starting comprehensive MeteoFrance API field analysis")
        print("=" * 80)
        
        # Test locations (from etappen.json)
        test_locations = [
            (42.4542, 8.7389, "Asco"),
            (41.7, 9.3, "Conca"),
            (42.426238, 8.900291, "Ascu"),
            (42.307, 9.150, "Corte"),
            (48.8566, 2.3522, "Paris")  # Control location
        ]
        
        for lat, lon, location_name in test_locations:
            print(f"\n📍 Testing location: {location_name}")
            print("-" * 50)
            
            # 1. API Response Structure Analysis
            structure_analysis = self.analyze_api_response_structure(lat, lon, location_name)
            self.results['field_matrix'].append(structure_analysis)
            
            # 2. Fallback Pattern Analysis
            fallback_analysis = self.analyze_fallback_patterns(lat, lon, location_name)
            self.results['fallback_reasons'].append(fallback_analysis)
            
            # 3. Alerts Parsing Analysis
            alerts_analysis = self.analyze_alerts_parsing(lat, lon, location_name)
            self.results['alerts_parsing_issues'].append(alerts_analysis)
            
            # 4. OpenMeteo Comparison
            comparison_analysis = self.compare_with_openmeteo(lat, lon, location_name)
            self.results['api_usage_breakdown'][location_name] = comparison_analysis
        
        # Generate output files
        self.generate_output_files()
        
        print("\n✅ Analysis complete! Output files generated.")
    
    def generate_output_files(self):
        """Generate the required output files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Field Matrix CSV
        field_matrix_file = f"field_matrix_meteofrance_{timestamp}.csv"
        with open(field_matrix_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Location', 'Coordinates', 'Timestamp', 'Status', 'Entries_Analyzed',
                'Total_Fields', 'Field_Name', 'Available', 'Availability_Percentage',
                'Total_Entries', 'Non_Null_Entries', 'Sample_Values'
            ])
            
            for analysis in self.results['field_matrix']:
                if analysis['status'] == 'success':
                    for field_name, field_data in analysis['field_availability'].items():
                        writer.writerow([
                            analysis['location'],
                            analysis['coordinates'],
                            analysis['timestamp'],
                            analysis['status'],
                            analysis['entries_analyzed'],
                            analysis['total_fields_found'],
                            field_name,
                            field_data['available'],
                            field_data['availability_percentage'],
                            field_data['total_entries'],
                            field_data['non_null_entries'],
                            str(field_data['sample_values'])
                        ])
        
        # 2. Fallback Reason Log CSV
        fallback_log_file = f"fallback_reason_log_{timestamp}.csv"
        with open(fallback_log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Location', 'Coordinates', 'Timestamp', 'MeteoFrance_Available',
                'MeteoFrance_Error', 'Fallback_Used', 'Fallback_Reason', 'Final_Data_Source'
            ])
            
            for analysis in self.results['fallback_reasons']:
                if 'fallback_analysis' in analysis:
                    fallback_data = analysis['fallback_analysis']
                    writer.writerow([
                        analysis['location'],
                        analysis['coordinates'],
                        analysis['timestamp'],
                        fallback_data['meteofrance_available'],
                        fallback_data['meteofrance_error'],
                        fallback_data['fallback_used'],
                        fallback_data['fallback_reason'],
                        fallback_data['final_data_source']
                    ])
        
        # 3. Alerts Parsing Issues CSV
        alerts_file = f"alerts_parsing_issues_{timestamp}.csv"
        with open(alerts_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Location', 'Coordinates', 'Timestamp', 'Alerts_Available',
                'Alerts_Count', 'Alerts_Error', 'Phenomenon', 'Level', 'Description'
            ])
            
            for analysis in self.results['alerts_parsing_issues']:
                if 'alerts_analysis' in analysis:
                    alerts_data = analysis['alerts_analysis']
                    if alerts_data['alerts_structure']:
                        for alert in alerts_data['alerts_structure']:
                            writer.writerow([
                                analysis['location'],
                                analysis['coordinates'],
                                analysis['timestamp'],
                                alerts_data['alerts_available'],
                                alerts_data['alerts_count'],
                                alerts_data['alerts_error'],
                                alert['phenomenon'],
                                alert['level'],
                                alert['description']
                            ])
                    else:
                        writer.writerow([
                            analysis['location'],
                            analysis['coordinates'],
                            analysis['timestamp'],
                            alerts_data['alerts_available'],
                            alerts_data['alerts_count'],
                            alerts_data['alerts_error'],
                            '', '', ''
                        ])
        
        # 4. API Usage Breakdown Markdown
        api_usage_file = f"api_usage_breakdown_{timestamp}.md"
        with open(api_usage_file, 'w', encoding='utf-8') as f:
            f.write("# MeteoFrance API Usage Breakdown\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("## Test Locations\n\n")
            for location_name, analysis in self.results['api_usage_breakdown'].items():
                f.write(f"### {location_name}\n")
                f.write(f"- Coordinates: {analysis['coordinates']}\n")
                f.write(f"- MeteoFrance Available: {analysis['comparison']['meteofrance_available']}\n")
                f.write(f"- OpenMeteo Available: {analysis['comparison']['openmeteo_available']}\n")
                
                if analysis['comparison']['field_comparison']:
                    f.write("- Field Comparison:\n")
                    for field, comparison in analysis['comparison']['field_comparison'].items():
                        f.write(f"  - {field}: MF={comparison['meteofrance']}, OM={comparison['openmeteo']}\n")
                f.write("\n")
        
        print(f"📁 Generated output files:")
        print(f"   - {field_matrix_file}")
        print(f"   - {fallback_log_file}")
        print(f"   - {alerts_file}")
        print(f"   - {api_usage_file}")


def main():
    """Main function to run the analysis."""
    analyzer = MeteoFranceFieldAnalyzer()
    analyzer.run_comprehensive_analysis()


if __name__ == "__main__":
    main() 