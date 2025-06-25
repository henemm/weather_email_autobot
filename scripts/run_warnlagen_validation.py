#!/usr/bin/env python3
"""
Script to run comprehensive weather warning validation.

This script validates the meteofrance-api during complex weather warning situations
and generates a detailed report of the validation results.
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.config_loader import load_config
from wetter.warnlagen_validator import run_comprehensive_validation


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/warnlagen_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )


def main():
    """Main function to run the validation."""
    print("=" * 60)
    print("WEATHER WARNING VALIDATION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Run comprehensive validation
        logger.info("Starting comprehensive validation...")
        report = run_comprehensive_validation(config)
        
        # Print report
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"output/warnlagen_validation_report_{timestamp}.txt"
        
        os.makedirs("output", exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info(f"Validation report saved to: {report_file}")
        
        print()
        print("=" * 60)
        print("VALIDATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"ERROR: Validation failed - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 