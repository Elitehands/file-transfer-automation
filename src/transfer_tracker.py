"""Transaction tracking for resumable file transfers"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class TransferTracker:
    """Tracks file transfer operations to support resumable transfers"""

    def __init__(self, log_directory: str = "logs", retention_days: int = 7):
        self.log_dir = Path(log_directory)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.transaction_file = self.log_dir / "transfer_transactions.json"
        self.retention_days = retention_days
        self.logger = logging.getLogger(__name__)
        self._ensure_transaction_file()
        self._cleanup_old_transactions()

    def _ensure_transaction_file(self):
        """Create transaction file if it doesn't exist"""
        if not self.transaction_file.exists():
            with open(self.transaction_file, "w") as f:
                json.dump({"transfers": [], "last_cleanup": datetime.now().isoformat()}, f)

    def _cleanup_old_transactions(self):
        """Remove old transfer records beyond retention period"""
        try:
            with open(self.transaction_file, "r") as f:
                data = json.load(f)
            
            last_cleanup = datetime.fromisoformat(data.get("last_cleanup", "2000-01-01T00:00:00"))
            

            if datetime.now() - last_cleanup < timedelta(days=1):
                return
                
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            

            data["transfers"] = [
                transfer for transfer in data["transfers"]
                if datetime.fromisoformat(transfer["timestamp"]) >= cutoff_date
            ]
            
            data["last_cleanup"] = datetime.now().isoformat()
            

            with open(self.transaction_file, "w") as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Cleaned up transfer transactions older than {self.retention_days} days")
            
        except Exception as e:
            self.logger.error(f"Error during transaction cleanup: {str(e)}")

    def record_transfer(self, batch_id: str, file_path: str, success: bool, 
                       source_path: str, dest_path: str):
        """
        Record a file transfer transaction
        
        Args:
            batch_id: Identifier for the batch
            file_path: Path of the transferred file (relative to batch folder)
            success: Whether transfer was successful
            source_path: Source file path
            dest_path: Destination file path
        """
        try:
            with open(self.transaction_file, "r") as f:
                data = json.load(f)
            

            transaction = {
                "batch_id": batch_id,
                "file_path": file_path,
                "success": success,
                "source_path": str(source_path),
                "dest_path": str(dest_path),
                "timestamp": datetime.now().isoformat(),
                "size_bytes": os.path.getsize(source_path) if os.path.exists(source_path) else 0
            }
            
            data["transfers"].append(transaction)
            
            # Save updated data
            with open(self.transaction_file, "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error recording transfer transaction: {str(e)}")

    def get_pending_transfers(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Get list of pending transfers for a batch
        
        Args:
            batch_id: Identifier for the batch
            
        Returns:
            List of pending transfer records
        """
        try:
            with open(self.transaction_file, "r") as f:
                data = json.load(f)
            
            # Find failed transfers for this batch
            pending_transfers = [
                transfer for transfer in data["transfers"]
                if transfer["batch_id"] == batch_id and not transfer["success"]
            ]
            
            return pending_transfers
            
        except Exception as e:
            self.logger.error(f"Error getting pending transfers: {str(e)}")
            return []

    def get_transfer_summary(self) -> Dict[str, Any]:
        """
        Get summary of all transfer operations
        
        Returns:
            Dictionary with transfer statistics
        """
        try:
            with open(self.transaction_file, "r") as f:
                data = json.load(f)
            
            total_transfers = len(data["transfers"])
            successful = sum(1 for t in data["transfers"] if t["success"])
            failed = total_transfers - successful
            
            batches = set(t["batch_id"] for t in data["transfers"])
            
            # Calculate total data transferred
            total_bytes = sum(t.get("size_bytes", 0) for t in data["transfers"] if t["success"])
            
            return {
                "total_transfers": total_transfers,
                "successful_transfers": successful,
                "failed_transfers": failed,
                "unique_batches": len(batches),
                "total_bytes_transferred": total_bytes,
                "human_readable_size": self._format_size(total_bytes),
                "last_transfer": data["transfers"][-1]["timestamp"] if data["transfers"] else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting transfer summary: {str(e)}")
            return {
                "error": str(e),
                "total_transfers": 0,
                "successful_transfers": 0,
                "failed_transfers": 0
            }
    
    def mark_transfer_complete(self, batch_id: str, file_path: str):
        """
        Mark a previously failed transfer as complete
        
        Args:
            batch_id: Identifier for the batch
            file_path: Path of the transferred file (relative to batch folder)
        """
        try:
            with open(self.transaction_file, "r") as f:
                data = json.load(f)
            

            for transfer in data["transfers"]:
                if (transfer["batch_id"] == batch_id and 
                    transfer["file_path"] == file_path and 
                    not transfer["success"]):
                    transfer["success"] = True
                    transfer["retry_timestamp"] = datetime.now().isoformat()
            

            with open(self.transaction_file, "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error marking transfer complete: {str(e)}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes into human readable size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"