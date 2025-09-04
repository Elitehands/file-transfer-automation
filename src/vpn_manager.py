"""VPN connection management for automated file transfers"""

import subprocess
import logging
import time
from pathlib import Path


class VPNManager:
    """Manages VPN connections for secure file transfers"""

    def __init__(self, vpn_name: str, max_retries: int = 3, retry_delay: int = 5, test_mode: bool = False):
        """
        Initialize VPN manager
        
        Args:
            vpn_name: Name of VPN connection profile
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retries in seconds
            test_mode: Whether to run in test mode (no actual VPN operations)
        """
        self.vpn_name = vpn_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.test_mode = test_mode
        self.logger = logging.getLogger(__name__)
        self._test_hook = False  
        
    def is_connected(self) -> bool:
        """
        Check if VPN is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self.test_mode:
            self.logger.debug("Test mode: Simulating VPN connected status")
            return True
            
        try:
            cmd = f'powershell.exe "Get-VpnConnection -Name \'{self.vpn_name}\'"'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True  
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to get VPN status: {result.stderr}")
                return False

            if "ConnectionStatus : Disconnected" in result.stdout:
                self.logger.debug("VPN is disconnected")
                return False

            if "ConnectionStatus : Connected" in result.stdout:
                self.logger.debug("VPN is connected")
                return True

            self.logger.warning(f"Unexpected VPN status output: {result.stdout}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking VPN connection: {str(e)}")
            return False

    def connect(self) -> bool:
        """
        Connect to VPN
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            
            if self._test_hook:
                self.logger.debug("Test hook activated - forcing VPN connection attempt")
                cmd = f'rasdial "{self.vpn_name}"'
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                return True
                
            if self.is_connected():
                self.logger.info(f"VPN '{self.vpn_name}' already connected")
                return True
                
            self.logger.info(f"Connecting to VPN: {self.vpn_name}")
            
            cmd = f'rasdial "{self.vpn_name}"'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )
            
            # If test mode, return success regardless of result
            if self.test_mode:
                self.logger.debug(f"Test mode: Simulating successful VPN connection")
                return True
                
            if result.returncode != 0:
                self.logger.error(f"Failed to connect to VPN: {result.stderr}")
                return False
                
            time.sleep(2)  
            return self.is_connected()
            
        except Exception as e:
            self.logger.error(f"Error connecting to VPN: {str(e)}")
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from VPN
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if self.test_mode:
            self.logger.debug(f"Test mode: Simulating VPN disconnection from '{self.vpn_name}'")
            return True
            
        try:
            if not self.is_connected():
                self.logger.info(f"VPN '{self.vpn_name}' already disconnected")
                return True
                
            self.logger.info(f"Disconnecting from VPN: {self.vpn_name}")
            
            cmd = f'rasdial "{self.vpn_name}" /disconnect'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True  
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to disconnect from VPN: {result.stderr}")
                return False
                
            time.sleep(1)
            return not self.is_connected()
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from VPN: {str(e)}")
            return False

    def verify_and_connect(self) -> bool:
        """
        Verify VPN connection and connect if needed
        
        Returns:
            bool: True if connected, False if connection failed
        """
        if self.test_mode:
            self.logger.info(f"Test mode: Skipping actual VPN connection to '{self.vpn_name}'")
            return True
            
        attempt = 0
        
        if self.is_connected():
            return True
            
        while attempt < self.max_retries:
            attempt += 1
            self.logger.info(f"Attempting to connect to VPN (attempt {attempt}/{self.max_retries})")
            
            if self.connect():
                self.logger.info(f"Successfully connected to VPN: {self.vpn_name}")
                return True
                
            if attempt < self.max_retries:
                self.logger.warning(f"Connection attempt failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                self.retry_delay = min(self.retry_delay * 2, 30)
        
        self.logger.error(f"Failed to connect to VPN after {self.max_retries} attempts")
        return False