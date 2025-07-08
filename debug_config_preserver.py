#!/usr/bin/env python3
"""
Debug script for config preserver functionality.
"""

import tempfile
import yaml
from src.config.config_preserver import update_yaml_preserving_comments, _update_yaml_content, _find_key_line

# Test YAML content
yaml_content = """# SMS notification settings
sms:
  enabled: false
  mode: test  # 'test' or 'production'
  provider: seven  # 'seven' or 'twilio'
  
  # Seven.io configuration
  seven:
    api_key: ${SEVEN_API_KEY}
    sender: '4917717816897'
  
  # Phone numbers for notifications
  production_number: '+4917717816897'
  test_number: '+49123456789'
"""

# Test key finding
lines = yaml_content.split('\n')
print("Testing key finding:")
print(f"Looking for: ['sms', 'test_number']")
result = _find_key_line(lines, ['sms', 'test_number'])
print(f"Found at line: {result}")
if result is not None:
    print(f"Line content: {lines[result]}")
else:
    print("Key not found!")

print("\n" + "="*50 + "\n")

# Create temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
    temp_file.write(yaml_content)
    temp_file.flush()
    
    print(f"Original content:")
    print(yaml_content)
    print("\n" + "="*50 + "\n")
    
    # Test the update
    result = update_yaml_preserving_comments(temp_file.name, 'sms.test_number', '+49987654321')
    print(f"Update result: {result}")
    
    # Read the updated content
    with open(temp_file.name, 'r') as f:
        updated_content = f.read()
    
    print(f"Updated content:")
    print(updated_content)
    print("\n" + "="*50 + "\n")
    
    # Test YAML validity
    try:
        config = yaml.safe_load(updated_content)
        print("YAML is valid")
        print(f"Updated value: {config['sms']['test_number']}")
    except Exception as e:
        print(f"YAML error: {e}")
    
    # Clean up
    import os
    os.unlink(temp_file.name) 