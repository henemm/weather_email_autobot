#!/usr/bin/env python3
"""
Tests for SMS Polling Client.

This module tests the SMS polling functionality, including message filtering
and ID comparison logic.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.notification.sms_polling_client import SMSPollingClient


class TestSMSPollingClient:
    """Test cases for SMSPollingClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        self.last_id_file = os.path.join(self.temp_dir, "last_sms_id.txt")
        
        # Create a minimal config file
        with open(self.config_file, "w") as f:
            f.write("sms:\n  api_key: test_key\n")
        
        self.client = SMSPollingClient("test_key", self.config_file)
        self.client.last_id_file = self.last_id_file
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_filter_new_messages_with_numeric_ids(self):
        """Test filtering messages when last ID is numeric."""
        # Set last processed ID to a numeric value
        self.client.last_processed_id = "4795950"
        
        # Mock messages with numeric IDs
        messages = [
            {"id": "4795954", "text": "test message 1"},
            {"id": "4795976", "text": "test message 2"},
            {"id": "4795950", "text": "test message 3"},  # Same as last ID
            {"id": "4795949", "text": "test message 4"},  # Older than last ID
        ]
        
        filtered = self.client._filter_new_messages(messages)
        
        # Should only include messages with ID > 4795950
        expected_ids = ["4795954", "4795976"]
        actual_ids = [msg["id"] for msg in filtered]
        
        assert actual_ids == expected_ids
    
    def test_filter_new_messages_with_string_id(self):
        """Test filtering messages when last ID is a string (old format)."""
        # Set last processed ID to a string format (old buggy format)
        self.client.last_processed_id = "msg_789"
        
        # Mock messages with numeric IDs
        messages = [
            {"id": "4795954", "text": "test message 1"},
            {"id": "4795976", "text": "test message 2"},
        ]
        
        filtered = self.client._filter_new_messages(messages)
        
        # Should include all messages since string comparison would fail
        # This test documents the bug we're fixing
        expected_ids = ["4795954", "4795976"]
        actual_ids = [msg["id"] for msg in filtered]
        
        assert actual_ids == expected_ids
    
    def test_filter_new_messages_empty_last_id(self):
        """Test filtering messages when no last ID is set."""
        self.client.last_processed_id = ""
        
        messages = [
            {"id": "4795954", "text": "test message 1"},
            {"id": "4795976", "text": "test message 2"},
        ]
        
        filtered = self.client._filter_new_messages(messages)
        
        # Should include all messages when no last ID
        assert len(filtered) == 2
    
    def test_save_and_load_last_processed_id(self):
        """Test saving and loading the last processed ID."""
        test_id = "4795976"
        
        # Save ID
        self.client._save_last_processed_id(test_id)
        
        # Load ID
        loaded_id = self.client._load_last_processed_id()
        
        assert loaded_id == test_id
    
    def test_is_configuration_command(self):
        """Test configuration command detection."""
        # Valid configuration commands
        assert self.client._is_configuration_command("### sms.enabled: true")
        assert self.client._is_configuration_command("### min_interval_min: 90")
        assert self.client._is_configuration_command("  ### test: value  ")  # With whitespace
        
        # Invalid commands
        assert not self.client._is_configuration_command("sms.enabled: true")
        assert not self.client._is_configuration_command("###")  # No key-value
        assert not self.client._is_configuration_command("Hello world")
        assert not self.client._is_configuration_command("") 