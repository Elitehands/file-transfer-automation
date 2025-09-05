# src/vpn.py
"""Simple VPN connection management"""

import subprocess
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

def is_vpn_connected(vpn_name: str, test_mode: bool = False) -> bool:
    """Check if VPN is connected"""
    if test_mode:
        logger.info("Test mode: simulating VPN connected")
        return True
    
    try:
        cmd = f'powershell.exe "Get-VpnConnection -Name \'{vpn_name}\'"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to check VPN status: {result.stderr}")
            return False
        
        return "ConnectionStatus : Connected" in result.stdout
        
    except Exception as e:
        logger.error(f"Error checking VPN: {e}")
        return False

def connect_vpn(vpn_name: str, test_mode: bool = False) -> bool:
    """Connect to VPN"""
    if test_mode:
        logger.info("Test mode: simulating VPN connection")
        return True
    
    if is_vpn_connected(vpn_name):
        logger.info(f"VPN '{vpn_name}' already connected")
        return True
    
    try:
        logger.info(f"Connecting to VPN: {vpn_name}")
        cmd = f'rasdial "{vpn_name}"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to connect VPN: {result.stderr}")
            return False
        
        # Wait and verify
        time.sleep(2)
        return is_vpn_connected(vpn_name)
        
    except Exception as e:
        logger.error(f"Error connecting VPN: {e}")
        return False

def ensure_vpn_connection(vpn_name: str, max_retries: int = 3, test_mode: bool = False) -> bool:
    """Ensure VPN is connected with retries"""
    
    for attempt in range(max_retries):
        if connect_vpn(vpn_name, test_mode):
            return True
        
        if attempt < max_retries - 1:
            logger.warning(f"VPN connection attempt {attempt + 1} failed, retrying in 5s...")
            time.sleep(5)
    
    logger.error(f"Failed to connect VPN after {max_retries} attempts")
    return False