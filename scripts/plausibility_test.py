#!/usr/bin/env python3
"""
Comprehensive Plausibility Test for Weather Data Aggregation and Report Generation.

This script validates:
1. Data consistency across different report types
2. Correct date handling for morning/evening/update reports
3. Proper aggregation of weather data
4. Format compliance with email_format.mdc specification
5. Logical consistency of weather values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.wetter.weather_data_processor import WeatherDataProcessor
from src.report.weather_report_generator import generate_weather_report


class PlausibilityTest:
    """Comprehensive plausibility test for weather data processing."""
    
    def __init__(self):
        self.config = self._load_config()
        self.processor = WeatherDataProcessor(self.config)
        self.test_results = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.yaml."""
        config_path = "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def run_all_tests(self):
        """Run all plausibility tests."""
        print("🔍 Starting Comprehensive Plausibility Tests")
        print("=" * 70)
        
        # Test 1: Data Consistency Across Report Types
        self._test_data_consistency()
        
        # Test 2: Date Logic Validation
        self._test_date_logic()
        
        # Test 3: Weather Value Plausibility
        self._test_weather_value_plausibility()
        
        # Test 4: Aggregation Logic
        self._test_aggregation_logic()
        
        # Test 5: Report Format Compliance
        self._test_report_format_compliance()
        
        # Test 6: Character Limit Compliance
        self._test_character_limit_compliance()
        
        # Test 7: Edge Cases
        self._test_edge_cases()
        
        # Test 8: Thunderstorm Next Day Logic
        self._test_thunderstorm_next_day_logic()
        
        # Print summary
        self._print_summary()
    
    def _test_data_consistency(self):
        """Test that data is consistent across different report types."""
        print("\n📊 Test 1: Data Consistency Across Report Types")
        print("-" * 50)
        
        test_coords = {
            'latitude': 42.3069,
            'longitude': 9.1497,
            'location_name': 'Corte'
        }
        
        # Generate data for all report types
        report_types = ['morning', 'evening', 'update']
        data_by_type = {}
        
        for report_type in report_types:
            data = self.processor.process_weather_data(
                latitude=test_coords['latitude'],
                longitude=test_coords['longitude'],
                location_name=test_coords['location_name'],
                report_type=report_type
            )
            data_by_type[report_type] = data
        
        # Check consistency
        issues = []
        
        # Morning and Update should use same target date (today)
        morning_date = data_by_type['morning'].get('target_date', '')
        update_date = data_by_type['update'].get('target_date', '')
        if morning_date != update_date:
            issues.append(f"Morning and Update reports should use same date: {morning_date} vs {update_date}")
        
        # Evening should use different date (tomorrow)
        evening_date = data_by_type['evening'].get('target_date', '')
        if evening_date == morning_date:
            issues.append(f"Evening report should use different date than morning: {evening_date}")
        
        # Thunderstorm next day should be different for evening vs morning/update
        morning_next = data_by_type['morning'].get('thunderstorm_next_day_date', '')
        evening_next = data_by_type['evening'].get('thunderstorm_next_day_date', '')
        update_next = data_by_type['update'].get('thunderstorm_next_day_date', '')
        
        if morning_next != update_next:
            issues.append(f"Morning and Update should have same thunderstorm next day: {morning_next} vs {update_next}")
        
        if evening_next == morning_next:
            issues.append(f"Evening should have different thunderstorm next day: {evening_next} vs {morning_next}")
        
        # Min temperature should only be calculated for evening reports
        for report_type in report_types:
            min_temp = data_by_type[report_type].get('min_temperature', 0)
            if report_type == 'evening' and min_temp == 0:
                issues.append(f"Evening report should have min_temperature > 0: {min_temp}")
            elif report_type != 'evening' and min_temp > 0:
                issues.append(f"{report_type.capitalize()} report should have min_temperature = 0: {min_temp}")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Data Consistency', False, issue))
        else:
            print("✅ Data consistency across report types is correct")
            self.test_results.append(('Data Consistency', True, "All checks passed"))
    
    def _test_date_logic(self):
        """Test that date logic follows email_format.mdc specification."""
        print("\n📅 Test 2: Date Logic Validation")
        print("-" * 40)
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        
        test_coords = {
            'latitude': 42.3069,
            'longitude': 9.1497,
            'location_name': 'Corte'
        }
        
        issues = []
        
        # Test morning report date logic
        morning_data = self.processor.process_weather_data(
            latitude=test_coords['latitude'],
            longitude=test_coords['longitude'],
            location_name=test_coords['location_name'],
            report_type='morning'
        )
        
        morning_target = morning_data.get('target_date', '')
        if morning_target:
            morning_date = datetime.fromisoformat(morning_target).date()
            if morning_date != today:
                issues.append(f"Morning report should use today's date: {morning_date} vs {today}")
        
        morning_next = morning_data.get('thunderstorm_next_day_date', '')
        if morning_next:
            morning_next_date = datetime.fromisoformat(morning_next).date()
            if morning_next_date != tomorrow:
                issues.append(f"Morning report thunderstorm next day should be tomorrow: {morning_next_date} vs {tomorrow}")
        
        # Test evening report date logic
        evening_data = self.processor.process_weather_data(
            latitude=test_coords['latitude'],
            longitude=test_coords['longitude'],
            location_name=test_coords['location_name'],
            report_type='evening'
        )
        
        evening_target = evening_data.get('target_date', '')
        if evening_target:
            evening_date = datetime.fromisoformat(evening_target).date()
            if evening_date != tomorrow:
                issues.append(f"Evening report should use tomorrow's date: {evening_date} vs {tomorrow}")
        
        evening_next = evening_data.get('thunderstorm_next_day_date', '')
        if evening_next:
            evening_next_date = datetime.fromisoformat(evening_next).date()
            if evening_next_date != day_after_tomorrow:
                issues.append(f"Evening report thunderstorm next day should be day after tomorrow: {evening_next_date} vs {day_after_tomorrow}")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Date Logic', False, issue))
        else:
            print("✅ Date logic follows email_format.mdc specification")
            self.test_results.append(('Date Logic', True, "All date logic correct"))
    
    def _test_weather_value_plausibility(self):
        """Test that weather values are within plausible ranges."""
        print("\n🌡️ Test 3: Weather Value Plausibility")
        print("-" * 40)
        
        test_coords = {
            'latitude': 42.3069,
            'longitude': 9.1497,
            'location_name': 'Corte'
        }
        
        # Test with evening report (most likely to have data)
        data = self.processor.process_weather_data(
            latitude=test_coords['latitude'],
            longitude=test_coords['longitude'],
            location_name=test_coords['location_name'],
            report_type='evening'
        )
        
        issues = []
        
        # Temperature checks
        max_temp = data.get('max_temperature', 0)
        min_temp = data.get('min_temperature', 0)
        
        if max_temp < -50 or max_temp > 60:
            issues.append(f"Max temperature out of plausible range: {max_temp}°C")
        
        if min_temp < -50 or min_temp > 40:
            issues.append(f"Min temperature out of plausible range: {min_temp}°C")
        
        if min_temp > max_temp and min_temp > 0 and max_temp > 0:
            issues.append(f"Min temperature higher than max temperature: {min_temp}°C > {max_temp}°C")
        
        # Probability checks
        thunderstorm_prob = data.get('max_thunderstorm_probability', 0)
        rain_prob = data.get('max_rain_probability', 0)
        
        if thunderstorm_prob < 0 or thunderstorm_prob > 100:
            issues.append(f"Thunderstorm probability out of range: {thunderstorm_prob}%")
        
        if rain_prob < 0 or rain_prob > 100:
            issues.append(f"Rain probability out of range: {rain_prob}%")
        
        # Wind checks
        wind_speed = data.get('wind_speed', 0)
        max_wind = data.get('max_wind_speed', 0)
        
        if wind_speed < 0 or wind_speed > 200:
            issues.append(f"Wind speed out of plausible range: {wind_speed} km/h")
        
        if max_wind < 0 or max_wind > 300:
            issues.append(f"Max wind speed out of plausible range: {max_wind} km/h")
        
        if max_wind < wind_speed and max_wind > 0 and wind_speed > 0:
            issues.append(f"Max wind speed lower than average wind speed: {max_wind} < {wind_speed}")
        
        # Precipitation checks
        precipitation = data.get('max_precipitation', 0)
        if precipitation < 0 or precipitation > 100:
            issues.append(f"Precipitation amount out of plausible range: {precipitation} mm")
        
        # Thunderstorm next day
        thunderstorm_next = data.get('thunderstorm_next_day', 0)
        if thunderstorm_next < 0 or thunderstorm_next > 100:
            issues.append(f"Thunderstorm next day probability out of range: {thunderstorm_next}%")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Weather Value Plausibility', False, issue))
        else:
            print("✅ All weather values are within plausible ranges")
            self.test_results.append(('Weather Value Plausibility', True, "All values plausible"))
    
    def _test_aggregation_logic(self):
        """Test that aggregation logic works correctly."""
        print("\n🔄 Test 4: Aggregation Logic")
        print("-" * 30)
        
        # Test with multiple coordinates
        test_coords = [
            {'latitude': 42.3069, 'longitude': 9.1497, 'name': 'Corte'},
            {'latitude': 42.1500, 'longitude': 9.2500, 'name': 'Vizzavona'}
        ]
        
        issues = []
        
        # Process data for multiple coordinates
        data_list = []
        for coord in test_coords:
            data = self.processor.process_weather_data(
                latitude=coord['latitude'],
                longitude=coord['longitude'],
                location_name=coord['name'],
                report_type='evening'
            )
            data_list.append(data)
        
        # Test aggregation
        from src.report.weather_report_generator import _aggregate_weather_data
        aggregated = _aggregate_weather_data(data_list, 'evening')
        
        # Check that aggregated values are maximums
        max_temps = [d.get('max_temperature', 0) for d in data_list]
        max_thunderstorm = [d.get('max_thunderstorm_probability', 0) for d in data_list]
        max_rain = [d.get('max_rain_probability', 0) for d in data_list]
        
        if aggregated.get('max_temperature', 0) != max(max_temps):
            issues.append(f"Aggregated max temperature should be maximum: {aggregated.get('max_temperature', 0)} vs {max(max_temps)}")
        
        if aggregated.get('max_thunderstorm_probability', 0) != max(max_thunderstorm):
            issues.append(f"Aggregated max thunderstorm should be maximum: {aggregated.get('max_thunderstorm_probability', 0)} vs {max(max_thunderstorm)}")
        
        if aggregated.get('max_rain_probability', 0) != max(max_rain):
            issues.append(f"Aggregated max rain should be maximum: {aggregated.get('max_rain_probability', 0)} vs {max(max_rain)}")
        
        # Check min temperature for evening reports
        min_temps = [d.get('min_temperature', float('inf')) for d in data_list if d.get('min_temperature', 0) > 0]
        if min_temps:
            if aggregated.get('min_temperature', float('inf')) != min(min_temps):
                issues.append(f"Aggregated min temperature should be minimum: {aggregated.get('min_temperature', 0)} vs {min(min_temps)}")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Aggregation Logic', False, issue))
        else:
            print("✅ Aggregation logic works correctly")
            self.test_results.append(('Aggregation Logic', True, "Aggregation correct"))
    
    def _test_report_format_compliance(self):
        """Test that report format complies with email_format.mdc specification."""
        print("\n📋 Test 5: Report Format Compliance")
        print("-" * 40)
        
        issues = []
        
        # Test all report types
        report_types = ['morning', 'evening', 'update']
        
        for report_type in report_types:
            result = generate_weather_report(report_type=report_type)
            
            if not result['success']:
                issues.append(f"{report_type.capitalize()} report generation failed: {result.get('error', 'Unknown error')}")
                continue
            
            report_text = result['report_text']
            
            # Check required elements based on report type
            if report_type == 'morning':
                if 'Gew.' not in report_text or 'Regen' not in report_text or 'Hitze' not in report_text:
                    issues.append(f"Morning report missing required elements: {report_text}")
            
            elif report_type == 'evening':
                if 'Nacht' not in report_text or 'Gew.' not in report_text or 'Regen' not in report_text:
                    issues.append(f"Evening report missing required elements: {report_text}")
            
            elif report_type == 'update':
                if 'Update:' not in report_text or 'Gew.' not in report_text or 'Regen' not in report_text:
                    issues.append(f"Update report missing required elements: {report_text}")
            
            # Check separator format
            if ' | ' not in report_text:
                issues.append(f"{report_type.capitalize()} report missing proper separators: {report_text}")
            
            # Check time format (HH only)
            import re
            time_pattern = r'@(\d{1,2})'
            times = re.findall(time_pattern, report_text)
            for time in times:
                if not (0 <= int(time) <= 23):
                    issues.append(f"{report_type.capitalize()} report has invalid time format: {time}")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Report Format Compliance', False, issue))
        else:
            print("✅ Report format complies with email_format.mdc specification")
            self.test_results.append(('Report Format Compliance', True, "Format compliant"))
    
    def _test_character_limit_compliance(self):
        """Test that reports stay within 160 character limit."""
        print("\n📏 Test 6: Character Limit Compliance")
        print("-" * 40)
        
        issues = []
        
        # Test all report types
        report_types = ['morning', 'evening', 'update']
        
        for report_type in report_types:
            result = generate_weather_report(report_type=report_type)
            
            if not result['success']:
                continue
            
            report_text = result['report_text']
            char_count = len(report_text)
            
            if char_count > 160:
                issues.append(f"{report_type.capitalize()} report exceeds 160 character limit: {char_count} chars")
                print(f"   {report_type.capitalize()}: {char_count} chars - {report_text}")
            else:
                print(f"   {report_type.capitalize()}: {char_count} chars ✓")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Character Limit Compliance', False, issue))
        else:
            print("✅ All reports stay within 160 character limit")
            self.test_results.append(('Character Limit Compliance', True, "All within limit"))
    
    def _test_edge_cases(self):
        """Test edge cases and error handling."""
        print("\n⚠️ Test 7: Edge Cases")
        print("-" * 20)
        
        issues = []
        
        # Test with invalid coordinates
        try:
            data = self.processor.process_weather_data(
                latitude=999.0,  # Invalid latitude
                longitude=999.0,  # Invalid longitude
                location_name='Invalid',
                report_type='morning'
            )
            
            # Should handle gracefully
            if data.get('max_temperature', 0) != 0:
                issues.append("Invalid coordinates should return empty data")
        except Exception as e:
            issues.append(f"Invalid coordinates should be handled gracefully: {e}")
        
        # Test with invalid report type
        try:
            data = self.processor.process_weather_data(
                latitude=42.3069,
                longitude=9.1497,
                location_name='Corte',
                report_type='invalid'
            )
            
            # Should fallback to morning
            if data.get('report_type') != 'invalid':
                issues.append("Invalid report type should be preserved in data")
        except Exception as e:
            issues.append(f"Invalid report type should be handled gracefully: {e}")
        
        # Test empty weather data
        try:
            # This should not crash
            result = generate_weather_report(report_type='morning')
            if not result['success']:
                issues.append("Empty weather data should be handled gracefully")
        except Exception as e:
            issues.append(f"Empty weather data should not crash: {e}")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Edge Cases', False, issue))
        else:
            print("✅ Edge cases handled correctly")
            self.test_results.append(('Edge Cases', True, "Edge cases handled"))
    
    def _test_thunderstorm_next_day_logic(self):
        """Test thunderstorm next day logic specifically."""
        print("\n⚡ Test 8: Thunderstorm Next Day Logic")
        print("-" * 40)
        
        test_coords = {
            'latitude': 42.3069,
            'longitude': 9.1497,
            'location_name': 'Corte'
        }
        
        issues = []
        
        # Test all report types
        report_types = ['morning', 'evening', 'update']
        today = datetime.now().date()
        
        for report_type in report_types:
            data = self.processor.process_weather_data(
                latitude=test_coords['latitude'],
                longitude=test_coords['longitude'],
                location_name=test_coords['location_name'],
                report_type=report_type
            )
            
            next_day_date = data.get('thunderstorm_next_day_date', '')
            if next_day_date:
                next_day = datetime.fromisoformat(next_day_date).date()
                
                if report_type == 'evening':
                    expected = today + timedelta(days=2)  # übermorgen
                    if next_day != expected:
                        issues.append(f"Evening report thunderstorm next day should be übermorgen: {next_day} vs {expected}")
                else:
                    expected = today + timedelta(days=1)  # morgen
                    if next_day != expected:
                        issues.append(f"{report_type.capitalize()} report thunderstorm next day should be morgen: {next_day} vs {expected}")
        
        # Report results
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
                self.test_results.append(('Thunderstorm Next Day Logic', False, issue))
        else:
            print("✅ Thunderstorm next day logic is correct")
            self.test_results.append(('Thunderstorm Next Day Logic', True, "Logic correct"))
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("📊 PLAUSIBILITY TEST SUMMARY")
        print("=" * 70)
        
        passed = 0
        failed = 0
        
        for test_name, success, message in self.test_results:
            if success:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED - {message}")
                failed += 1
        
        print(f"\n📈 Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! The system is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        return failed == 0


def main():
    """Main function to run plausibility tests."""
    tester = PlausibilityTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Plausibility test completed successfully!")
        return 0
    else:
        print("\n💥 Plausibility test found issues!")
        return 1


if __name__ == "__main__":
    exit(main()) 