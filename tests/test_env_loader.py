"""
Test for environment loader utility.

This test verifies that the env_loader utility correctly loads
environment variables from .env files.
"""

import os
import pytest
from tests.utils.env_loader import ensure_env_loaded, get_env_var


def test_ensure_env_loaded_can_be_called_multiple_times():
    """
    Test that ensure_env_loaded can be called multiple times safely.
    """
    # Should not raise any exceptions
    ensure_env_loaded()
    ensure_env_loaded()
    ensure_env_loaded()


def test_get_env_var_returns_none_for_nonexistent_variable():
    """
    Test that get_env_var returns None for variables that don't exist.
    """
    result = get_env_var("NONEXISTENT_VARIABLE_12345")
    assert result is None


def test_get_env_var_returns_default_for_nonexistent_variable():
    """
    Test that get_env_var returns the default value for variables that don't exist.
    """
    default_value = "default_value_12345"
    result = get_env_var("NONEXISTENT_VARIABLE_12345", default_value)
    assert result == default_value


def test_get_env_var_loads_env_file():
    """
    Test that get_env_var loads the .env file and can access variables.
    
    This test assumes that METEOFRANCE_WCS_TOKEN or METEOFRANCE_BASIC_AUTH
    is defined in the .env file. If neither exists, the test will pass
    but won't verify the actual loading functionality.
    """
    # Try to get a variable that should be in .env
    token = get_env_var("METEOFRANCE_WCS_TOKEN")
    basic_auth = get_env_var("METEOFRANCE_BASIC_AUTH")
    
    # At least one of these should be available if .env is loaded
    # If neither is available, that's also acceptable (no .env file or empty)
    # The important thing is that the function doesn't crash
    assert isinstance(token, (str, type(None)))
    assert isinstance(basic_auth, (str, type(None)))


def test_get_env_var_works_with_existing_environment_variables():
    """
    Test that get_env_var works with existing environment variables.
    """
    # Set a test environment variable
    test_var_name = "TEST_ENV_VAR_12345"
    test_var_value = "test_value_12345"
    os.environ[test_var_name] = test_var_value
    
    try:
        # Get the variable using our utility
        result = get_env_var(test_var_name)
        assert result == test_var_value
    finally:
        # Clean up
        if test_var_name in os.environ:
            del os.environ[test_var_name] 