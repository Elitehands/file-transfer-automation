"""Configuration manager loads from settings.json with environment variable substitution"""

import os
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration with settings.json as source of truth"""

    ENV_PATTERN = re.compile(r'\${([A-Za-z0-9_]+)}')
    
    def __init__(self, env_file=None, config_path=None):
        self.logger = logging.getLogger(__name__)
        self.config = {}
        self.env_file = env_file
        self.config_path = config_path
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from settings.json and substitute environment variables"""
        try:
            self._load_from_settings_json()
            self._substitute_env_variables()
            self._apply_cli_overrides()
            self._validate_config()
            return self.config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise

    def _load_from_settings_json(self):
        """Load configuration from settings.json file"""
        search_paths = [
            self.config_path if self.config_path else None,
            "config/settings.json",
            "settings.json"
        ]
        
        for path in [p for p in search_paths if p]:
            if Path(path).exists():
                try:
                    with open(path, "r") as f:
                        self.config = json.load(f)
                    self.logger.info(f"Loaded configuration from {path}")
                    return
                except Exception as e:
                    self.logger.error(f"Error loading {path}: {str(e)}")
                    
        self.logger.warning("settings.json not found, using defaults")
        self.config = {
            "vpn": {"connection_name": "bbuk vpn"},
            "paths": {
                "remote_server": "Z:\\Quality Assurance(QA Common)",
                "excel_file": "Z:\\Quality Assurance(QA Common)\\25.Product Status Log\\Product status Log.xlsx",
                "batch_documents": "Z:\\Quality Assurance(QA Common)\\3.Batch Documents",
                "local_gdrive": "G:\\My Drive\\status log"
            },
            "excel": {"filter_criteria": {"initials_column": "AJ", "initials_value": "PP", "release_status_column": "AK"}},
            "notifications": {"enabled": False},
            "system": {"test_mode": False}
        }

    def _substitute_env_variables(self):
        """Replace ${ENV_VAR} patterns with environment variables"""
        def _replace_env_vars(obj):
            if isinstance(obj, str):
                matches = self.ENV_PATTERN.findall(obj)
                if matches:
                    result = obj
                    for env_var in matches:
                        env_value = os.environ.get(env_var, "")
                        if not env_value and env_var.endswith("_PASSWORD"):
                            self.logger.warning(f"Environment variable {env_var} not found. Using empty string for security.")
                        elif not env_value:
                            self.logger.warning(f"Environment variable {env_var} not found")
                        placeholder = f"${{{env_var}}}"
                        result = result.replace(placeholder, env_value)
                    return result
                return obj
            elif isinstance(obj, dict):
                return {k: _replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_replace_env_vars(i) for i in obj]
            else:
                return obj
                
        self.config = _replace_env_vars(self.config)

    def _apply_cli_overrides(self):
        """Apply any command-line overrides that may be set"""
        pass

    def _validate_config(self):
        """Validate required configuration values"""
        required_sections = ["vpn", "paths", "excel"]
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required configuration section: {section}")
                self.config[section] = {}

        required_paths = [
            "remote_server", 
            "excel_file", 
            "batch_documents", 
            "local_gdrive"
        ]
        
        for path_key in required_paths:
            if path_key not in self.config["paths"]:
                self.logger.error(f"Missing required path configuration: {path_key}")
                self.config["paths"][path_key] = f"MISSING_{path_key.upper()}"

    def get_flattened_config(self) -> Dict[str, Any]:
        """
        Get a flattened version of config for backward compatibility
        
        This helps transition from the old flat structure to the new nested structure
        """
        flat_config = {}
        
        if "vpn" in self.config:
            flat_config["vpn_connection_name"] = self.config["vpn"].get("connection_name")
        
        if "paths" in self.config:
            flat_config["remote_server_path"] = self.config["paths"].get("remote_server")
            flat_config["excel_file_path"] = self.config["paths"].get("excel_file")
            flat_config["batch_documents_path"] = self.config["paths"].get("batch_documents")
            flat_config["local_gdrive_path"] = self.config["paths"].get("local_gdrive")
        
        if "excel" in self.config and "filter_criteria" in self.config["excel"]:
            flat_config["filter_criteria"] = self.config["excel"]["filter_criteria"]
        
        if "notifications" in self.config:
            flat_config["notifications"] = self.config["notifications"]
        
        if "system" in self.config:
            for key, value in self.config["system"].items():
                flat_config[key] = value
            
        return flat_config