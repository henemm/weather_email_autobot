#!/usr/bin/env python3
"""
SMS Command Checker.

This script polls for incoming SMS messages and processes configuration commands.
It can be run manually or as a scheduled task (cron job).
"""

import argparse
import logging
import sys
import os
import yaml
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.notification.sms_polling_client import SMSPollingClient


def setup_logging(level: str = "INFO"):
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/sms_polling.log')
        ]
    )


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        sys.exit(1)


def get_api_key(config: dict) -> str:
    """
    Get Seven.io API key from configuration or environment.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        API key string
    """
    # Try to get from config first
    if config.get('sms', {}).get('api_key'):
        api_key = config['sms']['api_key']
        # Handle environment variable substitution
        if api_key.startswith('${') and api_key.endswith('}'):
            env_var = api_key[2:-1]
            api_key = os.getenv(env_var)
            if not api_key:
                logging.error(f"Environment variable {env_var} not set")
                sys.exit(1)
        return api_key
    
    # Fallback to environment variable
    api_key = os.getenv('SEVEN_API_KEY')
    if not api_key:
        logging.error("Seven.io API key not found in config or SEVEN_API_KEY environment variable")
        sys.exit(1)
    
    return api_key


def main():
    """Main function to check SMS commands."""
    parser = argparse.ArgumentParser(description="Check SMS Commands")
    parser.add_argument("--config", default="config.yaml", 
                       help="Path to configuration file (default: config.yaml)")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level (default: INFO)")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up old processed messages")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    try:
        logger.info("Starting SMS command check...")
        
        # Load configuration
        config = load_config(args.config)
        logger.info(f"Configuration loaded from: {args.config}")
        
        # Get API key
        api_key = get_api_key(config)
        logger.info("Seven.io API key loaded successfully")
        
        # Create SMS polling client
        client = SMSPollingClient(api_key, args.config)
        
        # Cleanup old messages if requested
        if args.cleanup:
            logger.info("Cleaning up old processed messages...")
            client.cleanup_old_messages()
        
        # Poll for incoming SMS
        logger.info("Polling for incoming SMS messages...")
        result = client.poll_incoming_sms()
        
        # Log results
        if result["success"]:
            logger.info(f"SMS polling completed: {result['message']}")
            if result["commands_processed"] > 0:
                logger.info(f"Successfully processed {result['commands_processed']} configuration command(s)")
        else:
            logger.error(f"SMS polling failed: {result['message']}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("SMS command check interrupted by user")
    except Exception as e:
        logger.error(f"Error during SMS command check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 