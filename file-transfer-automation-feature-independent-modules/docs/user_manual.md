# File Transfer Automation - User Manual

## Overview

This application automatically transfers batch files from the remote server (Z: drive) to Google Drive (G: drive). It filters batch documents based on the Product Status Log Excel file, looking for entries with "PP" in column AJ and empty cells in column AK.

## Installation

1. Extract the application to a folder on the PC
2. Copy the `.env.example` file to `.env` and update settings if needed
3. Run the application once to verify it works

## Configuration

Settings can be modified in the `config/settings.json` file:

- **vpn_connection_name**: Name of the VPN connection ("bbuk vpn")
- **remote_server_path**: Path to the remote server (Z: drive location)
- **excel_file_path**: Path to the Product Status Log Excel file
- **batch_documents_path**: Path to the batch documents folder
- **local_gdrive_path**: Path to the Google Drive destination folder
- **filter_criteria**: Configuration for filtering batch records
- **schedule_times**: Times when the task should run daily
- **retry_attempts**: Number of retry attempts for failed operations
- **notifications**: Email notification settings

## Running the Application

### Manual Execution

Simply run the `file_transfer_automation.exe` file to start the transfer process.

### Scheduled Execution

The application is configured to run automatically at 8am, 12pm, and 4pm daily. See the "Task Scheduler Setup" guide for details on configuring or modifying this schedule.

## Logs

Log files are stored in the `logs` directory:
- Daily operation logs: `transfer_automation_YYYY-MM-DD.log`
- Transfer history: `transfer_history.json`
- Transaction log: `transfer_transactions.json`

## Support

For issues or assistance, please contact the IT support team.