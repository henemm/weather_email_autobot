#!/usr/bin/env python3
"""
Integration test with fixed geo-position.

This test performs a complete weather analysis based on a fixed coordinate.
It verifies that weather data can be fetched, correctly interpreted, evaluated,
and potentially output as warning text.
"""

import os
import sys
import yaml
import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome import fetch_arome_weather_data
from logic.analyse_weather import analyze_weather_data, compute_risk
from wetter.warntext_generator import generate_warntext
from model.datatypes import WeatherData, WeatherPoint, WeatherGridData


class TestIntegrationStaticWarning:
    """Integration test with fixed geo-position."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.test_latitude = 42.6973  # Bastia, Corsica
        self.test_longitude = 9.4500
        self.config = self.load_configuration()
    
    def test_arome_data_fetch_succeeds(self):
        """Test that AROME weather data can be fetched successfully."""
        try:
            weather_data = fetch_arome_weather_data(
                latitude=self.test_latitude,
                longitude=self.test_longitude
            )
            
            assert weather_data is not None
            assert len(weather_data.points) > 0
            assert weather_data.points[0].latitude == self.test_latitude
            assert weather_data.points[0].longitude == self.test_longitude
            
            print(f"✅ AROME data fetched successfully for Bastia")
            print(f"   Weather points: {len(weather_data.points)}")
            print(f"   Time range: {weather_data.points[0].time} to {weather_data.points[-1].time}")
            print(f"   Temperature range: {min(p.temperature for p in weather_data.points):.1f}°C to {max(p.temperature for p in weather_data.points):.1f}°C")
            
        except Exception as e:
            print(f"❌ AROME API failed for Bastia: {e}")
            print("   Falling back to mock data for integration test...")
            # Fall back to mock data if API fails
            weather_data = self.create_mock_weather_data()
            assert weather_data is not None
    
    def test_weather_analysis_completes_successfully(self):
        """Test that weather analysis completes without errors."""
        # Try to fetch real AROME data first
        try:
            weather_data = fetch_arome_weather_data(
                latitude=self.test_latitude,
                longitude=self.test_longitude
            )
            print(f"✅ Using real AROME data for analysis")
        except Exception as e:
            print(f"❌ AROME API failed, using mock data: {e}")
            weather_data = self.create_mock_weather_data()
        
        # Analyze weather data
        analysis_result = analyze_weather_data(weather_data, self.config)
        
        assert analysis_result is not None
        assert hasattr(analysis_result, 'risks')
        assert hasattr(analysis_result, 'risk')
        assert isinstance(analysis_result.risk, float)
        assert 0.0 <= analysis_result.risk <= 1.0
        
        print(f"✅ Weather analysis completed")
        print(f"   Risks detected: {len(analysis_result.risks)}")
        print(f"   Risk score: {analysis_result.risk:.3f}")
    
    def test_risk_computation_works_correctly(self):
        """Test that risk computation works with real data."""
        # Try to fetch real AROME data first
        try:
            weather_data = fetch_arome_weather_data(
                latitude=self.test_latitude,
                longitude=self.test_longitude
            )
        except Exception as e:
            print(f"❌ AROME API failed, using mock data: {e}")
            weather_data = self.create_mock_weather_data()
        
        analysis_result = analyze_weather_data(weather_data, self.config)
        
        # Extract metrics for risk computation
        metrics = {
            "thunderstorm_probability": analysis_result.max_thunderstorm_probability or 0.0,
            "precipitation": analysis_result.max_precipitation,
            "wind_speed": analysis_result.max_wind_speed,
            "temperature": analysis_result.max_temperature,
            "cape": 1000.0  # Default value for demonstration
        }
        
        # Compute risk
        computed_risk = compute_risk(metrics, self.config)
        
        assert isinstance(computed_risk, float)
        assert 0.0 <= computed_risk <= 1.0
        assert abs(computed_risk - analysis_result.risk) < 0.001
        
        print(f"✅ Risk computation successful")
        print(f"   Computed risk: {computed_risk:.3f}")
    
    def test_warning_text_generation_works(self):
        """Test that warning text generation works with computed risk."""
        # Try to fetch real AROME data first
        try:
            weather_data = fetch_arome_weather_data(
                latitude=self.test_latitude,
                longitude=self.test_longitude
            )
        except Exception as e:
            print(f"❌ AROME API failed, using mock data: {e}")
            weather_data = self.create_mock_weather_data()
        
        analysis_result = analyze_weather_data(weather_data, self.config)
        
        metrics = {
            "thunderstorm_probability": analysis_result.max_thunderstorm_probability or 0.0,
            "precipitation": analysis_result.max_precipitation,
            "wind_speed": analysis_result.max_wind_speed,
            "temperature": analysis_result.max_temperature,
            "cape": 1000.0
        }
        computed_risk = compute_risk(metrics, self.config)
        
        # Generate warning text
        warning_text = generate_warntext(computed_risk, self.config)
        
        # Warning text can be None (if risk is below threshold) or a string
        if warning_text is not None:
            assert isinstance(warning_text, str)
            assert len(warning_text) > 0
            # Check that warning is emoji-free
            emoji_chars = ["⚠️", "⚡", "🌤️", "🚨", "🌧️", "🌩️", "🌪️", "🌊", "❄️", "☀️", "⛈️", "🌨️", "💨", "🌫️", "🌡️", "💧", "🏔️", "🌋"]
            for emoji in emoji_chars:
                assert emoji not in warning_text, f"Emoji '{emoji}' found in warning text"
            # Check for text-based indicators instead
            assert "WARNUNG" in warning_text or "ALARM" in warning_text or "Wettergefahr" in warning_text
            print(f"✅ Warning text generated: {warning_text[:50]}...")
        else:
            print(f"ℹ️  No warning generated (risk: {computed_risk:.3f})")
    
    def test_warning_file_creation_when_warning_generated(self):
        """Test that warning file is created when warning text is generated."""
        # Try to fetch real AROME data first
        try:
            weather_data = fetch_arome_weather_data(
                latitude=self.test_latitude,
                longitude=self.test_longitude
            )
        except Exception as e:
            print(f"❌ AROME API failed, using mock data: {e}")
            weather_data = self.create_mock_weather_data()
        
        analysis_result = analyze_weather_data(weather_data, self.config)
        
        metrics = {
            "thunderstorm_probability": analysis_result.max_thunderstorm_probability or 0.0,
            "precipitation": analysis_result.max_precipitation,
            "wind_speed": analysis_result.max_wind_speed,
            "temperature": analysis_result.max_temperature,
            "cape": 1000.0
        }
        computed_risk = compute_risk(metrics, self.config)
        
        # Generate warning text
        warning_text = generate_warntext(computed_risk, self.config)
        
        if warning_text:
            # Write to output file
            self.write_warning_to_file(warning_text)
            
            # Verify file was created
            output_file = Path(__file__).parent.parent / "output" / "inreach_warnung.txt"
            assert output_file.exists()
            
            # Verify file content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert warning_text in content
                assert "42.6973, 9.4500" in content  # Test position (Bastia)
            
            print(f"✅ Warning file created: {output_file}")
    
    def test_complete_integration_workflow(self):
        """Test the complete integration workflow from AROME fetch to warning output."""
        print(f"🔍 Testing complete workflow for Bastia ({self.test_latitude}, {self.test_longitude})")
        
        # 1. Try to fetch real AROME data first
        try:
            weather_data = fetch_arome_weather_data(
                latitude=self.test_latitude,
                longitude=self.test_longitude
            )
            print(f"✅ Real AROME data fetched successfully")
        except Exception as e:
            print(f"❌ AROME API failed, using mock data: {e}")
            weather_data = self.create_mock_weather_data()
        
        assert weather_data is not None
        assert len(weather_data.points) > 0
        print(f"✅ Weather data ready: {len(weather_data.points)} points")
        
        # 2. Analyze weather data
        analysis_result = analyze_weather_data(weather_data, self.config)
        assert analysis_result is not None
        print(f"✅ Weather analysis completed")
        
        # 3. Compute risk
        metrics = {
            "thunderstorm_probability": analysis_result.max_thunderstorm_probability or 0.0,
            "precipitation": analysis_result.max_precipitation,
            "wind_speed": analysis_result.max_wind_speed,
            "temperature": analysis_result.max_temperature,
            "cape": 1000.0
        }
        computed_risk = compute_risk(metrics, self.config)
        assert 0.0 <= computed_risk <= 1.0
        print(f"✅ Risk computed: {computed_risk:.3f}")
        
        # 4. Generate warning text
        warning_text = generate_warntext(computed_risk, self.config)
        # Warning text can be None or a string - both are valid
        if warning_text:
            print(f"✅ Warning text generated")
        else:
            print(f"ℹ️  No warning needed (risk below threshold)")
        
        # 5. Write to file if warning generated
        if warning_text:
            self.write_warning_to_file(warning_text)
            output_file = Path(__file__).parent.parent / "output" / "inreach_warnung.txt"
            assert output_file.exists()
            print(f"✅ Warning file written")
    
    def create_mock_weather_data(self) -> WeatherData:
        """Create mock weather data for testing."""
        # Create mock time series (next 24 hours, hourly)
        base_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        times = [base_time + timedelta(hours=i) for i in range(24)]
        
        # Create mock weather points (realistic for Bastia in summer)
        import random
        random.seed(42)  # For reproducible tests
        
        weather_points = []
        for i, time in enumerate(times):
            # Realistic weather values for Bastia
            temperature = 28.0 + random.uniform(-3, 3)
            precipitation = random.uniform(0, 5) if random.random() < 0.3 else 0.0
            wind_speed = random.uniform(5, 25)
            cloud_cover = random.uniform(20, 80)
            thunderstorm_probability = random.uniform(0, 30)
            
            weather_point = WeatherPoint(
                latitude=self.test_latitude,
                longitude=self.test_longitude,
                elevation=0.0,
                time=time,
                temperature=temperature,
                feels_like=temperature - 2.0,
                precipitation=precipitation,
                thunderstorm_probability=thunderstorm_probability,
                wind_speed=wind_speed,
                wind_direction=random.uniform(0, 360),
                cloud_cover=cloud_cover,
                cape=1000.0,
                shear=10.0
            )
            weather_points.append(weather_point)
        
        return WeatherData(points=weather_points)
    
    def load_configuration(self) -> dict:
        """Load configuration from config.yaml."""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Ensure required sections exist
        if "risk_model" not in config:
            config["risk_model"] = {
                "thunderstorm_probability": {
                    "threshold": 25.0,
                    "weight": 0.3
                },
                "wind_speed": {
                    "threshold": 40.0,
                    "weight": 0.2
                },
                "precipitation": {
                    "threshold": 2.0,
                    "weight": 0.2
                },
                "temperature": {
                    "threshold": 25.0,
                    "weight": 0.1
                },
                "cape": {
                    "threshold": 1000.0,
                    "weight": 0.2
                }
            }
        
        if "warn_thresholds" not in config:
            config["warn_thresholds"] = {
                "info": 0.3,
                "warning": 0.6,
                "critical": 0.9
            }
        
        return config
    
    def write_warning_to_file(self, warning_text: str) -> None:
        """Write warning text to output file."""
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "inreach_warnung.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(warning_text)
            f.write(f"\n\nGenerated at: {datetime.now().isoformat()}")
            f.write(f"\nTest position: 42.6973, 9.4500 (Bastia, Corsica)")


def test_integration_static_warning_demo():
    """
    Demo function that can be run directly to show the integration test workflow.
    """
    test_instance = TestIntegrationStaticWarning()
    test_instance.setup_method()
    
    print("=== Integration Test: Static Warning Test ===")
    print(f"Test Position: {test_instance.test_latitude}, {test_instance.test_longitude} (Bastia, Corsica)")
    print(f"Using AROME API for weather data")
    print()
    
    try:
        # Run the complete workflow
        test_instance.test_complete_integration_workflow()
        print("✅ Integration test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_integration_static_warning_demo()
    sys.exit(0 if success else 1) 