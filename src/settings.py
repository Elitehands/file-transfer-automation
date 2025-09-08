"""Configuration management with settings.json as source of truth"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration with external file priority"""
    
    # Handle PyInstaller bundled executable
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        bundle_dir = Path(sys._MEIPASS)  
        external_dir = Path(sys.executable).parent  
    else:
        
        bundle_dir = Path(__file__).parent.parent
        external_dir = Path.cwd()
    
    search_paths = [
        config_path if config_path else None,
        # PRIORITY: External files first (can be edited by client)
        external_dir / "settings.json",             # Next to exe
        external_dir / "config" / "settings.json",  # In config folder next to exe
        # FALLBACK: Internal bundled files
        bundle_dir / "settings.json",              # Inside bundle
        bundle_dir / "config" / "settings.json",   # Inside bundle
        "config/settings.json",                    # Current working dir
        "settings.json",                           # Current working dir
        "mock_settings.json"                       # Development fallback
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

    # Log which config was loaded
    print(f"Config loaded from: {config_source}")

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


if __name__ == "__main__":
    """Test configuration loading independently"""
    import argparse
    import logging
    
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Test Configuration Loading")
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()
    
    try:
        print("Testing configuration loading...")
        config = load_config(args.config)
        
        print("✅ Configuration loaded successfully")
        print(f"Paths found: {list(config.get('paths', {}).keys())}")
        print(f"VPN name: {config.get('vpn', {}).get('connection_name', 'Not set')}")
        print(f"Notifications enabled: {config.get('notifications', {}).get('enabled', False)}")
        
        # Test path extraction
        paths = get_paths(config)
        criteria = get_filter_criteria(config)
        
        print("✅ All configuration validation passed")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        sys.exit(1)