"""
Test for thunderstorm details enhancement for Font-Romeu-Odeillo-Via.

This test analyzes the data structure mismatch between get_forecast_with_fallback()
and the Evening-Bericht processing to identify why thunderstorm details are not shown.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_meteofrance import get_forecast_with_fallback, get_thunderstorm_with_fallback
from wetter.enhanced_meteofrance_api import EnhancedMeteoFranceAPI, get_enhanced_forecast_data


class TestThunderstormDetailsFontRomeu:
    """Test thunderstorm details for Font-Romeu-Odeillo-Via coordinates."""
    
    def setup_method(self):
        """Initialize test coordinates for Font-Romeu-Odeillo-Via."""
        # Font-Romeu-Odeillo-Via coordinates from etappen.json
        self.latitude = 42.471359
        self.longitude = 2.029742
        self.location_name = "Font-Romeu-Odeillo-Via"
        
    def test_current_get_forecast_with_fallback_structure(self):
        """Test current get_forecast_with_fallback() data structure."""
        print(f"\n🔍 Testing current get_forecast_with_fallback() for {self.location_name}")
        
        try:
            # Test current implementation
            forecast_result = get_forecast_with_fallback(self.latitude, self.longitude)
            
            print(f"✅ Forecast Result:")
            print(f"   Temperature: {forecast_result.temperature}")
            print(f"   Weather Condition: {forecast_result.weather_condition}")
            print(f"   Precipitation Probability: {forecast_result.precipitation_probability}")
            print(f"   Wind Speed: {forecast_result.wind_speed}")
            print(f"   Wind Gusts: {forecast_result.wind_gusts}")
            print(f"   Thunderstorm Probability: {forecast_result.thunderstorm_probability}")
            print(f"   Data Source: {forecast_result.data_source}")
            print(f"   Timestamp: {forecast_result.timestamp}")
            
            # Check if thunderstorm data is available
            thunderstorm_info = get_thunderstorm_with_fallback(self.latitude, self.longitude)
            print(f"   Thunderstorm Info: {thunderstorm_info}")
            
            # Verify data structure
            assert isinstance(forecast_result.temperature, (int, float))
            assert forecast_result.data_source in ["meteofrance-api", "open-meteo"]
            
            # Check if raw forecast data is available
            if hasattr(forecast_result, 'raw_forecast_data') and forecast_result.raw_forecast_data:
                print(f"   Raw Forecast Data Available: {len(forecast_result.raw_forecast_data)} entries")
                print(f"   ✅ Raw data available for enhanced processing")
            else:
                print(f"   Raw Forecast Data Available: No")
                print(f"   ⚠️ Raw data not available")
            
            print(f"✅ Current implementation works correctly")
            
        except Exception as e:
            print(f"❌ Error in current implementation: {e}")
            pytest.fail(f"Current implementation failed: {e}")
    
    def test_enhanced_meteofrance_api_structure(self):
        """Test enhanced MeteoFrance API data structure."""
        print(f"\n🔍 Testing enhanced MeteoFrance API for {self.location_name}")
        
        try:
            # Test enhanced implementation
            enhanced_data = get_enhanced_forecast_data(self.latitude, self.longitude, self.location_name)
            
            print(f"✅ Enhanced Data Structure:")
            print(f"   Location: {enhanced_data.get('location_name')}")
            print(f"   Hourly Data Count: {len(enhanced_data.get('hourly_data', []))}")
            print(f"   Daily Forecast Count: {len(enhanced_data.get('daily_forecast', {}).get('daily', []))}")
            print(f"   Probability Data Count: {len(enhanced_data.get('probability_data', []))}")
            print(f"   Rain Probability Data Count: {len(enhanced_data.get('rain_probability_data', []))}")
            print(f"   Thunderstorm Data Count: {len(enhanced_data.get('thunderstorm_data', []))}")
            
            # Show sample hourly data
            hourly_data = enhanced_data.get('hourly_data', [])
            if hourly_data:
                print(f"   Sample Hourly Entry:")
                sample_entry = hourly_data[0]
                print(f"     Timestamp: {sample_entry.timestamp}")
                print(f"     Temperature: {sample_entry.temperature}")
                print(f"     Weather Description: {sample_entry.weather_description}")
                print(f"     Rain Amount: {sample_entry.rain_amount}")
                print(f"     Wind Speed: {sample_entry.wind_speed}")
                print(f"     Wind Gusts: {sample_entry.wind_gusts}")
            
            # Show thunderstorm data
            thunderstorm_data = enhanced_data.get('thunderstorm_data', [])
            if thunderstorm_data:
                print(f"   Thunderstorm Entries:")
                for i, entry in enumerate(thunderstorm_data[:3]):  # Show first 3
                    print(f"     {i+1}. {entry.timestamp}: {entry.description} (Rain: {entry.rain_amount}mm/h, Wind: {entry.wind_speed}km/h)")
            else:
                print(f"   No thunderstorm data found")
            
            # Verify data structure
            assert 'hourly_data' in enhanced_data
            assert 'thunderstorm_data' in enhanced_data
            assert isinstance(enhanced_data['hourly_data'], list)
            assert isinstance(enhanced_data['thunderstorm_data'], list)
            
            print(f"✅ Enhanced implementation works correctly")
            
        except Exception as e:
            print(f"❌ Error in enhanced implementation: {e}")
            pytest.fail(f"Enhanced implementation failed: {e}")
    
    def test_data_structure_compatibility(self):
        """Test compatibility between current and enhanced data structures."""
        print(f"\n🔍 Testing data structure compatibility for {self.location_name}")
        
        try:
            # Get both data structures
            current_result = get_forecast_with_fallback(self.latitude, self.longitude)
            enhanced_data = get_enhanced_forecast_data(self.latitude, self.longitude, self.location_name)
            
            print(f"✅ Data Structure Comparison:")
            print(f"   Current - Temperature: {current_result.temperature}")
            print(f"   Current - Wind Gusts: {current_result.wind_gusts}")
            print(f"   Current - Thunderstorm Probability: {current_result.thunderstorm_probability}")
            
            # Check if enhanced data has more detailed thunderstorm info
            thunderstorm_data = enhanced_data.get('thunderstorm_data', [])
            if thunderstorm_data:
                print(f"   Enhanced - Thunderstorm Entries: {len(thunderstorm_data)}")
                for entry in thunderstorm_data:
                    print(f"     {entry.timestamp}: {entry.description}")
            else:
                print(f"   Enhanced - No thunderstorm data")
            
            # Check hourly data for wind gusts
            hourly_data = enhanced_data.get('hourly_data', [])
            if hourly_data:
                max_gust = max([entry.wind_gusts for entry in hourly_data if entry.wind_gusts is not None], default=0)
                print(f"   Enhanced - Max Wind Gust: {max_gust} km/h")
                
                # Find entries with high wind gusts
                high_gust_entries = [entry for entry in hourly_data if entry.wind_gusts and entry.wind_gusts > 30]
                if high_gust_entries:
                    print(f"   Enhanced - High Gust Entries:")
                    for entry in high_gust_entries[:3]:  # Show first 3
                        print(f"     {entry.timestamp}: {entry.wind_gusts} km/h")
            
            print(f"✅ Data structure compatibility analysis complete")
            
        except Exception as e:
            print(f"❌ Error in compatibility test: {e}")
            pytest.fail(f"Compatibility test failed: {e}")
    
    def test_evening_report_data_requirements(self):
        """Test what data the Evening-Bericht processing expects."""
        print(f"\n🔍 Testing Evening-Bericht data requirements for {self.location_name}")
        
        try:
            # Get enhanced data
            enhanced_data = get_enhanced_forecast_data(self.latitude, self.longitude, self.location_name)
            
            # Simulate what Evening-Bericht processing expects
            hourly_data = enhanced_data.get('hourly_data', [])
            thunderstorm_data = enhanced_data.get('thunderstorm_data', [])
            
            print(f"✅ Evening-Bericht Data Requirements:")
            print(f"   Hourly Data Available: {len(hourly_data)} entries")
            print(f"   Thunderstorm Data Available: {len(thunderstorm_data)} entries")
            
            # Check if we have enough data for tomorrow (04:00-22:00)
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_start = datetime.combine(tomorrow.date(), datetime.min.time().replace(hour=4))
            tomorrow_end = datetime.combine(tomorrow.date(), datetime.min.time().replace(hour=22))
            
            tomorrow_entries = [
                entry for entry in hourly_data 
                if tomorrow_start <= entry.timestamp <= tomorrow_end
            ]
            
            print(f"   Tomorrow Entries (04:00-22:00): {len(tomorrow_entries)}")
            
            if tomorrow_entries:
                print(f"   Tomorrow Data Sample:")
                for entry in tomorrow_entries[:3]:  # Show first 3
                    print(f"     {entry.timestamp}: Temp={entry.temperature}°C, Wind={entry.wind_speed}km/h, Gust={entry.wind_gusts}km/h")
            
            # Check thunderstorm data for tomorrow
            tomorrow_thunderstorms = [
                entry for entry in thunderstorm_data 
                if tomorrow_start <= entry.timestamp <= tomorrow_end
            ]
            
            print(f"   Tomorrow Thunderstorms: {len(tomorrow_thunderstorms)}")
            if tomorrow_thunderstorms:
                for entry in tomorrow_thunderstorms:
                    print(f"     {entry.timestamp}: {entry.description}")
            
            print(f"✅ Evening-Bericht data requirements analysis complete")
            
        except Exception as e:
            print(f"❌ Error in Evening-Bericht test: {e}")
            pytest.fail(f"Evening-Bericht test failed: {e}")


if __name__ == "__main__":
    # Run the test manually
    test = TestThunderstormDetailsFontRomeu()
    test.setup_method()
    
    print("🧪 Running Thunderstorm Details Analysis for Font-Romeu-Odeillo-Via")
    print("=" * 70)
    
    test.test_current_get_forecast_with_fallback_structure()
    test.test_enhanced_meteofrance_api_structure()
    test.test_data_structure_compatibility()
    test.test_evening_report_data_requirements()
    
    print("\n✅ Analysis complete!") 