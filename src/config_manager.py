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
        """
        Load configuration from settings.json and environment variables
        Priority: .env file > environment variables > settings.json
        """
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
        try:

            possible_paths = [
                Path("config/settings.json"),  # New location
                Path("settings.json"),         # Old location
                Path(__file__).parent.parent / "config" / "settings.json"  
            ]
            
            settings_path = None
            for path in possible_paths:
                if path.exists():
                    settings_path = path
                    break
                    
            if not settings_path:
                self.logger.warning("settings.json not found, using defaults")
                return
                
            with open(settings_path, "r") as f:
                self.config = json.load(f)
                
            self.logger.info(f"Loaded configuration from {settings_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading settings.json: {str(e)}")
            self.config = {}  

    def _load_from_env(self):
        """Load configuration from environment variables or .env file"""
        try:
            # Load from .env file if specified
            if self.env_file:
                if Path(self.env_file).exists():
                    load_dotenv(self.env_file)
                    self.logger.info(f"Loaded environment from {self.env_file}")
                else:
                    self.logger.warning(f"Specified .env file not found: {self.env_file}")
            else:

                for env_path in [".env", "config/.env"]:
                    if Path(env_path).exists():
                        load_dotenv(env_path)
                        self.logger.info(f"Loaded environment from {env_path}")
                        break
            

            env_mapping = {
                "VPN_CONNECTION_NAME": ["vpn_connection_name"],
                "REMOTE_SERVER_PATH": ["remote_server_path"],
                "EXCEL_FILE_PATH": ["excel_file_path"],
                "BATCH_DOCUMENTS_PATH": ["batch_documents_path"],
                "LOCAL_GDRIVE_PATH": ["local_gdrive_path"],
                "INITIALS_COLUMN": ["filter_criteria", "initials_column"],
                "INITIALS_VALUE": ["filter_criteria", "initials_value"],
                "RELEASE_STATUS_COLUMN": ["filter_criteria", "release_status_column"],
                "TEST_MODE": ["system", "test_mode"],
                "LOG_LEVEL": ["system", "log_level"],
                "NOTIFICATIONS_ENABLED": ["notifications", "enabled"],
            }
            

            for env_var, config_path in env_mapping.items():
                if env_var in os.environ:
                    self._set_nested_config(config_path, os.environ[env_var])
                    
        except Exception as e:
            self.logger.error(f"Error loading environment variables: {str(e)}")

    def _set_nested_config(self, path_list, value):
        """Set a nested configuration value"""

        if isinstance(value, str) and value.lower() in ["true", "false"]:
            value = value.lower() == "true"
            

        if len(path_list) == 1:
            self.config[path_list[0]] = value
        else:

            current = self.config
            for key in path_list[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
                

            current[path_list[-1]] = value

    def _validate_config(self):
        """Validate required configuration items exist"""
        required_keys = [
            "vpn_connection_name",
            "remote_server_path",
            "excel_file_path",
            "batch_documents_path", 
            "local_gdrive_path"
        ]
        
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required configuration: {key}")
                self.config[key] = "MISSING_REQUIRED_CONFIG"
                

        if "system" not in self.config:
            self.config["system"] = {}
            

        if "test_mode" not in self.config.get("system", {}):
            self.config["system"]["test_mode"] = False
            
        if "log_level" not in self.config.get("system", {}):
            self.config["system"]["log_level"] = "INFO"