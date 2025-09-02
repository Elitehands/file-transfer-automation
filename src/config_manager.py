"""Configuration management for the file transfer system"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration loading from environment variables"""

    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)

    def load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration from environment variables

        Returns:
            Dict[str, Any]: Configuration dictionary

        Raises:
            ValueError: If required environment variables are missing
        """
        try:
            config = {
                "vpn_connection_name": self._get_required_env("VPN_CONNECTION_NAME"),
                "remote_server_path": self._get_required_env("REMOTE_SERVER_PATH"),
                "excel_file_path": self._get_required_env("EXCEL_FILE_PATH"),
                "batch_documents_path": self._get_required_env("BATCH_DOCUMENTS_PATH"),
                "local_gdrive_path": self._get_required_env("LOCAL_GDRIVE_PATH"),
                "filter_criteria": {
                    "initials_column": self._get_required_env("INITIALS_COLUMN"),
                    "initials_value": self._get_required_env("INITIALS_VALUE"),
                    "release_status_column": self._get_required_env(
                        "RELEASE_STATUS_COLUMN"
                    ),
                },
                "notifications": {
                    "enabled": os.getenv("NOTIFICATIONS_ENABLED", "false").lower()
                    == "true",
                    "email": {
                        "smtp_server": os.getenv("SMTP_SERVER", ""),
                        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                        "from_address": os.getenv("FROM_EMAIL", ""),
                        "to_addresses": (
                            os.getenv("TO_EMAILS", "").split(",")
                            if os.getenv("TO_EMAILS")
                            else []
                        ),
                    },
                },
                "system": {
                    "test_mode": os.getenv("TEST_MODE", "false").lower() == "true",
                    "max_retry_attempts": int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
                    "transfer_timeout": int(
                        os.getenv("TRANSFER_TIMEOUT_SECONDS", "300")
                    ),
                    "log_level": os.getenv("LOG_LEVEL", "INFO"),
                    "log_retention_days": int(os.getenv("LOG_RETENTION_DAYS", "30")),
                },
            }

            self._validate_paths(config)
            self.logger.info(
                "Configuration loaded successfully from environment variables"
            )
            return config

        except Exception as e:
            self.logger.error(f"Configuration loading failed: {str(e)}")
            raise

    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable not set: {key}")
        return value.strip()

    def _validate_paths(self, config: Dict[str, Any]) -> None:
        """Validate that critical paths are accessible"""
        critical_paths = [
            ("remote_server_path", config["remote_server_path"]),
            ("excel_file_path", config["excel_file_path"]),
            ("batch_documents_path", config["batch_documents_path"]),
        ]

        warnings = []
        for name, path in critical_paths:
            if not Path(path).exists():
                warning_msg = f"Path not accessible: {name} = {path}"
                warnings.append(warning_msg)
                self.logger.warning(warning_msg)

        if warnings:
            self.logger.warning(
                "Some paths not accessible - may be expected if VPN not connected yet"
            )
