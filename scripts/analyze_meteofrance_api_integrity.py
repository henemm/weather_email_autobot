#!/usr/bin/env python3
"""
MeteoFrance API Integrity Analysis Script

This script analyzes the usage and data quality of the meteofrance-api
over the last 14 days, identifying when and why fallbacks to open-meteo occur.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import csv
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_meteofrance import (
    get_forecast_with_fallback,
    get_thunderstorm_with_fallback,
    get_alerts_with_fallback,
    ForecastResult,
    Alert
)
from wetter.fetch_openmeteo import fetch_openmeteo_forecast


@dataclass
class APIAnalysisResult:
    """Result of API analysis for a single test."""
    timestamp: str
    etappe_name: str
    latitude: float
    longitude: float
    meteofrance_success: bool
    meteofrance_error: Optional[str]
    openmeteo_used: bool
    openmeteo_error: Optional[str]
    missing_fields: List[str]
    data_source: str
    temperature_meteofrance: Optional[float]
    temperature_openmeteo: Optional[float]
    precipitation_meteofrance: Optional[float]
    precipitation_openmeteo: Optional[float]
    wind_speed_meteofrance: Optional[float]
    wind_speed_openmeteo: Optional[float]
    thunderstorm_meteofrance: Optional[str]
    alerts_meteofrance: Optional[List[str]]


class MeteoFranceAPIAnalyzer:
    """Analyzer for MeteoFrance API integrity and fallback patterns."""
    
    def __init__(self, log_file: str = "logs/warning_monitor.log"):
        """Initialize the analyzer."""
        self.log_file = log_file
        self.results: List[APIAnalysisResult] = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_logs(self) -> Dict[str, Any]:
        """Analyze log files for API usage patterns."""
        if not os.path.exists(self.log_file):
            self.logger.warning(f"Log file not found: {self.log_file}")
            return {}
            
        self.logger.info(f"Analyzing log file: {self.log_file}")
        
        meteofrance_usage = 0
        openmeteo_fallbacks = 0
        meteofrance_errors = 0
        openmeteo_errors = 0
        
        error_patterns = {
            'meteofrance_api_failed': 0,
            'falling_back_to_openmeteo': 0,
            'openmeteo_failed': 0,
            'temperatures_too_low': 0,
            'alerts_parsing_error': 0
        }
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'meteofrance' in line.lower():
                        meteofrance_usage += 1
                        
                    if 'falling back to open-meteo' in line:
                        openmeteo_fallbacks += 1
                        error_patterns['falling_back_to_openmeteo'] += 1
                        
                    if 'meteofrance api failed' in line.lower():
                        meteofrance_errors += 1
                        error_patterns['meteofrance_api_failed'] += 1
                        
                    if 'open-meteo failed' in line.lower():
                        openmeteo_errors += 1
                        error_patterns['openmeteo_failed'] += 1
                        
                    if 'temperatures too low for summer' in line.lower():
                        error_patterns['temperatures_too_low'] += 1
                        
                    if "'list' object has no attribute 'items'" in line:
                        error_patterns['alerts_parsing_error'] += 1
                        
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            
        return {
            'meteofrance_usage': meteofrance_usage,
            'openmeteo_fallbacks': openmeteo_fallbacks,
            'meteofrance_errors': meteofrance_errors,
            'openmeteo_errors': openmeteo_errors,
            'error_patterns': error_patterns,
            'fallback_rate': (openmeteo_fallbacks / max(meteofrance_usage, 1)) * 100
        }
        
    def test_api_endpoints(self, coordinates: List[tuple]) -> List[APIAnalysisResult]:
        """Test API endpoints with given coordinates."""
        self.logger.info(f"Testing {len(coordinates)} coordinate pairs")
        
        for lat, lon, etappe_name in coordinates:
            try:
                result = self._test_single_location(lat, lon, etappe_name)
                self.results.append(result)
                self.logger.info(f"Tested {etappe_name}: MeteoFrance={'✅' if result.meteofrance_success else '❌'}, OpenMeteo={'✅' if result.openmeteo_used else '❌'}")
                
            except Exception as e:
                self.logger.error(f"Error testing {etappe_name}: {e}")
                
        return self.results
        
    def _test_single_location(self, lat: float, lon: float, etappe_name: str) -> APIAnalysisResult:
        """Test a single location with both APIs."""
        timestamp = datetime.now().isoformat()
        meteofrance_success = False
        meteofrance_error = None
        openmeteo_used = False
        openmeteo_error = None
        missing_fields = []
        data_source = "unknown"
        
        # Test MeteoFrance API
        temperature_meteofrance = None
        precipitation_meteofrance = None
        wind_speed_meteofrance = None
        thunderstorm_meteofrance = None
        alerts_meteofrance = None
        
        try:
            # Test forecast
            forecast_result = get_forecast_with_fallback(lat, lon)
            meteofrance_success = True
            data_source = forecast_result.data_source
            
            if data_source == "meteofrance-api":
                temperature_meteofrance = forecast_result.temperature
                precipitation_meteofrance = forecast_result.precipitation
                wind_speed_meteofrance = forecast_result.wind_speed
                
                # Check for missing fields
                if forecast_result.temperature is None:
                    missing_fields.append("temperature")
                if forecast_result.precipitation_probability is None:
                    missing_fields.append("precipitation_probability")
                if forecast_result.wind_speed is None:
                    missing_fields.append("wind_speed")
                if forecast_result.wind_gusts is None:
                    missing_fields.append("wind_gusts")
                if forecast_result.thunderstorm_probability is None:
                    missing_fields.append("thunderstorm_probability")
                    
            else:
                openmeteo_used = True
                
        except Exception as e:
            meteofrance_error = str(e)
            meteofrance_success = False
            
        # Test thunderstorm detection
        try:
            thunderstorm_result = get_thunderstorm_with_fallback(lat, lon)
            if "meteofrance-api" in thunderstorm_result:
                thunderstorm_meteofrance = thunderstorm_result
        except Exception as e:
            if meteofrance_error is None:
                meteofrance_error = f"Thunderstorm error: {e}"
                
        # Test alerts
        try:
            alerts_result = get_alerts_with_fallback(lat, lon)
            if alerts_result:
                alerts_meteofrance = [f"{alert.phenomenon}:{alert.level}" for alert in alerts_result]
        except Exception as e:
            if meteofrance_error is None:
                meteofrance_error = f"Alerts error: {e}"
                
        # Test OpenMeteo directly for comparison
        temperature_openmeteo = None
        precipitation_openmeteo = None
        wind_speed_openmeteo = None
        
        try:
            openmeteo_data = fetch_openmeteo_forecast(lat, lon)
            current = openmeteo_data.get('current', {})
            temperature_openmeteo = current.get('temperature_2m')
            precipitation_openmeteo = current.get('precipitation')
            wind_speed_openmeteo = current.get('wind_speed')
        except Exception as e:
            openmeteo_error = str(e)
            
        return APIAnalysisResult(
            timestamp=timestamp,
            etappe_name=etappe_name,
            latitude=lat,
            longitude=lon,
            meteofrance_success=meteofrance_success,
            meteofrance_error=meteofrance_error,
            openmeteo_used=openmeteo_used,
            openmeteo_error=openmeteo_error,
            missing_fields=missing_fields,
            data_source=data_source,
            temperature_meteofrance=temperature_meteofrance,
            temperature_openmeteo=temperature_openmeteo,
            precipitation_meteofrance=precipitation_meteofrance,
            precipitation_openmeteo=precipitation_openmeteo,
            wind_speed_meteofrance=wind_speed_meteofrance,
            wind_speed_openmeteo=wind_speed_openmeteo,
            thunderstorm_meteofrance=thunderstorm_meteofrance,
            alerts_meteofrance=alerts_meteofrance
        )
        
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of the analysis."""
        if not self.results:
            return {"error": "No test results available"}
            
        total_tests = len(self.results)
        meteofrance_success = sum(1 for r in self.results if r.meteofrance_success)
        openmeteo_used = sum(1 for r in self.results if r.openmeteo_used)
        meteofrance_errors = sum(1 for r in self.results if r.meteofrance_error is not None)
        openmeteo_errors = sum(1 for r in self.results if r.openmeteo_error is not None)
        
        # Analyze missing fields
        all_missing_fields = []
        for result in self.results:
            all_missing_fields.extend(result.missing_fields)
            
        field_missing_counts = {}
        for field in all_missing_fields:
            field_missing_counts[field] = field_missing_counts.get(field, 0) + 1
            
        # Analyze error patterns
        error_types = {}
        for result in self.results:
            if result.meteofrance_error:
                error_key = result.meteofrance_error.split(':')[0] if ':' in result.meteofrance_error else result.meteofrance_error
                error_types[error_key] = error_types.get(error_key, 0) + 1
                
        return {
            'total_tests': total_tests,
            'meteofrance_success_rate': (meteofrance_success / total_tests) * 100,
            'openmeteo_fallback_rate': (openmeteo_used / total_tests) * 100,
            'meteofrance_error_rate': (meteofrance_errors / total_tests) * 100,
            'openmeteo_error_rate': (openmeteo_errors / total_tests) * 100,
            'missing_fields_analysis': field_missing_counts,
            'error_patterns': error_types,
            'data_source_distribution': {
                'meteofrance-api': sum(1 for r in self.results if r.data_source == 'meteofrance-api'),
                'open-meteo': sum(1 for r in self.results if r.data_source == 'open-meteo')
            }
        }
        
    def export_results(self, output_file: str = "meteofrance_api_analysis.csv"):
        """Export results to CSV file."""
        if not self.results:
            self.logger.warning("No results to export")
            return
            
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp', 'etappe_name', 'latitude', 'longitude',
                'meteofrance_success', 'meteofrance_error', 'openmeteo_used',
                'openmeteo_error', 'missing_fields', 'data_source',
                'temperature_meteofrance', 'temperature_openmeteo',
                'precipitation_meteofrance', 'precipitation_openmeteo',
                'wind_speed_meteofrance', 'wind_speed_openmeteo',
                'thunderstorm_meteofrance', 'alerts_meteofrance'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                row = asdict(result)
                row['missing_fields'] = ','.join(result.missing_fields)
                row['alerts_meteofrance'] = ','.join(result.alerts_meteofrance) if result.alerts_meteofrance else ''
                writer.writerow(row)
                
        self.logger.info(f"Results exported to {output_file}")
        
    def export_summary(self, output_file: str = "meteofrance_api_summary.json"):
        """Export summary report to JSON file."""
        summary = self.generate_summary_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Summary exported to {output_file}")


def get_test_coordinates() -> List[tuple]:
    """Get test coordinates from etappen.json."""
    try:
        etappen_file = Path("etappen.json")
        if not etappen_file.exists():
            # Fallback coordinates for testing
            return [
                (43.2333, 0.0833, "Tarbes"),
                (48.8566, 2.3522, "Paris"),
                (43.2965, 5.3698, "Marseille"),
                (45.7640, 4.8357, "Lyon"),
                (43.6047, 1.4442, "Toulouse")
            ]
            
        with open(etappen_file, 'r', encoding='utf-8') as f:
            etappen_data = json.load(f)
            
        coordinates = []
        for etappe in etappen_data.get('etappen', []):
            if 'coordinates' in etappe:
                coords = etappe['coordinates']
                if isinstance(coords, dict) and 'lat' in coords and 'lon' in coords:
                    coordinates.append((
                        float(coords['lat']),
                        float(coords['lon']),
                        etappe.get('name', 'Unknown')
                    ))
                    
        return coordinates[:10]  # Limit to first 10 for testing
        
    except Exception as e:
        logging.error(f"Error reading etappen.json: {e}")
        # Fallback coordinates
        return [
            (43.2333, 0.0833, "Tarbes"),
            (48.8566, 2.3522, "Paris")
        ]


def main():
    """Main analysis function."""
    print("🌤️  MeteoFrance API Integrity Analysis")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = MeteoFranceAPIAnalyzer()
    
    # Analyze logs
    print("\n📊 Analyzing log files...")
    log_analysis = analyzer.analyze_logs()
    
    if log_analysis:
        print(f"   MeteoFrance API usage: {log_analysis.get('meteofrance_usage', 0)}")
        print(f"   OpenMeteo fallbacks: {log_analysis.get('openmeteo_fallbacks', 0)}")
        print(f"   Fallback rate: {log_analysis.get('fallback_rate', 0):.1f}%")
        print(f"   Error patterns: {log_analysis.get('error_patterns', {})}")
    
    # Test API endpoints
    print("\n🧪 Testing API endpoints...")
    coordinates = get_test_coordinates()
    results = analyzer.test_api_endpoints(coordinates)
    
    # Generate summary
    print("\n📈 Generating summary report...")
    summary = analyzer.generate_summary_report()
    
    if 'error' not in summary:
        print(f"   Total tests: {summary['total_tests']}")
        print(f"   MeteoFrance success rate: {summary['meteofrance_success_rate']:.1f}%")
        print(f"   OpenMeteo fallback rate: {summary['openmeteo_fallback_rate']:.1f}%")
        print(f"   MeteoFrance error rate: {summary['meteofrance_error_rate']:.1f}%")
        print(f"   Missing fields: {summary['missing_fields_analysis']}")
        print(f"   Data source distribution: {summary['data_source_distribution']}")
    
    # Export results
    print("\n💾 Exporting results...")
    analyzer.export_results()
    analyzer.export_summary()
    
    print("\n✅ Analysis complete!")
    print("   - Detailed results: meteofrance_api_analysis.csv")
    print("   - Summary report: meteofrance_api_summary.json")


if __name__ == "__main__":
    main() 