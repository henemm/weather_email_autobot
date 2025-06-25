"""
Garmin MapShare Message Sender

This module provides functionality to send messages to Garmin inReach devices
via the MapShare web interface. It handles configuration, HTTP requests with
retries, and proper error handling.

Note: This is for experimental/technical testing purposes only.
No production use or sending of sensitive data is intended.
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class MapShareConfig:
    """
    Configuration for MapShare message sending.
    
    Args:
        ext_id: Garmin-provided parameter from MapShare link
        adr: Target address (usually email or phone number of the sender)
        message_text: The message to be sent
    """
    ext_id: str
    adr: str
    message_text: str


@dataclass
class MapShareResult:
    """
    Result of a MapShare message sending operation.
    
    Args:
        success: Whether the operation was successful
        status_code: HTTP status code (None if request failed)
        response_text: Response text from the server
    """
    success: bool
    status_code: Optional[int]
    response_text: str


class MapShareSender:
    """
    Sender for Garmin MapShare messages.
    
    Handles HTTP requests to the Garmin MapShare web interface with
    proper headers, retry logic, and error handling.
    """
    
    def __init__(self, config: MapShareConfig):
        """
        Initialize the MapShare sender.
        
        Args:
            config: Configuration for message sending
        """
        self.config = config
        # This was the URL that returned 200 OK, even if messages were blocked.
        self.url = "https://share.garmin.com/textmessage/txtmsg"
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    def _prepare_request_data(self) -> dict:
        """
        Prepare the request data for the POST request.
        
        Returns:
            Dictionary with request data
        """
        return {
            "extId": self.config.ext_id,
            "adr": self.config.adr,
            "txt": self.config.message_text
        }
    
    def _prepare_headers(self) -> dict:
        """
        Prepare the request headers.
        
        Returns:
            Dictionary with request headers
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    
    def send_message(self) -> MapShareResult:
        """
        Send the message to the Garmin MapShare service.
        
        Returns:
            MapShareResult with operation status and details
        """
        data = self._prepare_request_data()
        headers = self._prepare_headers()
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.url,
                    data=data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return MapShareResult(
                        success=True,
                        status_code=response.status_code,
                        response_text=response.text
                    )
                else:
                    return MapShareResult(
                        success=False,
                        status_code=response.status_code,
                        response_text=response.text
                    )
                    
            except requests.exceptions.RequestException as e:
                error_message = f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                if attempt == self.max_retries - 1:
                    return MapShareResult(
                        success=False,
                        status_code=None,
                        response_text=error_message
                    )
                time.sleep(self.retry_delay)
        
        return MapShareResult(
            success=False,
            status_code=None,
            response_text="An unexpected error occurred."
        )


def send_mapshare_message(
    ext_id: str,
    adr: str,
    message_text: str
) -> MapShareResult:
    """
    Send a message to a Garmin inReach device via MapShare.
    
    Args:
        ext_id: Garmin-provided parameter from MapShare link
        adr: Target address (e.g., phone number of the sender)
        message_text: The message to be sent
        
    Returns:
        MapShareResult with operation status and details
    """
    config = MapShareConfig(
        ext_id=ext_id,
        adr=adr,
        message_text=message_text
    )
    
    sender = MapShareSender(config)
    return sender.send_message() 