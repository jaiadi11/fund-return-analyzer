
from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_excel


SAMPLE_FILE = (
    Path(__file__).resolve().parents[1]
    / "sample_data"
    / "sample_monthly_returns.xlsx"
)


def test_load_sample_excel():
    data = load_excel(SAMPLE_FILE, sheet_name="Monthly_Returns")

    assert not data.empty
    assert list(data.columns) == [
        "Month", "Fund_A", "Fund_B", "Fund_C"
    ]
    assert len(data) == 12


def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        load_excel("sample_data/does_not_exist.xlsx")


def test_non_xlsx_file_is_rejected(tmp_path):
    csv_file = tmp_path / "returns.csv"
    csv_file.write_text("Month,Fund_A\n2025-01,0.025")

    with pytest.raises(ValueError, match="Only .xlsx"):
        load_excel(csv_file)


def test_empty_worksheet_is_rejected(tmp_path):
    empty_file = tmp_path / "empty.xlsx"
    pd.DataFrame().to_excel(empty_file, index=False)

    with pytest.raises(ValueError, match="contains no data"):
        load_excel(empty_file)
