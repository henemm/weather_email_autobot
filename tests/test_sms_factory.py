"""
Tests for the SMS provider factory.
"""

import pytest
from src.notification.sms_factory import SmsProviderFactory
from src.notification.providers.seven_provider import SevenProvider
from src.notification.providers.twilio_provider import TwilioProvider


class TestSmsProviderFactory:
    """Test cases for SmsProviderFactory class."""
    
    def test_create_seven_provider(self):
        """Test creating a Seven.io provider."""
        config = {
            "api_key": "test_api_key",
            "from": "GR20-Info"
        }
        
        provider = SmsProviderFactory.create_provider("seven", config)
        
        assert isinstance(provider, SevenProvider)
        assert provider.api_key == "test_api_key"
        assert provider.sender == "GR20-Info"
    
    def test_create_twilio_provider(self):
        """Test creating a Twilio provider."""
        config = {
            "account_sid": "test_account_sid",
            "auth_token": "test_auth_token",
            "from": "+14151234567"
        }
        
        provider = SmsProviderFactory.create_provider("twilio", config)
        
        assert isinstance(provider, TwilioProvider)
        assert provider.account_sid == "test_account_sid"
        assert provider.auth_token == "test_auth_token"
        assert provider.sender == "+14151234567"
    
    def test_create_unsupported_provider(self):
        """Test creating an unsupported provider raises ValueError."""
        config = {"api_key": "test"}
        
        with pytest.raises(ValueError, match="Unsupported SMS provider: invalid_provider"):
            SmsProviderFactory.create_provider("invalid_provider", config)
    
    def test_get_supported_providers(self):
        """Test getting list of supported providers."""
        providers = SmsProviderFactory.get_supported_providers()
        
        assert isinstance(providers, list)
        assert "seven" in providers
        assert "twilio" in providers
        assert len(providers) == 2 