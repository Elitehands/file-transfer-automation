"""File Transfer Automation -  Entry Point"""

import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from src.vpn import ensure_vpn_connection
from src.notifications import send_completion_email

sys.path.insert(0, str(Path(__file__).parent))

from src.settings import load_config, get_paths, get_filter_criteria
from src.transfer import verify_paths, read_excel_batches, process_all_batches

def setup_logging(level: str = "INFO") -> None:
    """Setup simple logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / f"transfer_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )

def run_transfer_workflow(config: dict, test_mode: bool = False) -> bool:
    """Execute the complete file transfer workflow"""
    logger = logging.getLogger(__name__)
    
    try:
        paths = get_paths(config)
        filter_criteria = get_filter_criteria(config)
        vpn_name = config.get("vpn", {}).get("connection_name", "")
        
        if vpn_name:
            logger.info("Checking VPN connection...")
            if not ensure_vpn_connection(vpn_name, test_mode=test_mode):
                logger.error("VPN connection failed")
                return False
        
        logger.info("Verifying file system access...")
        if not verify_paths(paths):
            logger.error("File system access failed")
            return False
        
        logger.info("Reading Excel file for unreleased batches...")
        batches = read_excel_batches(
            paths["excel_file"],
            filter_criteria["initials_column"],
            filter_criteria["initials_value"], 
            filter_criteria["release_status_column"]
        )
        
        if not batches:
            logger.info("No unreleased batches found")
            return True
        
        logger.info(f"Processing {len(batches)} batches...")
        results = process_all_batches(batches, paths)
        
        send_completion_email(results, config)
        
        logger.info(f"Transfer complete: {results['successful_transfers']}/{results['total_batches']} successful")
        logger.info(f"Total files transferred: {results['total_files_copied']}")
        
        return results["failed_transfers"] == 0
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return False

def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(description="File Transfer Automation")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        config = load_config(args.config)
        
        if args.test_mode:
            config.setdefault("system", {})["test_mode"] = True
            logger.info("Running in TEST MODE")
        
        start_time = datetime.now()
        success = run_transfer_workflow(config, test_mode=args.test_mode)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Execution completed in {duration:.2f} seconds")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())