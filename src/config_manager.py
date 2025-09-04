"""Configuration manager that loads from settings.json or .env"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    """Manages application configuration from multiple sources"""

    def __init__(self, env_file=None):
        self.logger = logging.getLogger(__name__)
        self.config = {}
        self.env_file = env_file

    def load_config(self):
        """Load configuration from settings.json and environment variables"""
        try:
            self._load_from_settings_json()
            self._load_from_env()
            self._validate_config()
            return self.config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise

    def _load_from_settings_json(self):
        """Load configuration from settings.json file"""
        # Simplified path checking
        for path in ["config/settings.json", "settings.json"]:
            if Path(path).exists():
                try:
                    with open(path, "r") as f:
                        self.config = json.load(f)
                    self.logger.info(f"Loaded configuration from {path}")
                    return
                except Exception as e:
                    self.logger.error(f"Error loading {path}: {str(e)}")
                    
        self.logger.warning("settings.json not found, using defaults")
        self.config = {}

    def _load_from_env(self):
        """Load configuration from environment variables or .env file"""
        # Load .env file
        if self.env_file and Path(self.env_file).exists():
            load_dotenv(self.env_file)
            self.logger.info(f"Loaded environment from {self.env_file}")
        else:
            for env_path in [".env", "config/.env"]:
                if Path(env_path).exists():
                    load_dotenv(env_path)
                    self.logger.info(f"Loaded environment from {env_path}")
                    break

        # Simplified env mapping with direct keys
        env_vars = {
            "VPN_CONNECTION_NAME": "vpn_connection_name",
            "REMOTE_SERVER_PATH": "remote_server_path",
            "EXCEL_FILE_PATH": "excel_file_path",
            "BATCH_DOCUMENTS_PATH": "batch_documents_path",
            "LOCAL_GDRIVE_PATH": "local_gdrive_path",
            "TEST_MODE": "test_mode",
            "LOG_LEVEL": "log_level"
        }
        
        # Process simple key mappings
        for env_var, config_key in env_vars.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"
                self.config[config_key] = value
        
        # Handle nested keys separately - keeps code cleaner
        if "INITIALS_COLUMN" in os.environ:
            if "filter_criteria" not in self.config:
                self.config["filter_criteria"] = {}
            self.config["filter_criteria"]["initials_column"] = os.environ["INITIALS_COLUMN"]
            
        if "INITIALS_VALUE" in os.environ:
            if "filter_criteria" not in self.config:
                self.config["filter_criteria"] = {}
            self.config["filter_criteria"]["initials_value"] = os.environ["INITIALS_VALUE"]
            
        if "RELEASE_STATUS_COLUMN" in os.environ:
            if "filter_criteria" not in self.config:
                self.config["filter_criteria"] = {}
            self.config["filter_criteria"]["release_status_column"] = os.environ["RELEASE_STATUS_COLUMN"]

    def _validate_config(self):
        """Validate required configuration items exist"""
        required_keys = [
            "vpn_connection_name",
            "remote_server_path",
            "excel_file_path",
            "batch_documents_path", 
            "local_gdrive_path"
        ]
        
        # Default values all in one place
        defaults = {
            "test_mode": False,
            "log_level": "INFO"
        }
        
        # Apply defaults
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
                
        # Check required keys
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required configuration: {key}")
                self.config[key] = "MISSING_REQUIRED_CONFIG"