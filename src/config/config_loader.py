import os
import yaml
import re
try:
    from utils.env_loader import get_required_env_var, get_env_var
except ImportError:
    from ..utils.env_loader import get_required_env_var, get_env_var


def substitute_environment_variables(value):
    """
    Replace environment variable placeholders in a string value.
    
    Args:
        value: String value that may contain ${VAR_NAME} placeholders
        
    Returns:
        String with environment variables substituted
    """
    if not isinstance(value, str):
        return value
    
    def replace_var(match):
        var_name = match.group(1)
        env_value = get_env_var(var_name)
        if env_value is None:
            raise ValueError(f"Environment variable '{var_name}' not found")
        return env_value
    
    return re.sub(r'\$\{([^}]+)\}', replace_var, value)


def process_config_values(config, skip_sms_env=False):
    """
    Recursively process config dictionary to substitute environment variables.
    If skip_sms_env is True, do not process environment variables in the sms block.
    
    Args:
        config: Configuration dictionary
        skip_sms_env: If True, skip env substitution in sms block
        
    Returns:
        Configuration dictionary with environment variables substituted
    """
    if isinstance(config, dict):
        new_config = {}
        for key, value in config.items():
            if skip_sms_env and key == "sms":
                new_config[key] = value  # Do not process env vars in sms block
            else:
                new_config[key] = process_config_values(value, skip_sms_env=skip_sms_env)
        return new_config
    elif isinstance(config, list):
        return [process_config_values(v, skip_sms_env=skip_sms_env) for v in config]
    elif isinstance(config, str):
        return substitute_environment_variables(config)
    return config


def load_config(path: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file with environment variable support.
    
    Args:
        path: Path to configuration file
        
    Returns:
        Configuration dictionary with environment variables substituted
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If YAML is invalid or required env vars are missing
        KeyError: If required config sections are missing
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Konfigurationsdatei '{path}' nicht gefunden.")

    with open(path, "r", encoding="utf-8") as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML konnte nicht geladen werden: {e}")

    # Check required sections
    for key in ["startdatum", "thresholds", "smtp"]:
        if key not in config:
            raise KeyError(f"Pflichtfeld '{key}' fehlt in config.yaml")

    # If SMS is disabled, skip env substitution in sms block
    sms_enabled = config.get("sms", {}).get("enabled", False)
    config = process_config_values(config, skip_sms_env=not sms_enabled)

    # Handle SMTP password
    smtp_pw = get_required_env_var("GMAIL_APP_PW")
    config["smtp"]["password"] = smtp_pw

    # Handle SMS configuration
    if "sms" in config and config["sms"].get("enabled", False):
        # Validate SMS configuration
        sms_config = config["sms"]
        required_sms_fields = ["api_key", "test_number", "production_number", "mode", "sender"]
        
        for field in required_sms_fields:
            if field not in sms_config:
                raise KeyError(f"SMS configuration missing required field: {field}")
        
        # Validate mode
        if sms_config["mode"] not in ["test", "production"]:
            raise ValueError("SMS mode must be 'test' or 'production'")
        
        # Set the appropriate phone number based on mode
        if sms_config["mode"] == "test":
            sms_config["to"] = sms_config["test_number"]
        else:
            sms_config["to"] = sms_config["production_number"]
        
        # Validate API key is not placeholder
        if sms_config["api_key"] == "${SEVEN_API_KEY}":
            raise ValueError("SEVEN_API_KEY environment variable not set")

    return config