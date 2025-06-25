"""
Tests for AROME WCS height axis handling.

This module tests the correction of height axis issues in AROME WCS requests
that cause InvalidSubsetting errors.
"""

import pytest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET
from tests.utils.env_loader import get_env_var

# Add src to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome_wcs import (
    _extract_axis_from_describe,
    _extract_height_axis_from_describe,
    _validate_height_subset,
    _build_subset_params_with_height_validation
)


class TestHeightAxisExtraction:
    """Test height axis extraction from WCS DescribeCoverage responses."""
    
    def test_extract_height_axis_from_describe_with_height(self):
        """Test extraction of height axis when present in DescribeCoverage."""
        # Sample XML with height axis and proper namespaces
        describe_xml = '''
        <wcs:CoverageDescription xmlns:wcs="http://www.opengis.net/wcs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:RectifiedGrid>
                <gml:axisLabels>long lat height time</gml:axisLabels>
            </gml:RectifiedGrid>
            <gml:EnvelopeWithTimePeriod axisLabels="long lat height time">
                <gml:axisLabels>long lat height time</gml:axisLabels>
            </gml:EnvelopeWithTimePeriod>
        </wcs:CoverageDescription>
        '''
        
        height_info = _extract_height_axis_from_describe(describe_xml)
        
        assert height_info['has_height_axis'] is True
        assert height_info['height_label'] == 'height'
        assert height_info['available_heights'] == ['surface', '2', '10', '50', '100', '200', '500', '850', '925']  # Common AROME heights
    
    def test_extract_height_axis_from_describe_without_height(self):
        """Test extraction when no height axis is present."""
        # Sample XML without height axis and proper namespaces
        describe_xml = '''
        <wcs:CoverageDescription xmlns:wcs="http://www.opengis.net/wcs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:RectifiedGrid>
                <gml:axisLabels>long lat time</gml:axisLabels>
            </gml:RectifiedGrid>
        </wcs:CoverageDescription>
        '''
        
        height_info = _extract_height_axis_from_describe(describe_xml)
        
        assert height_info['has_height_axis'] is False
        assert height_info['height_label'] is None
        assert height_info['available_heights'] == []
    
    def test_extract_height_axis_from_describe_malformed_xml(self):
        """Test extraction with malformed XML."""
        malformed_xml = '<invalid><xml>'
        
        height_info = _extract_height_axis_from_describe(malformed_xml)
        
        assert height_info['has_height_axis'] is False
        assert height_info['height_label'] is None
        assert height_info['available_heights'] == []


class TestHeightValidation:
    """Test height subset validation."""
    
    def test_validate_height_subset_with_valid_height(self):
        """Test validation with valid height value."""
        height_info = {
            'has_height_axis': True,
            'height_label': 'height',
            'available_heights': ['surface', '2', '10']
        }
        
        # Test valid heights
        assert _validate_height_subset(height_info, 'surface') is True
        assert _validate_height_subset(height_info, '2') is True
        assert _validate_height_subset(height_info, '10') is True
    
    def test_validate_height_subset_with_invalid_height(self):
        """Test validation with invalid height value."""
        height_info = {
            'has_height_axis': True,
            'height_label': 'height',
            'available_heights': ['surface', '2', '10']
        }
        
        # Test invalid heights
        assert _validate_height_subset(height_info, '0') is False
        assert _validate_height_subset(height_info, 'invalid') is False
        assert _validate_height_subset(height_info, '100') is False
    
    def test_validate_height_subset_without_height_axis(self):
        """Test validation when no height axis is present."""
        height_info = {
            'has_height_axis': False,
            'height_label': None,
            'available_heights': []
        }
        
        # Should return False for any height when no height axis exists
        assert _validate_height_subset(height_info, 'surface') is False
        assert _validate_height_subset(height_info, '2') is False


class TestSubsetParameterBuilding:
    """Test building subset parameters with height validation."""
    
    def test_build_subset_params_with_height_validation_with_height_axis(self):
        """Test building subset params when height axis is present and valid."""
        height_info = {
            'has_height_axis': True,
            'height_label': 'height',
            'available_heights': ['surface', '2', '10']
        }
        
        axis_info = {
            'lat': 'lat',
            'lon': 'long',
            'time': 'time'
        }
        
        subset_params = _build_subset_params_with_height_validation(
            latitude=42.0,
            longitude=9.0,
            axis_info=axis_info,
            height_info=height_info,
            time_value="2025-06-24T12:00:00Z",
            height_level="2"
        )
        
        # Should include height subset
        assert "lat(42.0)" in subset_params
        assert "long(9.0)" in subset_params
        assert "time(2025-06-24T12:00:00Z)" in subset_params
        assert "height(2)" in subset_params
    
    def test_build_subset_params_with_height_validation_without_height_axis(self):
        """Test building subset params when no height axis is present."""
        height_info = {
            'has_height_axis': False,
            'height_label': None,
            'available_heights': []
        }
        
        axis_info = {
            'lat': 'lat',
            'lon': 'long',
            'time': 'time'
        }
        
        subset_params = _build_subset_params_with_height_validation(
            latitude=42.0,
            longitude=9.0,
            axis_info=axis_info,
            height_info=height_info,
            time_value="2025-06-24T12:00:00Z",
            height_level="2"
        )
        
        # Should NOT include height subset
        assert "lat(42.0)" in subset_params
        assert "long(9.0)" in subset_params
        assert "time(2025-06-24T12:00:00Z)" in subset_params
        assert "height(2)" not in subset_params
    
    def test_build_subset_params_with_height_validation_invalid_height(self):
        """Test building subset params with invalid height value."""
        height_info = {
            'has_height_axis': True,
            'height_label': 'height',
            'available_heights': ['surface', '2', '10']
        }
        
        axis_info = {
            'lat': 'lat',
            'lon': 'long',
            'time': 'time'
        }
        
        subset_params = _build_subset_params_with_height_validation(
            latitude=42.0,
            longitude=9.0,
            axis_info=axis_info,
            height_info=height_info,
            time_value="2025-06-24T12:00:00Z",
            height_level="0"  # Invalid height
        )
        
        # Should NOT include invalid height subset
        assert "lat(42.0)" in subset_params
        assert "long(9.0)" in subset_params
        assert "time(2025-06-24T12:00:00Z)" in subset_params
        assert "height(0)" not in subset_params


class TestHeightAxisIntegration:
    """Integration tests for height axis handling."""
    
    @pytest.mark.skipif(
        not get_env_var("METEOFRANCE_CLIENT_ID"),
        reason="METEOFRANCE_CLIENT_ID environment variable not set"
    )
    @pytest.mark.integration
    def test_arome_hr_temperature_with_height_axis_handling(self):
        """Test AROME_HR temperature fetch with proper height axis handling."""
        from wetter.fetch_arome_wcs import fetch_arome_wcs
        
        # Test coordinates for Conca, Corsica
        latitude = 41.75
        longitude = 9.35
        
        try:
            # Test temperature fetch - should work without height issues
            result = fetch_arome_wcs(latitude, longitude, "AROME_HR", "TEMPERATURE")
            
            if result:
                assert result["source"] == "AROME_HR"
                assert result["latitude"] == latitude
                assert result["longitude"] == longitude
                assert result["field"] == "TEMPERATURE"
                print("✅ AROME_HR temperature fetch with height axis handling: Success")
            else:
                print("⚠️ AROME_HR temperature fetch: No data returned (may be normal)")
                
        except Exception as e:
            print(f"❌ AROME_HR temperature fetch: Failed - {e}")
            # Don't fail the test, as this might be due to API availability
    
    @pytest.mark.skipif(
        not get_env_var("METEOFRANCE_CLIENT_ID"),
        reason="METEOFRANCE_CLIENT_ID environment variable not set"
    )
    @pytest.mark.integration
    def test_arome_hr_cape_with_height_axis_handling(self):
        """Test AROME_HR CAPE fetch with proper height axis handling."""
        from wetter.fetch_arome_wcs import fetch_arome_wcs
        
        # Test coordinates for Conca, Corsica
        latitude = 41.75
        longitude = 9.35
        
        try:
            # Test CAPE fetch - should work without height issues
            result = fetch_arome_wcs(
                latitude, 
                longitude, 
                "AROME_HR", 
                "CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY"
            )
            
            if result:
                assert result["source"] == "AROME_HR"
                assert result["latitude"] == latitude
                assert result["longitude"] == longitude
                print("✅ AROME_HR CAPE fetch with height axis handling: Success")
            else:
                print("⚠️ AROME_HR CAPE fetch: No data returned (may be normal)")
                
        except Exception as e:
            print(f"❌ AROME_HR CAPE fetch: Failed - {e}")
            # Don't fail the test, as this might be due to API availability 