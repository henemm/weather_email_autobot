"""
OAuth2 token provider for Météo-France APIs.

This module provides a centralized component for managing access tokens
for Météo-France APIs (AROME, Vigilance, etc.) using OAuth2 Client Credentials flow.
"""

import base64
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Optional

try:
    from src.utils.env_loader import get_required_env_var
except ImportError:
    from utils.env_loader import get_required_env_var


class MeteoTokenProvider:
    """
    Manages OAuth2 access tokens for Météo-France APIs.
    
    This class implements the singleton pattern to ensure only one instance
    exists per runtime, providing centralized token management across all modules.
    Tokens are cached in memory and automatically renewed when expired.
    """
    
    _instance: Optional['MeteoTokenProvider'] = None
    
    def __new__(cls):
        """
        Create a new instance only if one doesn't exist.
        
        Returns:
            MeteoTokenProvider: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize the token provider (only once for singleton).
        
        Sets up internal state for token caching and expiry tracking.
        The singleton pattern ensures this initialization happens only once.
        """
        # Only initialize if this is the first time
        if not hasattr(self, '_initialized'):
            self._access_token: Optional[str] = None
            self._token_expiry: Optional[datetime] = None
            self._token_endpoint = "https://portail-api.meteofrance.fr/token"
            self._logger = logging.getLogger(__name__)
            self._max_retries = 3
            self._initialized = True
    
    def get_token(self) -> str:
        """
        Get a valid access token for Météo-France APIs.
        
        Returns a cached token if still valid, otherwise requests a new one.
        The token is automatically managed by the OAuth2 session.
        
        Returns:
            str: The access token to use in Authorization header
            
        Raises:
            RuntimeError: If METEOFRANCE_CLIENT_ID or METEOFRANCE_CLIENT_SECRET environment variables are missing
            Exception: If token request fails after retry attempts
        """
        if self._is_token_valid():
            self._logger.debug("Reusing cached token: %s...", self._access_token[:10] if self._access_token else "None")
            return self._access_token
        
        return self._request_new_token()
    
    def _is_token_valid(self) -> bool:
        """
        Check if the current token is still valid.
        
        A token is considered valid if it exists and hasn't expired.
        Tokens expire after 1 hour from acquisition.
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self._access_token or not self._token_expiry:
            return False
        
        # Add 5 minute buffer to ensure token doesn't expire during use
        buffer_time = datetime.now() + timedelta(minutes=5)
        return self._token_expiry > buffer_time
    
    def _get_client_credentials(self) -> tuple[str, str]:
        """
        Get the client credentials from environment variables.
        
        Returns:
            tuple[str, str]: The client_id and client_secret for OAuth2 authentication
            
        Raises:
            RuntimeError: If METEOFRANCE_CLIENT_ID or METEOFRANCE_CLIENT_SECRET environment variables are missing
        """
        client_id = get_required_env_var('METEOFRANCE_CLIENT_ID')
        client_secret = get_required_env_var('METEOFRANCE_CLIENT_SECRET')
        return client_id, client_secret
    
    def _request_new_token(self) -> str:
        """
        Request a new access token from Météo-France OAuth2 endpoint.
        
        Uses the OAuth2 client credentials flow to obtain a new token with retry logic.
        Requires METEOFRANCE_CLIENT_ID and METEOFRANCE_CLIENT_SECRET environment variables.
        
        Returns:
            str: The new access token
            
        Raises:
            RuntimeError: If required environment variables are missing
            Exception: If token request fails after retry attempts
        """
        client_id, client_secret = self._get_client_credentials()
        
        # Create Basic Auth header with client_id:client_secret
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = 'grant_type=client_credentials'
        
        last_exception = None
        
        for attempt in range(self._max_retries):
            try:
                self._logger.info("Requesting new OAuth2 token from Météo-France API (attempt %d/%d)...", 
                                attempt + 1, self._max_retries)
                
                response = requests.post(
                    self._token_endpoint,
                    headers=headers,
                    data=data,
                    timeout=30
                )
                
                if response.status_code != 200:
                    raise Exception(
                        f"Failed to obtain access token. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                
                token_data = response.json()
                self._access_token = token_data['access_token']
                
                # Calculate expiry time (tokens typically expire in 1 hour)
                expires_in = token_data.get('expires_in', 3600)
                self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                # Log token creation with timestamp and abbreviated token
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                token_preview = self._access_token[:10] + "..." if len(self._access_token) > 10 else self._access_token
                self._logger.info("New token created at %s: %s", timestamp, token_preview)
                
                return self._access_token
                
            except RuntimeError as e:
                # Propagate RuntimeError immediately (e.g., missing environment variables)
                raise e
            except Exception as e:
                last_exception = e
                if attempt < self._max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    self._logger.warning("Token request failed, retrying in %d seconds... Error: %s", wait_time, str(e))
                    time.sleep(wait_time)
                else:
                    self._logger.error("Token request failed after %d attempts", self._max_retries)
                    raise Exception(f"Failed to obtain access token after {self._max_retries} attempts: {str(e)}")
        
        # This should never be reached, but just in case
        raise Exception(f"Failed to obtain access token after {self._max_retries} attempts: {str(last_exception)}")
    
    def clear_cache(self) -> None:
        """
        Clear the cached token.
        
        Forces the next get_token() call to request a new token from the API.
        Useful for testing or when token needs to be refreshed immediately.
        """
        self._logger.debug("Clearing token cache")
        self._access_token = None
        self._token_expiry = None 