"""Unit tests for File Processor"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from pathlib import Path

from src.file_processor import FileProcessor


class TestFileProcessor(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            'batch_documents_path': 'Z:\\test\\path',
            'local_gdrive_path': 'G:\\test\\path',
            'filter_criteria': {
                'initials_column': 'AJ',
                'initials_value': 'PP',
                'release_status_column': 'AK'
            }
        }
        self.file_processor = FileProcessor(self.config, test_mode=True)
    
    def test_get_batch_id(self):
        """Test batch ID extraction"""
        batch_record = {'Batch ID': 'TEST001', 'AJ': 'PP', 'AK': ''}
        result = self.file_processor._get_batch_id(batch_record)
        self.assertEqual(result, 'TEST001')
    
    def test_should_copy_file_new_file(self):
        """Test file copy decision for new file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / 'source.txt'
            dest_file = Path(temp_dir) / 'dest.txt'
            
            source_file.write_text('test content')
            
            result = self.file_processor._should_copy_file(source_file, dest_file)
            self.assertTrue(result)
    
    def test_should_copy_file_same_file(self):
        """Test file copy decision for identical files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / 'source.txt'
            dest_file = Path(temp_dir) / 'dest.txt'
            
            content = 'test content'
            source_file.write_text(content)
            dest_file.write_text(content)
            
            result = self.file_processor._should_copy_file(source_file, dest_file)
            self.assertFalse(result)
