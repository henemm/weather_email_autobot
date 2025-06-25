"""
Tests for the production environment loader utility.
"""

import os
import tempfile
import pytest
from src.utils.env_loader import get_env_var, get_required_env_var, ensure_env_loaded


class TestEnvLoader:
    """Test cases for the environment loader utility."""
    
    def test_get_env_var_with_existing_variable(self):
        """Test getting an environment variable that exists."""
        # Set a test environment variable
        os.environ['TEST_VAR'] = 'test_value'
        
        try:
            result = get_env_var('TEST_VAR')
            assert result == 'test_value'
        finally:
            # Clean up
            del os.environ['TEST_VAR']
    
    def test_get_env_var_with_default_value(self):
        """Test getting an environment variable with default value when not found."""
        result = get_env_var('NONEXISTENT_VAR', default='default_value')
        assert result == 'default_value'
    
    def test_get_env_var_with_none_default(self):
        """Test getting an environment variable that doesn't exist with None default."""
        result = get_env_var('NONEXISTENT_VAR')
        assert result is None
    
    def test_get_required_env_var_with_existing_variable(self):
        """Test getting a required environment variable that exists."""
        # Set a test environment variable
        os.environ['REQUIRED_VAR'] = 'required_value'
        
        try:
            result = get_required_env_var('REQUIRED_VAR')
            assert result == 'required_value'
        finally:
            # Clean up
            del os.environ['REQUIRED_VAR']
    
    def test_get_required_env_var_with_missing_variable(self):
        """Test getting a required environment variable that doesn't exist raises error."""
        with pytest.raises(RuntimeError, match="Environment variable MISSING_VAR is not set"):
            get_required_env_var('MISSING_VAR')
    
    def test_env_file_loading_with_override(self):
        """Test that .env file values override existing environment variables."""
        # Set an environment variable in the shell
        os.environ['OVERRIDE_VAR'] = 'shell_value'
        
        # Create a temporary .env file in the current directory
        env_file_path = '.env'
        with open(env_file_path, 'w') as env_file:
            env_file.write('OVERRIDE_VAR=env_file_value\n')
        
        try:
            # The env_loader should load the .env file and override the shell value
            result = get_env_var('OVERRIDE_VAR')
            assert result == 'env_file_value'
            
        finally:
            # Clean up
            del os.environ['OVERRIDE_VAR']
            if os.path.exists(env_file_path):
                os.unlink(env_file_path)
    
    def test_ensure_env_loaded_can_be_called_multiple_times(self):
        """Test that ensure_env_loaded can be called multiple times without issues."""
        # This should not raise any exceptions
        ensure_env_loaded()
        ensure_env_loaded()
        ensure_env_loaded()
        
        # Should still work normally
        result = get_env_var('SOME_VAR', default='test')
        assert result == 'test' 