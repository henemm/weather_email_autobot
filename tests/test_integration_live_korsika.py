"""
Integration test for live weather data fetching and risk analysis for Corsica.

This test performs a complete live workflow from weather data fetching
to risk analysis and warning text generation for coordinates in Corsica.
"""

import pytest
import yaml
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.wetter.fetch_arome_wcs import fetch_arome_wcs_data
from src.logic.analyse_weather import analyze_weather_data, WeatherAnalysis
from src.wetter.warntext_generator import generate_warntext
from src.model.datatypes import WeatherData, WeatherPoint
from src.utils.env_loader import get_env_var


class TestLiveCorsicaWeatherAnalysis:
    """Integration test for live weather analysis workflow in Corsica."""
    
    @pytest.fixture(autouse=True)
    def check_api_credentials(self):
        """Check if required API credentials are available."""
        required_vars = [
            'METEOFRANCE_CLIENT_ID',
            'METEOFRANCE_CLIENT_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not get_env_var(var):
                missing_vars.append(var)
        
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @pytest.fixture
    def corsica_coordinates(self) -> Dict[str, float]:
        """Test coordinates for Corsica (near Corte)."""
        return {
            "latitude": 42.0396,
            "longitude": 9.0129
        }
    
    @pytest.fixture
    def weather_layers(self) -> list:
        """Weather layers to fetch for analysis."""
        return [
            "TEMPERATURE__GROUND_OR_WATER_SURFACE",
            "TOTAL_PRECIPITATION__SURFACE", 
            "CAPE__SURFACE"
        ]
    
    @pytest.fixture
    def test_config(self) -> Dict[str, Any]:
        """Load test configuration from config.yaml."""
        config_path = Path("config.yaml")
        if not config_path.exists():
            pytest.skip("config.yaml not found")
        
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    @pytest.mark.integration
    def test_fetch_arome_wcs_data_for_corsica(
        self, 
        corsica_coordinates: Dict[str, float], 
        weather_layers: list
    ):
        """Test fetching AROME WCS data for Corsica coordinates."""
        for layer in weather_layers:
            try:
                grid_data = fetch_arome_wcs_data(
                    latitude=corsica_coordinates["latitude"],
                    longitude=corsica_coordinates["longitude"],
                    layer_name=layer
                )
                
                # Verify data structure
                assert grid_data is not None
                assert grid_data.layer == layer
                assert grid_data.lat == corsica_coordinates["latitude"]
                assert grid_data.lon == corsica_coordinates["longitude"]
                assert isinstance(grid_data.times, list)
                assert isinstance(grid_data.values, list)
                
                # Verify data content
                if grid_data.times and grid_data.values:
                    assert len(grid_data.times) == len(grid_data.values)
                    assert all(isinstance(t, datetime) for t in grid_data.times)
                    assert all(isinstance(v, (int, float)) for v in grid_data.values)
                
                print(f"✓ Successfully fetched {layer} data")
                
            except Exception as e:
                pytest.fail(f"Failed to fetch {layer}: {str(e)}")
    
    @pytest.mark.integration
    def test_weather_data_analysis_for_corsica(
        self, 
        corsica_coordinates: Dict[str, float], 
        weather_layers: list,
        test_config: Dict[str, Any]
    ):
        """Test complete weather data analysis workflow for Corsica."""
        # Fetch weather data for all layers
        weather_data_list = []
        
        for layer in weather_layers:
            try:
                grid_data = fetch_arome_wcs_data(
                    latitude=corsica_coordinates["latitude"],
                    longitude=corsica_coordinates["longitude"],
                    layer_name=layer
                )
                
                # Convert grid data to weather points
                weather_points = []
                for i, (time, value) in enumerate(zip(grid_data.times, grid_data.values)):
                    point = WeatherPoint(
                        time=time,
                        latitude=corsica_coordinates["latitude"],
                        longitude=corsica_coordinates["longitude"],
                        temperature=value if "TEMPERATURE" in layer else 0.0,
                        precipitation=value if "PRECIPITATION" in layer else 0.0,
                        wind_speed=0.0,
                        wind_direction=0.0,
                        cloud_cover=0.0,
                        thunderstorm_probability=value if "CAPE" in layer else None,
                        humidity=0.0,
                        pressure=0.0
                    )
                    weather_points.append(point)
                
                weather_data = WeatherData(points=weather_points)
                weather_data_list.append(weather_data)
                
            except Exception as e:
                print(f"Warning: Could not fetch {layer}: {str(e)}")
                continue
        
        # Skip test if no data could be fetched
        if not weather_data_list:
            pytest.skip("No weather data could be fetched for analysis")
        
        # Analyze weather data
        analysis = analyze_weather_data(weather_data_list, test_config)
        
        # Verify analysis result
        assert isinstance(analysis, WeatherAnalysis)
        assert isinstance(analysis.risk, float)
        assert 0.0 <= analysis.risk <= 1.0
        assert isinstance(analysis.summary, str)
        assert len(analysis.summary) > 0
        
        print(f"✓ Weather analysis completed - Risk score: {analysis.risk:.2f}")
        print(f"✓ Analysis summary: {analysis.summary}")
    
    @pytest.mark.integration
    def test_warning_text_generation_for_corsica(
        self, 
        corsica_coordinates: Dict[str, float], 
        weather_layers: list,
        test_config: Dict[str, Any]
    ):
        """Test warning text generation based on weather analysis."""
        # Fetch and analyze weather data
        weather_data_list = []
        
        for layer in weather_layers:
            try:
                grid_data = fetch_arome_wcs_data(
                    latitude=corsica_coordinates["latitude"],
                    longitude=corsica_coordinates["longitude"],
                    layer_name=layer
                )
                
                # Convert grid data to weather points
                weather_points = []
                for i, (time, value) in enumerate(zip(grid_data.times, grid_data.values)):
                    point = WeatherPoint(
                        time=time,
                        latitude=corsica_coordinates["latitude"],
                        longitude=corsica_coordinates["longitude"],
                        temperature=value if "TEMPERATURE" in layer else 0.0,
                        precipitation=value if "PRECIPITATION" in layer else 0.0,
                        wind_speed=0.0,
                        wind_direction=0.0,
                        cloud_cover=0.0,
                        thunderstorm_probability=value if "CAPE" in layer else None,
                        humidity=0.0,
                        pressure=0.0
                    )
                    weather_points.append(point)
                
                weather_data = WeatherData(points=weather_points)
                weather_data_list.append(weather_data)
                
            except Exception as e:
                print(f"Warning: Could not fetch {layer}: {str(e)}")
                continue
        
        # Skip test if no data could be fetched
        if not weather_data_list:
            pytest.skip("No weather data could be fetched for warning generation")
        
        # Analyze weather data
        analysis = analyze_weather_data(weather_data_list, test_config)
        
        # Generate warning text
        warning_text = generate_warntext(analysis.risk, test_config)
        
        # Verify warning text result
        if analysis.risk >= test_config["warn_thresholds"]["info"]:
            assert warning_text is not None
            assert isinstance(warning_text, str)
            assert len(warning_text) > 0
            print(f"✓ Warning text generated: {warning_text}")
        else:
            assert warning_text is None
            print(f"✓ No warning generated (risk {analysis.risk:.2f} below info threshold)")
    
    @pytest.mark.integration
    def test_complete_workflow_with_file_output(
        self, 
        corsica_coordinates: Dict[str, float], 
        weather_layers: list,
        test_config: Dict[str, Any]
    ):
        """Test complete workflow including file output for InReach warning."""
        # Fetch and analyze weather data
        weather_data_list = []
        
        for layer in weather_layers:
            try:
                grid_data = fetch_arome_wcs_data(
                    latitude=corsica_coordinates["latitude"],
                    longitude=corsica_coordinates["longitude"],
                    layer_name=layer
                )
                
                # Convert grid data to weather points
                weather_points = []
                for i, (time, value) in enumerate(zip(grid_data.times, grid_data.values)):
                    point = WeatherPoint(
                        time=time,
                        latitude=corsica_coordinates["latitude"],
                        longitude=corsica_coordinates["longitude"],
                        temperature=value if "TEMPERATURE" in layer else 0.0,
                        precipitation=value if "PRECIPITATION" in layer else 0.0,
                        wind_speed=0.0,
                        wind_direction=0.0,
                        cloud_cover=0.0,
                        thunderstorm_probability=value if "CAPE" in layer else None,
                        humidity=0.0,
                        pressure=0.0
                    )
                    weather_points.append(point)
                
                weather_data = WeatherData(points=weather_points)
                weather_data_list.append(weather_data)
                
            except Exception as e:
                print(f"Warning: Could not fetch {layer}: {str(e)}")
                continue
        
        # Skip test if no data could be fetched
        if not weather_data_list:
            pytest.skip("No weather data could be fetched for complete workflow")
        
        # Analyze weather data
        analysis = analyze_weather_data(weather_data_list, test_config)
        
        # Generate warning text
        warning_text = generate_warntext(analysis.risk, test_config)
        
        # Write to output file if warning is generated
        output_file = Path("output/inreach_warnung.txt")
        output_file.parent.mkdir(exist_ok=True)
        
        if warning_text:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(f"Korsika Wetterwarnung\n")
                file.write(f"Koordinaten: {corsica_coordinates['latitude']:.4f}, {corsica_coordinates['longitude']:.4f}\n")
                file.write(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"Risiko: {analysis.risk:.2f}\n")
                file.write(f"\n{warning_text}\n")
                file.write(f"\nDetails: {analysis.summary}\n")
            
            print(f"✓ Warning file written to {output_file}")
            
            # Verify file was created and contains expected content
            assert output_file.exists()
            with open(output_file, 'r', encoding='utf-8') as file:
                content = file.read()
                assert "Korsika Wetterwarnung" in content
                assert warning_text in content
                assert str(analysis.risk) in content
        else:
            print(f"✓ No warning file created (risk {analysis.risk:.2f} below threshold)")
    
    @pytest.mark.integration
    def test_error_handling_for_invalid_layers(
        self, 
        corsica_coordinates: Dict[str, float]
    ):
        """Test error handling for invalid weather layers."""
        invalid_layers = [
            "INVALID_LAYER_NAME",
            "NONEXISTENT_LAYER",
            ""
        ]
        
        for layer in invalid_layers:
            with pytest.raises((ValueError, Exception)):
                fetch_arome_wcs_data(
                    latitude=corsica_coordinates["latitude"],
                    longitude=corsica_coordinates["longitude"],
                    layer_name=layer
                )
        
        print("✓ Error handling for invalid layers works correctly")
    
    @pytest.mark.integration
    def test_error_handling_for_invalid_coordinates(self):
        """Test error handling for invalid coordinates."""
        invalid_coordinates = [
            (91.0, 0.0),   # Latitude too high
            (-91.0, 0.0),  # Latitude too low
            (0.0, 181.0),  # Longitude too high
            (0.0, -181.0), # Longitude too low
        ]
        
        for lat, lon in invalid_coordinates:
            with pytest.raises(ValueError):
                fetch_arome_wcs_data(
                    latitude=lat,
                    longitude=lon,
                    layer_name="TEMPERATURE__GROUND_OR_WATER_SURFACE"
                )
        
        print("✓ Error handling for invalid coordinates works correctly") 