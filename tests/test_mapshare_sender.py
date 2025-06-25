import pytest
from unittest.mock import Mock, patch
from src.mapshare_sender.send_mapshare_message import (
    send_mapshare_message,
    MapShareSender,
    MapShareConfig,
    MapShareResult
)
import requests

@pytest.fixture
def basic_config():
    """Provides a basic MapShareConfig for tests."""
    return MapShareConfig(
        ext_id="test-ext-id",
        adr="test@example.com",
        message_text="Test message"
    )

class TestMapShareSender:
    """Test the MapShare sender functionality."""
    
    def test_sender_initialization(self, basic_config):
        """Test sender initialization with config."""
        sender = MapShareSender(basic_config)
        assert sender.config == basic_config
        assert sender.url == "https://share.garmin.com/textmessage/txtmsg"

    def test_prepare_request_data(self, basic_config):
        """Test request data preparation."""
        sender = MapShareSender(basic_config)
        data = sender._prepare_request_data()
        expected_data = {
            "extId": "test-ext-id",
            "adr": "test@example.com",
            "txt": "Test message"
        }
        assert data == expected_data

    def test_prepare_headers(self, basic_config):
        """Test headers preparation."""
        sender = MapShareSender(basic_config)
        headers = sender._prepare_headers()
        assert "User-Agent" in headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/x-www-form-urlencoded"

    @patch('requests.post')
    def test_send_message_success(self, mock_post, basic_config):
        """Test successful message sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response

        sender = MapShareSender(basic_config)
        result = sender.send_message()

        assert result.success is True
        assert result.status_code == 200
        mock_post.assert_called_once_with(
            sender.url,
            data=sender._prepare_request_data(),
            headers=sender._prepare_headers(),
            timeout=30
        )

    @patch('requests.post')
    def test_send_message_http_error(self, mock_post, basic_config):
        """Test handling of HTTP error responses."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_post.return_value = mock_response

        sender = MapShareSender(basic_config)
        result = sender.send_message()

        assert result.success is False
        assert result.status_code == 500

    @patch('requests.post')
    def test_send_message_retries_on_timeout(self, mock_post, basic_config):
        """Test that the sender retries on a timeout."""
        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout"),
            requests.exceptions.Timeout("Timeout"),
            Mock(status_code=200, text="Success")
        ]

        sender = MapShareSender(basic_config)
        result = sender.send_message()
        
        assert result.success is True
        assert mock_post.call_count == 3

    @patch('requests.post')
    def test_send_message_fails_after_all_retries(self, mock_post, basic_config):
        """Test that the sender fails after all retries are exhausted."""
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")
        
        sender = MapShareSender(basic_config)
        result = sender.send_message()
        
        assert result.success is False
        assert result.status_code is None
        assert "Request failed" in result.response_text
        assert mock_post.call_count == 3


class TestSendMapShareMessageFunction:
    """Tests the main `send_mapshare_message` function."""

    @patch('src.mapshare_sender.send_mapshare_message.MapShareSender.send_message')
    def test_main_function_call_success(self, mock_send):
        """Test that the main function returns a success result."""
        mock_send.return_value = MapShareResult(success=True, status_code=200, response_text="Success")
        
        result = send_mapshare_message("ext-id", "adr", "text")
        
        assert result.success is True
        mock_send.assert_called_once() 