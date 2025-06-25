"""
Environment loader utility for tests.

This module provides a function to ensure that environment variables
from .env files are loaded before running tests.
"""

import os
from typing import Optional
from dotenv import load_dotenv


def ensure_env_loaded() -> None:
    """
    Ensure that environment variables from .env file are loaded.
    
    This function loads the .env file if it exists and hasn't been loaded yet.
    It's safe to call multiple times as dotenv only loads once by default.
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