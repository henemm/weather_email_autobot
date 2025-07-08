"""
Configuration File Preserver (ruamel.yaml version).

This module provides utilities to update YAML configuration files
while preserving comments, formatting, and structure using ruamel.yaml.
"""

import os
from typing import Any, Dict
from ruamel.yaml import YAML

def update_yaml_preserving_comments(file_path: str, key: str, value: Any) -> bool:
    """
    Update a specific key in a YAML file while preserving comments and formatting using ruamel.yaml.
    
    Args:
        file_path: Path to the YAML file
        key: The configuration key to update (dot notation for nested keys)
        value: The new value to set
        
    Returns:
        True if update was successful, False otherwise
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
        
        # Create a backup of the original file
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        
        # Navigate to the nested key and update
        keys = key.split('.')
        current = data
        for k in keys[:-1]:
            if k not in current or current[k] is None:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        
        # Remove backup file on success
        try:
            os.remove(backup_path)
        except OSError:
            pass  # Ignore if backup removal fails
        
        return True
    except Exception as e:
        print(f"Failed to update configuration file: {e}")
        return False

def safe_yaml_dump(data: Dict[str, Any], file_path: str) -> bool:
    """
    Safely dump YAML data to a file, creating a backup first, using ruamel.yaml.
    
    Args:
        data: The data to dump
        file_path: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    try:
        # Create backup if file exists
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            with open(file_path, 'r', encoding='utf-8') as f:
                original_data = yaml.load(f)
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(original_data, f)
        
        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        
        # Remove backup on success
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except OSError:
                pass
        
        return True
    except Exception as e:
        print(f"Failed to write YAML file: {e}")
        return False 