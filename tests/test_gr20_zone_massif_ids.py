#!/usr/bin/env python3
"""
Tests for GR20 Zone and Massif ID extraction.

This module tests the extraction of zone and massif IDs relevant to the GR20 trail.
"""

import pytest
from unittest.mock import Mock, patch
from src.fire.gr20_zone_massif_ids import GR20ZoneMassifExtractor


class TestGR20ZoneMassifExtractor:
    """Test the GR20 zone and massif ID extractor."""
    
    def test_gr20_massif_ids_are_correct(self):
        """Test that GR20 massif IDs match the documented list."""
        extractor = GR20ZoneMassifExtractor()
        
        expected_massif_ids = [1, 29, 3, 4, 5, 6, 9, 10, 16, 24, 25, 26, 27, 28]
        assert extractor.gr20_massif_ids == expected_massif_ids
    
    def test_gr20_zone_names_are_correct(self):
        """Test that GR20 zone names match the documented list."""
        extractor = GR20ZoneMassifExtractor()
        
        expected_zone_names = [
            "BALAGNE", "MONTI", "MONTAGNE", "COTE DES NACRES", 
            "MOYENNE MONTAGNE SUD", "REGION DE CONCA"
        ]
        assert extractor.gr20_zone_names == expected_zone_names
    
    def test_massif_mapping_contains_gr20_massifs(self):
        """Test that massif mapping contains all GR20 massifs."""
        extractor = GR20ZoneMassifExtractor()
        
        for massif_id in extractor.gr20_massif_ids:
            assert massif_id in extractor.massif_mapping
            assert isinstance(extractor.massif_mapping[massif_id], str)
            assert len(extractor.massif_mapping[massif_id]) > 0
    
    def test_get_restricted_massif_ids_returns_list(self):
        """Test that restricted massif IDs are returned as a list."""
        extractor = GR20ZoneMassifExtractor()
        
        restricted_ids = extractor.get_restricted_massif_ids()
        assert isinstance(restricted_ids, list)
        assert all(isinstance(id, int) for id in restricted_ids)
        assert all(id in extractor.gr20_massif_ids for id in restricted_ids)
    
    def test_get_high_risk_zone_ids_returns_list(self):
        """Test that high risk zone IDs are returned as a list."""
        extractor = GR20ZoneMassifExtractor()
        
        zone_ids = extractor.get_high_risk_zone_ids()
        assert isinstance(zone_ids, list)
        assert all(isinstance(id, int) for id in zone_ids)
    
    def test_format_output_contains_required_sections(self):
        """Test that formatted output contains all required sections."""
        extractor = GR20ZoneMassifExtractor()
        
        output = extractor.format_output()
        
        # Check that output contains required sections
        assert "Massif_IDs:" in output
        assert "Zone_IDs:" in output
        assert "Mapping_Massifs:" in output
        assert "Mapping_Zones:" in output
    
    def test_format_output_massif_ids_format(self):
        """Test that massif IDs are formatted as comma-separated list."""
        extractor = GR20ZoneMassifExtractor()
        
        output = extractor.format_output()
        
        # Extract massif IDs line
        lines = output.split('\n')
        massif_line = next(line for line in lines if line.startswith('Massif_IDs:'))
        
        # Check format: "Massif_IDs: 3,4,5,9,10,16,24,26"
        assert massif_line.startswith('Massif_IDs: ')
        ids_part = massif_line.replace('Massif_IDs: ', '')
        
        if ids_part.strip():  # If there are any restricted massifs
            ids = [int(id.strip()) for id in ids_part.split(',')]
            assert all(id in extractor.gr20_massif_ids for id in ids)
    
    def test_format_output_zone_ids_format(self):
        """Test that zone IDs are formatted as comma-separated list."""
        extractor = GR20ZoneMassifExtractor()
        
        output = extractor.format_output()
        
        # Extract zone IDs line
        lines = output.split('\n')
        zone_line = next(line for line in lines if line.startswith('Zone_IDs:'))
        
        # Check format: "Zone_IDs: 204,205,207,208"
        assert zone_line.startswith('Zone_IDs: ')
        ids_part = zone_line.replace('Zone_IDs: ', '')
        
        if ids_part.strip():  # If there are any high risk zones
            ids = [int(id.strip()) for id in ids_part.split(',')]
            assert all(isinstance(id, int) for id in ids)
    
    def test_mapping_massifs_format(self):
        """Test that massif mapping is formatted correctly."""
        extractor = GR20ZoneMassifExtractor()
        
        output = extractor.format_output()
        
        # Find mapping section
        lines = output.split('\n')
        mapping_start = next(i for i, line in enumerate(lines) if line == 'Mapping_Massifs:')
        
        # Check that mapping contains GR20 massifs
        mapping_lines = []
        for line in lines[mapping_start + 1:]:
            if line.startswith('Mapping_Zones:') or not line.strip():
                break
            if '→' in line:
                mapping_lines.append(line)
        
        # Should have mappings for all GR20 massifs
        assert len(mapping_lines) == len(extractor.gr20_massif_ids)
        
        for line in mapping_lines:
            # Format: "  3 → BONIFATO"
            parts = line.strip().split(' → ')
            assert len(parts) == 2
            massif_id = int(parts[0])
            massif_name = parts[1]
            
            assert massif_id in extractor.gr20_massif_ids
            assert massif_name == extractor.massif_mapping[massif_id]
    
    def test_mapping_zones_format(self):
        """Test that zone mapping is formatted correctly."""
        extractor = GR20ZoneMassifExtractor()
        
        output = extractor.format_output()
        
        # Find mapping section
        lines = output.split('\n')
        mapping_start = next(i for i, line in enumerate(lines) if line == 'Mapping_Zones:')
        
        # Check that mapping contains GR20 zones (if any are found)
        mapping_lines = []
        for line in lines[mapping_start + 1:]:
            if not line.strip():
                break
            if '→' in line:
                mapping_lines.append(line)
        
        # Each mapping line should have correct format
        for line in mapping_lines:
            # Format: "  204 → MONTAGNE"
            parts = line.strip().split(' → ')
            assert len(parts) == 2
            zone_id = int(parts[0])
            zone_name = parts[1]
            
            assert isinstance(zone_id, int)
            assert isinstance(zone_name, str)
            assert len(zone_name) > 0
    
    def test_restricted_massifs_are_marked_with_asterisk(self):
        """Test that restricted massifs are correctly identified."""
        extractor = GR20ZoneMassifExtractor()
        
        # Get restricted massifs
        restricted_ids = extractor.get_restricted_massif_ids()
        
        # Check that all restricted massifs are marked with (*) in the mapping
        for massif_id in restricted_ids:
            massif_name = extractor.massif_mapping[massif_id]
            assert massif_name.endswith(' (*)')
    
    def test_non_restricted_massifs_not_marked_with_asterisk(self):
        """Test that non-restricted massifs are not marked with asterisk."""
        extractor = GR20ZoneMassifExtractor()
        
        # Get all GR20 massifs
        all_massif_ids = extractor.gr20_massif_ids
        restricted_ids = extractor.get_restricted_massif_ids()
        
        # Check that non-restricted massifs are not marked with (*)
        for massif_id in all_massif_ids:
            if massif_id not in restricted_ids:
                massif_name = extractor.massif_mapping[massif_id]
                assert not massif_name.endswith(' (*)') 