"""Unit tests for VPN Manager"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess

from src.vpn_manager import VPNManager


class TestVPNManager(unittest.TestCase):
    
    def setUp(self):
        self.vpn_manager = VPNManager("bbuk vpn")
    
    @patch('subprocess.run')
    def test_is_connected_success(self, mock_run):
        """Test VPN connection check when connected"""

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="ConnectionStatus : Connected"
        )
        
        result = self.vpn_manager.is_connected()
        self.assertTrue(result)
        

        expected_cmd = 'powershell.exe "Get-VpnConnection -Name \'bbuk vpn\'"'
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True, shell=True)
    
    @patch('subprocess.run')
    def test_is_connected_disconnected(self, mock_run):
        """Test VPN connection check when disconnected"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="ConnectionStatus : Disconnected"
        )
        
        result = self.vpn_manager.is_connected()
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_is_connected_command_failure(self, mock_run):
        """Test VPN connection check when PowerShell command fails"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Command failed"
        )
        
        result = self.vpn_manager.is_connected()
        self.assertFalse(result)
    
    @patch('src.vpn_manager.time.sleep')
    @patch.object(VPNManager, 'is_connected')
    @patch('subprocess.run')
    def test_connect_success(self, mock_run, mock_is_connected, mock_sleep):
        """Test successful VPN connection"""

        mock_run.return_value = MagicMock(returncode=0)
        mock_is_connected.return_value = True
        
        result = self.vpn_manager.connect()
        self.assertTrue(result)
        

        expected_cmd = 'rasdial "bbuk vpn"'
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True, shell=True)
    
    @patch('subprocess.run')
    def test_connect_failure(self, mock_run):
        """Test VPN connection failure"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Connection failed"
        )
        
        result = self.vpn_manager.connect()
        self.assertFalse(result)

