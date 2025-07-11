"""
Test live parsing of massif restrictions and zone risk levels from the official website.
"""

import pytest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup

from src.fire.risk_block_formatter import (
    get_massif_restrictions, 
    get_zone_risk_levels,
    format_risk_block,
    GR20_MASSIFS,
    GR20_ZONES
)


class TestLiveRiskParsing:
    """Test cases for live risk parsing from the official website."""
    
    def test_get_massif_restrictions_success(self):
        """Test successful parsing of massif restrictions."""
        # Mock HTML with some restricted massifs
        mock_html = """
        <table>
            <tr><td>1</td><td>AGRIATES OUEST</td><td><img src="/static/20/img/legende_noir.png"></td></tr>
            <tr><td>3</td><td>BONIFATO</td><td><img src="/static/20/img/legende_noir.png"></td></tr>
            <tr><td>5</td><td>FANGO</td><td><img src="/static/20/img/legende_points.png"></td></tr>
            <tr><td>24</td><td>BAVELLA</td><td><img src="/static/20/img/legende_noir.png"></td></tr>
            <tr><td>99</td><td>NOT GR20</td><td><img src="/static/20/img/legende_noir.png"></td></tr>
        </table>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = get_massif_restrictions()
            
            # Should return only GR20 massifs that are restricted
            assert 1 in result  # AGRIATES OUEST
            assert 3 in result  # BONIFATO
            assert 24 in result  # BAVELLA
            assert 5 not in result  # FANGO (not restricted)
            assert 99 not in result  # Not in GR20 list
    
    def test_get_massif_restrictions_no_table(self):
        """Test handling when massif table is not found."""
        mock_html = "<html><body><p>No table here</p></body></html>"
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = get_massif_restrictions()
            assert result == []
    
    def test_get_massif_restrictions_request_error(self):
        """Test handling of request errors."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")
            
            result = get_massif_restrictions()
            assert result == []
    
    def test_get_zone_risk_levels_geojson(self):
        """Test parsing zone risk levels from GeoJSON data."""
        mock_html = """
        <script>
        var geojson = [
            {"type": "Feature", "properties": {"id": 217, "level": 2}},
            {"type": "Feature", "properties": {"id": 208, "level": 3}},
            {"type": "Feature", "properties": {"id": 209, "level": 4}},
            {"type": "Feature", "properties": {"id": 999, "level": 5}}
        ];
        </script>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = get_zone_risk_levels(42.0, 9.0)
            
            assert result[217] == 2  # BALAGNE - medium
            assert result[208] == 3  # REGION DE CONCA - high
            assert result[209] == 4  # COTE DES NACRES - very high
            assert 999 not in result  # Not in GR20 zones
    
    def test_get_zone_risk_levels_zone_objects(self):
        """Test parsing zone risk levels from JavaScript zone objects."""
        mock_html = """
        <script>
        var zones = [
            {"id": 216, "level": 2},
            {"id": 206, "level": 1},
            {"id": 205, "level": 1}
        ];
        </script>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = get_zone_risk_levels(42.0, 9.0)
            
            assert result[216] == 2  # MONTI - medium
            assert result[206] == 1  # MONTAGNE - low
            assert result[205] == 1  # MOYENNE MONTAGNE SUD - low
    
    def test_get_zone_risk_levels_css_classes(self):
        """Test parsing zone risk levels from CSS classes."""
        mock_html = """
        <div data-zone="217" class="zone-high">BALAGNE</div>
        <div id="zone-208" class="zone-very-high">REGION DE CONCA</div>
        <div data-zone="216" class="zone-medium">MONTI</div>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = get_zone_risk_levels(42.0, 9.0)
            
            assert result[217] == 3  # BALAGNE - high (from zone-high class)
            assert result[208] == 4  # REGION DE CONCA - very high
            assert result[216] == 2  # MONTI - medium
    
    def test_get_zone_risk_levels_no_data(self):
        """Test handling when no zone data is found."""
        mock_html = "<html><body><p>No zone data here</p></body></html>"
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = get_zone_risk_levels(42.0, 9.0)
            assert result == {}
    
    def test_get_zone_risk_levels_request_error(self):
        """Test handling of request errors for zone data."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")
            
            result = get_zone_risk_levels(42.0, 9.0)
            assert result == {}
    
    def test_format_risk_block_with_live_data(self):
        """Test format_risk_block with live data (mocked)."""
        # Mock both functions to return realistic data
        with patch('src.fire.risk_block_formatter.get_zone_risk_levels') as mock_zones:
            with patch('src.fire.risk_block_formatter.get_massif_restrictions') as mock_massifs:
                mock_zones.return_value = {
                    217: 2,  # BALAGNE - medium
                    208: 3,  # REGION DE CONCA - high
                    209: 4,  # COTE DES NACRES - very high
                    216: 2,  # MONTI - medium
                    206: 1,  # MONTAGNE - low (should be ignored)
                    205: 1   # MOYENNE MONTAGNE SUD - low (should be ignored)
                }
                mock_massifs.return_value = [3, 5, 24, 26]  # BONIFATO, FANGO, BAVELLA, CAVU LIVIU
                
                result = format_risk_block(42.0, 9.0)
                
                # Should contain zones with risk level >= 2 and restricted massifs
                assert "Z:HIGH" in result
                assert "MAX209" in result  # Very high risk zone
                assert "M:3,5,24,26" in result
                assert len(result) <= 50  # Reasonable length for risk block
    
    def test_format_risk_block_no_risks(self):
        """Test format_risk_block when no risks are present."""
        with patch('src.fire.risk_block_formatter.get_zone_risk_levels') as mock_zones:
            with patch('src.fire.risk_block_formatter.get_massif_restrictions') as mock_massifs:
                mock_zones.return_value = {
                    206: 1,  # MONTAGNE - low (should be ignored)
                    205: 1   # MOYENNE MONTAGNE SUD - low (should be ignored)
                }
                mock_massifs.return_value = []  # No restricted massifs
                
                result = format_risk_block(42.0, 9.0)
                
                # Should return None when no relevant risks
                assert result is None
    
    def test_format_risk_block_exception_handling(self):
        """Test format_risk_block handles exceptions gracefully."""
        with patch('src.fire.risk_block_formatter.get_zone_risk_levels') as mock_zones:
            mock_zones.side_effect = Exception("Test error")
            
            result = format_risk_block(42.0, 9.0)
            
            # Should return None when exception occurs
            assert result is None 