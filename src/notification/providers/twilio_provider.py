"""
Twilio SMS provider implementation.

This module provides the concrete implementation for sending SMS
via the Twilio REST API.
"""

import requests
import logging
from typing import Dict, Any
from ..sms_provider import SmsProvider

logger = logging.getLogger(__name__)


class TwilioProvider(SmsProvider):
    """
    Twilio SMS provider implementation.
    
    This class handles SMS sending via the Twilio REST API
    with proper authentication and error handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Twilio SMS provider.
        
        Args:
            config: Configuration dictionary containing Twilio settings:
                - account_sid: Twilio Account SID
                - auth_token: Twilio Auth Token
                - from: Sender phone number
                
        Raises:
            ValueError: If required configuration is missing
        """
        if not config:
            raise ValueError("Twilio configuration is required")
        
        required_fields = ["account_sid", "auth_token", "from"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Twilio configuration missing required field: {field}")
        
        self.account_sid = config["account_sid"]
        self.auth_token = config["auth_token"]
        self.sender = config["from"]
        self.api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        logger.info("Twilio SMS provider initialized")
    
    def send_sms(self, to: str, message: str) -> bool:
        """
        Send an SMS via Twilio API.
        
        Args:
            to: Recipient phone number
            message: Message text to send (max 160 characters)
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.error("Twilio provider not properly configured")
            return False
        
        if not message or not message.strip():
            logger.warning("Empty message text provided")
            return False
        
        # Ensure message doesn't exceed 160 characters
        message = message.strip()
        if len(message) > 160:
            message = message[:160]
            logger.info("Message truncated to 160 characters")
        
        logger.info(f"Sending SMS via Twilio to {to}: {message[:50]}...")
        
        try:
            # Prepare the API request with Basic Auth
            import base64
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "To": to,
                "From": self.sender,
                "Body": message
            }
            
            logger.debug(f"Twilio API request: URL={self.api_url}, to={to}, from={self.sender}")
            
            # Send the SMS
            response = requests.post(self.api_url, headers=headers, data=data, timeout=30)
            
            logger.info(f"Twilio API response: {response.status_code}")
            
            # Check if the request was successful
            if response.status_code == 201:
                logger.info("SMS sent successfully via Twilio")
                return True
            else:
                logger.error(f"Failed to send SMS via Twilio: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS via Twilio: {e}")
            return False
    
    def is_configured(self) -> bool:
        """
        Check if the Twilio provider is properly configured.
        
        Returns:
            True if provider is configured and ready to send SMS
        """
        return bool(self.account_sid and self.auth_token and self.sender) 