"""Drive and network path management"""

import os
import logging
from pathlib import Path

# from typing import bool  # bool is built-in in Python 3.9+


class DriveManager:
    """Manages drive mounting and accessibility verification"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_drives(self, remote_path: str, local_gdrive_path: str) -> bool:
        """
        Verify that both remote and local drives are accessible

        Args:
            remote_path: Path to remote server (Z: drive)
            local_gdrive_path: Path to local Google Drive (G: drive)

        Returns:
            bool: True if both drives accessible, False otherwise
        """
        try:
            if not self.is_path_accessible(remote_path):
                self.logger.error(f"Remote drive not accessible: {remote_path}")
                return False

            if not self.is_path_accessible(local_gdrive_path):
                self.logger.warning(
                    f"Local Google Drive path not found, creating: {local_gdrive_path}"
                )
                if not self.create_directory(local_gdrive_path):
                    return False

            self.logger.info("All drives verified and accessible")
            return True

        except Exception as e:
            self.logger.error(f"Drive verification failed: {str(e)}")
            return False

    def is_path_accessible(self, path: str) -> bool:
        """
        Check if a path is accessible

        Args:
            path: File system path to check

        Returns:
            bool: True if accessible, False otherwise
        """
        try:
            path_obj = Path(path)
            return path_obj.exists() and os.access(path, os.R_OK)
        except Exception as e:
            self.logger.debug(f"Path access check failed for {path}: {str(e)}")
            return False

    def create_directory(self, path: str) -> bool:
        """
        Create directory if it doesn't exist

        Args:
            path: Directory path to create

        Returns:
            bool: True if created successfully, False otherwise
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {path}: {str(e)}")
            return False
