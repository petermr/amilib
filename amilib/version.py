"""
Version management for amilib package.
"""
import configparser
import os
from pathlib import Path

def get_version():
    """Get the current version of amilib from config.ini."""
    config_path = Path(__file__).parent / "config.ini"
    if not config_path.exists():
        return "0.0.0"
    
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(config_path)
    return config.get("amilib", "version")

__version__ = get_version() 