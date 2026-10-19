
from pathlib import Path

import pandas as pd


def load_excel(file_path, sheet_name=0):
    """
    Load monthly fund returns from an Excel .xlsx workbook.

    Parameters
    ----------
    file_path : str or Path
        Path to the Excel workbook.
    sheet_name : str or int
        Worksheet name or zero-based worksheet index.

    Returns
    -------
    pandas.DataFrame
        Imported data, with column names stripped of extra spaces.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Excel file not found: {path}")

    if path.suffix.lower() != ".xlsx":
        raise ValueError("Only .xlsx Excel files are supported.")

    data = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

    if data.empty:
        raise ValueError("The selected worksheet contains no data.")

    # Normalize column names without changing the underlying data.
    data.columns = [str(column).strip() for column in data.columns]

    if len(data.columns) != len(set(data.columns)):
        raise ValueError("Duplicate column names found in the worksheet.")

    return data
