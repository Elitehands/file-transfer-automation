# tests/test_settings.py
"""Test configuration loading"""
import pytest
import tempfile
import json
from pathlib import Path
from src.settings import load_config, get_paths

def test_load_config_success():
    """Test successful config loading"""
    config_data = {
        "vpn": {"connection_name": "test_vpn"},
        "paths": {
            "remote_server": "/test/remote",
            "excel_file": "/test/excel.xlsx", 
            "batch_documents": "/test/batches",
            "local_gdrive": "/test/gdrive"
        },
        "excel": {
            "filter_criteria": {
                "initials_column": "AJ",
                "initials_value": "PP", 
                "release_status_column": "AK"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    config = load_config(config_path)
    assert config["vpn"]["connection_name"] == "test_vpn"
    
    Path(config_path).unlink()

def test_get_paths():
    """Test path extraction"""
    config = {
        "paths": {
            "remote_server": "/remote",
            "excel_file": "/excel.xlsx",
            "batch_documents": "/batches", 
            "local_gdrive": "/gdrive"
        }
    }
    
    paths = get_paths(config)
    assert len(paths) == 4
    assert paths["remote_server"] == "/remote"