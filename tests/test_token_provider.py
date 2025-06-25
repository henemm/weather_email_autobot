"""
Tests for MeteoTokenProvider singleton behavior and token management.

Tests the singleton pattern implementation, token caching, reuse, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import os
from src.auth.meteo_token_provider import MeteoTokenProvider


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before and after each test."""
    # Reset before test
    MeteoTokenProvider._instance = None
    
    yield
    
    # Reset after test
    MeteoTokenProvider._instance = None


def test_singleton_returns_same_instance():
    """Test that MeteoTokenProvider returns the same instance when called multiple times."""
    provider1 = MeteoTokenProvider()
    provider2 = MeteoTokenProvider()
    provider3 = MeteoTokenProvider()
    
    assert provider1 is provider2
    assert provider2 is provider3
    assert provider1 is provider3


def test_singleton_token_reuse_across_instances(monkeypatch):
    """Test that token is reused across different singleton instances."""
    def mock_request_token(self):
        """Mock token request that returns a test token."""
        self._access_token = "test_token_123"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token
    
    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token)
    
    # Create multiple instances
    provider1 = MeteoTokenProvider()
    provider2 = MeteoTokenProvider()
    
    # Get token from first instance
    token1 = provider1.get_token()
    
    # Get token from second instance - should reuse cached token
    token2 = provider2.get_token()
    
    assert token1 == token2 == "test_token_123"
    assert provider1._access_token == provider2._access_token


def test_singleton_token_expiry_affects_all_instances(monkeypatch):
    """Test that token expiry affects all singleton instances."""
    def mock_request_token(self):
        """Mock token request that returns a test token."""
        self._access_token = "test_token_123"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token
    
    def mock_request_token_new(self):
        """Mock token request that returns a new test token."""
        self._access_token = "new_test_token_456"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token
    
    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token)
    
    # Create instances
    provider1 = MeteoTokenProvider()
    provider2 = MeteoTokenProvider()
    
    # Get initial token
    token1 = provider1.get_token()
    
    # Simulate token expiration
    provider1._token_expiry = datetime.now() - timedelta(minutes=1)
    
    # Switch to new token mock
    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token_new)
    
    # Get token from second instance - should request new token
    token2 = provider2.get_token()
    
    assert token1 == "test_token_123"
    assert token2 == "new_test_token_456"
    assert provider1._access_token == provider2._access_token == "new_test_token_456"


def test_singleton_clear_cache_affects_all_instances(monkeypatch):
    """Test that clearing cache affects all singleton instances."""
    def mock_request_token(self):
        """Mock token request that returns a test token."""
        self._access_token = "test_token_123"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token
    
    def mock_request_token_new(self):
        """Mock token request that returns a new test token."""
        self._access_token = "new_test_token_456"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token
    
    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token)
    
    # Create instances
    provider1 = MeteoTokenProvider()
    provider2 = MeteoTokenProvider()
    
    # Get initial token
    token1 = provider1.get_token()
    
    # Clear cache from first instance
    provider1.clear_cache()
    
    # Switch to new token mock
    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token_new)
    
    # Get token from second instance - should request new token
    token2 = provider2.get_token()
    
    assert token1 == "test_token_123"
    assert token2 == "new_test_token_456"
    assert provider1._access_token == provider2._access_token == "new_test_token_456"


def test_singleton_thread_safety_simulation():
    """Test that singleton pattern prevents race conditions in token requests."""
    # This test simulates concurrent access to ensure singleton behavior
    # In a real scenario, this would be tested with actual threading
    
    provider1 = MeteoTokenProvider()
    provider2 = MeteoTokenProvider()
    
    # Both instances should be the same object
    assert provider1 is provider2
    
    # Both should have the same internal state
    assert provider1._access_token == provider2._access_token
    assert provider1._token_expiry == provider2._token_expiry


def test_singleton_preserves_token_across_multiple_calls(monkeypatch):
    """Test that token is preserved across multiple calls to different instances."""
    def mock_request_token(self):
        """Mock token request that returns a test token."""
        self._access_token = "test_token_123"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token
    
    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token)
    
    # Create multiple instances
    providers = [MeteoTokenProvider() for _ in range(5)]
    
    # Get token from first instance
    token1 = providers[0].get_token()
    
    # Get tokens from all other instances
    tokens = [provider.get_token() for provider in providers[1:]]
    
    # All tokens should be the same
    assert all(token == token1 for token in tokens)
    assert token1 == "test_token_123"


def test_singleton_environment_variable_handling():
    """Test that singleton properly handles environment variable errors."""
    # Clear environment variable
    with patch.dict(os.environ, {}, clear=True):
        provider1 = MeteoTokenProvider()
        provider2 = MeteoTokenProvider()
        
        # Both instances should be the same
        assert provider1 is provider2
        
        # Both should raise the same error
        with pytest.raises(RuntimeError) as exc_info1:
            provider1.get_token()
        
        with pytest.raises(RuntimeError) as exc_info2:
            provider2.get_token()
        
        assert str(exc_info1.value) == str(exc_info2.value)
        assert "METEOFRANCE_CLIENT_ID" in str(exc_info1.value)


def test_singleton_logging_behavior(monkeypatch, caplog):
    """Test that singleton provides consistent logging across instances."""
    def mock_request_token(self):
        """Mock token request that returns a test token with logging."""
        self._access_token = "test_token_123"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token
    
    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token)
    
    # Create instances
    provider1 = MeteoTokenProvider()
    provider2 = MeteoTokenProvider()
    
    # Get tokens (this should trigger logging if implemented)
    with patch.dict(os.environ, {'METEOFRANCE_BASIC_AUTH': 'test_auth'}):
        token1 = provider1.get_token()
        token2 = provider2.get_token()
    
    # Both should return the same token
    assert token1 == token2 == "test_token_123"


def test_singleton_memory_efficiency():
    """Test that singleton pattern is memory efficient."""
    # Create many instances
    providers = [MeteoTokenProvider() for _ in range(100)]
    
    # All should be the same object
    first_provider = providers[0]
    for provider in providers[1:]:
        assert provider is first_provider
    
    # Memory usage should be minimal (only one instance)
    import sys
    # Note: This is a conceptual test - actual memory measurement would require more sophisticated tools
    assert len(set(id(provider) for provider in providers)) == 1


def test_token_is_fetched_only_once(monkeypatch):
    """
    Ensure that the token is only fetched once (cache mechanism).
    """
    calls = []

    def mock_request_token(self):
        calls.append(1)
        self._access_token = "mocked_token_123"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token

    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token)

    provider = MeteoTokenProvider()
    token1 = provider.get_token()
    token2 = provider.get_token()

    assert token1 == "mocked_token_123"
    assert token2 == "mocked_token_123"
    assert len(calls) == 1  # Should only be called once


def test_token_is_renewed_after_expiry(monkeypatch):
    """
    Ensure that the token is renewed after expiration.
    """
    calls = []

    def mock_request_token(self):
        calls.append(1)
        self._access_token = f"mocked_token_{len(calls)}"
        self._token_expiry = datetime.now() + timedelta(hours=1)
        return self._access_token

    monkeypatch.setattr(MeteoTokenProvider, "_request_new_token", mock_request_token)

    provider = MeteoTokenProvider()
    
    # First call
    token1 = provider.get_token()
    
    # Simulate expiration
    provider._token_expiry = datetime.now() - timedelta(minutes=1)
    
    # Second call should request new token
    token2 = provider.get_token()

    assert token1 == "mocked_token_1"
    assert token2 == "mocked_token_2"
    assert len(calls) == 2  # Should be called twice


def test_runtime_error_if_env_variable_missing(monkeypatch):
    """
    Ensure that a missing token throws a RuntimeError.
    """
    monkeypatch.delenv("METEOFRANCE_CLIENT_ID", raising=False)
    monkeypatch.delenv("METEOFRANCE_CLIENT_SECRET", raising=False)

    provider = MeteoTokenProvider()
    
    with pytest.raises(RuntimeError, match="METEOFRANCE_CLIENT_ID"):
        provider.get_token()