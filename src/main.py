"""
Main entry point for the GR20 Weather Email Autobot.

This module initializes the logging system and coordinates the main application flow.
"""

from config.config_loader import load_config
from utils.logging_setup import setup_logging, get_logger

def main():
    """Main application entry point."""
    # Initialize logging system
    setup_logging(log_level="INFO", console_output=True)
    logger = get_logger(__name__)
    
    logger.info("Starting GR20 Weather Email Autobot")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # TODO: Implement main application logic here
        # - Weather data fetching
        # - Risk analysis
        # - Report generation
        # - Email sending
        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise

if __name__ == "__main__":
    main()