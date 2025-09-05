"""Test transfer functionality"""
import pytest
import tempfile
from pathlib import Path
from src.transfer import get_batch_id, verify_paths

def test_get_batch_id():
    """Test batch ID extraction"""
    batch_record = {"Batch ID": "TEST001", "Product": "Test Product"}
    batch_id = get_batch_id(batch_record)
    assert batch_id == "TEST001"

def test_get_batch_id_alternative_column():
    """Test batch ID from alternative column"""
    batch_record = {"BatchID": "TEST002", "Product": "Test Product"}
    batch_id = get_batch_id(batch_record)
    assert batch_id == "TEST002"

def test_verify_paths_success():
    """Test path verification with valid paths"""
    with tempfile.TemporaryDirectory() as temp_dir:
        paths = {
            "remote_server": temp_dir,
            "excel_file": temp_dir + "/test.xlsx",
            "batch_documents": temp_dir,
            "local_gdrive": temp_dir
        }
        
        Path(paths["excel_file"]).touch()
        
        result = verify_paths(paths)
        assert result == True

def test_verify_paths_failure():
    """Test path verification with invalid paths"""
    paths = {
        "remote_server": "/nonexistent/path",
        "excel_file": "/nonexistent/file.xlsx",
        "batch_documents": "/nonexistent/batches",
        "local_gdrive": "/nonexistent/gdrive"
    }
    
    result = verify_paths(paths)
    assert result == False