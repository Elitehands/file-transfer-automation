import pytest
from unittest.mock import patch, MagicMock
import unittest
from src.vpn_manager import VPNManager

class TestVPNManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.vpn_name = "bbuk vpn"
        self.vpn_manager = VPNManager(self.vpn_name)
        self.vpn_manager._test_hook = True 
        
    def test_init(self):
        """Test that VPNManager initializes with correct connection name"""
        self.assertEqual(self.vpn_manager.connection_name, self.vpn_name)
        
    @patch('src.vpn_manager.subprocess.run')
    def test_is_connected_true(self, mock_run):
        """Test VPN is connected status"""
        mock_process = MagicMock()
        mock_process.stdout = "ConnectionStatus    : Connected"
        mock_run.return_value = mock_process
        
        result = self.vpn_manager.is_connected()
        self.assertTrue(result)
        
    @patch('src.vpn_manager.subprocess.run')
    def test_is_connected_false(self, mock_run):
        """Test VPN is not connected status"""
        mock_process = MagicMock()
        mock_process.stdout = "ConnectionStatus    : Disconnected"
        mock_run.return_value = mock_process
        
        result = self.vpn_manager.is_connected()
        self.assertFalse(result)
    
    @patch('src.vpn_manager.subprocess.run')
    def test_connect(self, mock_run):
        """Test VPN connect method"""
        mock_process = MagicMock()
        mock_process.stdout = "Success"
        mock_run.return_value = mock_process
        
        result = self.vpn_manager.connect()
        self.assertTrue(result)
        
        mock_run.assert_called_once()


def test_vpn_initialization():
    """Test VPN Manager initialization with pytest style"""
    vpn = VPNManager("test_vpn")
    assert vpn.connection_name == "test_vpn"