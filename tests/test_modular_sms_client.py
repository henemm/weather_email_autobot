"""
Tests for the modular SMS client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.notification.modular_sms_client import ModularSmsClient


class TestModularSmsClient:
    """Test cases for ModularSmsClient class."""
    
    def test_modular_sms_client_initialization_seven(self):
        """Test ModularSmsClient initialization with seven provider."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        client = ModularSmsClient(config)
        
        assert client.enabled is True
        assert client.provider_name == "seven"
        assert client.mode == "test"
        assert client.recipient_number == "+49123456789"
        assert client.provider is not None
    
    def test_modular_sms_client_initialization_twilio(self):
        """Test ModularSmsClient initialization with twilio provider."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "twilio",
                "account_sid": "test_account_sid",
                "auth_token": "test_auth_token",
                "from": "+14151234567",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "production"
            }
        }
        
        client = ModularSmsClient(config)
        
        assert client.enabled is True
        assert client.provider_name == "twilio"
        assert client.mode == "production"
        assert client.recipient_number == "+49987654321"
        assert client.provider is not None
    
    def test_modular_sms_client_missing_config(self):
        """Test ModularSmsClient initialization with missing config."""
        with pytest.raises(ValueError, match="SMS configuration is required"):
            ModularSmsClient(None)
    
    def test_modular_sms_client_missing_sms_config(self):
        """Test ModularSmsClient initialization with missing SMS config."""
        config = {}
        
        with pytest.raises(ValueError, match="SMS configuration is required"):
            ModularSmsClient(config)
    
    def test_modular_sms_client_missing_provider(self):
        """Test ModularSmsClient initialization with missing provider."""
        config = {
            "sms": {
                "enabled": True,
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: provider"):
            ModularSmsClient(config)
    
    def test_modular_sms_client_unsupported_provider(self):
        """Test ModularSmsClient initialization with unsupported provider."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "invalid_provider",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        with pytest.raises(ValueError, match="Unsupported SMS provider: invalid_provider"):
            ModularSmsClient(config)
    
    def test_modular_sms_client_invalid_mode(self):
        """Test ModularSmsClient initialization with invalid mode."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "invalid_mode"
            }
        }
        
        with pytest.raises(ValueError, match="SMS mode must be 'test' or 'production'"):
            ModularSmsClient(config)
    
    def test_modular_sms_client_missing_test_number(self):
        """Test ModularSmsClient initialization with missing test_number."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: test_number"):
            ModularSmsClient(config)
    
    def test_modular_sms_client_missing_production_number(self):
        """Test ModularSmsClient initialization with missing production_number."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "mode": "test"
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: production_number"):
            ModularSmsClient(config)
    
    def test_modular_sms_client_missing_mode(self):
        """Test ModularSmsClient initialization with missing mode."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321"
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: mode"):
            ModularSmsClient(config)
    
    def test_send_sms_when_disabled(self):
        """Test SMS sending when SMS is disabled."""
        config = {
            "sms": {
                "enabled": False,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        client = ModularSmsClient(config)
        result = client.send_sms("Test message")
        
        assert result is False
    
    def test_send_sms_provider_not_configured(self):
        """Test SMS sending when provider is not configured."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "",  # Empty API key
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        client = ModularSmsClient(config)
        result = client.send_sms("Test message")
        
        assert result is False
    
    def test_send_sms_empty_message(self):
        """Test SMS sending with empty message."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        client = ModularSmsClient(config)
        result = client.send_sms("")
        
        assert result is False
    
    def test_send_sms_none_message(self):
        """Test SMS sending with None message."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        client = ModularSmsClient(config)
        result = client.send_sms(None)
        
        assert result is False
    
    @patch('src.notification.sms_factory.SmsProviderFactory.create_provider')
    def test_send_sms_success(self, mock_create_provider):
        """Test successful SMS sending."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.is_configured.return_value = True
        mock_provider.send_sms.return_value = True
        mock_create_provider.return_value = mock_provider
        
        client = ModularSmsClient(config)
        result = client.send_sms("Test message")
        
        assert result is True
        mock_provider.send_sms.assert_called_once_with("+49123456789", "Test message")
    
    @patch('src.notification.sms_factory.SmsProviderFactory.create_provider')
    def test_send_sms_provider_failure(self, mock_create_provider):
        """Test SMS sending when provider fails."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.is_configured.return_value = True
        mock_provider.send_sms.return_value = False
        mock_create_provider.return_value = mock_provider
        
        client = ModularSmsClient(config)
        result = client.send_sms("Test message")
        
        assert result is False
    
    @patch('src.notification.sms_factory.SmsProviderFactory.create_provider')
    def test_send_sms_provider_exception(self, mock_create_provider):
        """Test SMS sending when provider raises exception."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.is_configured.return_value = True
        mock_provider.send_sms.side_effect = Exception("Provider error")
        mock_create_provider.return_value = mock_provider
        
        client = ModularSmsClient(config)
        result = client.send_sms("Test message")
        
        assert result is False
    
    @patch('src.notification.sms_factory.SmsProviderFactory.create_provider')
    def test_send_sms_message_truncation(self, mock_create_provider):
        """Test that long messages are truncated to 160 characters."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        # Create a message longer than 160 characters
        long_message = "A" * 200
        
        # Mock provider
        mock_provider = Mock()
        mock_provider.is_configured.return_value = True
        mock_provider.send_sms.return_value = True
        mock_create_provider.return_value = mock_provider
        
        client = ModularSmsClient(config)
        result = client.send_sms(long_message)
        
        assert result is True
        
        # Verify the message was truncated
        call_args = mock_provider.send_sms.call_args
        sent_message = call_args[0][1]  # Second argument is the message
        assert len(sent_message) == 160
        assert sent_message == "A" * 160
    
    def test_send_gr20_report_when_disabled(self):
        """Test sending GR20 report when SMS is disabled."""
        config = {
            "sms": {
                "enabled": False,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        client = ModularSmsClient(config)
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {},
            "report_time": datetime.now()
        }
        
        result = client.send_gr20_report(report_data)
        
        assert result is False
    
    @patch('src.notification.modular_sms_client.generate_gr20_report_text')
    @patch('src.notification.sms_factory.SmsProviderFactory.create_provider')
    def test_send_gr20_report_success(self, mock_create_provider, mock_generate_text):
        """Test successful GR20 report sending."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "sender": "GR20-Info",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        # Mock dependencies
        mock_generate_text.return_value = "Generated report text"
        mock_provider = Mock()
        mock_provider.is_configured.return_value = True
        mock_provider.send_sms.return_value = True
        mock_create_provider.return_value = mock_provider
        
        client = ModularSmsClient(config)
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {
                "max_thunderstorm_probability": 45,
                "max_precipitation_probability": 30,
                "max_temperature": 25.5,
                "max_wind_speed": 15
            },
            "report_time": datetime.now()
        }
        
        result = client.send_gr20_report(report_data)
        
        assert result is True
        mock_generate_text.assert_called_once_with(report_data, config)
        mock_provider.send_sms.assert_called_once_with("+49123456789", "Generated report text") 