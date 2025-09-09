"""File Transfer Automation - Main Entry Point"""

import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

if len(sys.argv) > 0 and sys.argv[0].endswith('main.py'):
    sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vpn import ensure_vpn_connection
from src.notifications import send_completion_email
from src.settings import load_config, get_paths, get_filter_criteria, verify_paths
from src.transfer import read_excel_batches, process_all_batches

logger = logging.getLogger(__name__)


def setup_logging():
    """Configure logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"file_transfer_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def run_transfer_workflow(config: dict, test_mode: bool = False) -> bool:
    """Execute the complete file transfer workflow"""
    try:
        paths = get_paths(config)
        filter_criteria = get_filter_criteria(config)
        vpn_name = config.get("vpn", {}).get("connection_name", "")

        # VPN connection check
        if vpn_name:
            logger.info(f"Checking VPN connection: {vpn_name}")
            if not ensure_vpn_connection(vpn_name, test_mode=test_mode):
                logger.error("VPN connection failed - stopping execution")
                return False
            logger.info("VPN connection verified")

        # Path verification
        logger.info("Verifying paths accessibility")
        if not verify_paths(paths):
            logger.error("Path verification failed")
            return False

        # Excel processing
        logger.info("Reading Excel file and filtering batches")
        batches = read_excel_batches(
            paths["excel_file"],
            filter_criteria["initials_column"],
            filter_criteria["initials_value"],
            filter_criteria["release_status_column"]
        )

        if not batches:
            logger.info("No batches found for processing")
            return True

        # Process batches
        logger.info(f"Processing {len(batches)} batches")
        results = process_all_batches(batches, paths)

        # Send notification
        if config.get("notifications", {}).get("enabled", False):
            logger.info("Sending completion notification")
            send_completion_email(results, config)

        # Log final results
        logger.info(
            f"Workflow completed: {results['successful_transfers']}/{results['total_batches']} "
            f"successful transfers, {results['total_files_copied']} files copied"
        )

        return results["failed_transfers"] == 0

    except Exception as e:
        logger.error(f"Critical error in workflow: {e}")
        return False


def main():
    """Main entry point"""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="File Transfer Automation")
    parser.add_argument("--config", default="config/settings.json", help="Config file")
    parser.add_argument("--test-mode", action="store_true", help="Test mode")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        success = run_transfer_workflow(config, test_mode=args.test_mode)
        
        if success:
            logger.info("File transfer automation completed successfully")
        else:
            logger.error("File transfer automation failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()