import pytest
from datetime import datetime
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

# Add src to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.fetch_arome_wcs import _parse_gml_response, _extract_temperature_from_gml


class TestGMLParsing:
    """Test cases for GML parsing functionality"""

    def setup_method(self):
        """Setup test data"""
        self.sample_gml_response = """<?xml version="1.0" encoding="UTF-8"?>
<gml:RectifiedGridCoverage xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:wcs="http://www.opengis.net/wcs/2.0" gml:id="temperature_coverage">
  <gml:domainSet>
    <gml:RectifiedGrid gml:id="temperature_grid" dimension="2">
      <gml:limits>
        <gml:GridEnvelope>
          <gml:low>0 0</gml:low>
          <gml:high>1 1</gml:high>
        </gml:GridEnvelope>
      </gml:limits>
      <gml:axisLabels>i j</gml:axisLabels>
      <gml:origin>
        <gml:Point gml:id="origin_point">
          <gml:pos>9.3125 41.6875</gml:pos>
        </gml:Point>
      </gml:origin>
      <gml:offsetVector>0.0125 0</gml:offsetVector>
      <gml:offsetVector>0 0.0125</gml:offsetVector>
    </gml:RectifiedGrid>
  </gml:domainSet>
  <gml:rangeSet>
    <gml:DataBlock>
      <gml:rangeParameters>
        <gml:Quantity>
          <gml:name>Temperature</gml:name>
          <gml:uom code="°C"/>
        </gml:Quantity>
      </gml:rangeParameters>
      <gml:doubleOrNilReasonTupleList>24.5 25.1 24.8 25.3</gml:doubleOrNilReasonTupleList>
    </gml:DataBlock>
  </gml:rangeSet>
</gml:RectifiedGridCoverage>"""

        self.sample_gml_with_nil = """<?xml version="1.0" encoding="UTF-8"?>
<gml:RectifiedGridCoverage xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="temperature_coverage">
  <gml:domainSet>
    <gml:RectifiedGrid gml:id="temperature_grid" dimension="2">
      <gml:limits>
        <gml:GridEnvelope>
          <gml:low>0 0</gml:low>
          <gml:high>1 1</gml:high>
        </gml:GridEnvelope>
      </gml:limits>
      <gml:axisLabels>i j</gml:axisLabels>
      <gml:origin>
        <gml:Point gml:id="origin_point">
          <gml:pos>9.3125 41.6875</gml:pos>
        </gml:Point>
      </gml:origin>
      <gml:offsetVector>0.0125 0</gml:offsetVector>
      <gml:offsetVector>0 0.0125</gml:offsetVector>
    </gml:RectifiedGrid>
  </gml:domainSet>
  <gml:rangeSet>
    <gml:DataBlock>
      <gml:rangeParameters>
        <gml:Quantity>
          <gml:name>Temperature</gml:name>
          <gml:uom code="°C"/>
        </gml:Quantity>
      </gml:rangeParameters>
      <gml:doubleOrNilReasonTupleList>24.5 nil 24.8 25.3</gml:doubleOrNilReasonTupleList>
    </gml:DataBlock>
  </gml:rangeSet>
</gml:RectifiedGridCoverage>"""

        self.invalid_gml = """<?xml version="1.0" encoding="UTF-8"?>
<gml:RectifiedGridCoverage xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="invalid_coverage">
  <gml:domainSet>
    <gml:RectifiedGrid gml:id="invalid_grid" dimension="2">
      <gml:limits>
        <gml:GridEnvelope>
          <gml:low>0 0</gml:low>
          <gml:high>1 1</gml:high>
        </gml:GridEnvelope>
      </gml:limits>
    </gml:RectifiedGrid>
  </gml:domainSet>
  <gml:rangeSet>
    <gml:DataBlock>
      <gml:rangeParameters>
        <gml:Quantity>
          <gml:name>Invalid</gml:name>
        </gml:Quantity>
      </gml:rangeParameters>
      <gml:doubleOrNilReasonTupleList></gml:doubleOrNilReasonTupleList>
    </gml:DataBlock>
  </gml:rangeSet>
</gml:RectifiedGridCoverage>"""

    def test_extract_temperature_from_gml_valid_data(self):
        """Test extraction of temperature values from valid GML data"""
        # Arrange
        gml_content = self.sample_gml_response
        
        # Act
        result = _extract_temperature_from_gml(gml_content)
        
        # Assert
        assert result is not None, "Expected temperature data, got None"
        assert "values" in result, "Expected 'values' key in result"
        assert "unit" in result, "Expected 'unit' key in result"
        assert "bbox" in result, "Expected 'bbox' key in result"
        
        # Check temperature values
        expected_values = [24.5, 25.1, 24.8, 25.3]
        assert result["values"] == expected_values, f"Expected {expected_values}, got {result['values']}"
        
        # Check unit
        assert result["unit"] == "°C", f"Expected '°C', got {result['unit']}"
        
        # Check bounding box (should be extracted from origin and offset vectors)
        assert len(result["bbox"]) == 4, "Expected 4-element bounding box"
        assert all(isinstance(x, float) for x in result["bbox"]), "All bbox elements should be floats"

    def test_extract_temperature_from_gml_with_nil_values(self):
        """Test extraction of temperature values with nil values in GML"""
        # Arrange
        gml_content = self.sample_gml_with_nil
        
        # Act
        result = _extract_temperature_from_gml(gml_content)
        
        # Assert
        assert result is not None, "Expected temperature data, got None"
        assert "values" in result, "Expected 'values' key in result"
        
        # Check that nil values are handled (should be None or filtered out)
        expected_values = [24.5, None, 24.8, 25.3]  # or [24.5, 24.8, 25.3] if filtered
        assert len(result["values"]) > 0, "Should have at least some valid values"
        
        # All non-None values should be floats
        for value in result["values"]:
            if value is not None:
                assert isinstance(value, float), f"Expected float, got {type(value)}"

    def test_extract_temperature_from_gml_invalid_data(self):
        """Test extraction from invalid GML data"""
        # Arrange
        gml_content = self.invalid_gml
        
        # Act
        result = _extract_temperature_from_gml(gml_content)
        
        # Assert
        # Should return None or empty data structure for invalid GML
        assert result is None or result["values"] == [], "Expected None or empty values for invalid GML"

    def test_extract_temperature_from_gml_empty_content(self):
        """Test extraction from empty GML content"""
        # Arrange
        gml_content = ""
        
        # Act
        result = _extract_temperature_from_gml(gml_content)
        
        # Assert
        assert result is None, "Expected None for empty content"

    def test_extract_temperature_from_gml_malformed_xml(self):
        """Test extraction from malformed XML"""
        # Arrange
        gml_content = "<gml:invalid>not well formed xml"
        
        # Act
        result = _extract_temperature_from_gml(gml_content)
        
        # Assert
        assert result is None, "Expected None for malformed XML"

    def test_parse_gml_response_valid_data(self):
        """Test parsing complete GML response into WeatherGridData"""
        # Arrange
        gml_content = self.sample_gml_response
        latitude = 41.6875
        longitude = 9.3125
        layer_name = "TEMPERATURE__GROUND_OR_WATER_SURFACE"
        
        # Act
        result = _parse_gml_response(gml_content, latitude, longitude, layer_name)
        
        # Assert
        assert result is not None, "Expected WeatherGridData object, got None"
        assert result.layer == layer_name, f"Expected layer '{layer_name}', got '{result.layer}'"
        assert result.lat == latitude, f"Expected latitude {latitude}, got {result.lat}"
        assert result.lon == longitude, f"Expected longitude {longitude}, got {result.lon}"
        assert result.unit == "°C", f"Expected unit '°C', got '{result.unit}'"
        assert len(result.values) > 0, "Expected non-empty values array"
        assert all(isinstance(v, float) for v in result.values), "All values should be floats"

    def test_parse_gml_response_with_bounding_box(self):
        """Test parsing GML response with bounding box constraints"""
        # Arrange
        gml_content = self.sample_gml_response
        latitude = 41.6875
        longitude = 9.3125
        layer_name = "TEMPERATURE__GROUND_OR_WATER_SURFACE"
        bbox = [9.3, 41.68, 9.32, 41.69]  # Small bounding box around Conca
        
        # Act
        result = _parse_gml_response(gml_content, latitude, longitude, layer_name, bbox)
        
        # Assert
        assert result is not None, "Expected WeatherGridData object, got None"
        assert len(result.values) > 0, "Expected non-empty values array"
        # Values should be filtered to within the bounding box

    def test_parse_gml_response_invalid_data(self):
        """Test parsing invalid GML response"""
        # Arrange
        gml_content = self.invalid_gml
        latitude = 41.6875
        longitude = 9.3125
        layer_name = "TEMPERATURE__GROUND_OR_WATER_SURFACE"
        
        # Act
        result = _parse_gml_response(gml_content, latitude, longitude, layer_name)
        
        # Assert
        assert result is not None, "Expected WeatherGridData object even for invalid data"
        assert result.layer == layer_name, "Layer name should be preserved"
        assert result.lat == latitude, "Latitude should be preserved"
        assert result.lon == longitude, "Longitude should be preserved"
        assert result.unit == "", "Unit should be empty for invalid data"
        assert result.values == [], "Values should be empty for invalid data"
        assert result.times == [], "Times should be empty for invalid data" 