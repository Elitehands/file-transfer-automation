"""Integration tests for the complete workflow"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
from pathlib import Path

from main import execute_transfer_workflow
from src.vpn_manager import VPNManager
from src.drive_manager import DriveManager
from src.excel_reader import ExcelReader
from src.file_processor import FileProcessor
from src.notifier import Notifier


class TestIntegration(unittest.TestCase):
    """Integration tests that can be run locally with mock data"""
    
    def setUp(self):
        self.config = {
            'vpn_connection_name': 'bbuk vpn',
            'remote_server_path': 'Z:\\Quality Assurance(QA Common)',
            'excel_file_path': 'Z:\\Quality Assurance(QA Common)\\25.Product Status Log\\Product status Log.xlsb',
            'batch_documents_path': 'Z:\\Quality Assurance(QA Common)\\3.Batch Documents',
            'local_gdrive_path': 'G:\\BatchTransfers',
            'filter_criteria': {
                'initials_column': 'AJ',
                'initials_value': 'PP',
                'release_status_column': 'AK'
            }
        }
    
    @patch.object(VPNManager, 'verify_and_connect')
    @patch.object(DriveManager, 'verify_drives')
    @patch.object(ExcelReader, 'get_unreleased_batches')
    @patch.object(FileProcessor, 'process_batches')
    @patch.object(Notifier, 'send_completion_notification')
    def test_successful_workflow(self, mock_notify, mock_process, mock_excel, 
                                mock_drives, mock_vpn):
        """Test successful end-to-end workflow"""
        mock_vpn.return_value = True
        mock_drives.return_value = True
        mock_excel.return_value = [{'Batch ID': 'TEST001', 'AJ': 'PP', 'AK': ''}]
        mock_process.return_value = {
            'total_batches': 1,
            'successful_transfers': 1,
            'failed_transfers': 0,
            'total_files_copied': 5,
            'errors': [],
            'batch_details': []
        }
        
        vpn_manager = VPNManager(self.config['vpn_connection_name'])
        drive_manager = DriveManager()
        excel_reader = ExcelReader(self.config['excel_file_path'])
        file_processor = FileProcessor(self.config, test_mode=True)
        notifier = Notifier({})
        logger = MagicMock()
        
        result = execute_transfer_workflow(
            vpn_manager, drive_manager, excel_reader, 
            file_processor, notifier, self.config, logger
        )
        
        self.assertTrue(result)
        mock_vpn.assert_called_once()
        mock_drives.assert_called_once()
        mock_excel.assert_called_once()
        mock_process.assert_called_once()
        mock_notify.assert_called_once()
