"""
File Transfer Automation System
Automates the transfer of production batch files from remote server to Google Drive
"""

import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from vpn_manager import VPNManager
from excel_reader import ExcelReader
from file_processor import FileProcessor
from logger import setup_logging
from notifier import Notifier
from config_manager import ConfigManager


def main():
    """Main entry point for the file transfer automation"""
    parser = argparse.ArgumentParser(description='BBU File Transfer Automation')
    parser.add_argument('--test-mode', action='store_true', 
                       help='Run in test mode with mock data')
    parser.add_argument('--log-level', default=None,
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (overrides .env setting)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration from environment variables
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Setup logging
        log_level = args.log_level or config['system']['log_level']
        logger = setup_logging(log_level)
        
        logger.info("=" * 60)
        logger.info("BBU File Transfer Automation Started")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info(f"Test Mode: {args.test_mode or config['system']['test_mode']}")
        logger.info("=" * 60)
        
        # Initialize components
        vpn_manager = VPNManager(config['vpn_connection_name'])
        excel_reader = ExcelReader(config['excel_file_path'])
        file_processor = FileProcessor(config, args.test_mode or config['system']['test_mode'])
        notifier = Notifier(config.get('notifications', {}))
        
        # Execute workflow
        success = execute_transfer_workflow(
            vpn_manager, excel_reader, file_processor, 
            notifier, config, logger
        )
        
        if success:
            logger.info("File transfer automation completed successfully")
            return 0
        else:
            logger.error("File transfer automation failed")
            return 1
            
    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}")
        return 1


def execute_transfer_workflow(vpn_manager, excel_reader, file_processor, 
                            notifier, config, logger):
    """
    Execute the complete file transfer workflow
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Step 1: Check VPN connection
        logger.info("Step 1: Checking VPN connection...")
        if not vpn_manager.verify_and_connect():
            raise Exception("Failed to establish VPN connection")
        
        # Step 2: Verify drive access
        logger.info("Step 2: Verifying drive access...")
        remote_accessible = Path(config['remote_server_path']).exists()
        gdrive_accessible = Path(config['local_gdrive_path']).exists()
        
        if not remote_accessible:
            raise Exception(f"Remote server not accessible: {config['remote_server_path']}")
        
        if not gdrive_accessible:
            logger.warning(f"Google Drive path not found, will attempt to create: {config['local_gdrive_path']}")
        
        # Step 3: Read Excel file for batch status
        logger.info("Step 3: Reading Excel file for batch status...")
        batches_to_process = excel_reader.get_unreleased_batches(
            config['filter_criteria']['initials_column'],
            config['filter_criteria']['initials_value'],
            config['filter_criteria']['release_status_column']
        )
        
        if not batches_to_process:
            logger.info("No unreleased batches found to process")
            return True
        
        logger.info(f"Found {len(batches_to_process)} batches to process")
        
        # Step 4: Process batches
        logger.info("Step 4: Processing batches...")
        transfer_results = file_processor.process_batches(batches_to_process)
        
        # Step 5: Send notifications
        logger.info("Step 5: Sending notifications...")
        if config['notifications']['enabled']:
            notifier.send_completion_notification(transfer_results)
        else:
            logger.info("Notifications disabled")
        
        return True
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        if config.get('notifications', {}).get('enabled'):
            notifier.send_error_notification(str(e))
        return False


if __name__ == "__main__":
    sys.exit(main())