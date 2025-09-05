"""File processor for transferring batch files"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from .drive_manager import DriveManager


class FileProcessor:
    """Processes file transfers from source to destination"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.drive_manager = DriveManager(config)
        
    def initialize(self) -> bool:
        """Initialize the file processor and verify drives"""
        self.logger.info(f"File processor initializing - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"User: {os.getenv('USERNAME', 'Unknown')}")
        
        drive_status = self.drive_manager.verify_drives()
        
        if not drive_status["remote"]:
            self.logger.error("Remote server (Z: drive) not accessible or not writable")
            return False
            
        if not drive_status["gdrive"]:
            self.logger.error("Google Drive (G: drive) not accessible or not writable")
            return False
        
        self.logger.info("File processor initialized successfully")
        return True
        
    def process_batch(self, batch_id: str) -> Dict[str, Any]:
        """
        Process files for a single batch
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            dict: Results of batch processing
        """
        result = {
            "batch_id": batch_id,
            "success": False,
            "files_copied": 0,
            "errors": []
        }
        
        try:
            self.logger.info(f"Processing batch: {batch_id}")
            
            source_folder = self._find_batch_folder(batch_id)
            if not source_folder:
                error_msg = f"Source folder not found for batch {batch_id}"
                self.logger.error(error_msg)
                result["errors"].append(error_msg)
                return result
            
            dest_folder = self.drive_manager.create_destination_folder(batch_id)
            if not dest_folder:
                error_msg = f"Failed to create destination folder for batch {batch_id}"
                self.logger.error(error_msg)
                result["errors"].append(error_msg)
                return result
                
            source_files = list(source_folder.glob("**/*"))
            source_files = [f for f in source_files if f.is_file()]
            
            if not source_files:
                self.logger.warning(f"No files found in source folder for batch {batch_id}")
                result["success"] = True  
                return result
                
            for source_file in source_files:
                rel_path = source_file.relative_to(source_folder)
                dest_file = dest_folder / rel_path
                
                if self.drive_manager.copy_file(source_file, dest_file):
                    result["files_copied"] += 1
                else:
                    error_msg = f"Failed to copy {rel_path}"
                    self.logger.error(error_msg)
                    result["errors"].append(error_msg)
            
            if result["files_copied"] > 0:
                result["success"] = True
                self.logger.info(f"Successfully copied {result['files_copied']} files for batch {batch_id}")
            else:
                self.logger.error(f"No files copied for batch {batch_id}")
                
            return result
                
        except Exception as e:
            error_msg = f"Error processing batch {batch_id}: {str(e)}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
            return result
    
    def _find_batch_folder(self, batch_id: str) -> Optional[Path]:
        """Find the source folder for a given batch ID"""
        batch_documents_path = Path(self.config["batch_documents_path"])

        try:
            all_folders = [folder for folder in batch_documents_path.iterdir() if folder.is_dir()]
            
            folder_map = {folder.name.lower(): folder for folder in all_folders}
            
            if batch_id.lower() in folder_map:
                folder = folder_map[batch_id.lower()]
                self.logger.debug(f"Found exact batch folder match: {folder}")
                return folder
                
            for lower_name, folder in folder_map.items():
                if batch_id.lower() in lower_name:
                    self.logger.debug(f"Found batch folder containing ID: {folder}")
                    return folder

            self.logger.warning(f"No folder found for batch ID: {batch_id}")
            return None

        except Exception as e:
            self.logger.error(f"Error searching for batch folder {batch_id}: {str(e)}")
            return None
    
    def process_batches(self, batches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple batches
        
        Args:
            batches: List of batch dictionaries with at least 'Batch ID' key
            
        Returns:
            dict: Summary of processing results
        """
        results = {
            "total_batches": len(batches),
            "successful_transfers": 0,
            "failed_transfers": 0,
            "total_files_copied": 0,
            "batch_details": [],
            "errors": []
        }
        
        if not self.initialize():
            results["errors"].append("Failed to initialize file processor - drives not accessible")
            return results
        
        for batch in batches:
            batch_id = batch.get("Batch ID")
            if not batch_id:
                self.logger.warning("Skipping batch with no Batch ID")
                continue
                
            batch_result = self.process_batch(batch_id)
            results["batch_details"].append(batch_result)
            
            if batch_result["success"]:
                results["successful_transfers"] += 1
            else:
                results["failed_transfers"] += 1
                
            results["total_files_copied"] += batch_result["files_copied"]
        
        self.logger.info(f"Batch processing complete. Success: {results['successful_transfers']}, Failed: {results['failed_transfers']}")
        return results