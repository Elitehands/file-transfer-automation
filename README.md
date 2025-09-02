Automates the daily transfer of production batch files from remote server to Google Drive.

Overview
This system:
- Monitors Excel file for unreleased batches assigned to specific initials
- Automatically transfers batch documents from Z: drive to G: drive  
- Provides comprehensive logging and error handling
- Runs on scheduled intervals (8am, 12pm, 4pm)

Setup Instructions
Prerequisites
- Python 3.8+ installed
- VPN access to bbuk vpn
- Access to Z: and G: drives
- Required Python packages (see requirements.txt)

Installation

1. Clone/Download the project
   ```bash
   git clone [repository-url]
   cd file-transfer-automation
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure settings
   - Copy `config/settings.json.template` to `config/settings.json`
   - Update paths and notification settings as needed

4. Test the installation
   ```bash
   python main.py --test-mode --log-level DEBUG
   ```

 Configuration

Edit `config/settings.json`:

```json
{
    "vpn_connection_name": "bbuk vpn",
    "excel_file_path": "Z:\\Quality Assurance(QA Common)\\25.Product Status Log\\Product status Log.xlsb",
    "batch_documents_path": "Z:\\Quality Assurance(QA Common)\\3.Batch Documents",
    "local_gdrive_path": "G:\\BatchTransfers",
    "filter_criteria": {
        "initials_column": "AJ",
        "initials_value": "PP", 
        "release_status_column": "AK"
    }
}
```

 Usage
 Manual Execution
```bash
 Normal mode
python main.py

Test mode (uses mock data)
python main.py --test-mode

 Debug mode
python main.py --log-level DEBUG
```

Scheduled Execution
Set up Windows Task Scheduler to run at 8am, 12pm, and 4pm:
```bash
 Command to run
C:\Path\To\Python\python.exe C:\Path\To\Script\main.py

 Or use the compiled EXE
C:\Path\To\Script\file_transfer_automation.exe
```

 How It Works
1. VPN Verification: Checks 'bbuk vpn' connection, auto-connects if needed
2. Drive Access: Verifies Z: and G: drives are accessible
3. Excel Parsing: Reads Product status Log.xlsb, filters for:
   - Column AJ = "PP" (your initials)
   - Column AK = empty (not released)
4. File Transfer: Copies batch folders from Z: to G: drive
5. Verification: Confirms all files copied successfully
6. Logging: Records all operations with timestamps
7. Notifications: Sends completion/error alerts

 Project Structure
```
file-transfer-automation/
├── main.py                  Entry point
├── src/
│   ├── vpn_manager.py       VPN connection handling
│   ├── drive_manager.py     Drive access verification  
│   ├── excel_reader.py      Excel file parsing
│   ├── file_processor.py    File copying operations
│   ├── logger.py            Logging configuration
│   ├── notifier.py          Notification system
│   └── config_manager.py    Configuration management
├── tests/
│   ├── test_vpn_manager.py
│   ├── test_excel_reader.py
│   ├── test_file_processor.py
│   ├── test_drive_manager.py
│   └── test_integration.py
├── config/
│   └── settings.json        Configuration file
├── logs/                    Log files (auto-created)
├── mock_data/              Test data (for development)
├── requirements.txt
└── README.md
```

 Testing
 Run Unit Tests
```bash
 All tests
 pytest tests/ -v

 With coverage
 pytest tests/ -v --cov=src --cov-report=html

 Specific test file
 pytest tests/test_vpn_manager.py -v
```

 Test Scenarios Covered
- VPN connection and reconnection
- Drive accessibility verification
- Excel file parsing and filtering
- File copying with verification
- Error handling and recovery
- End-to-end workflow simulation

 Error Handling

The system includes comprehensive error handling:

- VPN Issues: Auto-reconnect with retry logic
- Drive Access: Verification before operations
- File Conflicts: Skip existing files, copy only new/modified
- Excel Errors: Graceful handling of locked/missing files
- Transfer Failures: Detailed logging and notifications

 Logging

Logs are saved to `logs/` directory:
- Console: INFO level and above
- File: Configurable level (DEBUG, INFO, WARNING, ERROR)
- Rotation: Automatic log rotation to prevent large files
- Transfer History: JSON log of all transfer operations

 Troubleshooting

 Common Issues

1. VPN Connection Fails
   - Check VPN credentials
   - Verify "bbuk vpn" connection name
   - Run manually: `rasdial "bbuk vpn"`

2. Drive Access Denied
   - Verify Z: drive mapping
   - Check G: drive (Google Drive) is running
   - Confirm user permissions

3. Excel File Locked
   - Close Excel if open on remote PC
   - Script will retry automatically

4. No Batches Found
   - Verify column names (AJ, AK)
   - Check initials value (PP)
   - Confirm Excel file path

 Debug Mode
 Run with `--log-level DEBUG` for detailed troubleshooting information.

 Building Executable

To create standalone EXE file:

```bash
 Install PyInstaller
pip install pyinstaller

 Build EXE
pyinstaller --onefile --add-data "config;config" main.py

 Output will be in dist/main.exe
```

 Security Considerations

- No credentials stored in code
- Configuration file should be secured
- VPN credentials managed by Windows
- File operations logged for audit trail

 Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Run in debug mode for detailed information
3. Review error notifications
4. Contact the development team

---

Version: 1.0  
Last Updated: September 2025  

