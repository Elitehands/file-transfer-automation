import json
import os
from pathlib import Path

# Create directories
demo_dir = Path("mock_demo")
config_dir = demo_dir / "config"
logs_dir = demo_dir / "logs"

os.makedirs(config_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

# Create settings.json
settings = {
  "vpn": {
    "connection_name": "bbuk vpn",
    "max_retries": 1,
    "retry_delay": 2
  },
  "paths": {
    "remote_server": "Z:\\Quality Assurance(QA Common)",
    "excel_file": "Z:\\Quality Assurance(QA Common)\\25.Product Status Log\\Product status Log.xlsx",
    "batch_documents": "Z:\\Quality Assurance(QA Common)\\3.Batch Documents",
    "local_gdrive": "G:\\My Drive\\status log"
  },
  "excel": {
    "filter_criteria": {
      "initials_column": "AJ",
      "initials_value": "PP",
      "release_status_column": "AK"
    }
  },
  "notifications": {
    "enabled": False
  },
  "system": {
    "test_mode": True,
    "vpn_enabled": False  # Bypass VPN check for demo
  }
}

# Write settings.json with proper formatting
with open(config_dir / "settings.json", "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)

# Create .env file
env_content = """
# VPN Configuration (for demo only)
VPN_CONNECTION_NAME=bbuk vpn
VPN_SERVER=vpn.bbukltd.com
VPN_PASSWORD=demopassword

# File Paths 
REMOTE_SERVER_PATH=Z:\\Quality Assurance(QA Common)
EXCEL_FILE_PATH=Z:\\Quality Assurance(QA Common)\\25.Product Status Log\\Product status Log.xlsx
BATCH_DOCUMENTS_PATH=Z:\\Quality Assurance(QA Common)\\3.Batch Documents
LOCAL_GDRIVE_PATH=G:\\My Drive\\status log

# Excel Filter Configuration
INITIALS_COLUMN=AJ
INITIALS_VALUE=PP
RELEASE_STATUS_COLUMN=AK

LOG_LEVEL=INFO
TEST_MODE=true
VPN_ENABLED=false
"""

with open(demo_dir / ".env", "w", encoding="utf-8") as f:
    f.write(env_content)

print("Demo configuration created successfully!")
