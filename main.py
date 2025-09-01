# main.py
"""
BBU File Transfer Automation System
Automates the transfer of production batch files from remote server to Google Drive
"""

import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

from src.vpn_manager import VPNManager
from src.drive_manager import DriveManager  
from src.excel_reader import ExcelReader
from src.file_processor import FileProcessor
from src.logger import setup_logging
from src.notifier import Notifier
from src.config_manager import ConfigManager


def main():
    """Main entry point for the file transfer automation"""
    parser = argparse.ArgumentParser(description='BBU File Transfer Automation')
    parser.add_argument('--test-mode', action='store_true', 
                       help='Run in test mode with mock data')
    parser.add_argument('--config', default='config/settings.json',
                       help='Path to configuration file')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    try:
        # Setup logging
        logger = setup_logging(args.log_level)
        logger.info("=" * 60)
        logger.info("BBU File Transfer Automation Started")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info(f"Test Mode: {args.test_mode}")
        logger.info("=" * 60)
        
        # Load configuration
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        
        # Initialize components
        vpn_manager = VPNManager(config['vpn_connection_name'])
        drive_manager = DriveManager()
        excel_reader = ExcelReader(config['excel_file_path'])
        file_processor = FileProcessor(config, args.test_mode)
        notifier = Notifier(config.get('notifications', {}))
        
        # Execute workflow
        success = execute_transfer_workflow(
            vpn_manager, drive_manager, excel_reader, 
            file_processor, notifier, config, logger
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


def execute_transfer_workflow(vpn_manager, drive_manager, excel_reader, 
                            file_processor, notifier, config, logger):
    """
    Execute the complete file transfer workflow
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Step 1: Verify VPN connection
        logger.info("Step 1: Checking VPN connection...")
        if not vpn_manager.verify_and_connect():
            raise Exception("Failed to establish VPN connection")
        
        # Step 2: Verify drive access
        logger.info("Step 2: Verifying drive access...")
        if not drive_manager.verify_drives(config['remote_server_path'], 
                                         config['local_gdrive_path']):
            raise Exception("Failed to access required drives")
        
        # Step 3: Read and filter Excel data
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
        
        # Step 4: Process each batch
        logger.info("Step 4: Processing batches...")
        transfer_results = file_processor.process_batches(batches_to_process)
        
        # Step 5: Send notifications
        logger.info("Step 5: Sending notifications...")
        notifier.send_completion_notification(transfer_results)
        
        return True
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        notifier.send_error_notification(str(e))
        return False


if __name__ == "__main__":
    sys.exit(main())