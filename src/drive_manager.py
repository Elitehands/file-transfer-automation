"""Drive management for file transfer operations"""

import os
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Union


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

    def verify_drives(self):
        """
        Verify that both remote and local paths are accessible
        
        Returns:
            bool: True if both paths are accessible, False otherwise
        """
        try:
            self.logger.debug("Verifying drive access...")
            

            if self.config:
                remote_path = self.config["remote_server_path"]
                local_path = self.config["local_gdrive_path"]
                

                if not self.is_path_accessible(remote_path):
                    self.logger.error(f"Remote path not accessible: {remote_path}")
                    return False
                    

                if not self.is_path_accessible(local_path):
                    self.logger.error(f"Local path not accessible: {local_path}")
                    return False
                
                self.logger.info("All drive paths verified successfully")
                return True
            else:

                self.logger.debug("No config provided for drive verification")
                return True
            
        except Exception as e:
            self.logger.error(f"Error verifying drives: {str(e)}")
            return False