"""Utility functions for YouTube Human Emulator"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import random
import yaml

def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Setup logging configuration"""
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger('youtube_human_emulator')
    logger.setLevel(getattr(logging, config.get('level', 'INFO')))
    
    # File handler
    log_file = log_dir / config.get('file', 'automation.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console_handler)
    
    return logger

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON or YAML file"""
    path = Path(config_path)
    
    if not path.exists():
        # Try example file
        example_path = path.parent / f"{path.stem}.example{path.suffix}"
        if example_path.exists():
            print(f"⚠️ Config not found, using example: {example_path}")
            path = example_path
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        if path.suffix == '.json':
            config = json.load(f)
        elif path.suffix in ['.yaml', '.yml']:
            config = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")
    
    # Validate config
    validate_config(config)
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure"""
    required_sections = ['youtube_urls', 'behavior']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")
    
    # Validate URLs
    if not config['youtube_urls']:
        raise ValueError("At least one YouTube URL required")
    
    # Validate behavior
    behavior = config['behavior']
    if 'min_watch_time' not in behavior or 'max_watch_time' not in behavior:
        raise ValueError("Watch time settings required")
    
    if behavior['min_watch_time'] > behavior['max_watch_time']:
        raise ValueError("min_watch_time cannot exceed max_watch_time")
    
    return True

def save_stats(stats: Dict[str, Any]) -> None:
    """Save statistics to file"""
    stats_dir = Path('data')
    stats_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    stats_file = stats_dir / f'stats_{timestamp}.json'
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    return str(stats_file)

def generate_session_id() -> str:
    """Generate unique session ID"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_num = random.randint(1000, 9999)
    return f"{timestamp}_{random_num}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename