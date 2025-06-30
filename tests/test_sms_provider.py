"""
Tests for the abstract SMS provider base class.
"""

import pytest
from abc import ABC
from src.notification.sms_provider import SmsProvider


class TestSmsProvider:
    """Test cases for SmsProvider abstract base class."""
    
    def test_sms_provider_is_abstract(self):
        """Test that SmsProvider is an abstract base class."""
        assert issubclass(SmsProvider, ABC)
    
    def test_sms_provider_has_send_sms_method(self):
        """Test that SmsProvider has the required send_sms method."""
        assert hasattr(SmsProvider, 'send_sms')
        assert callable(SmsProvider.send_sms)
    
    def test_sms_provider_has_is_configured_method(self):
        """Test that SmsProvider has the required is_configured method."""
        assert hasattr(SmsProvider, 'is_configured')
        assert callable(SmsProvider.is_configured)
    
    def test_sms_provider_methods_are_abstract(self):
        """Test that the required methods are abstract."""
        # Check if methods are abstract by trying to instantiate the class
        with pytest.raises(TypeError):
            SmsProvider() 