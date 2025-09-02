"""Excel file reading and batch filtering"""

import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any


class ExcelReader:
    """Reads and filters Excel files for batch processing"""

    def __init__(self, excel_file_path: str):
        self.excel_file_path = Path(excel_file_path)
        self.logger = logging.getLogger(__name__)

    def get_unreleased_batches(
        self, initials_column: str, initials_value: str, release_column: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of unreleased batches for specified initials

        Args:
            initials_column: Column containing initials (e.g., 'AJ')
            initials_value: Initials to filter for (e.g., 'PP')
            release_column: Column indicating release status (e.g., 'AK')

        Returns:
            List[Dict[str, Any]]: List of batch records to process
        """
        try:
            if not self.excel_file_path.exists():
                raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")

            self.logger.info(f"Reading Excel file: {self.excel_file_path}")
            
            # Determine engine based on file extension
            file_ext = self.excel_file_path.suffix.lower()
            
            if file_ext == '.xlsb':
                engine = 'pyxlsb'
            else:
                engine = 'openpyxl'
                
            self.logger.debug(f"Using Excel engine: {engine} for file type: {file_ext}")
                
            try:
                df = pd.read_excel(self.excel_file_path, engine=engine)
            except Exception as e:
                self.logger.warning(f"Failed to read with {engine} engine: {str(e)}, trying alternative engine")
                # Try alternative engine if first one fails
                engine = 'openpyxl' if engine == 'pyxlsb' else 'pyxlsb'
                df = pd.read_excel(self.excel_file_path, engine=engine)

            filtered_df = df[
                (df[initials_column].astype(str).str.upper() == initials_value.upper())
                & (
                    df[release_column].isna()
                    | (df[release_column].astype(str).str.strip() == "")
                )
            ]

            batches = filtered_df.to_dict("records")

            self.logger.info(
                f"Found {len(batches)} unreleased batches for initials '{initials_value}'"
            )

            for batch in batches:
                batch_id = batch.get("Batch ID", "Unknown")
                self.logger.debug(f"Batch to process: {batch_id}")

            return batches

        except Exception as e:
            self.logger.error(f"Failed to read Excel file: {str(e)}")
            return []

    def get_batch_id_from_record(self, batch_record: Dict[str, Any]) -> str:
        """
        Extract batch ID from batch record

        Args:
            batch_record: Dictionary containing batch information

        Returns:
            str: Batch ID or 'Unknown' if not found
        """
        possible_id_columns = ["Batch ID", "BatchID", "Batch_ID", "ID", "Batch Number"]

        for col in possible_id_columns:
            if col in batch_record and batch_record[col]:
                return str(batch_record[col]).strip()

        self.logger.warning(
            f"Could not find batch ID in record: {list(batch_record.keys())}"
        )
        return "Unknown"