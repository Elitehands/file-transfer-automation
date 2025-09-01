"""Unit tests for Excel Reader"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path

from src.excel_reader import ExcelReader


class TestExcelReader(unittest.TestCase):
    
    def setUp(self):
        self.excel_reader = ExcelReader("test_file.xlsb")
    
    @patch('pandas.read_excel')
    @patch('pathlib.Path.exists')
    def test_get_unreleased_batches_success(self, mock_exists, mock_read_excel):
        """Test successful batch filtering"""
        mock_exists.return_value = True
        
        # Mock Excel data
        mock_df = pd.DataFrame({
            'Batch ID': ['B001', 'B002', 'B003', 'B004'],
            'AJ': ['PP', 'JD', 'PP', 'PP'],
            'AK': ['', 'Released', '', 'Released']
        })
        mock_read_excel.return_value = mock_df
        
        result = self.excel_reader.get_unreleased_batches('AJ', 'PP', 'AK')
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Batch ID'], 'B001')
        self.assertEqual(result[1]['Batch ID'], 'B003')
    
    @patch('pathlib.Path.exists')
    def test_get_unreleased_batches_file_not_found(self, mock_exists):
        """Test behavior when Excel file doesn't exist"""
        mock_exists.return_value = False
        
        result = self.excel_reader.get_unreleased_batches('AJ', 'PP', 'AK')
        self.assertEqual(result, [])
    
    def test_get_batch_id_from_record(self):
        """Test batch ID extraction from record"""
        record1 = {'Batch ID': 'B001', 'Other': 'data'}
        result1 = self.excel_reader.get_batch_id_from_record(record1)
        self.assertEqual(result1, 'B001')
        
        record2 = {'BatchID': 'B002', 'Other': 'data'}
        result2 = self.excel_reader.get_batch_id_from_record(record2)
        self.assertEqual(result2, 'B002')
        
        record3 = {'Other': 'data', 'Random': 'value'}
        result3 = self.excel_reader.get_batch_id_from_record(record3)
        self.assertEqual(result3, 'Unknown')