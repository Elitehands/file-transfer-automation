"""Core file transfer functionality - batch processing and file operations"""

import shutil
import logging
import sys
import io
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import pandas as pd

logger = logging.getLogger(__name__)


def copy_excel_status_log(source_excel_path: str, dest_gdrive_path: str) -> str:
    """Copy Excel status log from shared drive to Google Drive first"""
    source_path = Path(source_excel_path)
    if not source_path.exists():
        logger.error(f"Excel file not found at source: {source_excel_path}")
        return source_excel_path
    
    dest_folder = Path(dest_gdrive_path)
    dest_folder.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_file = dest_folder / f"Product_status_Log_{timestamp}.xlsx"
    
    try:
        shutil.copy2(source_path, dest_file)
        logger.info(f"Excel status log copied to: {dest_file}")
        return str(dest_file)
    except Exception as e:
        logger.error(f"Failed to copy Excel status log: {e}")
        return source_excel_path


def get_processed_batches_from_logs() -> Set[str]:
    """Extract previously processed batch IDs from log files"""
    processed_batches = set()
    log_dir = Path("logs")
    
    if not log_dir.exists():
        return processed_batches
    
    pattern = re.compile(r"Successfully processed batch ([^:]+):")
    
    for log_file in log_dir.glob("file_transfer_*.log"):
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    match = pattern.search(line)
                    if match:
                        processed_batches.add(match.group(1).strip())
        except Exception as e:
            logger.warning(f"Could not read log file {log_file}: {e}")
    
    logger.info(f"Found {len(processed_batches)} previously processed batches in logs")
    return processed_batches


def filter_new_batches(batches: List[Dict[str, Any]], processed_batches: Set[str]) -> List[Dict[str, Any]]:
    """Filter out already processed batches"""
    if not processed_batches:
        return batches
    
    new_batches = []
    for batch in batches:
        batch_id = get_batch_id(batch)
        if batch_id not in processed_batches:
            new_batches.append(batch)
    
    logger.info(f"Filtered to {len(new_batches)} new batches (from {len(batches)} total)")
    return new_batches


def count_source_files(source_folder: Path) -> int:
    """Count total files in source folder"""
    if not source_folder.exists():
        return 0
    return len([f for f in source_folder.glob("**/*") if f.is_file()])


def copy_batch_files(source_folder: Path, dest_folder: Path) -> Dict[str, Any]:
    """Copy all files from source to destination with detailed counting"""
    result = {"files_copied": 0, "source_file_count": 0, "errors": []}
    
    result["source_file_count"] = count_source_files(source_folder)
    
    if result["source_file_count"] == 0:
        logger.warning(f"No files found in source folder: {source_folder}")
        return result

    dest_folder.mkdir(parents=True, exist_ok=True)
    source_files = [f for f in source_folder.glob("**/*") if f.is_file()]

    logger.info(f"Found {result['source_file_count']} files to copy from {source_folder}")

    for source_file in source_files:
        try:
            rel_path = source_file.relative_to(source_folder)
            dest_file = dest_folder / rel_path

            dest_file.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source_file, dest_file)
            result["files_copied"] += 1

        except Exception as e:
            error_msg = f"Failed to copy {source_file.name}: {e}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
    
    if result["files_copied"] == result["source_file_count"]:
        logger.info(f"Successfully copied all {result['files_copied']} files")
    else:
        logger.warning(f"Copied {result['files_copied']}/{result['source_file_count']} files")

    return result


def process_single_batch(batch_id: str, paths: Dict[str, str]) -> Dict[str, Any]:
    """Process files for a single batch with detailed file counting"""
    result = {
        "batch_id": batch_id,
        "success": False,
        "files_copied": 0,
        "source_file_count": 0,
        "copy_success_rate": 0.0,
        "errors": []
    }

    try:
        source_folder = find_batch_folder(batch_id, paths["batch_documents"])
        if not source_folder:
            result["errors"].append(f"Source folder not found for {batch_id}")
            return result

        timestamp = datetime.now().strftime("%Y%m%d")
        dest_folder = Path(paths["local_gdrive"]) / f"{batch_id}_{timestamp}"

        copy_result = copy_batch_files(source_folder, dest_folder)
        result["files_copied"] = copy_result["files_copied"]
        result["source_file_count"] = copy_result["source_file_count"]
        result["errors"].extend(copy_result["errors"])
        
        if result["source_file_count"] > 0:
            result["copy_success_rate"] = (result["files_copied"] / result["source_file_count"]) * 100
        
        result["success"] = result["files_copied"] > 0 and result["copy_success_rate"] == 100.0

        if result["success"]:
            logger.info(
                f"Successfully processed batch {batch_id}: "
                f"{result['files_copied']}/{result['source_file_count']} files "
                f"({result['copy_success_rate']:.1f}% success rate)"
            )
        else:
            logger.warning(
                f"Partial success for batch {batch_id}: "
                f"{result['files_copied']}/{result['source_file_count']} files copied"
            )

        return result

    except Exception as e:
        error_msg = f"Error processing batch {batch_id}: {e}"
        result["errors"].append(error_msg)
        logger.error(error_msg)
        return result


def process_all_batches(batches: List[Dict[str, Any]], paths: Dict[str, str]) -> Dict[str, Any]:
    """Process all batches and return detailed summary with file counts"""
    # Copy Excel status log first
    if "excel_file" in paths:
        copy_excel_status_log(paths["excel_file"], paths["local_gdrive"])
    
    # Get previously processed batches
    processed_batches = get_processed_batches_from_logs()
    
    # Filter to only new batches
    new_batches = filter_new_batches(batches, processed_batches)
    
    if not new_batches:
        logger.info("No new batches to process")
        return {
            "total_batches": len(batches),
            "successful_transfers": 0,
            "failed_transfers": 0,
            "partial_transfers": 0,
            "total_files_copied": 0,
            "total_source_files": 0,
            "overall_success_rate": 100.0,
            "batch_details": [],
            "skipped_batches": len(batches)
        }

    summary = {
        "total_batches": len(new_batches),
        "successful_transfers": 0,
        "failed_transfers": 0,
        "partial_transfers": 0,
        "total_files_copied": 0,
        "total_source_files": 0,
        "overall_success_rate": 0.0,
        "batch_details": [],
        "skipped_batches": len(batches) - len(new_batches)
    }

    for batch in new_batches:
        batch_id = get_batch_id(batch)
        result = process_single_batch(batch_id, paths)

        summary["batch_details"].append(result)
        summary["total_files_copied"] += result["files_copied"]
        summary["total_source_files"] += result["source_file_count"]

        if result["success"]:
            summary["successful_transfers"] += 1
        elif result["files_copied"] > 0:
            summary["partial_transfers"] += 1
        else:
            summary["failed_transfers"] += 1
    
    if summary["total_source_files"] > 0:
        summary["overall_success_rate"] = (summary["total_files_copied"] / summary["total_source_files"]) * 100

    logger.info(
        f"Batch processing complete: "
        f"{summary['successful_transfers']} successful, "
        f"{summary['partial_transfers']} partial, "
        f"{summary['failed_transfers']} failed, "
        f"{summary['skipped_batches']} skipped | "
        f"Files: {summary['total_files_copied']}/{summary['total_source_files']} "
        f"({summary['overall_success_rate']:.1f}% success rate)"
    )
    return summary


def read_excel_batches(excel_path: str, initials_col: str, initials_val: str, release_col: str, excel_password: str = None) -> List[Dict[str, Any]]:
    """Read Excel file with proper format and password handling"""
    if not Path(excel_path).exists():
        logger.warning(f"Excel file not found: {excel_path}")
        return []

    try:
        file_ext = Path(excel_path).suffix.lower()
        logger.info(f"Processing Excel file: {excel_path} (format: {file_ext})")
        
        # Select appropriate engine based on file extension
        if file_ext == '.xlsb':
            engine = 'pyxlsb'
        elif file_ext in ['.xlsx', '.xlsm']:
            engine = 'openpyxl'
        elif file_ext == '.xls':
            engine = 'xlrd'
        else:
            engine = 'openpyxl'
            logger.warning(f"Unknown Excel format: {file_ext}, using openpyxl")

        # Try password approach first if password provided
        if excel_password:
            try:
                import msoffcrypto
                
                with open(excel_path, 'rb') as file:
                    office_file = msoffcrypto.OfficeFile(file)
                    
                    if office_file.is_encrypted():
                        logger.info("File is encrypted, decrypting with password...")
                        office_file.load_key(password=excel_password)
                        
                        decrypted = io.BytesIO()
                        office_file.decrypt(decrypted)
                        decrypted.seek(0)
                        
                        df = pd.read_excel(decrypted, engine=engine)
                        logger.info("Successfully decrypted and loaded data")
                    else:
                        logger.info("File is not encrypted, reading directly")
                        df = pd.read_excel(excel_path, engine=engine)
                        
            except ImportError:
                logger.error("msoffcrypto-tool required for password-protected files. Install with: pip install msoffcrypto-tool")
                return []
            except Exception as e:
                logger.error(f"Failed to read with password method: {e}")
                # Fall back to direct reading
                logger.info("Attempting direct file reading...")
                try:
                    df = pd.read_excel(excel_path, engine=engine)
                    logger.info("Successfully loaded data directly")
                except Exception as fallback_error:
                    logger.error(f"Direct reading also failed: {fallback_error}")
                    return []
        else:
            # No password provided, try direct reading
            try:
                df = pd.read_excel(excel_path, engine=engine)
                logger.info("Successfully loaded data directly")
            except Exception as e:
                logger.error(f"Failed to read Excel file: {e}")
                return []

        logger.info(f"Excel data loaded: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Available columns: {list(df.columns)}")

        # Filter data
        logger.info(f"Filtering by {initials_col}='{initials_val}' and empty {release_col}")
        
        filtered_df = df[
            (df[initials_col].astype(str).str.upper() == initials_val.upper()) &
            (df[release_col].isna() | (df[release_col].astype(str).str.strip() == ""))
        ]

        batches = filtered_df.to_dict("records")
        logger.info(f"Found {len(batches)} unreleased batches for {initials_val}")
        
        if len(batches) > 0:
            logger.info(f"Sample batch IDs: {[get_batch_id(b) for b in batches[:3]]}")
        
        return batches

    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return []


def get_batch_id(batch_record: Dict[str, Any]) -> str:
    """Extract batch ID from record"""
    possible_columns = ["Batch ID", "BatchID", "Batch_ID", "ID", "batch_id"]
    for col in possible_columns:
        if col in batch_record and batch_record[col]:
            return str(batch_record[col]).strip()
    return "Unknown"


def find_batch_folder(batch_id: str, batch_docs_path: str) -> Optional[Path]:
    """Find source folder for batch ID"""
    batch_docs = Path(batch_docs_path)
    if not batch_docs.exists():
        logger.error(f"Batch documents path does not exist: {batch_docs_path}")
        return None

    # First try exact match
    for folder in batch_docs.iterdir():
        if folder.is_dir() and folder.name.lower() == batch_id.lower():
            logger.info(f"Found exact match for batch {batch_id}: {folder}")
            return folder

    # Then try partial match
    for folder in batch_docs.iterdir():
        if folder.is_dir() and batch_id.lower() in folder.name.lower():
            logger.info(f"Found partial match for batch {batch_id}: {folder}")
            return folder

    logger.warning(f"No folder found for batch ID: {batch_id}")
    return None


if __name__ == "__main__":
    import argparse
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.settings import load_config, get_paths, get_filter_criteria
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Test File Transfer")
    parser.add_argument("--config", default="test_settings.json", help="Config file")
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
        paths = get_paths(config)
        criteria = get_filter_criteria(config)
        excel_password = config.get("excel", {}).get("password", None)
        
        batches = read_excel_batches(
            paths["excel_file"], criteria["initials_column"], 
            criteria["initials_value"], criteria["release_status_column"],
            excel_password
        )
        
        logger.info(f"Transfer test: Found {len(batches)} batches")
        
    except Exception as e:
        logger.error(f"Transfer test failed: {e}")
        sys.exit(1)