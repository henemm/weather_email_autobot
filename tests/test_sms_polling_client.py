"""
Tests for SMS polling client.

This module tests the functionality to poll incoming SMS messages
from seven.io API and process configuration commands.
"""

import pytest
import json
from unittest.mock import patch, Mock
from src.notification.sms_polling_client import SMSPollingClient


class TestSMSPollingClient:
    """Test cases for SMS polling client."""

    def test_sms_polling_client_initialization(self):
        """Test SMSPollingClient initialization."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        assert client.api_key == "test_api_key"
        assert client.api_url == "https://gateway.seven.io/api/sms/inbox"
        assert client.processed_messages == set()

    def test_poll_incoming_sms_no_messages(self):
        """Test polling when no messages are found."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = []
            
            result = client.poll_incoming_sms()
            
            assert result["success"] is True
            assert result["messages_found"] == 0
            assert result["commands_processed"] == 0
            assert result["message"] == "No new messages found"

    def test_poll_incoming_sms_with_configuration_command(self):
        """Test polling with a configuration command."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        # Mock incoming message
        messages = [
            {
                "id": "msg_123",
                "text": "### thresholds.temperature: 25.0",
                "from": "+49987654321",
                "timestamp": "2025-01-27T10:30:00Z"
            }
        ]
        
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = messages
            
            with patch.object(client, 'config_processor') as mock_processor:
                mock_processor.process_sms_command.return_value = {
                    "success": True,
                    "key": "thresholds.temperature",
                    "value": 25.0,
                    "message": "Configuration updated successfully"
                }
                
                result = client.poll_incoming_sms()
                
                assert result["success"] is True
                assert result["messages_found"] == 1
                assert result["commands_processed"] == 1
                assert "Processed 1 configuration command" in result["message"]
                assert "msg_123" in client.processed_messages

    def test_poll_incoming_sms_with_non_config_message(self):
        """Test polling with a non-configuration message."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        messages = [
            {
                "id": "msg_456",
                "text": "Hello, this is a regular message",
                "from": "+49987654321",
                "timestamp": "2025-01-27T10:30:00Z"
            }
        ]
        
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = messages
            
            result = client.poll_incoming_sms()
            
            assert result["success"] is True
            assert result["messages_found"] == 1
            assert result["commands_processed"] == 0
            assert "Processed 0 configuration command" in result["message"]
            assert "msg_456" in client.processed_messages

    def test_poll_incoming_sms_with_invalid_command(self):
        """Test polling with an invalid configuration command."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        messages = [
            {
                "id": "msg_789",
                "text": "### invalid.key: value",
                "from": "+49987654321",
                "timestamp": "2025-01-27T10:30:00Z"
            }
        ]
        
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = messages
            
            with patch.object(client, 'config_processor') as mock_processor:
                mock_processor.process_sms_command.return_value = {
                    "success": False,
                    "key": None,
                    "value": None,
                    "message": "INVALID FORMAT: Key 'invalid.key' not in whitelist"
                }
                
                result = client.poll_incoming_sms()
                
                assert result["success"] is True
                assert result["messages_found"] == 1
                assert result["commands_processed"] == 1  # Still counts as processed
                assert "msg_789" in client.processed_messages

    def test_poll_incoming_sms_skip_already_processed(self):
        """Test that already processed messages are skipped."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        client.processed_messages.add("msg_123")
        
        messages = [
            {
                "id": "msg_123",
                "text": "### thresholds.temperature: 25.0",
                "from": "+49987654321",
                "timestamp": "2025-01-27T10:30:00Z"
            }
        ]
        
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = messages
            
            result = client.poll_incoming_sms()
            
            assert result["success"] is True
            assert result["messages_found"] == 1
            assert result["commands_processed"] == 0
            assert "Processed 0 configuration command" in result["message"]

    def test_fetch_incoming_messages_success(self):
        """Test successful fetching of incoming messages."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": "msg_123",
                    "text": "### thresholds.temperature: 25.0",
                    "from": "+49987654321",
                    "timestamp": "2025-01-27T10:30:00Z"
                }
            ]
        }
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            messages = client._fetch_incoming_messages()
            
            assert len(messages) == 1
            assert messages[0]["id"] == "msg_123"
            mock_get.assert_called_once_with(
                client.api_url,
                headers={"Authorization": "Bearer test_api_key"},
                timeout=30
            )

    def test_fetch_incoming_messages_api_error(self):
        """Test handling of API errors when fetching messages."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch('requests.get', return_value=mock_response):
            messages = client._fetch_incoming_messages()
            
            assert messages == []

    def test_fetch_incoming_messages_network_error(self):
        """Test handling of network errors when fetching messages."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        with patch('requests.get', side_effect=Exception("Network error")):
            messages = client._fetch_incoming_messages()
            
            assert messages == []

    def test_is_configuration_command_valid(self):
        """Test identification of valid configuration commands."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        assert client._is_configuration_command("### thresholds.temperature: 25.0") is True
        assert client._is_configuration_command("### max_daily_reports: 5") is True
        assert client._is_configuration_command("### startdatum: 2025-07-08") is True

    def test_is_configuration_command_invalid(self):
        """Test identification of invalid configuration commands."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        assert client._is_configuration_command("Hello world") is False
        assert client._is_configuration_command("thresholds.temperature: 25.0") is False
        assert client._is_configuration_command("###") is False
        assert client._is_configuration_command("") is False

    def test_process_message_success(self):
        """Test successful processing of a message."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        message = {
            "id": "msg_123",
            "text": "### thresholds.temperature: 25.0",
            "from": "+49987654321",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        with patch.object(client, 'config_processor') as mock_processor:
            mock_processor.process_sms_command.return_value = {
                "success": True,
                "key": "thresholds.temperature",
                "value": 25.0,
                "message": "Configuration updated successfully"
            }
            
            with patch.object(client, '_log_message_reception') as mock_log:
                result = client._process_message(message)
                
                assert result is True
                assert "msg_123" in client.processed_messages
                mock_log.assert_called_once_with("+49987654321", "### thresholds.temperature: 25.0")

    def test_process_message_non_config(self):
        """Test processing of a non-configuration message."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        message = {
            "id": "msg_456",
            "text": "Hello, this is a regular message",
            "from": "+49987654321",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        with patch.object(client, '_log_message_reception') as mock_log:
            result = client._process_message(message)
            
            assert result is False
            assert "msg_456" in client.processed_messages
            mock_log.assert_called_once_with("+49987654321", "Hello, this is a regular message")

    def test_process_message_already_processed(self):
        """Test processing of an already processed message."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        client.processed_messages.add("msg_123")
        
        message = {
            "id": "msg_123",
            "text": "### thresholds.temperature: 25.0",
            "from": "+49987654321",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        result = client._process_message(message)
        
        assert result is False

    def test_cleanup_old_messages(self):
        """Test cleanup of old processed messages."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        client.processed_messages.add("msg_123")
        client.processed_messages.add("msg_456")
        
        with patch('time.time', return_value=1000000):
            client.cleanup_old_messages(max_age_hours=24)
            
            # Note: Current implementation just logs, doesn't actually clean up
            # This test verifies the method doesn't crash
            assert len(client.processed_messages) == 2


class TestSMSPollingClientIntegration:
    """Integration tests for SMS polling client."""

    def test_full_polling_workflow(self):
        """Test complete workflow of polling and processing messages."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        # Mock multiple messages
        messages = [
            {
                "id": "msg_1",
                "text": "### thresholds.temperature: 25.0",
                "from": "+49987654321",
                "timestamp": "2025-01-27T10:30:00Z"
            },
            {
                "id": "msg_2",
                "text": "Hello, regular message",
                "from": "+49987654322",
                "timestamp": "2025-01-27T10:31:00Z"
            },
            {
                "id": "msg_3",
                "text": "### max_daily_reports: 5",
                "from": "+49987654323",
                "timestamp": "2025-01-27T10:32:00Z"
            }
        ]
        
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = messages
            
            with patch.object(client, 'config_processor') as mock_processor:
                mock_processor.process_sms_command.side_effect = [
                    {
                        "success": True,
                        "key": "thresholds.temperature",
                        "value": 25.0,
                        "message": "Configuration updated successfully"
                    },
                    {
                        "success": True,
                        "key": "max_daily_reports",
                        "value": 5,
                        "message": "Configuration updated successfully"
                    }
                ]
                
                result = client.poll_incoming_sms()
                
                assert result["success"] is True
                assert result["messages_found"] == 3
                assert result["commands_processed"] == 2
                assert "msg_1" in client.processed_messages
                assert "msg_2" in client.processed_messages
                assert "msg_3" in client.processed_messages
                assert mock_processor.process_sms_command.call_count == 2

    def test_polling_with_error_handling(self):
        """Test polling with error handling."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        with patch.object(client, '_fetch_incoming_messages', side_effect=Exception("API Error")):
            result = client.poll_incoming_sms()
            
            assert result["success"] is False
            assert result["messages_found"] == 0
            assert result["commands_processed"] == 0
            assert "Error polling SMS" in result["message"]

    def test_multiple_polling_sessions(self):
        """Test multiple polling sessions with message deduplication."""
        client = SMSPollingClient("test_api_key", "config.yaml")
        
        # First polling session
        messages_1 = [
            {
                "id": "msg_1",
                "text": "### thresholds.temperature: 25.0",
                "from": "+49987654321",
                "timestamp": "2025-01-27T10:30:00Z"
            }
        ]
        
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = messages_1
            
            with patch.object(client, 'config_processor') as mock_processor:
                mock_processor.process_sms_command.return_value = {
                    "success": True,
                    "key": "thresholds.temperature",
                    "value": 25.0,
                    "message": "Configuration updated successfully"
                }
                
                result_1 = client.poll_incoming_sms()
                assert result_1["commands_processed"] == 1
                assert "msg_1" in client.processed_messages
        
        # Second polling session (same message should be skipped)
        with patch.object(client, '_fetch_incoming_messages') as mock_fetch:
            mock_fetch.return_value = messages_1
            
            result_2 = client.poll_incoming_sms()
            assert result_2["commands_processed"] == 0 