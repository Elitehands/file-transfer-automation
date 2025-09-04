"""Drive management for file transfer operations"""

import os
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union, Dict, Tuple


class DriveManager:
    """Manages remote and local drive operations"""

    def __init__(self, config=None):
        """
        Initialize the drive manager
        
        Args:
            config: Optional configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config  

    def is_path_accessible(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is accessible
        
        Args:
            path: Path to check (string or Path object)
            
        Returns:
            bool: True if accessible, False otherwise
        """
        try:
            self.logger.debug(f"Checking if path is accessible: {path}")

            path_obj = Path(path) if isinstance(path, str) else path
            return path_obj.exists()
        except Exception as e:
            self.logger.error(f"Error checking path accessibility: {str(e)}")
            return False

    def create_directory(self, path: Union[str, Path]) -> bool:
        """
        Create a directory if it doesn't exist
        
        Args:
            path: Path to create (string or Path object)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Creating directory: {path}")

            path_obj = Path(path) if isinstance(path, str) else path
            path_obj.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory: {str(e)}")
            return False

    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """
        Copy a file from source to destination
        
        Args:
            source: Source file path (string or Path object)
            destination: Destination file path (string or Path object)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            source_path = Path(source) if isinstance(source, str) else source
            dest_path = Path(destination) if isinstance(destination, str) else destination
            
            self.logger.debug(f"Copying file: {source_path} -> {dest_path}")
            
            self.create_directory(dest_path.parent)
            
            shutil.copy2(source_path, dest_path)
            
            if not dest_path.exists() or dest_path.stat().st_size != source_path.stat().st_size:
                self.logger.error(f"File verification failed for {dest_path}")
                return False
                
            self.logger.info(f"File copied successfully: {dest_path.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error copying file {source}: {str(e)}")
            return False

    def list_files(self, directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """
        List all files in a directory matching pattern
        
        Args:
            directory: Directory to scan (string or Path object)
            pattern: File pattern to match
            
        Returns:
            List of paths to matching files
        """
        try:
            dir_path = Path(directory) if isinstance(directory, str) else directory
            
            self.logger.debug(f"Listing files in {dir_path} with pattern '{pattern}'")
            
            if not dir_path.exists():
                self.logger.warning(f"Directory does not exist: {dir_path}")
                return []
                
            return list(dir_path.glob(pattern))
        except Exception as e:
            self.logger.error(f"Error listing files in {directory}: {str(e)}")
            return []

    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """
        Get the size of a file in bytes
        
        Args:
            file_path: Path to the file (string or Path object)
            
        Returns:
            int: File size in bytes, or None if error
        """
        try:
            path_obj = Path(file_path) if isinstance(file_path, str) else file_path
            return path_obj.stat().st_size
        except Exception as e:
            self.logger.error(f"Error getting file size for {file_path}: {str(e)}")
            return None

    def verify_path_writable(self, path: Union[str, Path]) -> bool:
        """
        Verify that a path is writable by creating and deleting a test file
        
        Args:
            path: Path to verify (string or Path object)
            
        Returns:
            bool: True if writable, False otherwise
        """
        try:
            path_obj = Path(path) if isinstance(path, str) else path
            
            if not path_obj.exists():
                self.logger.error(f"Path does not exist: {path_obj}")
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_file = path_obj / f".test_write_{timestamp}.tmp"
            
            test_file.touch()
            
            if not test_file.exists():
                self.logger.error(f"Could not create test file at {test_file}")
                return False
                
            test_file.unlink()
            self.logger.debug(f"Path {path_obj} verified as writable")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying path writability: {str(e)}")
            return False

    def verify_drives(self) -> Dict[str, bool]:
        """
        Verify that both remote and local paths are accessible and writable
        
        Returns:
            dict: Status of each drive path {"remote": bool, "gdrive": bool}
        """
        results = {"remote": False, "gdrive": False}
        
        try:
            self.logger.debug("Verifying drive access...")
            
            if not self.config:
                self.logger.error("No config provided for drive verification")
                return results
                
            # Support both new nested and old flat config format
            if "paths" in self.config:
                remote_path = self.config["paths"].get("remote_server")
                local_path = self.config["paths"].get("local_gdrive")
            else:
                remote_path = self.config.get("remote_server_path")
                local_path = self.config.get("local_gdrive_path")
            
            if not self.is_path_accessible(remote_path):
                self.logger.error(f"Remote path not accessible: {remote_path}")
            else:
                results["remote"] = self.verify_path_writable(remote_path)
                
            if not self.is_path_accessible(local_path):
                self.logger.error(f"Google Drive path not accessible: {local_path}")
            else:
                results["gdrive"] = self.verify_path_writable(local_path)
            
            if results["remote"] and results["gdrive"]:
                self.logger.info("All drive paths verified and writable")
            else:
                self.logger.warning(f"Drive verification issues: {results}")
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error verifying drives: {str(e)}")
            return results
            
    def create_destination_folder(self, batch_id: str) -> Optional[Path]:
        """
        Create a destination folder for batch files with timestamp
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Path object to created folder or None if failed
        """
        try:
            if not self.config:
                self.logger.error("No config provided for destination folder creation")
                return None
                
            # Support both new nested and old flat config format
            if "paths" in self.config:
                gdrive_path = Path(self.config["paths"].get("local_gdrive"))
            else:
                gdrive_path = Path(self.config.get("local_gdrive_path"))
                
            timestamp = datetime.now().strftime("%Y%m%d")
            dest_folder = gdrive_path / f"{batch_id}_{timestamp}"
            
            self.logger.info(f"Creating destination folder: {dest_folder}")
            
            if self.create_directory(dest_folder):
                return dest_folder
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating destination folder: {str(e)}")
            return None

    def verify_gdrive_mount(self) -> bool:
        """
        Verify Google Drive is mounted and accessible
        
        Returns:
            bool: True if Google Drive is accessible and writable
        """
        if not self.config:
            self.logger.error("No config provided for drive verification")
            return False
            
        # Support both new nested and old flat config format
        if "paths" in self.config:
            gdrive_path = self.config["paths"].get("local_gdrive")
        else:
            gdrive_path = self.config.get("local_gdrive_path")
            
        return self.verify_path_writable(gdrive_path)