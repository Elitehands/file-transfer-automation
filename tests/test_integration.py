"""Integration tests for the complete workflow"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
import sys
import os
from pathlib import Path

# Add both src and project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import main
from src.vpn_manager import VPNManager
from src.excel_reader import ExcelReader
from src.file_processor import FileProcessor
from src.notifier import Notifier
from src.config_manager import ConfigManager
from src.drive_manager import DriveManager


class TestIntegration(unittest.TestCase):
    """Integration tests that can be run locally with mock data"""
    
    def setUp(self):
        # Create a mock config that doesn't require actual environment variables
        self.config = {
            'vpn_connection_name': 'test_vpn',
            'remote_server_path': '/tmp/remote',
            'excel_file_path': '/tmp/test.xlsb',
            'batch_documents_path': '/tmp/batch_docs',
            'local_gdrive_path': '/tmp/gdrive',
            'filter_criteria': {
                'initials_column': 'AJ',
                'initials_value': 'PP',
                'release_status_column': 'AK'
            },
            'notifications': {
                'enabled': False
            },
            'system': {
                'test_mode': True,
                'log_level': 'DEBUG'
            }
        }
    
    @patch.object(VPNManager, 'verify_and_connect')
    @patch('pathlib.Path.exists')
    @patch.object(ExcelReader, 'get_unreleased_batches')
    @patch.object(FileProcessor, 'process_batches')
    @patch.object(Notifier, 'send_completion_notification')
    @patch.object(DriveManager, 'verify_drives')  # Added mock for DriveManager
    def test_successful_workflow(self, mock_verify_drives, mock_notify, mock_process, 
                               mock_excel, mock_path_exists, mock_vpn):
        """Test successful end-to-end workflow"""
        # Setup mocks
        mock_vpn.return_value = True
        mock_verify_drives.return_value = True  # Mock the drive verification
        mock_path_exists.return_value = True
        mock_excel.return_value = [{'Batch ID': 'TEST001', 'AJ': 'PP', 'AK': ''}]
        mock_process.return_value = {
            'total_batches': 1,
            'successful_transfers': 1,
            'failed_transfers': 0,
            'total_files_copied': 5,
            'errors': [],
            'batch_details': []
        }
        
        # Create components
        vpn_manager = VPNManager(self.config['vpn_connection_name'])
        excel_reader = ExcelReader(self.config['excel_file_path'])
        file_processor = FileProcessor(self.config, test_mode=True)
        notifier = Notifier(self.config.get('notifications', {}))
        drive_manager = DriveManager()  # Added DriveManager instance
        logger = MagicMock()
        
        # Execute workflow with updated parameter list
        result = main.execute_transfer_workflow(
            vpn_manager, excel_reader, file_processor, 
            notifier, drive_manager, self.config, logger  # Added drive_manager parameter
        )
        
        # Assertions
        self.assertTrue(result)
        mock_vpn.assert_called_once()
        mock_verify_drives.assert_called_once()  # Verify drive_manager method was called
        mock_excel.assert_called_once()
        mock_process.assert_called_once()

    @patch('main.ConfigManager')
    @patch('main.setup_logging')
    @patch('main.DriveManager')  # Added mock for DriveManager
    def test_main_entry_point(self, mock_drive_manager, mock_logging, mock_config_manager):
        """Test main entry point with test mode"""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.load_config.return_value = self.config
        mock_config_manager.return_value = mock_config_instance
        
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger
        
        mock_drive_manager_instance = MagicMock()
        mock_drive_manager.return_value = mock_drive_manager_instance
        
        # Mock all the workflow components
        with patch('main.execute_transfer_workflow') as mock_workflow:
            mock_workflow.return_value = True
            
            # Test main function
            with patch('sys.argv', ['main.py', '--test-mode']):
                result = main.main()
                
            self.assertEqual(result, 0)
            mock_workflow.assert_called_once()
            # Verify that DriveManager was included in the workflow call
            self.assertIn(mock_drive_manager_instance, mock_workflow.call_args[0])