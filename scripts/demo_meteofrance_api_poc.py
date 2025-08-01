#!/usr/bin/env python3
"""
MeteoFrance API Proof of Concept for Tarbes, France.

This script tests the official meteofrance-api library to validate that it provides
comparable data to the public website, especially for thunderstorm conditions.

Location: Tarbes, France (43.2333°N, 0.0833°E)
Department: 65
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from meteofrance_api.client import MeteoFranceClient
except ImportError:
    print("Error: meteofrance-api not installed. Run: pip install meteofrance-api")
    sys.exit(1)


class MeteoFranceAPIPOC:
    """Proof of Concept for MeteoFrance API testing."""
    
    def __init__(self):
        """Initialize the API client and test parameters."""
        self.client = MeteoFranceClient()
        self.latitude = 43.2333
        self.longitude = 0.0833
        self.department = "65"  # Tarbes department
        
    def get_weather_forecast(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve weather forecast for Tarbes.
        
        Returns:
            Dictionary containing forecast data or None if error
        """
        try:
            print(f"Fetching weather forecast for Tarbes ({self.latitude}, {self.longitude})...")
            forecast = self.client.get_forecast(self.latitude, self.longitude)
            
            # Extract relevant forecast data
            forecast_data = {
                'location': 'Tarbes',
                'coordinates': {'lat': self.latitude, 'lon': self.longitude},
                'forecast_periods': []
            }
            
            for period in forecast.forecast[:24]:  # First 24 hours
                period_data = {
                    'datetime': getattr(period, 'datetime', 'Unknown'),
                    'temperature': getattr(period, 'T', {}).get('value', 'N/A'),
                    'weather_description': getattr(period, 'weather', 'Unknown'),
                    'precipitation_probability': getattr(period, 'precipitation_probability', 'N/A')
                }
                forecast_data['forecast_periods'].append(period_data)
                
            return forecast_data
            
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def get_weather_warnings(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve current weather warnings for department 65.
        
        Returns:
            Dictionary containing warning data or None if error
        """
        try:
            print(f"Fetching weather warnings for department {self.department}...")
            warnings = self.client.get_warning_current_phenomenons(self.department)
            
            warning_data = {
                'department': self.department,
                'phenomenons': warnings.phenomenons_max_colors,
                'domain_id': getattr(warnings, 'domain_id', 'Unknown'),
                'update_time': datetime.now().isoformat()
            }
            
            return warning_data
            
        except Exception as e:
            print(f"Error fetching warnings: {e}")
            return None
    
    def get_rain_forecast(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve rain forecast for Tarbes.
        
        Returns:
            Dictionary containing rain forecast data or None if error
        """
        try:
            print(f"Fetching rain forecast for Tarbes...")
            rain = self.client.get_rain(self.latitude, self.longitude)
            
            rain_data = {
                'location': 'Tarbes',
                'coordinates': {'lat': self.latitude, 'lon': self.longitude},
                'rain_forecast': []
            }
            
            for period in rain.forecast[:12]:  # First 12 periods
                period_data = {
                    'datetime': getattr(period, 'datetime', 'Unknown'),
                    'intensity': getattr(period, 'intensity', 'N/A')
                }
                rain_data['rain_forecast'].append(period_data)
                
            return rain_data
            
        except Exception as e:
            print(f"Error fetching rain forecast: {e}")
            return None
    
    def analyze_thunderstorm_conditions(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze forecast data for thunderstorm conditions.
        
        Args:
            forecast_data: Weather forecast data
            
        Returns:
            Dictionary with thunderstorm analysis
        """
        if not forecast_data or 'forecast_periods' not in forecast_data:
            return {'error': 'No forecast data available'}
        
        thunderstorm_periods = []
        high_precipitation_periods = []
        
        for period in forecast_data['forecast_periods']:
            weather = period.get('weather_description', '').lower()
            precip_prob = period.get('precipitation_probability', 0)
            
            if 'thunder' in weather or 'storm' in weather:
                thunderstorm_periods.append(period)
            
            if isinstance(precip_prob, (int, float)) and precip_prob > 70:
                high_precipitation_periods.append(period)
        
        analysis = {
            'thunderstorm_periods_count': len(thunderstorm_periods),
            'high_precipitation_periods_count': len(high_precipitation_periods),
            'thunderstorm_periods': thunderstorm_periods,
            'high_precipitation_periods': high_precipitation_periods
        }
        
        return analysis
    
    def compare_with_website_expectations(self, forecast_data: Dict[str, Any], 
                                        warning_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare API data with expected website data patterns.
        
        Args:
            forecast_data: Weather forecast from API
            warning_data: Weather warnings from API
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            'api_functional': True,
            'data_quality': 'unknown',
            'thunderstorm_detection': False,
            'warning_system_working': False,
            'temperature_range_plausible': False,
            'notes': []
        }
        
        # Check if API is functional
        if not forecast_data:
            comparison['api_functional'] = False
            comparison['notes'].append('Forecast API not responding')
            return comparison
        
        # Check thunderstorm detection
        if forecast_data.get('forecast_periods'):
            weather_descriptions = [
                period.get('weather_description', '').lower() 
                for period in forecast_data['forecast_periods']
            ]
            comparison['thunderstorm_detection'] = any(
                'thunder' in desc or 'storm' in desc for desc in weather_descriptions
            )
        
        # Check warning system
        if warning_data and warning_data.get('phenomenons'):
            comparison['warning_system_working'] = True
            if 'Thunderstorms' in warning_data['phenomenons']:
                comparison['notes'].append(
                    f"Thunderstorm warning active: {warning_data['phenomenons']['Thunderstorms']}"
                )
        
        # Check temperature plausibility
        if forecast_data.get('forecast_periods'):
            temperatures = [
                period.get('temperature') 
                for period in forecast_data['forecast_periods']
                if isinstance(period.get('temperature'), (int, float))
            ]
            if temperatures:
                temp_range = max(temperatures) - min(temperatures)
                comparison['temperature_range_plausible'] = 0 <= temp_range <= 30
        
        return comparison
    
    def run_full_test(self) -> Dict[str, Any]:
        """
        Run complete proof of concept test.
        
        Returns:
            Dictionary with all test results
        """
        print("=== MeteoFrance API Proof of Concept Test ===")
        print(f"Location: Tarbes, France (Department {self.department})")
        print(f"Coordinates: {self.latitude}°N, {self.longitude}°E")
        print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            'test_info': {
                'location': 'Tarbes',
                'department': self.department,
                'coordinates': {'lat': self.latitude, 'lon': self.longitude},
                'test_time': datetime.now().isoformat()
            },
            'forecast_data': None,
            'warning_data': None,
            'rain_data': None,
            'thunderstorm_analysis': None,
            'comparison_results': None
        }
        
        # Get forecast data
        results['forecast_data'] = self.get_weather_forecast()
        
        # Get warning data
        results['warning_data'] = self.get_weather_warnings()
        
        # Get rain forecast
        results['rain_data'] = self.get_rain_forecast()
        
        # Analyze thunderstorm conditions
        if results['forecast_data']:
            results['thunderstorm_analysis'] = self.analyze_thunderstorm_conditions(
                results['forecast_data']
            )
        
        # Compare with website expectations
        results['comparison_results'] = self.compare_with_website_expectations(
            results['forecast_data'], results['warning_data']
        )
        
        # Print summary
        self.print_test_summary(results)
        
        return results
    
    def print_test_summary(self, results: Dict[str, Any]):
        """Print a summary of test results."""
        print("\n=== Test Summary ===")
        
        comparison = results.get('comparison_results', {})
        
        print(f"API Functional: {'✅' if comparison.get('api_functional') else '❌'}")
        print(f"Thunderstorm Detection: {'✅' if comparison.get('thunderstorm_detection') else '❌'}")
        print(f"Warning System Working: {'✅' if comparison.get('warning_system_working') else '❌'}")
        print(f"Temperature Range Plausible: {'✅' if comparison.get('temperature_range_plausible') else '❌'}")
        
        if comparison.get('notes'):
            print("\nNotes:")
            for note in comparison['notes']:
                print(f"  - {note}")
        
        if results.get('thunderstorm_analysis'):
            analysis = results['thunderstorm_analysis']
            print(f"\nThunderstorm Analysis:")
            print(f"  - Thunderstorm periods: {analysis.get('thunderstorm_periods_count', 0)}")
            print(f"  - High precipitation periods: {analysis.get('high_precipitation_periods_count', 0)}")
        
        print("\n=== End of Test ===")


def main():
    """Main function to run the proof of concept test."""
    poc = MeteoFranceAPIPOC()
    results = poc.run_full_test()
    
    # Save results to file
    output_file = f"meteofrance_api_poc_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main() 