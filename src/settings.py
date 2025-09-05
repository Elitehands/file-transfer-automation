"""configuration management with settings.json as source of truth"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from settings.json with environment variable substitution"""

    search_paths = [
        config_path if config_path else None,
        "config/settings.json",
        "settings.json"
    ]

    config = None
    for path in [p for p in search_paths if p]:
        if Path(path).exists():
            with open(path, "r") as f:
                config = json.load(f)
            break

    if not config:
        raise FileNotFoundError("settings.json not found")

    def substitute_env_vars(obj):
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

    return substitute_env_vars(config)


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
    required = ["initials_column", "initials_value", "release_status_column"]

    for key in required:
        if not criteria.get(key):
            raise ValueError(f"Missing filter criteria: {key}")

    return criteria