import pandas as pd
from pathlib import Path

# Define the path
excel_path = Path("mock_demo/Z_content/Quality Assurance(QA Common)/25.Product Status Log")
excel_path.mkdir(parents=True, exist_ok=True)

# Create test data - 2 unreleased PP batches, 1 released PP batch, 1 other person's batch
data = {
    'Batch ID': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
    'Product': ['Test Product 1', 'Test Product 2', 'Test Product 3', 'Test Product 4'],
    'AJ': ['PP', 'PP', 'PP', 'JD'],
    'AK': ['', '', 'Released', '']  # First two are unreleased PP batches
}

# Create DataFrame and save to Excel
df = pd.DataFrame(data)
file_path = excel_path / "Product status Log.xlsx"
df.to_excel(file_path, index=False)

print(f"Created Excel file at {file_path} with test batch data")