"""
Tests for SMS sending with automatic GSM-7 normalization.

This module tests the complete SMS sending workflow including
automatic normalization of non-GSM-7 characters.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from src.notification.modular_sms_client import ModularSmsClient


class TestSMSWithNormalization:
    """Test cases for SMS sending with automatic normalization."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_config = {
            "sms": {
                "enabled": True,
                "provider": "seven",
                "seven": {
                    "api_key": "test_api_key",
                    "sender": "GR20-Info"
                },
                "test_number": "+49123456789",
                "production_number": "+49987654321",
                "mode": "test"
            }
        }
        
        # Create temporary log directory
        self.temp_log_dir = tempfile.mkdtemp()
        self.original_log_dir = os.path.join("output", "logs")
    
    def teardown_method(self):
        """Clean up test environment."""
        # Clean up any test log files
        if os.path.exists(self.temp_log_dir):
            import shutil
            shutil.rmtree(self.temp_log_dir)
    
    @patch('src.notification.modular_sms_client.os.path.join')
    @patch('src.notification.modular_sms_client.os.makedirs')
    @patch('builtins.open', create=True)
    @patch('src.notification.providers.seven_provider.SevenProvider.send_sms')
    @patch('src.notification.providers.seven_provider.SevenProvider.is_configured')
    def test_sms_normalization_with_german_umlauts(self, mock_is_configured, mock_send_sms, 
                                                   mock_open, mock_makedirs, mock_path_join):
        """Test SMS sending with automatic normalization of German umlauts."""
        # Setup mocks
        mock_is_configured.return_value = True
        mock_send_sms.return_value = True
        mock_path_join.return_value = os.path.join(self.temp_log_dir, "sms_normalization.log")
        mock_open.return_value.__enter__ = Mock()
        mock_open.return_value.__exit__ = Mock()
        
        # Create client
        client = ModularSmsClient(self.test_config)
        
        # Test message with German umlauts
        message_with_umlauts = "Hören Sie zu: Wetterbericht mit Böen und Gewitter"
        
        # Send SMS
        result = client.send_sms(message_with_umlauts)
        
        # Verify SMS was sent successfully
        assert result is True
        mock_send_sms.assert_called_once()
        
        # Verify the normalized message was sent
        sent_message = mock_send_sms.call_args[0][1]  # Second argument is the message
        expected_normalized = "Horen Sie zu: Wetterbericht mit Boen und Gewitter"
        assert sent_message == expected_normalized
        
        # Verify normalization was logged
        mock_open.assert_called()
    
    @patch('src.notification.modular_sms_client.os.path.join')
    @patch('src.notification.modular_sms_client.os.makedirs')
    @patch('builtins.open', create=True)
    @patch('src.notification.providers.seven_provider.SevenProvider.send_sms')
    @patch('src.notification.providers.seven_provider.SevenProvider.is_configured')
    def test_sms_normalization_with_symbols_and_emojis(self, mock_is_configured, mock_send_sms,
                                                       mock_open, mock_makedirs, mock_path_join):
        """Test SMS sending with automatic normalization of symbols and emojis."""
        # Setup mocks
        mock_is_configured.return_value = True
        mock_send_sms.return_value = True
        mock_path_join.return_value = os.path.join(self.temp_log_dir, "sms_normalization.log")
        mock_open.return_value.__enter__ = Mock()
        mock_open.return_value.__exit__ = Mock()
        
        # Create client
        client = ModularSmsClient(self.test_config)
        
        # Test message with symbols and emojis
        message_with_symbols = "Temperature: 25°C, Wind → 15km/h, Gewitter ⚡ möglich"
        
        # Send SMS
        result = client.send_sms(message_with_symbols)
        
        # Verify SMS was sent successfully
        assert result is True
        mock_send_sms.assert_called_once()
        
        # Verify the normalized message was sent
        sent_message = mock_send_sms.call_args[0][1]
        expected_normalized = "Temperature: 25degC, Wind -> 15km/h, Gewitter  moglich"
        assert sent_message == expected_normalized
    
    @patch('src.notification.providers.seven_provider.SevenProvider.send_sms')
    @patch('src.notification.providers.seven_provider.SevenProvider.is_configured')
    def test_sms_no_normalization_needed(self, mock_is_configured, mock_send_sms):
        """Test SMS sending when no normalization is needed."""
        # Setup mocks
        mock_is_configured.return_value = True
        mock_send_sms.return_value = True
        
        # Create client
        client = ModularSmsClient(self.test_config)
        
        # Test message with only GSM-7 characters
        valid_message = "Hello World! This is a valid GSM-7 message with 123 numbers."
        
        # Send SMS
        result = client.send_sms(valid_message)
        
        # Verify SMS was sent successfully
        assert result is True
        mock_send_sms.assert_called_once()
        
        # Verify the original message was sent unchanged
        sent_message = mock_send_sms.call_args[0][1]
        assert sent_message == valid_message
    
    @patch('src.notification.providers.seven_provider.SevenProvider.send_sms')
    @patch('src.notification.providers.seven_provider.SevenProvider.is_configured')
    def test_sms_normalization_preserves_length_limit(self, mock_is_configured, mock_send_sms):
        """Test that normalization works correctly with character length limits."""
        # Setup mocks
        mock_is_configured.return_value = True
        mock_send_sms.return_value = True
        
        # Create client
        client = ModularSmsClient(self.test_config)
        
        # Test message that would exceed 160 chars after normalization
        long_message = "A" * 150 + "ö" * 20  # 170 characters total
        
        # Send SMS
        result = client.send_sms(long_message)
        
        # Verify SMS was sent successfully
        assert result is True
        mock_send_sms.assert_called_once()
        
        # Verify the message was normalized and truncated
        sent_message = mock_send_sms.call_args[0][1]
        assert len(sent_message) <= 160
        assert sent_message.endswith("...") or len(sent_message) == 160
    
    @patch('src.notification.providers.seven_provider.SevenProvider.is_configured')
    def test_sms_normalization_logging(self, mock_is_configured):
        """Test that normalization changes are properly logged."""
        # Setup mocks
        mock_is_configured.return_value = True
        
        # Create client
        client = ModularSmsClient(self.test_config)
        
        # Test message requiring normalization
        test_message = "Hören Sie zu: 25°C"
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_open.return_value.__exit__.return_value = None
            
            # Mock path operations
            with patch('src.notification.modular_sms_client.os.path.join') as mock_path_join:
                mock_path_join.return_value = os.path.join(self.temp_log_dir, "sms_normalization.log")
                
                with patch('src.notification.modular_sms_client.os.makedirs'):
                    with patch('src.notification.providers.seven_provider.SevenProvider.send_sms') as mock_send_sms:
                        mock_send_sms.return_value = True
                        
                        # Send SMS
                        result = client.send_sms(test_message)
                        
                        # Verify logging occurred
                        assert mock_open.called
                        assert mock_file.write.called
                        
                        # Verify log content contains normalization info
                        log_calls = mock_file.write.call_args_list
                        log_content = "".join([call[0][0] for call in log_calls])
                        assert "SMS text normalized to GSM-7" in log_content
                        assert "Horen Sie zu: 25degC" in log_content 