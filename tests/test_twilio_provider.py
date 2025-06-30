"""
Tests for the Twilio SMS provider implementation.
"""

import pytest
from unittest.mock import Mock, patch
from src.notification.providers.twilio_provider import TwilioProvider


class TestTwilioProvider:
    """Test cases for TwilioProvider class."""
    
    def test_twilio_provider_initialization(self):
        """Test TwilioProvider initialization with valid config."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        provider = TwilioProvider(config)
        
        assert provider.account_sid == "test_account_sid"
        assert provider.auth_token == "test_auth_token"
        assert provider.sender == "+14151234567"
        assert provider.api_url == "https://api.twilio.com/2010-04-01/Accounts/test_account_sid/Messages.json"
    
    def test_twilio_provider_missing_config(self):
        """Test TwilioProvider initialization with missing config."""
        with pytest.raises(ValueError, match="Twilio configuration is required"):
            TwilioProvider(None)
    
    def test_twilio_provider_missing_account_sid(self):
        """Test TwilioProvider initialization with missing account_sid."""
        config = {
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        with pytest.raises(ValueError, match="Twilio configuration missing required field: account_sid"):
            TwilioProvider(config)
    
    def test_twilio_provider_missing_auth_token(self):
        """Test TwilioProvider initialization with missing auth_token."""
        config = {
            "account_sid": "test_account_sid",
            "from": "+14151234567"
        }
        
        with pytest.raises(ValueError, match="Twilio configuration missing required field: auth_token"):
            TwilioProvider(config)
    
    def test_twilio_provider_missing_from(self):
        """Test TwilioProvider initialization with missing from field."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token"
        }
        
        with pytest.raises(ValueError, match="Twilio configuration missing required field: from"):
            TwilioProvider(config)
    
    def test_twilio_provider_is_configured_true(self):
        """Test is_configured returns True with valid configuration."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        provider = TwilioProvider(config)
        assert provider.is_configured() is True
    
    def test_twilio_provider_is_configured_false_no_account_sid(self):
        """Test is_configured returns False with missing account_sid."""
        config = {
            "account_sid": "",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        provider = TwilioProvider(config)
        assert provider.is_configured() is False
    
    def test_twilio_provider_is_configured_false_no_auth_token(self):
        """Test is_configured returns False with missing auth_token."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "",
            "from": "+14151234567"
        }
        
        provider = TwilioProvider(config)
        assert provider.is_configured() is False
    
    def test_twilio_provider_is_configured_false_no_sender(self):
        """Test is_configured returns False with missing sender."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": ""
        }
        
        provider = TwilioProvider(config)
        assert provider.is_configured() is False
    
    @patch('src.notification.providers.twilio_provider.requests.post')
    def test_send_sms_success(self, mock_post):
        """Test successful SMS sending."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        provider = TwilioProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is True
        
        # Verify the API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL
        assert call_args[0][0] == "https://api.twilio.com/2010-04-01/Accounts/test_account_sid/Messages.json"
        
        # Check headers
        headers = call_args[1]['headers']
        assert headers['Content-Type'] == "application/x-www-form-urlencoded"
        assert headers['Authorization'].startswith("Basic ")
        
        # Check data
        data = call_args[1]['data']
        assert data['To'] == "+49123456789"
        assert data['From'] == "+14151234567"
        assert data['Body'] == "Test message"
    
    @patch('src.notification.providers.twilio_provider.requests.post')
    def test_send_sms_api_error(self, mock_post):
        """Test SMS sending with API error."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        provider = TwilioProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is False
    
    @patch('src.notification.providers.twilio_provider.requests.post')
    def test_send_sms_network_error(self, mock_post):
        """Test SMS sending with network error."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        # Mock network error
        mock_post.side_effect = Exception("Network error")
        
        provider = TwilioProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is False
    
    def test_send_sms_not_configured(self):
        """Test SMS sending when provider is not configured."""
        config = {
            "account_sid": "",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        provider = TwilioProvider(config)
        result = provider.send_sms("+49123456789", "Test message")
        
        assert result is False
    
    def test_send_sms_empty_message(self):
        """Test SMS sending with empty message."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        provider = TwilioProvider(config)
        result = provider.send_sms("+49123456789", "")
        
        assert result is False
    
    def test_send_sms_none_message(self):
        """Test SMS sending with None message."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        provider = TwilioProvider(config)
        result = provider.send_sms("+49123456789", None)
        
        assert result is False
    
    def test_send_sms_message_truncation(self):
        """Test that long messages are truncated to 160 characters."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        # Create a message longer than 160 characters
        long_message = "A" * 200
        
        with patch('src.notification.providers.twilio_provider.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_post.return_value = mock_response
            
            provider = TwilioProvider(config)
            result = provider.send_sms("+49123456789", long_message)
            
            assert result is True
            
            # Verify the message was truncated
            call_args = mock_post.call_args
            data = call_args[1]['data']
            assert len(data['Body']) == 160
            assert data['Body'] == "A" * 160 