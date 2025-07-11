"""
SMS Polling Client.

This module provides functionality to poll incoming SMS messages
from seven.io API and process configuration commands.
"""

import requests
import logging
import time
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..config.sms_config_processor import SMSConfigProcessor
import os

logger = logging.getLogger(__name__)


class SMSPollingClient:
    """
    Client for polling incoming SMS messages from seven.io API.
    
    This class fetches incoming SMS messages from seven.io and processes
    configuration commands without requiring a webhook server.
    """
    
    def __init__(self, api_key: str, config_file_path: str = "config.yaml"):
        """
        Initialize the SMS polling client.
        
        Args:
            api_key: Seven.io API key
            config_file_path: Path to the configuration file to update
        """
        self.api_key = api_key
        self.api_url = "https://gateway.seven.io/api/sms/inbox"
        self.config_processor = SMSConfigProcessor(config_file_path)
        self.processed_messages = set()  # Track processed message IDs (in-memory)
        self.last_id_file = "data/last_sms_id.txt"
        self.last_processed_id = self._load_last_processed_id()
        logger.info("SMS Polling Client initialized")
    
    def _load_last_processed_id(self) -> str:
        try:
            if os.path.exists(self.last_id_file):
                with open(self.last_id_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read last processed SMS ID: {e}")
        return ""

    def _save_last_processed_id(self, last_id: str):
        try:
            os.makedirs(os.path.dirname(self.last_id_file), exist_ok=True)
            with open(self.last_id_file, "w", encoding="utf-8") as f:
                f.write(str(last_id))
        except Exception as e:
            logger.warning(f"Could not save last processed SMS ID: {e}")

    def poll_incoming_sms(self) -> Dict[str, Any]:
        """
        Poll for incoming SMS messages and process configuration commands.
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if polling was successful
                - messages_found: Number of messages found
                - commands_processed: Number of configuration commands processed
                - message: Human-readable message about the result
        """
        try:
            logger.debug("Polling for incoming SMS messages...")
            
            # Fetch incoming messages from seven.io
            messages = self._fetch_incoming_messages()
            if not messages:
                return {
                    "success": True,
                    "messages_found": 0,
                    "commands_processed": 0,
                    "message": "No new messages found"
                }
            
            logger.info(f"Found {len(messages)} incoming message(s)")
            
            # Filter messages by last processed ID
            filtered = self._filter_new_messages(messages)
            logger.info(f"Processing {len(filtered)} new message(s) since last ID {self.last_processed_id}")
            
            # Process each message
            commands_processed = 0
            max_id = None
            for message in filtered:
                if self._process_message(message):
                    commands_processed += 1
                # Track max ID (only for numeric IDs)
                msg_id = str(message.get("id", ""))
                if msg_id.isdigit():
                    if max_id is None or int(msg_id) > int(max_id):
                        max_id = msg_id
            # Save last processed ID
            if filtered and max_id:
                self._save_last_processed_id(max_id)
                self.last_processed_id = max_id
            return {
                "success": True,
                "messages_found": len(messages),
                "commands_processed": commands_processed,
                "message": f"Processed {commands_processed} configuration command(s) from {len(filtered)} new message(s)"
            }
            
        except Exception as e:
            logger.error(f"Error polling incoming SMS: {e}")
            return {
                "success": False,
                "messages_found": 0,
                "commands_processed": 0,
                "message": f"Error polling SMS: {str(e)}"
            }
    
    def _fetch_incoming_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch incoming SMS messages from seven.io API (journal/inbound).
        
        Returns:
            List of message dictionaries
        """
        api_url = "https://gateway.seven.io/api/journal/inbound"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            logger.debug(f"Seven.io API response status: {response.status_code}")
            logger.debug(f"Seven.io API response text: {response.text}")
            try:
                data = response.json()
                logger.debug(f"Seven.io API response JSON: {data}")
            except Exception as e:
                logger.warning(f"Could not parse JSON from Seven.io API response: {e}")
                data = response.text
            # Expecting a list of messages
            if isinstance(data, list):
                messages = data
            elif isinstance(data, dict) and "data" in data:
                messages = data["data"]
            else:
                logger.warning(f"Unexpected response format from seven.io: {type(data)}")
                messages = []
            logger.debug(f"Fetched {len(messages)} inbound messages from seven.io")
            return messages
        except Exception as e:
            logger.error(f"Error fetching inbound messages from seven.io: {e}")
            return []
    
    def _filter_new_messages(self, messages):
        """
        Filter messages to only those with ID greater than the last processed ID.
        Handles both numeric and legacy string IDs.
        If last_processed_id is not numeric, all messages are considered new.
        Args:
            messages: List of message dicts with 'id' field
        Returns:
            List of new message dicts
        """
        if not self.last_processed_id:
            return messages
        # If last_processed_id is not numeric, treat as no last ID (process all)
        if not str(self.last_processed_id).isdigit():
            return messages
        filtered = [m for m in messages if str(m.get("id", "")).isdigit() and int(m["id"]) > int(self.last_processed_id)]
        return filtered

    def _process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a single SMS message.
        
        Args:
            message: Message dictionary from seven.io API
            
        Returns:
            True if a configuration command was processed, False otherwise
        """
        try:
            # Extract message details
            message_id = message.get("id")
            message_text = message.get("text", "")
            sender = message.get("from", "")
            timestamp = message.get("timestamp", "")
            
            # Skip if already processed
            if message_id in self.processed_messages:
                logger.debug(f"Message {message_id} already processed, skipping")
                return False
            
            # Log message reception
            self._log_message_reception(sender, message_text)
            
            # Check if it's a report mode command
            if self._is_report_mode_command(message_text):
                # Process report mode command
                result = self._process_report_mode_command(message_text)
                
                if result["success"]:
                    logger.info(f"Report mode command processed successfully: {result['mode']}")
                else:
                    logger.warning(f"Report mode command failed: {result['message']}")
                
                # Mark as processed
                self.processed_messages.add(message_id)
                return True
            
            # Check if it's a configuration command
            elif self._is_configuration_command(message_text):
                # Process configuration command
                result = self.config_processor.process_sms_command(message_text)
                
                if result["success"]:
                    logger.info(f"Configuration command processed successfully: {result['key']} = {result['value']}")
                else:
                    logger.warning(f"Configuration command failed: {result['message']}")
                
                # Mark as processed
                self.processed_messages.add(message_id)
                return True
            else:
                # Non-configuration message
                logger.debug(f"Non-configuration message received from {sender}")
                self.processed_messages.add(message_id)
                return False
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    def _is_configuration_command(self, message_text: str) -> bool:
        """
        Check if a message is a configuration command.
        
        Args:
            message_text: The message text to check
            
        Returns:
            True if the message is a configuration command
        """
        return message_text.strip().startswith("### ")
    
    def _is_report_mode_command(self, message_text: str) -> bool:
        """
        Check if a message is a report mode command.
        
        Args:
            message_text: The message text to check
            
        Returns:
            True if the message is a report mode command
        """
        return message_text.strip().startswith("### report.modus:")
    
    def _process_report_mode_command(self, message_text: str) -> Dict[str, Any]:
        """
        Process a report mode command and trigger the weather report.
        
        Args:
            message_text: The message text to process
            
        Returns:
            Dictionary containing:
                - success: Boolean indicating if command was processed successfully
                - mode: The report mode that was triggered (if successful)
                - message: Human-readable message about the result
        """
        try:
            # Extract mode from command
            command_part = message_text[4:].strip()  # Remove "### "
            
            if ":" not in command_part:
                return {
                    "success": False,
                    "mode": None,
                    "message": "INVALID FORMAT: Missing colon separator"
                }
            
            key, value = command_part.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            if key != "report.modus":
                return {
                    "success": False,
                    "mode": None,
                    "message": f"INVALID COMMAND: Expected 'report.modus', got '{key}'"
                }
            
            if not value:
                return {
                    "success": False,
                    "mode": None,
                    "message": "INVALID FORMAT: Empty mode value"
                }
            
            # Validate mode
            valid_modes = ["morning", "evening", "dynamic"]
            if value not in valid_modes:
                return {
                    "success": False,
                    "mode": None,
                    "message": f"INVALID MODE: Must be one of {valid_modes}"
                }
            
            # Trigger the weather report
            logger.info(f"Triggering weather report in {value} mode")
            success = self._trigger_weather_report(value)
            
            if success:
                return {
                    "success": True,
                    "mode": value,
                    "message": f"Weather report triggered in {value} mode"
                }
            else:
                return {
                    "success": False,
                    "mode": None,
                    "message": "Failed to trigger weather report"
                }
                
        except Exception as e:
            logger.error(f"Error processing report mode command '{message_text}': {e}")
            return {
                "success": False,
                "mode": None,
                "message": f"Error processing command: {str(e)}"
            }
    
    def _trigger_weather_report(self, mode: str) -> bool:
        """
        Trigger the weather report script with the specified mode.
        
        Args:
            mode: The report mode (morning, evening, dynamic)
            
        Returns:
            True if the script was triggered successfully, False otherwise
        """
        try:
            import subprocess
            import os
            
            # Get the script path
            script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'run_gr20_weather_monitor.py')
            
            # Build the command
            cmd = [sys.executable, script_path, "--modus", mode]
            
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            # Execute the script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Weather report in {mode} mode executed successfully")
                logger.debug(f"Script output: {result.stdout}")
                return True
            else:
                logger.error(f"Weather report script failed with return code {result.returncode}")
                logger.error(f"Script stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Weather report script timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"Error triggering weather report: {e}")
            return False
    
    def _log_message_reception(self, sender: str, message_text: str):
        """
        Log message reception.
        
        Args:
            sender: Sender phone number
            message_text: Message text
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | seven | {sender} | {message_text[:50]}..."
        
        # Write to log file
        try:
            with open("logs/sms_polling.log", "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            logger.error(f"Error writing to log file: {e}")
        
        logger.info(f"Received SMS from {sender}: {message_text[:50]}...")
    
    def cleanup_old_messages(self, max_age_hours: int = 24):
        """
        Clean up processed message IDs older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours to keep message IDs
        """
        # This is a simple implementation - in production you might want
        # to use a database or more sophisticated tracking
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        # For now, we'll just log the cleanup
        logger.info(f"Cleaning up message tracking (older than {max_age_hours} hours)")
        logger.debug(f"Current processed messages count: {len(self.processed_messages)}") 