"""
Test module for department mapper functionality.
"""

import pytest
from src.wetter.department_mapper import DepartmentMapper, get_department_from_coordinates, get_warning_data_for_coordinates


class TestDepartmentMapper:
    """Test cases for DepartmentMapper class."""
    
    def test_get_department_from_coordinates_corsica_south(self):
        """Test department mapping for South Corsica coordinates."""
        mapper = DepartmentMapper()
        
        # Test coordinates in South Corsica (Corse-du-Sud)
        lat, lon = 41.5, 9.0  # South Corsica
        department = mapper.get_department_from_coordinates(lat, lon)
        
        assert department == "2A"
    
    def test_get_department_from_coordinates_corsica_north(self):
        """Test department mapping for North Corsica coordinates."""
        mapper = DepartmentMapper()
        
        # Test coordinates in North Corsica (Haute-Corse)
        lat, lon = 42.5, 9.0  # North Corsica
        department = mapper.get_department_from_coordinates(lat, lon)
        
        assert department == "2B"
    
    def test_get_department_from_coordinates_outside_corsica(self):
        """Test department mapping for coordinates outside Corsica."""
        mapper = DepartmentMapper()
        
        # Test coordinates outside Corsica
        lat, lon = 48.0, 2.0  # Paris area
        department = mapper.get_department_from_coordinates(lat, lon)
        
        assert department is None
    
    def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        # Test convenience function for South Corsica
        lat, lon = 41.5, 9.0
        department = get_department_from_coordinates(lat, lon)
        assert department == "2A"
        
        # Test convenience function for North Corsica
        lat, lon = 42.5, 9.0
        department = get_department_from_coordinates(lat, lon)
        assert department == "2B"


class TestWarningDataIntegration:
    """Test integration with warning data retrieval."""
    
    def test_get_warning_data_for_coordinates(self):
        """Test warning data retrieval for coordinates."""
        # Test with North Corsica coordinates
        lat, lon = 42.5, 9.0
        warning_data = get_warning_data_for_coordinates(lat, lon)
        
        # Should return either warning data or None (depending on API availability)
        assert warning_data is None or isinstance(warning_data, dict)
    
    def test_get_warning_data_for_invalid_coordinates(self):
        """Test warning data retrieval for invalid coordinates."""
        # Test with coordinates outside Corsica
        lat, lon = 48.0, 2.0
        warning_data = get_warning_data_for_coordinates(lat, lon)
        
        # Should return None for invalid coordinates
        assert warning_data is None


if __name__ == "__main__":
    pytest.main([__file__])
