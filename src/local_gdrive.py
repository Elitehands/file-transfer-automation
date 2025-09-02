"""Google Drive local mount verification and operations"""

import os
import logging
from pathlib import Path
from typing import bool


class LocalGDriveManager:
    """Manages Google Drive local mount operations"""

    def __init__(self, gdrive_path: str):
        self.gdrive_path = Path(gdrive_path)
        self.logger = logging.getLogger(__name__)

    def verify_gdrive_mount(self) -> bool:
        """Verify Google Drive is mounted and accessible"""
        try:
            if not self.gdrive_path.exists():
                self.logger.error(f"Google Drive path not found: {self.gdrive_path}")
                return False

            test_file = self.gdrive_path / ".test_write_access"
            test_file.touch()
            test_file.unlink()

            self.logger.info("Google Drive mount verified and writable")
            return True

        except Exception as e:
            self.logger.error(f"Google Drive verification failed: {str(e)}")
            return False
