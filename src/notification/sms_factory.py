"""
SMS provider factory.

This module provides a factory for creating SMS providers based on configuration.
"""

import logging
from typing import Dict, Any
from .sms_provider import SmsProvider
from .providers.seven_provider import SevenProvider
from .providers.twilio_provider import TwilioProvider

logger = logging.getLogger(__name__)


class SmsProviderFactory:
    """
    Factory for creating SMS providers.
    
    This class creates the appropriate SMS provider based on the configuration.
    """
    
    @staticmethod
    def create_provider(provider_name: str, config: Dict[str, Any]) -> SmsProvider:
        """
        Create an SMS provider based on the provider name and configuration.
        
        Args:
            provider_name: Name of the provider ("seven" or "twilio")
            config: Provider-specific configuration
            
        Returns:
            Configured SMS provider instance
            
        Raises:
            ValueError: If provider name is not supported or configuration is invalid
        """
        if provider_name == "seven":
            return SevenProvider(config)
        elif provider_name == "twilio":
            return TwilioProvider(config)
        else:
            raise ValueError(f"Unsupported SMS provider: {provider_name}")
    
    @staticmethod
    def get_supported_providers() -> list:
        """
        Get list of supported SMS providers.
        
        Returns:
            List of supported provider names
        """
        return ["seven", "twilio"] 