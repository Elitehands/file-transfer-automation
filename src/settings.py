"""Configuration management with settings.json as source of truth"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration with external file priority"""
    
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
        external_dir = Path(sys.executable).parent
    else:
        bundle_dir = Path(__file__).parent.parent
        external_dir = Path.cwd()
    
    search_paths = [
        config_path if config_path else None,
        external_dir / "settings.json",
        external_dir / "config" / "settings.json",
        bundle_dir / "settings.json",
        bundle_dir / "config" / "settings.json",
        "config/settings.json",
        "settings.json",
        "test_settings.json"
    ]

    config = None
    config_source = None
    for path in [p for p in search_paths if p]:
        if Path(path).exists():
            with open(path, "r") as f:
                config = json.load(f)
            config_source = str(path)
            break

    if not config:
        available_paths = [str(p) for p in search_paths if p]
        raise FileNotFoundError(f"settings.json not found in: {available_paths}")

    logger.info(f"Config loaded from: {config_source}")
    return substitute_env_vars(config)


def substitute_env_vars(obj):
    """Replace ${VAR} with environment variables"""
    if isinstance(obj, str):
        pattern = re.compile(r'\${([A-Za-z0-9_]+)}')
        def replacer(match):
            var_name = match.group(1)
            return os.environ.get(var_name, "")
        return pattern.sub(replacer, obj)
    elif isinstance(obj, dict):
        return {k: substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [substitute_env_vars(item) for item in obj]
    return obj


def get_paths(config: Dict[str, Any]) -> Dict[str, str]:
    """Extract and validate required paths from config"""
    paths = config.get("paths", {})
    required = ["remote_server", "excel_file", "batch_documents", "local_gdrive"]

    for key in required:
        if not paths.get(key):
            raise ValueError(f"Missing required path: {key}")

    return paths


def get_filter_criteria(config: Dict[str, Any]) -> Dict[str, str]:
    """Extract Excel filter criteria from config"""
    criteria = config.get("excel", {}).get("filter_criteria", {})
    required = ["initials_column", "initials_value", "release_status_column", "release_quantity_column"]  

    for key in required:
        if not criteria.get(key):
            raise ValueError(f"Missing filter criteria: {key}")

    return criteria


def verify_paths(paths: Dict[str, str]) -> bool:
    """Verify all required paths are accessible"""
    for name, path in paths.items():
        if not Path(path).exists():
            logger.error(f"Path not accessible: {name} = {path}")
            return False

    logger.info("All paths verified successfully")
    return True