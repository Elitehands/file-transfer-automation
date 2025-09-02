"""Create test Excel file for local testing"""
import pandas as pd
from pathlib import Path


excel_dir = Path("mock_environment/Z_drive/Quality Assurance(QA Common)/25.Product Status Log")
excel_dir.mkdir(exist_ok=True, parents=True)

# test data
data = {
    'Batch ID': ['TEST001', 'TEST002', 'TEST003'],
    'Product': ['Product1', 'Product2', 'Product3'],
    'AJ': ['PP', 'JD', 'PP'],
    'AK': ['', 'Released', '']
}

df = pd.DataFrame(data)

# Save to Excel file
file_path = excel_dir / "test_status.xlsx"
df.to_excel(file_path, index=False)

print(f"Created test Excel file at {file_path}")