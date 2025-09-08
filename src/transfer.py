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


if __name__ == "__main__":
    """Test transfer functionality independently"""
    import argparse
    import sys
    
    #  import for standalone execution
    try:
        from src.settings import load_config, get_paths, get_filter_criteria
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.settings import load_config, get_paths, get_filter_criteria
    
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Test File Transfer Operations")
    parser.add_argument("--config", help="Path to config file (default: config/settings.json)", 
                       default="config/settings.json")
    parser.add_argument("--verify-only", action="store_true", help="Only verify paths")
    parser.add_argument("--read-excel-only", action="store_true", help="Only read Excel file")
    parser.add_argument("--show-batches", action="store_true", help="Show found batch details")
    args = parser.parse_args()
    
    try:
        print(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
        paths = get_paths(config)
        criteria = get_filter_criteria(config)
        
        if args.verify_only:
            print("Testing path verification...")
            success = verify_paths(paths)
            if success:
                print("✅ All paths accessible:")
                for name, path in paths.items():
                    print(f"  {name}: {path}")
            else:
                print("❌ Some paths not accessible")
            sys.exit(0 if success else 1)
        
        if args.read_excel_only:
            print("Testing Excel file reading...")
            batches = read_excel_batches(
                paths["excel_file"],
                criteria["initials_column"],
                criteria["initials_value"],
                criteria["release_status_column"]
            )
            print(f"✅ Found {len(batches)} unreleased batches")
            
            if args.show_batches and batches:
                print("Batch details:")
                for i, batch in enumerate(batches[:5]):  # Show first 5
                    batch_id = get_batch_id(batch)
                    print(f"  {i+1}. {batch_id}")
            sys.exit(0)
        
        # Full test
        print("Testing complete transfer workflow...")
        print("1. Verifying paths...")
        if not verify_paths(paths):
            print("❌ Path verification failed")
            sys.exit(1)
        
        print("2. Reading Excel file...")
        batches = read_excel_batches(
            paths["excel_file"],
            criteria["initials_column"],
            criteria["initials_value"],
            criteria["release_status_column"]
        )
        
        print(f"3. Found {len(batches)} batches to process")
        if batches:
            print("4. Processing batches...")
            results = process_all_batches(batches, paths)
            print(f"✅ Transfer complete: {results['successful_transfers']}/{results['total_batches']} successful")
            print(f"   Total files copied: {results['total_files_copied']}")
        else:
            print("✅ No batches to process")
        
    except Exception as e:
        print(f"❌ Transfer test failed: {e}")
        sys.exit(1)