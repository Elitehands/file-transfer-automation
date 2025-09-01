"""Unit tests for Drive Manager"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from src.drive_manager import DriveManager


class TestDriveManager(unittest.TestCase):
    
    def setUp(self):
        self.drive_manager = DriveManager()
    
    def test_is_path_accessible_exists(self):
        """Test path accessibility check for existing path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.drive_manager.is_path_accessible(temp_dir)
            self.assertTrue(result)
    
    def test_is_path_accessible_not_exists(self):
        """Test path accessibility check for non-existing path"""
        result = self.drive_manager.is_path_accessible('/non/existent/path')
        self.assertFalse(result)
    
    def test_create_directory_success(self):
        """Test directory creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / 'new_folder'
            result = self.drive_manager.create_directory(str(new_dir))
            self.assertTrue(result)
            self.assertTrue(new_dir.exists())