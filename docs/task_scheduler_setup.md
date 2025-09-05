# Windows Task Scheduler Setup Guide

This guide explains how to set up the File Transfer Automation tool to run automatically at scheduled times using Windows Task Scheduler.

## Prerequisites

- Windows 10 or Windows Server 2016+
- Administrative privileges
- File Transfer Automation executable installed

## Setup Instructions

### Step 1: Open Task Scheduler

1. Press `Win + R` to open the Run dialog
2. Type `taskschd.msc` and press Enter
3. Task Scheduler will open

### Step 2: Create a New Task

1. In the right pane, click on "Create Basic Task..."
2. Enter a name: `File Transfer Automation`
3. Description: `Automated transfer of batch files from remote server to Google Drive`
4. Click "Next"

### Step 3: Set the Trigger Schedule

For running at 8am, 12pm, and 4pm:

1. Select "Daily" and click "Next"
2. Set start date to today and time to 8:00:00 AM
3. Click "Next"
4. Select "Start a program" and click "Next"
5. Browse to select the `file_transfer_automation.exe` file
6. Click "Next" and then "Finish"

### Step 4: Edit the Task for Multiple Daily Times

1. Find your task in the Task Scheduler Library
2. Right-click on the task and select "Properties"
3. Go to the "Triggers" tab
4. Select the trigger you created and click "Edit"
5. Click "New" to add additional times:
   - Add 12:00:00 PM
   - Add 4:00:00 PM
6. Click "OK" to save the triggers
7. Click "OK" to save the task

### Step 5: Configure Additional Settings

1. Right-click on the task and select "Properties" again
2. On the "General" tab, check "Run whether user is logged in or not"
3. Under "Configure for:" select your Windows version
4. Go to the "Settings" tab
5. Check "Allow task to be run on demand"
6. Check "Run task as soon as possible after a scheduled start is missed"
7. Set "If the task fails, restart every:" to 5 minutes
8. Set "Attempt to restart up to:" to 3 times
9. Click "OK" to save changes

### Step 6: Test the Task

1. Right-click on the task
2. Select "Run"
3. Check the logs in the application folder to verify it's working correctly

## Troubleshooting

- **Task doesn't run**: Verify the user account has appropriate permissions
- **VPN connection fails**: Ensure VPN credentials are saved in Windows
- **File access errors**: Check that drive mappings are correct

For more assistance, refer to the troubleshooting guide or contact IT support.