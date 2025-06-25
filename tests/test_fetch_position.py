import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.position.fetch_sharemap import fetch_sharemap_position
from src.model.datatypes import CurrentPosition


class TestFetchSharemapPosition:
    """Test cases for Garmin ShareMap position fetching"""

    def test_fetch_sharemap_position_with_valid_kml_response_returns_position(self):
        """Test that valid KML response returns correct position object"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <Point>
                <coordinates>-122.4194,37.7749,0</coordinates>
            </Point>
            <TimeStamp>
                <when>2024-01-15T10:30:00Z</when>
            </TimeStamp>
        </Placemark>
    </Document>
</kml>"""
        
        with patch('requests.get', return_value=mock_response):
            # Act
            result = fetch_sharemap_position("https://share.garmin.com/PDFCF")
            
            # Assert
            assert result is not None
            assert isinstance(result, CurrentPosition)
            assert result.latitude == 37.7749
            assert result.longitude == -122.4194
            assert result.source_url == "https://share.garmin.com/PDFCF"
            assert isinstance(result.timestamp, datetime)

    def test_fetch_sharemap_position_with_empty_data_returns_none(self):
        """Test that empty KML response returns None"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
    </Document>
</kml>"""
        
        with patch('requests.get', return_value=mock_response):
            # Act
            result = fetch_sharemap_position("https://share.garmin.com/PDFCF")
            
            # Assert
            assert result is None

    def test_fetch_sharemap_position_with_invalid_url_raises_request_exception(self):
        """Test that invalid URL raises RequestException"""
        # Arrange
        with patch('requests.get', side_effect=Exception("Connection failed")):
            # Act & Assert
            with pytest.raises(Exception):
                fetch_sharemap_position("https://invalid-url.com")

    def test_fetch_sharemap_position_with_invalid_kml_format_raises_value_error(self):
        """Test that invalid KML format raises ValueError"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Invalid XML content"
        
        with patch('requests.get', return_value=mock_response):
            # Act & Assert
            with pytest.raises(ValueError):
                fetch_sharemap_position("https://share.garmin.com/PDFCF")

    def test_fetch_sharemap_position_with_missing_coordinates_returns_none(self):
        """Test that KML without coordinates returns None"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <TimeStamp>
                <when>2024-01-15T10:30:00Z</when>
            </TimeStamp>
        </Placemark>
    </Document>
</kml>"""
        
        with patch('requests.get', return_value=mock_response):
            # Act
            result = fetch_sharemap_position("https://share.garmin.com/PDFCF")
            
            # Assert
            assert result is None 