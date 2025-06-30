"""
Seven.io SMS provider implementation.

This module provides the concrete implementation for sending SMS
via the seven.io HTTP REST API.
"""

import requests
import logging
from typing import Dict, Any
from ..sms_provider import SmsProvider

logger = logging.getLogger(__name__)


class SevenProvider(SmsProvider):
    """
    Seven.io SMS provider implementation.
    
    This class handles SMS sending via the seven.io HTTP REST API
    with proper authentication and error handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Seven.io SMS provider.
        
        Args:
            config: Configuration dictionary containing seven.io settings:
                - api_key: Seven.io API key
                - from: Sender phone number or name
                
        Raises:
            ValueError: If required configuration is missing
        """
        if not config:
            raise ValueError("Seven.io configuration is required")
        
        required_fields = ["api_key", "from"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Seven.io configuration missing required field: {field}")
        
        self.api_key = config["api_key"]
        self.sender = config["from"]
        self.api_url = "https://gateway.seven.io/api/sms"
        
        logger.info("Seven.io SMS provider initialized")
    
    def send_sms(self, to: str, message: str) -> bool:
        """
        Send an SMS via seven.io API.
        
        Args:
            to: Recipient phone number
            message: Message text to send (max 160 characters)
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.error("Seven.io provider not properly configured")
            return False
        
        if not message or not message.strip():
            logger.warning("Empty message text provided")
            return False
        
        # Ensure message doesn't exceed 160 characters
        message = message.strip()
        if len(message) > 160:
            message = message[:160]
            logger.info("Message truncated to 160 characters")
        
        logger.info(f"Sending SMS via seven.io to {to}: {message[:50]}...")
        
        try:
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "to": to,
                "from": self.sender,
                "text": message
            }
            
            logger.debug(f"Seven.io API request: URL={self.api_url}, to={to}, from={self.sender}")
            
            # Send the SMS
            response = requests.post(self.api_url, headers=headers, data=data, timeout=30)
            
            logger.info(f"Seven.io API response: {response.status_code}")
            
            # Check if the request was successful
            if response.status_code == 200:
                logger.info("SMS sent successfully via seven.io")
                return True
            else:
                logger.error(f"Failed to send SMS via seven.io: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS via seven.io: {e}")
            return False
    
    def is_configured(self) -> bool:
        """
        Check if the Seven.io provider is properly configured.
        
        Returns:
            True if provider is configured and ready to send SMS
        """
        return bool(self.api_key and self.sender) 