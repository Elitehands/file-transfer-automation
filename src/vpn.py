"""VPN connection management for secure access to remote resources"""

import subprocess
import logging
import time
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def is_vpn_connected(vpn_name: str) -> bool:
    """Check if VPN connection is active"""
    try:
        cmd = f'powershell.exe "Get-VpnConnection -Name \'{vpn_name}\'"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return "Connected" in result.stdout
        return False
        
    except Exception as e:
        logger.error(f"Error checking VPN status: {e}")
        return False


def connect_vpn(vpn_name: str, test_mode: bool = False) -> bool:
    """Attempt to connect to VPN"""
    if test_mode:
        logger.info(f"TEST MODE: Simulating VPN connection to {vpn_name}")
        return True

    try:
        cmd = f'rasdial "{vpn_name}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info(f"VPN connection successful: {vpn_name}")
            return True
        else:
            logger.error(f"VPN connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error connecting to VPN: {e}")
        return False


def ensure_vpn_connection(vpn_name: str, test_mode: bool = False, max_retries: int = 3) -> bool:
    """Ensure VPN is connected with retry logic"""
    if test_mode:
        logger.info("TEST MODE: VPN connection check bypassed")
        return True

    if is_vpn_connected(vpn_name):
        logger.info(f"VPN already connected: {vpn_name}")
        return True

    logger.info(f"VPN not connected, attempting connection: {vpn_name}")
    
    for attempt in range(max_retries):
        if connect_vpn(vpn_name, test_mode):
            return True
        
        if attempt < max_retries - 1:
            logger.warning(f"VPN connection attempt {attempt + 1} failed, retrying...")
            time.sleep(5)
    
    logger.error(f"VPN connection failed after {max_retries} attempts")
    return False


if __name__ == "__main__":
    import argparse
    
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Test VPN Connection")
    parser.add_argument("--vpn-name", default="bbuk vpn", help="VPN connection name")
    parser.add_argument("--test-mode", action="store_true", help="Test mode")
    args = parser.parse_args()
    
    success = ensure_vpn_connection(args.vpn_name, args.test_mode)
    logger.info(f"VPN test: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
