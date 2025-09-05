# tests/test_integration.py
"""Integration tests that can run without actual files"""
import pytest
from unittest.mock import patch, MagicMock
from src.main import run_transfer_workflow

@patch('src.main.ensure_vpn_connection')
@patch('src.main.verify_paths') 
@patch('src.main.read_excel_batches')
@patch('src.main.process_all_batches')
@patch('src.main.send_completion_email')
def test_successful_workflow(mock_email, mock_process, mock_excel, mock_verify, mock_vpn):
    """Test complete workflow with mocks"""
    # Setup mocks
    mock_vpn.return_value = True
    mock_verify.return_value = True
    mock_excel.return_value = [{"Batch ID": "TEST001"}]
    mock_process.return_value = {
        "total_batches": 1,
        "successful_transfers": 1, 
        "failed_transfers": 0,
        "total_files_copied": 5
    }
    mock_email.return_value = True
    
    config = {
        "vpn": {"connection_name": "test_vpn"},
        "paths": {
            "remote_server": "/test", "excel_file": "/test.xlsx",
            "batch_documents": "/test", "local_gdrive": "/test"
        },
        "excel": {
            "filter_criteria": {
                "initials_column": "AJ", "initials_value": "PP", 
                "release_status_column": "AK"
            }
        }
    }
    
    result = run_transfer_workflow(config, test_mode=True)
    assert result == True
    
    # Verify all functions were called
    mock_vpn.assert_called_once()
    mock_verify.assert_called_once()
    mock_excel.assert_called_once()
    mock_process.assert_called_once()