"""VPN connection management"""

import subprocess
import logging
import time
import sys
import argparse


logger = logging.getLogger(__name__)


def ensure_vpn_connection(vpn_name: str, test_mode: bool = False) -> bool:
    """Ensure VPN is connected, with retries"""

    if test_mode:
        logger.info("Test mode: Simulating VPN connection")
        return True

    if is_vpn_connected(vpn_name):
        logger.info(f"VPN '{vpn_name}' already connected")
        return True

    for attempt in range(3):
        logger.info(f"VPN connection attempt {attempt + 1}/3")

        if connect_vpn(vpn_name):
            logger.info(f"VPN '{vpn_name}' connected successfully")
            return True

        if attempt < 2:
            logger.warning("VPN connection failed, retrying in 5 seconds...")
            time.sleep(5)

    logger.error(f"Failed to connect VPN '{vpn_name}' after 3 attempts")
    return False


def is_vpn_connected(vpn_name: str) -> bool:
    """Check if VPN is connected using PowerShell"""
    try:
        cmd = f'powershell.exe -NoProfile -Command "(Get-VpnConnection -Name \\"{vpn_name}\\" -ErrorAction SilentlyContinue).ConnectionStatus"'
       #cmd = f'powershell.exe "Get-VpnConnection -Name \'{vpn_name}\'"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)

        if result.returncode != 0:
            logger.debug(f"VPN status check failed: {result.stderr}")
            return False
        
        return result.stdout.strip().lower() == "connected"

        #return "ConnectionStatus : Connected" in result.stdout

    except Exception as e:
        logger.error(f"Error checking VPN connection: {e}")
        return False


def connect_vpn(vpn_name: str) -> bool:
    """Connect to VPN using rasdial"""
    try:
        cmd = f'rasdial "{vpn_name}"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=30)

        if result.returncode != 0:
            logger.error(f"VPN connection failed: {result.stderr}")
            return False

        time.sleep(2)
        return is_vpn_connected(vpn_name)

    except Exception as e:
        logger.error(f"Error connecting VPN: {e}")
        return False


if __name__ == "__main__":
    """Test VPN functionality independently"""
    
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Test VPN Connection")
    parser.add_argument("--vpn-name", default="bbuk vpn", help="VPN connection name")
    parser.add_argument("--test-mode", action="store_true", help="Simulate connection")
    parser.add_argument("--check-only", action="store_true", help="Only check current status")
    args = parser.parse_args()
    
    print(f"Testing VPN: '{args.vpn_name}'")
    
    if args.check_only:
        connected = is_vpn_connected(args.vpn_name)
        status = "✅ CONNECTED" if connected else "❌ NOT CONNECTED"
        print(f"VPN Status: {status}")
        sys.exit(0 if connected else 1)
    
    success = ensure_vpn_connection(args.vpn_name, args.test_mode)
    
    result = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"VPN Connection: {result}")
    sys.exit(0 if success else 1)
