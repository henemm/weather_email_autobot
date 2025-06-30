"""
Modular SMS client for sending GR20 weather reports.

This module provides a modular SMS client that can work with different
SMS providers (seven.io, Twilio, etc.) through a unified interface.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .sms_factory import SmsProviderFactory
from .sms_provider import SmsProvider
from .email_client import generate_gr20_report_text

logger = logging.getLogger(__name__)


class ModularSmsClient:
    """
    Modular SMS client for sending GR20 weather reports.
    
    This class provides a unified interface for sending SMS via different
    providers, with proper configuration management and error handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the modular SMS client.
        
        Args:
            config: Configuration dictionary with SMS settings
            
        Raises:
            ValueError: If SMS configuration is missing or invalid
        """
        if not config or "sms" not in config:
            raise ValueError("SMS configuration is required")
        
        sms_config = config["sms"]
        required_fields = ["provider", "test_number", "production_number", "mode"]
        
        for field in required_fields:
            if field not in sms_config:
                raise ValueError(f"SMS configuration missing required field: {field}")
        
        # Validate mode
        mode = sms_config["mode"]
        if mode not in ["test", "production"]:
            raise ValueError("SMS mode must be 'test' or 'production'")
        
        # Validate provider
        provider_name = sms_config["provider"]
        if provider_name not in SmsProviderFactory.get_supported_providers():
            raise ValueError(f"Unsupported SMS provider: {provider_name}")
        
        self.enabled = sms_config.get("enabled", True)
        self.provider_name = provider_name
        self.mode = mode
        self.config = config
        
        # Set recipient number based on mode
        if mode == "test":
            self.recipient_number = sms_config["test_number"]
        else:
            self.recipient_number = sms_config["production_number"]
        
        # Create provider instance
        provider_config = self._get_provider_config(sms_config)
        self.provider = SmsProviderFactory.create_provider(provider_name, provider_config)
        
        logger.info(f"Modular SMS client initialized with {provider_name} provider")
        logger.info(f"SMS mode: {mode}")
        logger.info(f"SMS recipient: {self.recipient_number}")
    
    def _get_provider_config(self, sms_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract provider-specific configuration from SMS config.
        
        Args:
            sms_config: SMS configuration dictionary
            
        Returns:
            Provider-specific configuration dictionary
        """
        provider_name = sms_config["provider"]
        
        if provider_name == "seven":
            return {
                "api_key": sms_config.get("api_key"),
                "from": sms_config.get("sender")
            }
        elif provider_name == "twilio":
            return {
                "account_sid": sms_config.get("account_sid"),
                "auth_token": sms_config.get("auth_token"),
                "from": sms_config.get("from")
            }
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
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
        
        if not self.provider.is_configured():
            logger.error(f"{self.provider_name} provider not properly configured")
            return False
        
        if not message_text or not message_text.strip():
            logger.warning("Empty message text provided")
            return False
        
        # Ensure message doesn't exceed 160 characters
        message_text = message_text.strip()
        if len(message_text) > 160:
            message_text = message_text[:160]
            logger.info("Message truncated to 160 characters")
        
        logger.info(f"Sending SMS via {self.provider_name} to {self.recipient_number}: {message_text[:50]}...")
        
        try:
            success = self.provider.send_sms(self.recipient_number, message_text)
            if success:
                logger.info(f"SMS sent successfully via {self.provider_name}")
            else:
                logger.error(f"Failed to send SMS via {self.provider_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to send SMS via {self.provider_name}: {e}")
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
        logger.info("Modular SMS send_gr20_report called")
        
        if not self.enabled:
            logger.info("SMS sending disabled")
            return False
        
        # Use the central report text generation for SMS
        message_text = generate_gr20_report_text(report_data, self.config)
        logger.info(f"Generated SMS text: {message_text}")
        
        # Send SMS
        return self.send_sms(message_text) 