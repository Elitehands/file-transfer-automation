# Troubleshooting Guide

## Common Issues and Solutions

### VPN Connection Failures

**Issue:** The application cannot connect to the VPN
**Possible causes:**
- VPN credentials expired
- Network connectivity issues
- VPN client configuration problems

**Solutions:**
1. Manually connect to the VPN to verify credentials
2. Check network connectivity
3. Ensure VPN profile "bbuk vpn" exists on the system
4. Check Windows Credential Manager for stored VPN credentials

### Remote Server Access Issues

**Issue:** Cannot access files on the Z: drive
**Possible causes:**
- VPN connection failed
- Drive mapping issues
- Permission problems

**Solutions:**
1. Verify the Z: drive is mapped after VPN connection
2. Check network connectivity to the server
3. Verify user permissions to access the required folders

### Excel File Access Problems

**Issue:** Cannot read or filter the Excel file
**Possible causes:**
- File is locked by another user
- File path is incorrect
- Excel format not supported

**Solutions:**
1. Check if the Excel file is open in another application
2. Verify the file path in settings.json
3. Ensure the pyxlsb package is installed for .xlsb files

### Google Drive Access Issues

**Issue:** Cannot write to Google Drive
**Possible causes:**
- Google Drive not mounted
- Permission issues
- Disk space limitations

**Solutions:**
1. Verify Google Drive is mounted and accessible
2. Check write permissions on the G: drive
3. Ensure sufficient disk space

### Application Crashes

**Issue:** The application crashes unexpectedly
**Possible causes:**
- Python environment issues
- Missing dependencies
- Corrupted configuration

**Solutions:**
1. Check the log files for error details
2. Reinstall the application
3. Reset the configuration file to defaults

## Logging Information

Detailed logs are stored in the `logs` directory. When reporting an issue, please include:

1. The exact error message
2. The date and time when the error occurred
3. The relevant log file
4. Any changes made to the system prior to the error

## Recovery Procedures

### Manual Transfer Process

If the automation fails completely, follow these steps:

1. Connect to the VPN manually
2. Open the Excel file and filter for PP in column AJ and empty cells in column AK
3. Locate the corresponding batch folders on the Z: drive
4. Copy the files manually to the G: drive

### Reset Application State

To reset the application state:

1. Close the application
2. Delete the `logs/transfer_transactions.json` file (optional)
3. Restart the application