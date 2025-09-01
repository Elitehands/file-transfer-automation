"""Configuration management for the file transfer system"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration from JSON file
        
        Returns:
            Dict[str, Any]: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self._validate_config(config)
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate required configuration keys"""
        required_keys = [
            'vpn_connection_name',
            'remote_server_path', 
            'excel_file_path',
            'batch_documents_path',
            'local_gdrive_path',
            'filter_criteria'
        ]
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")