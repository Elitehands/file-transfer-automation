"""Build script for creating executable with PyInstaller"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_previous_build():
    """Remove previous build artifacts"""
    print("Cleaning previous build artifacts...")
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    for item in Path(".").glob("*.spec"):
        item.unlink()

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    

    with open("version.txt", "w") as f:
        from datetime import datetime
        f.write(f"Build: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=file_transfer_automation",
        "--add-data=version.txt;.",
        "--icon=resources/icon.ico" if Path("resources/icon.ico").exists() else "",
        "--noconsole",  # Remove this if you want console output
        "main.py"
    ]
    

    cmd = [arg for arg in cmd if arg]
    
    # Run PyInstaller
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("Error building executable")
        sys.exit(1)
    
    print(f"Executable built successfully: {Path('dist/file_transfer_automation.exe').absolute()}")
    

    copy_additional_files()

def copy_additional_files():
    """Copy additional files to dist directory"""
    print("Copying additional files...")
    

    with open("dist/.env.example", "w") as f:
        f.write("""# File Transfer Automation Configuration
VPN_CONNECTION_NAME=bbuk vpn
VPN_SERVER=vpn.bbukltd.com

# File Paths (Update these based on actual drive mappings)
REMOTE_SERVER_PATH=Z:\\Quality Assurance(QA Common)
EXCEL_FILE_PATH=Z:\\Quality Assurance(QA Common)\\25.Product Status Log\\Product status Log.xlsb
BATCH_DOCUMENTS_PATH=Z:\\Quality Assurance(QA Common)\\3.Batch Documents
LOCAL_GDRIVE_PATH=G:\\My Drive\\status log

# Excel Filter Configuration
INITIALS_COLUMN=AJ
INITIALS_VALUE=PP
RELEASE_STATUS_COLUMN=AK

# Logging Configuration
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# Notification Configuration
NOTIFICATIONS_ENABLED=false
SMTP_SERVER=smtp.company.com
SMTP_PORT=587
FROM_EMAIL=automation@company.com
TO_EMAILS=example@company.com

# System Configuration
TEST_MODE=false
MAX_RETRY_ATTEMPTS=3
TRANSFER_TIMEOUT_SECONDS=300
""")


    if Path("docs").exists():
        if not Path("dist/docs").exists():
            Path("dist/docs").mkdir()
        
        for doc_file in Path("docs").glob("*.md"):
            shutil.copy(doc_file, f"dist/docs/{doc_file.name}")
    
    print("Additional files copied successfully")

if __name__ == "__main__":
    clean_previous_build()
    build_executable()
    print("Build complete!")