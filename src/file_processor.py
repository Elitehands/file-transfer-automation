"""File processing and copying operations"""

import os
import shutil
import hashlib
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple


class FileProcessor:
    """Handles file discovery, copying, and verification"""
    
    def __init__(self, config: Dict[str, Any], test_mode: bool = False):
        self.config = config
        self.test_mode = test_mode
        self.logger = logging.getLogger(__name__)
        self.transfer_log_path = Path('logs/transfer_history.json')
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Ensure logs directory exists"""
        self.transfer_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def process_batches(self, batches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process list of batches for file transfer
        
        Args:
            batches: List of batch records from Excel
            
        Returns:
            Dict[str, Any]: Transfer results summary
        """
        results = {
            'total_batches': len(batches),
            'successful_transfers': 0,
            'failed_transfers': 0,
            'total_files_copied': 0,
            'errors': [],
            'batch_details': []
        }
        
        for batch in batches:
            try:
                batch_id = self._get_batch_id(batch)
                self.logger.info(f"Processing batch: {batch_id}")
                
                batch_result = self.process_single_batch(batch_id, batch)
                results['batch_details'].append(batch_result)
                
                if batch_result['success']:
                    results['successful_transfers'] += 1
                    results['total_files_copied'] += batch_result['files_copied']
                else:
                    results['failed_transfers'] += 1
                    results['errors'].extend(batch_result['errors'])
                    
            except Exception as e:
                error_msg = f"Failed to process batch {batch.get('Batch ID', 'Unknown')}: {str(e)}"
                self.logger.error(error_msg)
                results['failed_transfers'] += 1
                results['errors'].append(error_msg)
        
        self._save_transfer_log(results)
        return results
    
    def process_single_batch(self, batch_id: str, batch_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single batch for file transfer
        
        Args:
            batch_id: Unique identifier for the batch
            batch_record: Full batch record from Excel
            
        Returns:
            Dict[str, Any]: Processing results for this batch
        """
        result = {
            'batch_id': batch_id,
            'success': False,
            'files_copied': 0,
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            source_folder = self._find_batch_folder(batch_id)
            if not source_folder:
                error_msg = f"Source folder not found for batch: {batch_id}"
                result['errors'].append(error_msg)
                return result
            
            dest_folder = self._create_destination_folder(batch_id)
            if not dest_folder:
                error_msg = f"Failed to create destination folder for batch: {batch_id}"
                result['errors'].append(error_msg)
                return result
            
            files_to_copy = self._get_new_files(source_folder, dest_folder)
            
            if not files_to_copy:
                self.logger.info(f"No new files to copy for batch: {batch_id}")
                result['success'] = True
                return result
            
            copied_count = self._copy_files(files_to_copy, source_folder, dest_folder)
            
            result['files_copied'] = copied_count
            result['success'] = copied_count == len(files_to_copy)
            
            if result['success']:
                self.logger.info(f"Successfully copied {copied_count} files for batch: {batch_id}")
            else:
                error_msg = f"Only copied {copied_count}/{len(files_to_copy)} files for batch: {batch_id}"
                result['errors'].append(error_msg)
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing batch {batch_id}: {str(e)}"
            self.logger.error(error_msg)
            result['errors'].append(error_msg)
            return result
    
    def _find_batch_folder(self, batch_id: str) -> Path:
        """Find the source folder for a given batch ID"""
        batch_documents_path = Path(self.config['batch_documents_path'])
        
        if self.test_mode:
            test_path = Path('mock_data/batch_documents') / batch_id
            return test_path if test_path.exists() else None
        
        try:
            for folder in batch_documents_path.iterdir():
                if folder.is_dir() and batch_id.lower() in folder.name.lower():
                    self.logger.debug(f"Found batch folder: {folder}")
                    return folder
            
            self.logger.warning(f"No folder found for batch ID: {batch_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching for batch folder {batch_id}: {str(e)}")
            return None
    
    def _create_destination_folder(self, batch_id: str) -> Path:
        """Create destination folder for batch"""
        try:
            if self.test_mode:
                dest_base = Path('mock_data/gdrive_destination')
            else:
                dest_base = Path(self.config['local_gdrive_path'])
            
            timestamp = datetime.now().strftime('%Y%m%d')
            dest_folder = dest_base / f"{batch_id}_{timestamp}"
            
            dest_folder.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created destination folder: {dest_folder}")
            return dest_folder
            
        except Exception as e:
            self.logger.error(f"Failed to create destination folder for {batch_id}: {str(e)}")
            return None
    
    def _get_new_files(self, source_folder: Path, dest_folder: Path) -> List[Path]:
        """Get list of files that need to be copied (new or modified)"""
        try:
            if not source_folder.exists():
                return []
            
            new_files = []
            
            for file_path in source_folder.rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(source_folder)
                    dest_file = dest_folder / rel_path
                    
                    if self._should_copy_file(file_path, dest_file):
                        new_files.append(file_path)
            
            self.logger.info(f"Found {len(new_files)} files to copy from {source_folder}")
            return new_files
            
        except Exception as e:
            self.logger.error(f"Error getting file list from {source_folder}: {str(e)}")
            return []
    
    def _should_copy_file(self, source_file: Path, dest_file: Path) -> bool:
        """Determine if a file should be copied"""
        try:
            if not dest_file.exists():
                return True
            
            source_mtime = source_file.stat().st_mtime
            dest_mtime = dest_file.stat().st_mtime
            
            if source_mtime > dest_mtime:
                self.logger.debug(f"Source file newer: {source_file.name}")
                return True
            
            source_size = source_file.stat().st_size
            dest_size = dest_file.stat().st_size
            
            if source_size != dest_size:
                self.logger.debug(f"File size different: {source_file.name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error comparing files, will copy: {str(e)}")
            return True
    
    def _copy_files(self, files_to_copy: List[Path], source_folder: Path, 
                   dest_folder: Path) -> int:
        """Copy files from source to destination"""
        copied_count = 0
        
        for file_path in files_to_copy:
            try:
                rel_path = file_path.relative_to(source_folder)
                dest_file = dest_folder / rel_path
                
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                if self.test_mode:
                    dest_file.touch()
                    self.logger.debug(f"Test mode: Created placeholder file {dest_file}")
                else:
                    shutil.copy2(file_path, dest_file)
                    self.logger.debug(f"Copied: {file_path} -> {dest_file}")
                
                if self._verify_file_copy(file_path, dest_file):
                    copied_count += 1
                else:
                    self.logger.error(f"File verification failed: {file_path}")
                    
            except Exception as e:
                self.logger.error(f"Failed to copy {file_path}: {str(e)}")
        
        return copied_count
    
    def _verify_file_copy(self, source_file: Path, dest_file: Path) -> bool:
        """Verify that file was copied correctly"""
        try:
            if self.test_mode:
                return dest_file.exists()
            
            if not dest_file.exists():
                return False
            
            if source_file.stat().st_size != dest_file.stat().st_size:
                return False
            
            if source_file.stat().st_size < 10 * 1024 * 1024:  # 10MB threshold
                return self._compare_checksums(source_file, dest_file)
            
            return True
            
        except Exception as e:
            self.logger.error(f"File verification error: {str(e)}")
            return False
    
    def _compare_checksums(self, file1: Path, file2: Path) -> bool:
        """Compare MD5 checksums of two files"""
        try:
            hash1 = self._calculate_md5(file1)
            hash2 = self._calculate_md5(file2)
            return hash1 == hash2
        except Exception as e:
            self.logger.warning(f"Checksum comparison failed: {str(e)}")
            return True  
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_batch_id(self, batch_record: Dict[str, Any]) -> str:
        """Extract batch ID from record"""
        possible_columns = ['Batch ID', 'BatchID', 'Batch_ID', 'ID', 'Batch Number']
        
        for col in possible_columns:
            if col in batch_record and batch_record[col]:
                return str(batch_record[col]).strip()
        
        return f"Unknown_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _save_transfer_log(self, results: Dict[str, Any]):
        """Save transfer results to log file"""
        try:
            if self.transfer_log_path.exists():
                with open(self.transfer_log_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'transfers': []}
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            log_data['transfers'].append(log_entry)
            
            log_data['transfers'] = log_data['transfers'][-100:]
            
            # Save updated log
            with open(self.transfer_log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save transfer log: {str(e)}")
