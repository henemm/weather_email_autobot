"""
SMS client for sending GR20 weather reports via seven.io.

This module provides functionality to send weather reports via SMS
using the seven.io HTTP REST API with proper formatting and character limits.
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from src.notification.email_client import generate_gr20_report_text

logger = logging.getLogger(__name__)

class SMSClient:
    """
    SMS client for sending GR20 weather reports via seven.io.
    
    This class handles SMS configuration and sending with proper
    formatting for mobile devices using the seven.io API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SMS client.
        
        Args:
            config: Configuration dictionary with SMS settings
            
        Raises:
            ValueError: If SMS configuration is missing or invalid
        """
        if not config or "sms" not in config:
            raise ValueError("SMS configuration is required")
        
        sms_config = config["sms"]
        required_fields = ["api_key", "test_number", "production_number", "mode", "sender"]
        
        for field in required_fields:
            if field not in sms_config:
                raise ValueError(f"SMS configuration missing required field: {field}")
        
        # Validate mode
        mode = sms_config["mode"]
        if mode not in ["test", "production"]:
            raise ValueError("SMS mode must be 'test' or 'production'")
        
        self.enabled = sms_config.get("enabled", True)
        self.provider = sms_config.get("provider", "seven")
        self.api_key = sms_config["api_key"]
        self.mode = mode
        self.sender_name = sms_config["sender"]
        self.config = config  # Store full config for report generation
        
        # Set recipient number based on mode
        if mode == "test":
            self.recipient_number = sms_config["test_number"]
        else:
            self.recipient_number = sms_config["production_number"]
    
    def send_sms(self, message_text: str) -> bool:
        """
        Send an SMS with the given message.
        
        Args:
            message_text: The message text to send (max 160 characters)
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("SMS sending disabled")
            return False
        
        if not message_text or not message_text.strip():
            logger.warning("Empty message text provided")
            return False
        
        # Ensure message doesn't exceed 160 characters
        message_text = message_text.strip()
        if len(message_text) > 160:
            message_text = message_text[:160]
        
        logger.info(f"Sending SMS to {self.recipient_number}: {message_text[:50]}...")
        
        try:
            # Prepare the API request
            url = "https://gateway.seven.io/api/sms"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "to": self.recipient_number,
                "from": self.sender_name,
                "text": message_text
            }
            
            logger.debug(f"SMS API request: URL={url}, to={self.recipient_number}, from={self.sender_name}")
            
            # Send the SMS
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            logger.info(f"SMS API response: {response.status_code}")
            
            # Check if the request was successful
            if response.status_code == 200:
                logger.info("SMS sent successfully")
                return True
            else:
                logger.error(f"Failed to send SMS: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def send_gr20_report(self, report_data: Dict[str, Any]) -> bool:
        """
        Send a GR20 weather report SMS.
        
        Args:
            report_data: Dictionary containing report information:
                - location: Current location name
                - report_type: "morning", "evening", or "dynamic"
                - weather_data: Detailed weather data for formatting
                - report_time: Datetime of the report
                
        Returns:
            True if SMS sent successfully, False otherwise
        """
        logger.info("SMS send_gr20_report called")
        
        if not self.enabled:
            logger.info("SMS sending disabled")
            return False
        
        # Use the central report text generation for SMS
        message_text = generate_gr20_report_text(report_data, self.config)
        logger.info(f"Generated SMS text: {message_text}")
        
        # Send SMS
        return self.send_sms(message_text) 