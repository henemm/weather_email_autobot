import pytest
import json
from unittest.mock import patch, Mock
from src.wetter.analyze_arome_layers import (
    fetch_capabilities,
    parse_wms_capabilities,
    parse_wcs_capabilities,
    check_conca_coverage,
    analyze_arome_layers
)


class TestAromeLayerAnalysis:
    """Test cases for AROME layer analysis functionality."""
    
    def test_fetch_capabilities_success(self):
        """Test successful capabilities fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<xml>test data</xml>"
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            result = fetch_capabilities("https://test.url")
            
            # Check that get was called with URL and headers
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://test.url"
            assert "Authorization" in call_args[1]["headers"]
            assert result == "<xml>test data</xml>"
    
    def test_fetch_capabilities_error(self):
        """Test capabilities fetch with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(RuntimeError, match="HTTP 401"):
                fetch_capabilities("https://test.url")
    
    def test_parse_wms_capabilities(self):
        """Test WMS capabilities parsing."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<WMS_Capabilities version="1.3.0" xmlns="http://www.opengis.net/wms" xmlns:ows="http://www.opengis.net/ows/1.1">
    <Capability>
        <Layer>
            <Layer>
                <Name>test_layer</Name>
                <Title>Test Layer</Title>
                <Abstract>Test description</Abstract>
                <EX_GeographicBoundingBox>
                    <westBoundLongitude>9.0</westBoundLongitude>
                    <eastBoundLongitude>10.0</eastBoundLongitude>
                    <southBoundLatitude>41.0</southBoundLatitude>
                    <northBoundLatitude>42.0</northBoundLatitude>
                </EX_GeographicBoundingBox>
                <Dimension name="time" units="ISO8601">2024-01-01T00:00:00Z/2024-01-02T00:00:00Z</Dimension>
            </Layer>
        </Layer>
    </Capability>
</WMS_Capabilities>
        """
        
        layers = parse_wms_capabilities(xml_content)
        
        assert len(layers) == 1
        layer = layers[0]
        assert layer['id'] == 'test_layer'
        assert layer['title'] == 'Test Layer'
        assert layer['bbox'] == [9.0, 41.0, 10.0, 42.0]
        assert layer['time_range'] == '2024-01-01T00:00:00Z/2024-01-02T00:00:00Z'
    
    def test_parse_wcs_capabilities(self):
        """Test WCS capabilities parsing."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<wcs:Capabilities version="2.0.1" xmlns:wcs="http://www.opengis.net/wcs/2.0" xmlns:ows="http://www.opengis.net/ows/1.1">
    <wcs:Contents>
        <wcs:CoverageSummary>
            <wcs:CoverageId>test_coverage</wcs:CoverageId>
            <wcs:CoverageSubtype>test_subtype</wcs:CoverageSubtype>
            <wcs:BoundingBox crs="http://www.opengis.net/def/crs/EPSG/0/4326">
                <ows:LowerCorner>9.0 41.0</ows:LowerCorner>
                <ows:UpperCorner>10.0 42.0</ows:UpperCorner>
            </wcs:BoundingBox>
            <wcs:WGS84BoundingBox>
                <ows:LowerCorner>9.0 41.0</ows:LowerCorner>
                <ows:UpperCorner>10.0 42.0</ows:UpperCorner>
            </wcs:WGS84BoundingBox>
        </wcs:CoverageSummary>
    </wcs:Contents>
</wcs:Capabilities>
        """
        
        layers = parse_wcs_capabilities(xml_content)
        
        assert len(layers) == 1
        layer = layers[0]
        assert layer['id'] == 'test_coverage'
        assert layer['bbox'] == [9.0, 41.0, 10.0, 42.0]
    
    def test_check_conca_coverage_inside(self):
        """Test Conca coverage check when point is inside bbox."""
        bbox = [9.0, 41.0, 10.0, 42.0]  # Conca (9.35, 41.75) is inside
        assert check_conca_coverage(bbox) is True
    
    def test_check_conca_coverage_outside(self):
        """Test Conca coverage check when point is outside bbox."""
        bbox = [8.0, 40.0, 9.0, 41.0]  # Conca (9.35, 41.75) is outside
        assert check_conca_coverage(bbox) is False
    
    def test_analyze_arome_layers_integration(self):
        """Test complete analysis integration."""
        mock_wms_response = """<?xml version="1.0" encoding="UTF-8"?>
<WMS_Capabilities version="1.3.0" xmlns="http://www.opengis.net/wms" xmlns:ows="http://www.opengis.net/ows/1.1">
    <Capability>
        <Layer>
            <Layer>
                <Name>arome_layer</Name>
                <Title>AROME Layer</Title>
                <EX_GeographicBoundingBox>
                    <westBoundLongitude>9.0</westBoundLongitude>
                    <eastBoundLongitude>10.0</eastBoundLongitude>
                    <southBoundLatitude>41.0</southBoundLatitude>
                    <northBoundLatitude>42.0</northBoundLatitude>
                </EX_GeographicBoundingBox>
            </Layer>
        </Layer>
    </Capability>
</WMS_Capabilities>
        """
        
        mock_wcs_response = """<?xml version="1.0" encoding="UTF-8"?>
<wcs:Capabilities version="2.0.1" xmlns:wcs="http://www.opengis.net/wcs/2.0" xmlns:ows="http://www.opengis.net/ows/1.1">
    <wcs:Contents>
        <wcs:CoverageSummary>
            <wcs:CoverageId>wcs_coverage</wcs:CoverageId>
            <wcs:WGS84BoundingBox>
                <ows:LowerCorner>9.0 41.0</ows:LowerCorner>
                <ows:UpperCorner>10.0 42.0</ows:UpperCorner>
            </wcs:WGS84BoundingBox>
        </wcs:CoverageSummary>
    </wcs:Contents>
</wcs:Capabilities>
        """
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = [
                Mock(status_code=200, text=mock_wms_response),
                Mock(status_code=200, text=mock_wcs_response),
                Mock(status_code=200, text=mock_wcs_response)
            ]
            
            result = analyze_arome_layers()
            
            assert len(result) == 3
            assert all('endpoint' in service for service in result)
            assert all('layers' in service for service in result)
            
            # Check that Conca coverage is correctly identified
            for service in result:
                for layer in service['layers']:
                    assert 'covers_conca' in layer
                    assert layer['covers_conca'] is True  # Should be inside our test bbox 