"""Core file transfer functionality - batch processing and file operations"""

import shutil
import logging
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


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
    summary = {
        "total_batches": len(batches),
        "successful_transfers": 0,
        "failed_transfers": 0,
        "partial_transfers": 0,
        "total_files_copied": 0,
        "total_source_files": 0,
        "overall_success_rate": 0.0,
        "batch_details": []
    }

    for batch in batches:
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
        f"{summary['failed_transfers']} failed | "
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
        
        
        if excel_password:
            if file_ext == '.xlsb':
                logger.error("Password-protected .xlsb files are not supported. Please convert to .xlsx format.")
                raise Exception("Password-protected .xlsb files not supported. Convert to .xlsx format.")
            
            
            try:
                import msoffcrypto
                logger.info("Attempting to decrypt password-protected Excel file...")
                
                with open(excel_path, 'rb') as file:
                    office_file = msoffcrypto.OfficeFile(file)
                    
                    
                    if not office_file.is_encrypted():
                        logger.info("Excel file is not encrypted, reading normally")
                        df = pd.read_excel(excel_path, engine='openpyxl')
                    else:
                        
                        office_file.load_key(password=excel_password)
                        
                        decrypted = io.BytesIO()
                        office_file.save(decrypted)
                        decrypted.seek(0)
                        
                        df = pd.read_excel(decrypted, engine='openpyxl')
                        logger.info("Password-protected Excel file decrypted and read successfully")
                        
            except ImportError:
                logger.error("msoffcrypto-tool required for password-protected Excel files.")
                logger.error("Please install with: pip install msoffcrypto-tool")
                return []
            except Exception as e:
                if "Invalid password" in str(e) or "Bad decrypt" in str(e) or "incorrect password" in str(e).lower():
                    logger.error(f"Incorrect Excel password provided: {e}")
                    return []
                else:
                    logger.error(f"Failed to decrypt Excel file: {e}")
                    return []
        else:
            
            if file_ext == '.xlsb':
                try:
                    df = pd.read_excel(excel_path, engine='pyxlsb')
                    logger.info("Excel Binary (.xlsb) file read successfully with pyxlsb engine")
                except ImportError:
                    logger.error("pyxlsb required for .xlsb files. Please install with: pip install pyxlsb")
                    return []
                except Exception as e:
                    logger.error(f"Failed to read .xlsb file: {e}")
                    return []
            elif file_ext in ['.xlsx', '.xlsm']:
                df = pd.read_excel(excel_path, engine='openpyxl')
                logger.info("Excel file (.xlsx/.xlsm) read successfully with openpyxl engine")
            elif file_ext == '.xls':
                df = pd.read_excel(excel_path, engine='xlrd')
                logger.info("Legacy Excel file (.xls) read successfully with xlrd engine")
            else:
                logger.warning(f"Unknown Excel format: {file_ext}, attempting with openpyxl")
                df = pd.read_excel(excel_path, engine='openpyxl')

        
        logger.info(f"Excel data loaded: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Available columns: {list(df.columns)}")


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

    
    for folder in batch_docs.iterdir():
        if folder.is_dir() and folder.name.lower() == batch_id.lower():
            logger.info(f"Found exact match for batch {batch_id}: {folder}")
            return folder

    
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