"""
Environment loader utility for production code.

This module provides a function to ensure that environment variables
from .env files are loaded with proper override behavior.
"""

import os
from typing import Optional
from dotenv import load_dotenv


def ensure_env_loaded() -> None:
    """
    Ensure that environment variables from .env file are loaded.
    
    This function loads the .env file with override=True to ensure
    .env values take precedence over existing environment variables.
    """
    # Force reload to ensure .env values override existing environment variables
    load_dotenv(override=True)


def get_env_var(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable, ensuring .env is loaded first.
    
    Args:
        var_name: Name of the environment variable to retrieve
        default: Default value to return if variable is not found
        
    Returns:
        The environment variable value or default if not found
    """
    ensure_env_loaded()
    return os.getenv(var_name, default)


def get_required_env_var(var_name: str) -> str:
    """
    Get a required environment variable, raising an error if not found.
    
    Args:
        var_name: Name of the environment variable to retrieve
        
    Returns:
        The environment variable value
        
    Raises:
        RuntimeError: If the environment variable is not set
    """
    value = get_env_var(var_name)
    if value is None:
        raise RuntimeError(f"Environment variable {var_name} is not set.")
    return value 