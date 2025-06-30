"""
Abstract SMS provider interface.

This module defines the base interface for SMS providers,
allowing easy integration of different SMS services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class SmsProvider(ABC):
    """
    Abstract base class for SMS providers.
    
    This class defines the interface that all SMS providers must implement.
    Concrete implementations should inherit from this class and implement
    the required methods.
    """
    
    @abstractmethod
    def send_sms(self, to: str, message: str) -> bool:
        """
        Send an SMS message.
        
        Args:
            to: Recipient phone number
            message: Message text to send
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if the provider is properly configured.
        
        Returns:
            True if provider is configured and ready to send SMS
        """
        pass 