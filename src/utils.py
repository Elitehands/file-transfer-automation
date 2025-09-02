"""Utility functions for file paths and system operations"""

import os
import platform
from pathlib import Path

def normalize_path(path_str):
    """
    Normalize path for the current operating system
    
    Args:
        path_str: Path string which may use / or \\ separators
        
    Returns:
        Normalized Path object
    """
    return Path(path_str)

def get_project_root():
    """Get the absolute path to the project root directory"""
    return Path(__file__).parent.parent.absolute()

def get_config_path():
    """Get path to configuration directory"""
    return get_project_root() / "config"

def get_logs_path():
    """Get path to logs directory"""
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir

def is_windows():
    """Check if running on Windows"""
    return platform.system() == "Windows"