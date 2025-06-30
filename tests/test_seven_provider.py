"""
Tests for the Seven.io SMS provider implementation.
"""

import pytest
from unittest.mock import Mock, patch
from src.notification.providers.seven_provider import SevenProvider


class TestSevenProvider:
    """Test cases for SevenProvider class."""
    
    def test_seven_provider_initialization(self):
        """Test SevenProvider initialization with valid config."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        provider = SevenProvider(config)
        
        assert provider.api_key == "test_api_key"
        assert provider.sender == "GR20-Info"
        assert provider.api_url == "https://gateway.seven.io/api/sms"
    
    def test_seven_provider_missing_config(self):
        """Test SevenProvider initialization with missing config."""
        with pytest.raises(ValueError, match="Seven.io configuration is required"):
            SevenProvider(None)
    
    def test_seven_provider_missing_api_key(self):
        """Test SevenProvider initialization with missing api_key."""
        config = {
            "from": "GR20-Info"
        }
        
        with pytest.raises(ValueError, match="Seven.io configuration missing required field: api_key"):
            SevenProvider(config)
    
    def test_seven_provider_missing_from(self):
        """Test SevenProvider initialization with missing from field."""
        config = {
            "api_key": "test_api_key"
        }
        
        with pytest.raises(ValueError, match="Seven.io configuration missing required field: from"):
            SevenProvider(config)
    
    def test_seven_provider_is_configured_true(self):
        """Test is_configured returns True with valid configuration."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        provider = SevenProvider(config)
        assert provider.is_configured() is True
    
    def test_seven_provider_is_configured_false_no_api_key(self):
        """Test is_configured returns False with missing api_key."""
        config = {
            "api_key": "",
            "from": "GR20-Info"
        }
        
        provider = SevenProvider(config)
        assert provider.is_configured() is False
    
    def test_seven_provider_is_configured_false_no_sender(self):
        """Test is_configured returns False with missing sender."""
        config = {
            "api_key": "test_api_key",
            "from": ""
        }
        
        provider = SevenProvider(config)
        assert provider.is_configured() is False
    
    @patch('src.notification.providers.seven_provider.requests.post')
    def test_send_sms_success(self, mock_post):
        """Test successful SMS sending."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        provider = SevenProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is True
        
        # Verify the API call
        mock_post.assert_called_once_with(
            "https://gateway.seven.io/api/sms",
            headers={"Authorization": "Bearer test_api_key"},
            data={
                "to": "+49123456789",
                "from": "GR20-Info",
                "text": "Test message"
            },
            timeout=30
        )
    
    @patch('src.notification.providers.seven_provider.requests.post')
    def test_send_sms_api_error(self, mock_post):
        """Test SMS sending with API error."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        provider = SevenProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is False
    
    @patch('src.notification.providers.seven_provider.requests.post')
    def test_send_sms_network_error(self, mock_post):
        """Test SMS sending with network error."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        # Mock network error
        mock_post.side_effect = Exception("Network error")
        
        provider = SevenProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is False
    
    def test_send_sms_not_configured(self):
        """Test SMS sending when provider is not configured."""
        config = {
            "api_key": "",
            "from": "GR20-Info"
        }
        
        provider = SevenProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is False
    
    def test_send_sms_empty_message(self):
        """Test SMS sending with empty message."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        provider = SevenProvider(config)
        result = provider.send_sms("+49123456789", "")
        
        assert result is False
    
    def test_send_sms_none_message(self):
        """Test SMS sending with None message."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        provider = SevenProvider(config)
        result = provider.send_sms("+49123456789", None)
        
        assert result is False
    
    def test_send_sms_message_truncation(self):
        """Test that long messages are truncated to 160 characters."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        # Create a message longer than 160 characters
        long_message = "A" * 200
        
        with patch('src.notification.providers.seven_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            provider = SevenProvider(config)
            result = provider.send_sms("+49123456789", long_message)
            
            assert result is True
            
            # Verify the message was truncated
            call_args = mock_post.call_args
            data = call_args[1]['data']
            assert len(data['text']) == 160
            assert data['text'] == "A" * 160 