"""Enhanced mock test with QA checklist simulation - AL filter removed"""

import json
import shutil
from pathlib import Path
import pandas as pd

def setup_mock_environment_with_qa():
    """Create mock data including QA checklist files"""
    print("Setting up mock environment with QA testing...")
    
    if Path("mock_data").exists():
        shutil.rmtree("mock_data")
    
    # Create folder structure
    Path("mock_data/batch_documents/TEST001").mkdir(parents=True)
    Path("mock_data/batch_documents/TEST002").mkdir(parents=True) 
    Path("mock_data/batch_documents/TEST003").mkdir(parents=True)
    Path("mock_data/gdrive").mkdir(parents=True)
    Path("mock_data/excel").mkdir(parents=True)
    
    # TEST001 - Regular batch (no QA)
    Path("mock_data/batch_documents/TEST001/document.pdf").write_text("Mock PDF")
    Path("mock_data/batch_documents/TEST001/specs.txt").write_text("Mock Specs")
    
    # TEST002 - QA Ready batch (has checklist)
    Path("mock_data/batch_documents/TEST002/report.txt").write_text("Mock Report")
    Path("mock_data/batch_documents/TEST002/QA_Batch_Review_Checklist.xlsx").write_text("Mock QA Checklist")
    Path("mock_data/batch_documents/TEST002/data.csv").write_text("Mock Data")
    
    # TEST003 - Another QA Ready batch (different QA pattern)
    Path("mock_data/batch_documents/TEST003/analysis.pdf").write_text("Mock Analysis")
    Path("mock_data/batch_documents/TEST003/qa_checklist_final.docx").write_text("Mock QA Final")
    
    # Create Excel with all 3 batches (AL column removed)
    data = {
        'Batch ID': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'AJ': ['PP', 'PP', 'PP', 'JD'],  # PP batches will be processed
        'AK': ['', '', '', 'Released']   # Empty = ready for processing
    }
    df = pd.DataFrame(data)
    df.to_excel("mock_data/excel/test.xlsx", index=False)
    
    # Config with QA recipients (AL filter removed)
    config = {
        "paths": {
            "remote_server": str(Path("mock_data").absolute()),
            "excel_file": str(Path("mock_data/excel/test.xlsx").absolute()),
            "batch_documents": str(Path("mock_data/batch_documents").absolute()),
            "local_gdrive": str(Path("mock_data/gdrive").absolute())
        },
        "excel": {
            "filter_criteria": {
                "initials_column": "AJ",
                "initials_value": "PP", 
                "release_status_column": "AK"
            }
        },
        "notifications": {
            "enabled": True,
            "qa_recipients": ["aneta.jell@company.com", "paul.palmer@company.com"],
            "recipients": ["admin@company.com"],
            "smtp": {
                "server": "smtp.gmail.com",
                "port": 587,
                "username": "test@company.com",
                "password": "test_password"
            },
            "sender": {
                "name": "File Transfer System",
                "email": "test@company.com"
            }
        }
    }
    
    with open("mock_settings_qa.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Mock environment with QA ready")
    print("Run: python src/main.py --config=mock_settings_qa.json --test-mode")

def setup_mock_environment():
    """Create essential mock data for testing"""
    if Path("mock_data").exists():
        shutil.rmtree("mock_data")
    
    # Create required folders  
    Path("mock_data/batch_documents/TEST001").mkdir(parents=True)
    Path("mock_data/batch_documents/TEST002").mkdir(parents=True) 
    Path("mock_data/batch_documents/TEST003").mkdir(parents=True)
    Path("mock_data/gdrive").mkdir(parents=True)
    
    # Create Excel file (AL column removed)
    data = {
        'Batch ID': ['TEST001', 'TEST002', 'TEST003'],
        'AJ': ['PP', 'PP', 'PP'],
        'AK': ['', '', '']
    }
    df = pd.DataFrame(data)
    df.to_excel("mock_data/Product_Status_Log.xlsx", index=False)
    
    print("Mock environment ready")
    print("Run: python src/main.py --config=test_settings.json --test-mode")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test workflow code here
        pass
    else:
        setup_mock_environment()