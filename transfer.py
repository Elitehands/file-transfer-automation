#!/usr/bin/env python3
"""
Simplified File Transfer Automation
Transfers batch files from remote server to Google Drive based on Excel criteria
"""

import os
import sys
import json
import shutil
import logging
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration data class"""
    vpn_name: str
    remote_path: str
    excel_path: str
    batch_docs_path: str
    gdrive_path: str
    initials_column: str
    initials_value: str
    release_column: str
    test_mode: bool = False
    
    @classmethod
    def load(cls) -> 'Config':
        """Load config from settings.json with env overrides"""
        # Load base config
        config_file = Path("settings.json")
        if not config_file.exists():
            raise FileNotFoundError("settings.json not found")
            
        with open(config_file) as f:
            data = json.load(f)
        
        # Override with environment variables if present
        return cls(
            vpn_name=os.getenv("VPN_NAME", data["vpn_connection_name"]),
            remote_path=os.getenv("REMOTE_PATH", data["remote_server_path"]),
            excel_path=os.getenv("EXCEL_PATH", data["excel_file_path"]),
            batch_docs_path=os.getenv("BATCH_DOCS_PATH", data["batch_documents_path"]),
            gdrive_path=os.getenv("GDRIVE_PATH", data["local_gdrive_path"]),
            initials_column=data["filter_criteria"]["initials_column"],
            initials_value=os.getenv("INITIALS", data["filter_criteria"]["initials_value"]),
            release_column=data["filter_criteria"]["release_status_column"],
            test_mode=os.getenv("TEST_MODE", "").lower() == "true"
        )


class Logger:
    """Simple logging setup"""
    
    def __init__(self, level: str = "INFO"):
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Setup logger
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"logs/transfer_{datetime.now():%Y%m%d}.log")
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def info(self, msg: str): self.logger.info(msg)
    def error(self, msg: str): self.logger.error(msg)
    def warning(self, msg: str): self.logger.warning(msg)
    def debug(self, msg: str): self.logger.debug(msg)


class VPN:
    """Simple VPN management"""
    
    def __init__(self, vpn_name: str, test_mode: bool = False):
        self.vpn_name = vpn_name
        self.test_mode = test_mode
        self.logger = Logger().logger
    
    def is_connected(self) -> bool:
        """Check if VPN is connected"""
        if self.test_mode:
            return True
            
        try:
            result = subprocess.run(
                f'powershell "Get-VpnConnection -Name \'{self.vpn_name}\'"',
                capture_output=True, text=True, shell=True
            )
            return "ConnectionStatus : Connected" in result.stdout
        except Exception as e:
            self.logger.error(f"VPN check failed: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to VPN if not already connected"""
        if self.is_connected():
            self.logger.info("VPN already connected")
            return True
            
        if self.test_mode:
            self.logger.info("Test mode: Simulating VPN connection")
            return True
        
        try:
            self.logger.info(f"Connecting to VPN: {self.vpn_name}")
            result = subprocess.run(
                f'rasdial "{self.vpn_name}"',
                capture_output=True, text=True, shell=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"VPN connection failed: {e}")
            return False


class FileTransfer:
    """Main file transfer logic"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger().logger
        self.vpn = VPN(config.vpn_name, config.test_mode)
    
    def get_unreleased_batches(self) -> List[Dict[str, Any]]:
        """Get unreleased batches from Excel"""
        if self.config.test_mode:
            return [{"Batch ID": "TEST001", "Product": "Test Product"}]
        
        try:
            # Try different Excel engines
            for engine in ['openpyxl', 'pyxlsb']:
                try:
                    df = pd.read_excel(self.config.excel_path, engine=engine)
                    break
                except:
                    continue
            else:
                raise Exception("Could not read Excel file with any engine")
            
            # Filter for unreleased batches
            mask = (
                (df[self.config.initials_column].astype(str).str.upper() == self.config.initials_value.upper()) &
                (df[self.config.release_column].isna() | (df[self.config.release_column].astype(str).str.strip() == ""))
            )
            
            batches = df[mask].to_dict("records")
            self.logger.info(f"Found {len(batches)} unreleased batches")
            return batches
            
        except Exception as e:
            self.logger.error(f"Failed to read Excel: {e}")
            return []
    
    def find_batch_folder(self, batch_id: str) -> Optional[Path]:
        """Find batch folder by ID"""
        if self.config.test_mode:
            return Path(f"test_data/{batch_id}")
        
        batch_path = Path(self.config.batch_docs_path)
        for folder in batch_path.iterdir():
            if folder.is_dir() and batch_id.lower() in folder.name.lower():
                return folder
        return None
    
    def copy_batch_files(self, batch_id: str) -> Dict[str, Any]:
        """Copy files for a single batch"""
        result = {"batch_id": batch_id, "success": False, "files_copied": 0, "errors": []}
        
        try:
            # Find source folder
            source_folder = self.find_batch_folder(batch_id)
            if not source_folder:
                result["errors"].append(f"Source folder not found for {batch_id}")
                return result
            
            # Create destination folder
            dest_folder = Path(self.config.gdrive_path) / f"{batch_id}_{datetime.now():%Y%m%d}"
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy new/modified files only
            files_copied = 0
            if self.config.test_mode:
                self.logger.info(f"Test mode: Would copy files from {source_folder} to {dest_folder}")
                files_copied = 3  # Simulate copying files
            else:
                for file_path in source_folder.rglob("*"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(source_folder)
                        dest_file = dest_folder / rel_path
                        
                        # Skip if file already exists and is identical
                        if self._should_copy_file(file_path, dest_file):
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, dest_file)
                            files_copied += 1
            
            result["files_copied"] = files_copied
            result["success"] = True
            self.logger.info(f"Copied {files_copied} files for batch {batch_id}")
            
        except Exception as e:
            error_msg = f"Failed to process batch {batch_id}: {e}"
            result["errors"].append(error_msg)
            self.logger.error(error_msg)
        
        return result
    
    def _should_copy_file(self, source: Path, dest: Path) -> bool:
        """Check if file should be copied (new or modified)"""
        if not dest.exists():
            return True
        
        # Compare modification time and size
        source_stat = source.stat()
        dest_stat = dest.stat()
        
        return (source_stat.st_mtime > dest_stat.st_mtime or 
                source_stat.st_size != dest_stat.st_size)
    
    def run(self) -> int:
        """Main execution flow"""
        try:
            self.logger.info("Starting file transfer automation")
            
            # 1. Connect to VPN
            if not self.vpn.connect():
                self.logger.error("VPN connection failed")
                return 1
            
            # 2. Verify paths exist
            if not self.config.test_mode:
                for path_name, path_value in [
                    ("Remote path", self.config.remote_path),
                    ("Google Drive", self.config.gdrive_path)
                ]:
                    if not Path(path_value).exists():
                        self.logger.error(f"{path_name} not accessible: {path_value}")
                        return 1
            
            # 3. Get unreleased batches
            batches = self.get_unreleased_batches()
            if not batches:
                self.logger.info("No batches to process")
                return 0
            
            # 4. Process each batch
            total_files = 0
            successful_batches = 0
            
            for batch in batches:
                batch_id = self._extract_batch_id(batch)
                result = self.copy_batch_files(batch_id)
                
                if result["success"]:
                    successful_batches += 1
                    total_files += result["files_copied"]
                else:
                    for error in result["errors"]:
                        self.logger.error(error)
            
            # 5. Summary
            self.logger.info(f"Transfer complete: {successful_batches}/{len(batches)} batches, {total_files} files")
            return 0
            
        except Exception as e:
            self.logger.error(f"Critical error: {e}")
            return 1
    
    def _extract_batch_id(self, batch_record: Dict[str, Any]) -> str:
        """Extract batch ID from record"""
        for key in ["Batch ID", "BatchID", "Batch_ID", "ID"]:
            if key in batch_record and batch_record[key]:
                return str(batch_record[key]).strip()
        return f"Unknown_{datetime.now():%Y%m%d_%H%M%S}"


def main():
    """Main entry point"""
    try:
        # Load configuration
        config = Config.load()
        
        # Override with command line flags
        if "--test-mode" in sys.argv:
            config.test_mode = True
        
        # Run file transfer
        transfer = FileTransfer(config)
        return transfer.run()
        
    except Exception as e:
        print(f"Startup error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())