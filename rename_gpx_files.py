#!/usr/bin/env python3
"""
Intelligent GPX File Renamer

This script renames GPX files from complex names to simple "E1 Ballone - De Vergio.gpx" format
for use with the generate_etappen_json.py script.

Usage:
    python rename_gpx_files.py --input-dir input_gpx/ --dry-run
    python rename_gpx_files.py --input-dir input_gpx/ --execute
"""

import argparse
import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_etappe_number(filename: str) -> int:
    """
    Extract stage number from filename using various patterns.
    
    Args:
        filename: The filename to parse
        
    Returns:
        Stage number as integer
        
    Raises:
        ValueError: If no stage number can be extracted
    """
    # Special case: "Etappe 13d_14" should be stage 14
    if "Etappe 13d_14" in filename:
        return 14
    
    # Special case: "Etappe 16" should be stage 15
    if "Etappe 16" in filename:
        return 15
    
    # Pattern 1: "Etappe 1", "Etappe 2", etc.
    pattern1 = r'Etappe\s+(\d+)'
    match = re.search(pattern1, filename)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "Etappe 13d" (with letter suffix) - treat as stage 13
    pattern2 = r'Etappe\s+(\d+)[a-z]'
    match = re.search(pattern2, filename)
    if match:
        return int(match.group(1))
    
    # Pattern 3: Look for numbers that might be stage numbers
    # This is more heuristic and should be used carefully
    numbers = re.findall(r'\d+', filename)
    if numbers:
        # Try to find a reasonable stage number (1-20 range)
        for num in numbers:
            num_int = int(num)
            if 1 <= num_int <= 20:
                return num_int
    
    raise ValueError(f"Could not extract stage number from: {filename}")

def extract_location_name(location: str) -> str:
    """
    Extract a short, recognizable name from a location string.
    
    Args:
        location: Full location name
        
    Returns:
        Short location name
    """
    # Remove common words
    location = location.strip()
    
    # Remove parenthetical information
    location = re.sub(r'\s*\([^)]*\)', '', location)
    
    # Remove elevation information
    location = re.sub(r'\s*\(\d+m\)', '', location)
    
    # Common replacements for shorter names
    replacements = {
        'Refuge de ': '',
        'Refuge d\'': '',
        'Refuge ': '',
        'Hôtel ': '',
        'Hotel ': '',
        'Gîte ': '',
        'Bergerie de ': '',
        'Bergerie ': '',
        'Relais ': '',
        'San Petru di Verde': 'San Petru',
        'Castel De Vergio': 'De Vergio',
        'Monte d\'Oro': 'Monte d\'Oro',
        'Bergeries de E Capanelle': 'Capanelle',
        'U Fugone': 'Fugone',
        'Petra Piana': 'Petra Piana',
        'L\'Onda': 'L\'Onda',
        'Manganu': 'Manganu',
        'd\'Usciolu': 'Usciolu',
        'd\'i Paliri': 'Paliri',
        'i Paliri': 'Paliri',
        'I Croci': 'Croci',
        'Calenzana': 'Calenzana',
        'Conca': 'Conca',
        'Ortu di u Piobbu': 'Ortu',
        'l\'Ortu di u Piobbu': 'Ortu',
        'Carozzu': 'Carozzu',
        'Ascu Stagnu': 'Ascu',
        'Haut Asco': 'Asco',
        'Ballone': 'Ballone',
        'Von ': '',
        'von ': '',
        'Etappe 13d': 'Croci',
        'Etappe 16': 'Paliri'
    }
    
    for old, new in replacements.items():
        location = location.replace(old, new)
    
    # Clean up extra spaces
    location = re.sub(r'\s+', ' ', location).strip()
    
    # If still too long, take first few words
    if len(location) > 15:
        words = location.split()
        if len(words) > 2:
            location = ' '.join(words[:2])
    
    return location

def create_short_name(filename: str) -> str:
    """
    Create a short, recognizable name from the filename.
    
    Args:
        filename: The original filename
        
    Returns:
        Short name in format "E1 Ballone - De Vergio"
    """
    # Extract stage number
    stage_num = extract_etappe_number(filename)
    
    # Remove common prefixes and suffixes
    name = filename.replace(f"Etappe {stage_num}", "").replace(f"Etappe {stage_num}_", "")
    name = name.replace("_ Von ", " ").replace("_ von ", " ")
    name = name.replace(" nach ", " - ")
    name = name.replace(" to ", " - ")
    
    # Handle special cases
    if "Etappe 13d_14" in filename:
        name = name.replace("Etappe 13d_14_", "")
    elif "Etappe 16" in filename:
        name = name.replace("Etappe 16_", "")
    
    # Remove date prefixes and IDs
    name = re.sub(r'^\d{4}-\d{2}-\d{2}_\d+_', '', name)
    
    # Remove file extension
    name = name.replace('.gpx', '')
    
    # Clean up extra spaces and underscores
    name = re.sub(r'[_\s]+', ' ', name).strip()
    
    # Special handling for specific stages
    if stage_num == 1:
        # E1: Calenzana - Ortu
        return "E1 Calenzana - Ortu"
    elif stage_num == 5:
        # E5: Ballone - De Vergio
        return "E5 Ballone - De Vergio"
    elif stage_num == 10:
        # E10: Monte d'Oro - Capanelle
        return "E10 Monte d'Oro - Capanelle"
    elif stage_num == 14:
        # E14: Croci - Paliri
        return "E14 Croci - Paliri"
    elif stage_num == 15:
        # E15: Paliri - Conca
        return "E15 Paliri - Conca"
    
    # Extract start and end locations for other stages
    if ' - ' in name:
        parts = name.split(' - ')
        if len(parts) >= 2:
            start = extract_location_name(parts[0])
            end = extract_location_name(parts[1])
            return f"E{stage_num} {start} - {end}"
    
    # Fallback: just use the cleaned name
    return f"E{stage_num} {extract_location_name(name)}"

def analyze_gpx_files(input_dir: str) -> List[Tuple[str, int, str]]:
    """
    Analyze GPX files and extract stage numbers.
    
    Args:
        input_dir: Directory containing GPX files
        
    Returns:
        List of tuples: (original_filename, stage_number, proposed_new_name)
    """
    gpx_files = []
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.gpx'):
            try:
                stage_number = extract_etappe_number(filename)
                new_name = create_short_name(filename) + ".gpx"
                gpx_files.append((filename, stage_number, new_name))
                logger.info(f"Found: {filename} -> Stage {stage_number} -> {new_name}")
            except ValueError as e:
                logger.warning(f"Skipping {filename}: {e}")
    
    # Sort by stage number
    gpx_files.sort(key=lambda x: x[1])
    return gpx_files

def check_for_conflicts(gpx_files: List[Tuple[str, int, str]], input_dir: str) -> List[str]:
    """
    Check for naming conflicts.
    
    Args:
        gpx_files: List of file information
        input_dir: Input directory
        
    Returns:
        List of conflict messages
    """
    conflicts = []
    
    # Check for duplicate stage numbers
    stage_numbers = [f[1] for f in gpx_files]
    duplicates = [num for num in set(stage_numbers) if stage_numbers.count(num) > 1]
    
    for dup in duplicates:
        files_with_dup = [f[0] for f in gpx_files if f[1] == dup]
        conflicts.append(f"Stage {dup} appears in multiple files: {', '.join(files_with_dup)}")
    
    # Check if target files already exist
    for _, stage_num, new_name in gpx_files:
        target_path = os.path.join(input_dir, new_name)
        if os.path.exists(target_path):
            conflicts.append(f"Target file already exists: {new_name}")
    
    return conflicts

def rename_files(gpx_files: List[Tuple[str, int, str]], input_dir: str, dry_run: bool = True) -> None:
    """
    Rename the files.
    
    Args:
        gpx_files: List of file information
        input_dir: Input directory
        dry_run: If True, only show what would be done
    """
    if dry_run:
        logger.info("=== DRY RUN - No files will be modified ===")
    else:
        logger.info("=== EXECUTING RENAMES ===")
    
    for original_name, stage_num, new_name in gpx_files:
        original_path = os.path.join(input_dir, original_name)
        new_path = os.path.join(input_dir, new_name)
        
        if dry_run:
            logger.info(f"Would rename: {original_name} -> {new_name}")
        else:
            try:
                shutil.move(original_path, new_path)
                logger.info(f"Renamed: {original_name} -> {new_name}")
            except Exception as e:
                logger.error(f"Failed to rename {original_name}: {e}")

def create_backup(input_dir: str) -> str:
    """
    Create a backup of the input directory.
    
    Args:
        input_dir: Directory to backup
        
    Returns:
        Path to backup directory
    """
    import time
    backup_dir = f"{input_dir}_backup_{int(time.time())}"
    shutil.copytree(input_dir, backup_dir)
    logger.info(f"Created backup: {backup_dir}")
    return backup_dir

def main():
    parser = argparse.ArgumentParser(
        description="Intelligently rename GPX files to 'E1 Ballone - De Vergio.gpx' format"
    )
    parser.add_argument(
        '--input-dir', 
        required=True, 
        help='Directory containing GPX files'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--execute', 
        action='store_true',
        help='Actually perform the renames (use with caution)'
    )
    parser.add_argument(
        '--backup', 
        action='store_true',
        help='Create backup before renaming'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1
    
    # Analyze files
    logger.info(f"Analyzing GPX files in: {args.input_dir}")
    gpx_files = analyze_gpx_files(args.input_dir)
    
    if not gpx_files:
        logger.warning("No GPX files found or no stage numbers could be extracted")
        return 1
    
    # Check for conflicts
    conflicts = check_for_conflicts(gpx_files, args.input_dir)
    if conflicts:
        logger.error("Conflicts detected:")
        for conflict in conflicts:
            logger.error(f"  - {conflict}")
        
        if args.execute:
            logger.error("Cannot proceed with conflicts. Please resolve them first.")
            return 1
    
    # Show summary
    logger.info(f"\nFound {len(gpx_files)} GPX files:")
    for original_name, stage_num, new_name in gpx_files:
        logger.info(f"  Stage {stage_num:2d}: {original_name} -> {new_name}")
    
    # Perform renames
    if args.execute:
        if args.backup:
            create_backup(args.input_dir)
        rename_files(gpx_files, args.input_dir, dry_run=False)
        logger.info("Renaming completed successfully!")
    else:
        rename_files(gpx_files, args.input_dir, dry_run=True)
        logger.info("Use --execute to actually perform the renames")
    
    return 0

if __name__ == "__main__":
    exit(main()) 