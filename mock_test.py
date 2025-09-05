"""Simple mock environment for local testing"""

import json
import shutil
from pathlib import Path
import pandas as pd

def setup_mock_environment():
    """Create minimal mock data for testing"""
    print("Setting up mock environment...")
    
    if Path("mock_data").exists():
        shutil.rmtree("mock_data")
    
    Path("mock_data/batch_documents/TEST001").mkdir(parents=True)
    Path("mock_data/batch_documents/TEST002").mkdir(parents=True)
    Path("mock_data/gdrive").mkdir(parents=True)
    Path("mock_data/excel").mkdir(parents=True)
    
    Path("mock_data/batch_documents/TEST001/document.pdf").write_text("Mock PDF")
    Path("mock_data/batch_documents/TEST002/report.txt").write_text("Mock Report")
    
    data = {
        'Batch ID': ['TEST001', 'TEST002', 'TEST003'],
        'AJ': ['PP', 'PP', 'JD'],
        'AK': ['', '', 'Released']
    }
    df = pd.DataFrame(data)
    df.to_excel("mock_data/excel/test.xlsx", index=False)
    
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
        "notifications": {"enabled": False}
    }
    
    with open("mock_settings.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Mock environment ready")
    print("Run: python src/main.py --config=mock_settings.json --test-mode")

def test_mock_workflow():
    """Test with mock data"""
    from src.settings import load_config
    from src.main import run_transfer_workflow
    
    if not Path("mock_settings.json").exists():
        print("❌ Run setup first: python mock_test.py")
        return
    
    config = load_config("mock_settings.json")
    result = run_transfer_workflow(config, test_mode=True)
    
    # Check results
    copied_folders = list(Path("mock_data/gdrive").glob("TEST*"))
    print(f"✅ Workflow result: {result}")
    print(f"✅ Copied folders: {len(copied_folders)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mock_workflow()
    else:
        setup_mock_environment()