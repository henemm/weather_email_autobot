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
import os
from .gsm7_validator import GSM7Validator

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
            seven_config = sms_config.get("seven", {})
            return {
                "api_key": seven_config.get("api_key"),
                "from": seven_config.get("sender")
            }
        elif provider_name == "twilio":
            twilio_config = sms_config.get("twilio", {})
            return {
                "account_sid": twilio_config.get("account_sid"),
                "auth_token": twilio_config.get("auth_token"),
                "from": twilio_config.get("from")
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

        # Normalize message to GSM-7
        validator = GSM7Validator()
        normalization_result = validator.normalize_with_logging(message_text)
        
        if normalization_result["was_changed"]:
            # Log normalization changes
            log_dir = os.path.join("output", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "sms_normalization.log")
            from datetime import datetime
            now = datetime.now().strftime("[%Y-%m-%d %H:%M]")
            
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{now} SMS text normalized to GSM-7\n")
                f.write(f"Original: {message_text}\n")
                f.write(f"Normalized: {normalization_result['normalized_text']}\n")
                
                if normalization_result["replacements"]:
                    f.write("Replacements:\n")
                    for rep in normalization_result["replacements"]:
                        f.write(f"  '{rep['original']}' -> '{rep['replacement']}' at position {rep['position']}\n")
                
                if normalization_result["removed_chars"]:
                    f.write("Removed characters:\n")
                    for rem in normalization_result["removed_chars"]:
                        f.write(f"  '{rem['character']}' at position {rem['position']}\n")
                
                f.write(f"Sender: SMS module weather report\n\n")
            
            logger.info(f"SMS text normalized to GSM-7. See sms_normalization.log for details.")
            message_text = normalization_result["normalized_text"]

        # GSM-7 validation (should now always pass)
        validation_result = validator.validate_message(message_text)
        if not validation_result["is_valid"]:
            # This should not happen after normalization, but log as error
            log_dir = os.path.join("output", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "sms_encoding_violation.log")
            from datetime import datetime
            now = datetime.now().strftime("[%Y-%m-%d %H:%M]")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{now} Aborted SMS send: Invalid characters found in text after normalization.\n")
                for v in validation_result["violations"]:
                    f.write(f"Character: '{v['character']}', Position: {v['position']}, Context: '{v['context']}'\n")
                f.write(f"Sender: SMS module weather report\n")
            logger.error("SMS send aborted due to invalid GSM-7 characters after normalization. See sms_encoding_violation.log for details.")
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
        
        # SMS must ONLY contain the compact result_output (no debug)
        message_text = report_data.get("result_output")
        if not message_text:
            # Fallback: generate text but do NOT append debug
            generated = generate_gr20_report_text(report_data, self.config)
            # If generate_gr20_report_text appended debug, strip it at marker
            marker = "# DEBUG DATENEXPORT"
            if marker in generated:
                message_text = generated.split(marker, 1)[0].strip()
            else:
                message_text = generated
        logger.info(f"Generated SMS text: {message_text}")
        
        # Send SMS
        return self.send_sms(message_text) 