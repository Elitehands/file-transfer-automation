
# Create package directory
$packageDir = "file_transfer_package"
if (Test-Path $packageDir) {
    Remove-Item -Path $packageDir -Recurse -Force
}
New-Item -Path $packageDir -ItemType Directory | Out-Null

# Copy executable from correct location
Copy-Item -Path "dist\file_transfer_tool.exe" -Destination $packageDir

# Create config directory and copy settings from mock_demo
New-Item -Path "$packageDir\config" -ItemType Directory | Out-Null
Copy-Item -Path "mock_demo\config\settings.json" -Destination "$packageDir\config"

# Create logs directory
New-Item -Path "$packageDir\logs" -ItemType Directory | Out-Null

# Create README file
$readmeContent = @"
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
"@
Set-Content -Path "$packageDir\README.txt" -Value $readmeContent

# Create sample .env file
$envContent = @"
# Example .env file - REPLACE WITH ACTUAL CREDENTIALS
VPN_PASSWORD=your_vpn_password
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_email_password
"@
Set-Content -Path "$packageDir\.env.example" -Value $envContent

# Create the zip file
Compress-Archive -Path "$packageDir\*" -DestinationPath "file_transfer_tool.zip" -Force

Write-Host "Package created successfully at $(Get-Location)\file_transfer_tool.zip"
Write-Host "Contents:"
Get-ChildItem -Path $packageDir -Recurse | Select-Object FullName