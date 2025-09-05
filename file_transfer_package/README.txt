# File Transfer Automation Tool

## Setup Instructions

1. Extract all files to a folder (e.g., C:\FileTransferTool)
2. Edit config\settings.json to match your network paths:
   - Set "vpn_enabled": true for production use (it's disabled in this package for testing)
   - Update VPN connection name to match your system
   - Update all file paths to match your environment
3. Create .env file in the same folder as the .exe with:
4. Run file_transfer_tool.exe to test the tool
5. For production use, set up a scheduled task in Windows

## Requirements

- Windows 10 or 11
- Access to required network drives (Z: and G:)
- VPN access configured on your system

## Troubleshooting

- Check logs folder for detailed error messages
- Ensure all network drives are accessible
- Verify Excel file format matches expected structure

## Support

Contact TobiWilliams001@example.com for assistance
