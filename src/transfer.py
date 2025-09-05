"""Core file transfer functionality - batch processing and file operations"""

import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def read_excel_batches(
    excel_path: str,
    initials_col: str,
    initials_val: str,
    release_col: str
) -> List[Dict[str, Any]]:
    """Read Excel file and return unreleased batches"""

    if not Path(excel_path).exists():
        logger.warning(f"Excel file not found: {excel_path}")
        return []

    try:
        for engine in ['openpyxl', 'pyxlsb']:
            try:
                df = pd.read_excel(excel_path, engine=engine)
                break
            except Exception:
                continue
        else:
            raise Exception("Could not read Excel file with any engine")

        # Filter unreleased batches
        filtered_df = df[
            (df[initials_col].astype(str).str.upper() == initials_val.upper()) &
            (df[release_col].isna() |
             (df[release_col].astype(str).str.strip() == ""))
        ]

        batches = filtered_df.to_dict("records")
        logger.info(f"Found {len(batches)} unreleased batches")
        return batches

    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return []


def get_batch_id(batch_record: Dict[str, Any]) -> str:
    """Extract batch ID from record"""
    possible_columns = ["Batch ID", "BatchID", "Batch_ID", "ID"]

    for col in possible_columns:
        if col in batch_record and batch_record[col]:
            return str(batch_record[col]).strip()

    return "Unknown"


def verify_paths(paths: Dict[str, str]) -> bool:
    """Verify all required paths are accessible"""
    for name, path in paths.items():
        if not Path(path).exists():
            logger.error(f"Path not accessible: {name} = {path}")
            return False

    logger.info("All paths verified")
    return True


def find_batch_folder(batch_id: str, batch_docs_path: str) -> Optional[Path]:
    """Find source folder for batch ID"""
    batch_docs = Path(batch_docs_path)

    if not batch_docs.exists():
        return None

    # Try exact match first
    for folder in batch_docs.iterdir():
        if folder.is_dir() and folder.name.lower() == batch_id.lower():
            return folder

    # Try partial match
    for folder in batch_docs.iterdir():
        if folder.is_dir() and batch_id.lower() in folder.name.lower():
            return folder

    return None


def copy_batch_files(source_folder: Path, dest_folder: Path) -> Dict[str, Any]:
    """Copy all files from source to destination"""
    result = {"files_copied": 0, "errors": []}

    dest_folder.mkdir(parents=True, exist_ok=True)

    source_files = [f for f in source_folder.glob("**/*") if f.is_file()]

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

    return result


def process_single_batch(batch_id: str, paths: Dict[str, str]) -> Dict[str, Any]:
    """Process files for a single batch"""
    result = {
        "batch_id": batch_id,
        "success": False,
        "files_copied": 0,
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
        result["errors"].extend(copy_result["errors"])

        # Mark success if any files copied
        result["success"] = copy_result["files_copied"] > 0

        if result["success"]:
            logger.info(
                f"Successfully processed batch {batch_id}: "
                f"{result['files_copied']} files"
            )

        return result

    except Exception as e:
        error_msg = f"Error processing batch {batch_id}: {e}"
        result["errors"].append(error_msg)
        logger.error(error_msg)
        return result


def process_all_batches(batches: List[Dict[str, Any]],
                        paths: Dict[str, str]) -> Dict[str, Any]:
    """Process all batches and return summary"""
    summary = {
        "total_batches": len(batches),
        "successful_transfers": 0,
        "failed_transfers": 0,
        "total_files_copied": 0,
        "batch_details": []
    }

    for batch in batches:
        batch_id = get_batch_id(batch)
        result = process_single_batch(batch_id, paths)

        summary["batch_details"].append(result)
        summary["total_files_copied"] += result["files_copied"]

        if result["success"]:
            summary["successful_transfers"] += 1
        else:
            summary["failed_transfers"] += 1

    logger.info(
        f"Batch processing complete: {summary['successful_transfers']}/"
        f"{summary['total_batches']} successful"
    )
    return summary