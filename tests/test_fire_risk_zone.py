#!/usr/bin/env python3
"""
Tests for the new fire risk zone system using official zones.
"""

import pytest
import sys
import os
from datetime import date

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.fire.fire_risk_zone import FireRiskZone
from src.fire.fire_zone_mapper import FireZoneMapper


class TestFireZoneMapper:
    """Test the fire zone mapper functionality."""
    
    def test_zone_mapper_initialization(self):
        """Test that the zone mapper initializes correctly."""
        mapper = FireZoneMapper()
        assert mapper.gdf is not None
        assert len(mapper.ZONE_NUMBER_TO_NAME) > 0
        
    def test_get_zone_for_coordinates(self):
        """Test zone assignment for specific coordinates."""
        mapper = FireZoneMapper()
        
        # Test coordinates for known zones
        test_cases = [
            (42.4653, 8.9070, "BALAGNE"),  # Ortu area
            (41.7330, 9.3377, "REGION DE CONCA"),  # Conca area
        ]
        
        for lat, lon, expected_zone in test_cases:
            zone_info = mapper.get_zone_for_coordinates(lat, lon)
            assert zone_info is not None, f"No zone found for ({lat}, {lon})"
            assert zone_info['zone_name'] == expected_zone, f"Expected {expected_zone}, got {zone_info['zone_name']}"
            
    def test_validate_coordinates(self):
        """Test coordinate validation."""
        mapper = FireZoneMapper()
        
        # Valid coordinates (within Corsica)
        assert mapper.validate_coordinates(42.0, 9.0) is True
        
        # Invalid coordinates (outside Corsica)
        assert mapper.validate_coordinates(0.0, 0.0) is False
        
    def test_get_all_zones(self):
        """Test retrieval of all zones."""
        mapper = FireZoneMapper()
        zones = mapper.get_all_zones()
        
        assert isinstance(zones, dict)
        assert len(zones) > 0
        
        # Check that all zone numbers are present
        expected_zones = ["201", "202", "203", "214", "215", "216"]
        for zone_num in expected_zones:
            assert zone_num in zones


class TestFireRiskZone:
    """Test the fire risk zone functionality."""
    
    def test_fire_risk_zone_initialization(self):
        """Test that the fire risk zone handler initializes correctly."""
        fire_risk = FireRiskZone()
        assert fire_risk.zone_mapper is not None
        assert fire_risk.api_url is not None
        
    def test_fetch_fire_risk_data(self):
        """Test fetching fire risk data from API."""
        fire_risk = FireRiskZone()
        data = fire_risk.fetch_fire_risk_data()
        
        # API should return data
        assert data is not None
        assert 'zm' in data
        
        # Check that we have zone data
        zm_data = data['zm']
        assert isinstance(zm_data, dict)
        assert len(zm_data) > 0
        
    def test_get_zone_fire_alert_for_location(self):
        """Test getting fire risk alert for a location."""
        fire_risk = FireRiskZone()
        
        # Test with known coordinates
        lat, lon = 42.4653, 8.9070  # Ortu area
        alert = fire_risk.get_zone_fire_alert_for_location(lat, lon)
        
        if alert:  # API data might not be available in tests
            assert 'zone_number' in alert
            assert 'zone_name' in alert
            assert 'level' in alert
            assert 'description' in alert
            assert isinstance(alert['level'], int)
            
    def test_format_fire_warnings(self):
        """Test formatting of fire warnings."""
        fire_risk = FireRiskZone()
        
        # Test with coordinates that should have a zone
        lat, lon = 42.4653, 8.9070
        warning = fire_risk.format_fire_warnings(lat, lon)
        
        # Warning should be either empty or a valid format
        if warning:
            assert warning in ["WARN Waldbrand", "HIGH Waldbrand", "MAX Waldbrand"]
        else:
            # No warning is also valid (level < 2)
            pass
            
    def test_level_descriptions(self):
        """Test level description mapping."""
        fire_risk = FireRiskZone()
        
        assert fire_risk._get_level_description(0) == "Faible"
        assert fire_risk._get_level_description(1) == "Modéré"
        assert fire_risk._get_level_description(2) == "Élevé"
        assert fire_risk._get_level_description(3) == "Très élevé"
        assert fire_risk._get_level_description(4) == "Exceptionnel"
        
    def test_level_to_warning(self):
        """Test level to warning conversion."""
        fire_risk = FireRiskZone()
        
        assert fire_risk._level_to_warning(0) == ""
        assert fire_risk._level_to_warning(1) == ""
        assert fire_risk._level_to_warning(2) == "WARN"
        assert fire_risk._level_to_warning(3) == "HIGH"
        assert fire_risk._level_to_warning(4) == "MAX"


class TestGR20StageIntegration:
    """Test integration with GR20 stages."""
    
    def test_all_gr20_stages_have_zones(self):
        """Test that all GR20 stage endpoints can be assigned to zones."""
        import json
        
        # Load GR20 stages
        etappen_path = os.path.join(os.path.dirname(__file__), '../etappen.json')
        with open(etappen_path, 'r', encoding='utf-8') as f:
            etappen = json.load(f)
            
        mapper = FireZoneMapper()
        fire_risk = FireRiskZone()
        
        for stage in etappen:
            if 'punkte' in stage and stage['punkte']:
                # Test the last point of each stage
                last_point = stage['punkte'][-1]
                lat, lon = float(last_point['lat']), float(last_point['lon'])
                stage_name = stage.get('name', 'Unknown')
                
                # Should find a zone for all GR20 stages
                zone_info = mapper.get_zone_for_coordinates(lat, lon)
                assert zone_info is not None, f"No zone found for stage {stage_name} ({lat}, {lon})"
                
                # Should be able to get fire risk data
                alert = fire_risk.get_zone_fire_alert_for_location(lat, lon)
                if alert:  # API data might not be available
                    assert 'zone_number' in alert
                    assert 'level' in alert


if __name__ == "__main__":
    pytest.main([__file__]) 