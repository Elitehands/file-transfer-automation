"""VPN connection management"""

import subprocess
import logging
import time
# from typing import bool  # bool is built-in in Python 3.9+


class VPNManager:
    """Manages VPN connection status and reconnection"""
    
    def __init__(self, connection_name: str):
        self.connection_name = connection_name
        self.logger = logging.getLogger(__name__)
    
    def verify_and_connect(self) -> bool:
        """
        Verify VPN connection and reconnect if needed
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            if self.is_connected():
                self.logger.info(f"VPN '{self.connection_name}' already connected")
                return True
            
            self.logger.warning(f"VPN '{self.connection_name}' not connected, attempting to connect...")
            return self.connect()
            
        except Exception as e:
            self.logger.error(f"VPN verification failed: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if VPN is currently connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            cmd = f'powershell.exe "Get-VpnConnection -Name \'{self.connection_name}\'"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                return "connected" in output
            else:
                self.logger.warning(f"Failed to check VPN status: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking VPN status: {str(e)}")
            return False
    
    def connect(self) -> bool:
        """
        Attempt to connect to VPN
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            cmd = f'rasdial "{self.connection_name}"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                time.sleep(5)
                
                if self.is_connected():
                    self.logger.info(f"Successfully connected to VPN '{self.connection_name}'")
                    return True
                else:
                    self.logger.error("VPN connection command succeeded but verification failed")
                    return False
            else:
                self.logger.error(f"VPN connection failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to VPN: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from VPN
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            cmd = f'rasdial "{self.connection_name}" /disconnect'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                self.logger.info(f"Disconnected from VPN '{self.connection_name}'")
                return True
            else:
                self.logger.warning(f"VPN disconnection warning: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from VPN: {str(e)}")
            return False
