"""
Live test for AROME_HR (main model) API for a defined stage position on Corsica.

Model:
    - Model shortname: AROME_HR
    - API endpoint: WCS /public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS
    - Token: METEOFRANCE_WCS_TOKEN

Test objective:
    - Query temperature, precipitation, CAPE, SHEAR
    - Use configured height parameter
    - Ensure BoundingBox and height information
    - Verify that real values can be extracted
"""

import json
import pytest
from typing import Dict, Any, Optional
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from wetter.fetch_arome_wcs import fetch_arome_wcs, get_model_config
from tests.utils.env_loader import get_env_var


def load_etappen_data() -> list:
    """
    Load stage data from etappen.json file.
    
    Returns:
        List of stage data
    """
    etappen_path = os.path.join(os.path.dirname(__file__), '..', '..', 'etappen.json')
    with open(etappen_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_second_stage_coordinates() -> tuple[float, float]:
    """
    Get coordinates from the second stage (E2 Carozzu).
    
    Returns:
        Tuple of (latitude, longitude) for the first point of E2
    """
    etappen = load_etappen_data()
    if len(etappen) < 2:
        raise ValueError("Not enough stages in etappen.json")
    
    second_stage = etappen[1]  # E2 Carozzu
    first_point = second_stage['punkte'][0]
    return first_point['lat'], first_point['lon']


def test_arome_hr_model_configuration():
    """Test that AROME_HR model configuration is correct."""
    config = get_model_config("AROME_HR")
    
    assert config["base_url"] == "https://public-api.meteofrance.fr/public/arome/1.0"
    assert config["wcs_path"] == "/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS"
    assert "Hauptmodell" in config["description"]


def test_meteofrance_token_available():
    """Test that METEOFRANCE_WCS_TOKEN is available."""
    token = get_env_var("METEOFRANCE_WCS_TOKEN")
    assert token is not None, "METEOFRANCE_WCS_TOKEN not found in environment"
    assert len(token) > 0, "METEOFRANCE_WCS_TOKEN is empty"


def test_etappen_data_loading():
    """Test that etappen.json can be loaded and contains expected data."""
    etappen = load_etappen_data()
    assert len(etappen) >= 2, "At least 2 stages should be available"
    
    second_stage = etappen[1]
    assert second_stage["name"] == "E2 Carozzu"
    assert len(second_stage["punkte"]) > 0
    
    lat, lon = get_second_stage_coordinates()
    assert isinstance(lat, float)
    assert isinstance(lon, float)
    assert 42.0 <= lat <= 43.0  # Corsica latitude range
    assert 8.0 <= lon <= 9.0    # Corsica longitude range


def test_arome_hr_temperature_fetch():
    """Test fetching temperature data from AROME_HR model."""
    lat, lon = get_second_stage_coordinates()
    
    result = fetch_arome_wcs(
        latitude=lat,
        longitude=lon,
        model="AROME_HR",
        field="TEMPERATURE"
    )
    
    assert result is not None, "API should respond with data"
    assert "value" in result, "Response should contain 'value' field"
    assert "unit" in result, "Response should contain 'unit' field"
    assert "source" in result, "Response should contain 'source' field"
    assert "layer" in result, "Response should contain 'layer' field"
    assert "latitude" in result, "Response should contain 'latitude' field"
    assert "longitude" in result, "Response should contain 'longitude' field"
    assert "field" in result, "Response should contain 'field' field"
    assert "data_size" in result, "Response should contain 'data_size' field"
    
    # Check temperature value is reasonable
    temperature = result["value"]
    assert isinstance(temperature, (int, float)), "Temperature should be numeric"
    assert -50 <= temperature <= 50, f"Temperature {temperature}°C is outside reasonable range"
    
    # Check unit is Celsius
    assert result["unit"] == "°C", f"Expected unit '°C', got '{result['unit']}'"
    
    # Check source is correct
    assert result["source"] == "AROME_HR", f"Expected source 'AROME_HR', got '{result['source']}'"
    
    # Check coordinates match input
    assert result["latitude"] == lat, f"Expected latitude {lat}, got {result['latitude']}"
    assert result["longitude"] == lon, f"Expected longitude {lon}, got {result['longitude']}"
    
    # Check field is correct
    assert result["field"] == "TEMPERATURE", f"Expected field 'TEMPERATURE', got '{result['field']}'"
    
    # Check data size is reasonable
    assert result["data_size"] > 0, "Data size should be positive"


def test_arome_hr_precipitation_fetch():
    """Test fetching precipitation data from AROME_HR model."""
    lat, lon = get_second_stage_coordinates()
    
    result = fetch_arome_wcs(
        latitude=lat,
        longitude=lon,
        model="AROME_HR",
        field="PRECIPITATION"
    )
    
    assert result is not None, "API should respond with precipitation data"
    assert "value" in result, "Response should contain 'value' field"
    assert "unit" in result, "Response should contain 'unit' field"
    
    # Check precipitation value is reasonable
    precipitation = result["value"]
    assert isinstance(precipitation, (int, float)), "Precipitation should be numeric"
    assert precipitation >= 0, f"Precipitation {precipitation} should be non-negative"
    
    # Check unit is mm
    assert result["unit"] == "mm", f"Expected unit 'mm', got '{result['unit']}'"


def test_arome_hr_cape_fetch():
    """Test fetching CAPE (Convective Available Potential Energy) data from AROME_HR model."""
    lat, lon = get_second_stage_coordinates()
    
    result = fetch_arome_wcs(
        latitude=lat,
        longitude=lon,
        model="AROME_HR",
        field="CAPE"
    )
    
    if result is not None:
        assert "value" in result, "Response should contain 'value' field"
        assert "unit" in result, "Response should contain 'unit' field"
        
        cape_value = result["value"]
        assert isinstance(cape_value, (int, float)), "CAPE should be numeric"
        assert cape_value >= 0, f"CAPE {cape_value} should be non-negative"
        
        # CAPE is typically measured in J/kg
        assert result["unit"] in ["J/kg", "j/kg"], f"Expected unit 'J/kg', got '{result['unit']}'"


def test_arome_hr_shear_fetch():
    """Test fetching wind shear data from AROME_HR model."""
    lat, lon = get_second_stage_coordinates()
    
    result = fetch_arome_wcs(
        latitude=lat,
        longitude=lon,
        model="AROME_HR",
        field="SHEAR"
    )
    
    if result is not None:
        assert "value" in result, "Response should contain 'value' field"
        assert "unit" in result, "Response should contain 'unit' field"
        
        shear_value = result["value"]
        assert isinstance(shear_value, (int, float)), "Wind shear should be numeric"
        assert shear_value >= 0, f"Wind shear {shear_value} should be non-negative"
        
        # Wind shear is typically measured in m/s or s^-1
        assert result["unit"] in ["m/s", "s^-1", "1/s"], f"Expected wind shear unit, got '{result['unit']}'"


def test_arome_hr_height_parameter():
    """Test that height parameter is properly handled (surface level, e.g., 2m)."""
    lat, lon = get_second_stage_coordinates()
    
    # Test with explicit height parameter
    result = fetch_arome_wcs(
        latitude=lat,
        longitude=lon,
        model="AROME_HR",
        field="TEMPERATURE",
        height_level="2m"  # Surface level temperature
    )
    
    assert result is not None, "API should respond with height-specific data"
    assert "value" in result, "Response should contain 'value' field"
    assert "unit" in result, "Response should contain 'unit' field"


if __name__ == "__main__":
    # Run tests manually if executed directly
    pytest.main([__file__, "-v"])