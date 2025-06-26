"""
Tests for the SMS client functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.notification.sms_client import SMSClient
import os


class TestSMSClient:
    """Test cases for SMSClient class."""
    
    def test_sms_client_initialization(self):
        """Test SMSClient initialization with config."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        
        assert client.enabled is True
        assert client.provider == "seven"
        assert client.api_key == "test_api_key"
        assert client.recipient_number == "+49123456789"  # Should use test_number in test mode
        assert client.sender_name == "GR20-Info"
    
    def test_sms_client_production_mode(self):
        """Test SMSClient initialization in production mode."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "production",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        
        assert client.enabled is True
        assert client.recipient_number == "+49987654321"  # Should use production_number in production mode
        assert client.sender_name == "GR20-Info"
    
    def test_sms_client_disabled(self):
        """Test SMSClient initialization when SMS is disabled."""
        config = {
            "sms": {
                "enabled": False,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        
        assert client.enabled is False
    
    def test_sms_client_missing_config(self):
        """Test SMSClient initialization with missing config."""
        config = {}
        
        with pytest.raises(ValueError, match="SMS configuration is required"):
            SMSClient(config)
    
    def test_sms_client_missing_sms_section(self):
        """Test SMSClient initialization with missing SMS section."""
        config = {"other_section": {}}
        
        with pytest.raises(ValueError, match="SMS configuration is required"):
            SMSClient(config)
    
    def test_sms_client_missing_required_fields(self):
        """Test SMSClient initialization with missing required fields."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven"
                # Missing api_key, test_number, production_number, mode, sender
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: api_key"):
            SMSClient(config)
    
    def test_sms_client_missing_test_number(self):
        """Test SMSClient initialization with missing test_number field."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
                # Missing 'test_number'
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: test_number"):
            SMSClient(config)
    
    def test_sms_client_missing_production_number(self):
        """Test SMSClient initialization with missing production_number field."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "mode": "production",
                "sender": "GR20-Info"
                # Missing 'production_number'
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: production_number"):
            SMSClient(config)
    
    def test_sms_client_missing_mode(self):
        """Test SMSClient initialization with missing mode field."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "sender": "GR20-Info"
                # Missing 'mode'
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: mode"):
            SMSClient(config)
    
    def test_sms_client_invalid_mode(self):
        """Test SMSClient initialization with invalid mode."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "invalid_mode",
                "sender": "GR20-Info"
            }
        }
        
        with pytest.raises(ValueError, match="SMS mode must be 'test' or 'production'"):
            SMSClient(config)
    
    def test_sms_client_missing_sender_field(self):
        """Test SMSClient initialization with missing 'sender' field."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
                # Missing 'sender'
            }
        }
        
        with pytest.raises(ValueError, match="SMS configuration missing required field: sender"):
            SMSClient(config)
    
    @patch('src.notification.sms_client.requests.post')
    def test_send_sms_success(self, mock_post):
        """Test successful SMS sending."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "id": "12345"}
        mock_post.return_value = mock_response
        
        client = SMSClient(config)
        result = client.send_sms("Test message")
        
        assert result is True
        
        # Verify the API call
        mock_post.assert_called_once_with(
            "https://gateway.seven.io/api/sms",
            headers={"Authorization": "Bearer test_api_key"},
            data={
                "to": "+49123456789",  # Should use test_number
                "from": "GR20-Info",
                "text": "Test message"
            },
            timeout=30
        )
    
    @patch('src.notification.sms_client.requests.post')
    def test_send_sms_production_mode(self, mock_post):
        """Test SMS sending in production mode."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "production",
                "sender": "GR20-Info"
            }
        }
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "id": "12345"}
        mock_post.return_value = mock_response
        
        client = SMSClient(config)
        result = client.send_sms("Test message")
        
        assert result is True
        
        # Verify the API call uses production number
        mock_post.assert_called_once_with(
            "https://gateway.seven.io/api/sms",
            headers={"Authorization": "Bearer test_api_key"},
            data={
                "to": "+49987654321",  # Should use production_number
                "from": "GR20-Info",
                "text": "Test message"
            },
            timeout=30
        )
    
    @patch('src.notification.sms_client.requests.post')
    def test_send_sms_api_error(self, mock_post):
        """Test SMS sending with API error."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        client = SMSClient(config)
        result = client.send_sms("Test message")
        
        assert result is False
    
    @patch('src.notification.sms_client.requests.post')
    def test_send_sms_network_error(self, mock_post):
        """Test SMS sending with network error."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        # Mock network error
        mock_post.side_effect = Exception("Network error")
        
        client = SMSClient(config)
        result = client.send_sms("Test message")
        
        assert result is False
    
    def test_send_sms_when_disabled(self):
        """Test SMS sending when SMS is disabled."""
        config = {
            "sms": {
                "enabled": False,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        result = client.send_sms("Test message")
        
        assert result is False
    
    def test_send_gr20_report(self):
        """Test sending GR20 weather report via SMS."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        with patch.object(SMSClient, 'send_sms', return_value=True) as mock_send:
            client = SMSClient(config)
            
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
            mock_send.assert_called_once()
            
            # Check that the sent message contains expected content
            sent_message = mock_send.call_args[0][0]
            assert "Vizzavona" in sent_message
            assert "Gewitter" in sent_message
            assert "Regen" in sent_message
    
    def test_send_gr20_report_when_disabled(self):
        """Test sending GR20 report when SMS is disabled."""
        config = {
            "sms": {
                "enabled": False,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        
        report_data = {
            "location": "Vizzavona",
            "report_type": "morning",
            "weather_data": {},
            "report_time": datetime.now()
        }
        
        result = client.send_gr20_report(report_data)
        
        assert result is False
    
    @patch('src.notification.sms_client.requests.post')
    def test_send_sms_character_limit(self, mock_post):
        """Test SMS sending with message that exceeds character limit."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # Create a message that's too long (over 160 characters)
        long_message = "A" * 200
        
        client = SMSClient(config)
        result = client.send_sms(long_message)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verify the message was truncated
        call_args = mock_post.call_args
        sent_data = call_args[1]['data']
        sent_message = sent_data['text']
        assert len(sent_message) <= 160
        assert sent_message == "A" * 160  # Should be truncated to exactly 160 characters
    
    def test_send_sms_empty_message(self):
        """Test SMS sending with empty message."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        result = client.send_sms("")
        
        assert result is False
    
    def test_send_sms_none_message(self):
        """Test SMS sending with None message."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        result = client.send_sms(None)
        
        assert result is False


class TestSMSClientIntegration:
    """Integration tests for SMS client."""
    
    def test_sms_client_with_real_config_format(self):
        """Test SMSClient with configuration format matching the requirements."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "real_api_key_here",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        client = SMSClient(config)
        
        assert client.enabled is True
        assert client.provider == "seven"
        assert client.api_key == "real_api_key_here"
        assert client.recipient_number == "+49123456789"
        assert client.sender_name == "GR20-Info"
    
    def test_sms_client_api_url_format(self):
        """Test that the correct API URL is used."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        with patch('src.notification.sms_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_post.return_value = mock_response
            
            client = SMSClient(config)
            client.send_sms("Test")
            
            # Verify the correct API endpoint is called
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://gateway.seven.io/api/sms"
    
    def test_sms_client_headers_format(self):
        """Test that the correct headers are sent."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        with patch('src.notification.sms_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_post.return_value = mock_response
            
            client = SMSClient(config)
            client.send_sms("Test")
            
            # Verify the correct headers are sent
            call_args = mock_post.call_args
            headers = call_args[1]['headers']
            assert headers == {"Authorization": "Bearer test_api_key"}
    
    def test_sms_client_form_data_format(self):
        """Test that the correct form data is sent."""
        config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "api_key": "test_api_key",
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test",
                "sender": "GR20-Info"
            }
        }
        
        with patch('src.notification.sms_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_post.return_value = mock_response
            
            client = SMSClient(config)
            client.send_sms("Test message")
            
            # Verify the correct form data is sent
            call_args = mock_post.call_args
            data = call_args[1]['data']
            expected_data = {
                "to": "+49123456789",  # Should use test_number in test mode
                "from": "GR20-Info",
                "text": "Test message"
            }
            assert data == expected_data 