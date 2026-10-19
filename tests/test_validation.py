
import pandas as pd

from src.validation import validate_returns


def valid_data():
    return pd.DataFrame({
        "Month": ["2025-01", "2025-02", "2025-03"],
        "Fund_A": [0.025, -0.010, 0.015],
        "Fund_B": [0.020, 0.005, -0.005],
    })


def test_valid_data_has_no_issues():
    assert validate_returns(valid_data()) == []


def test_missing_month_column_is_detected():
    data = valid_data().drop(columns=["Month"])

    issues = validate_returns(data)

    assert any("Month" in issue for issue in issues)


def test_duplicate_month_is_detected():
    data = valid_data()
    data.loc[1, "Month"] = "2025-01"

    issues = validate_returns(data)

    assert any("Duplicate monthly" in issue for issue in issues)


def test_missing_return_is_detected():
    data = valid_data()
    data.loc[0, "Fund_A"] = None

    issues = validate_returns(data)

    assert any("missing return" in issue for issue in issues)


def test_nonnumeric_return_is_detected():
    data = valid_data()
    data["Fund_A"] = data["Fund_A"].astype(object)
    data.loc[0, "Fund_A"] = "invalid"

    issues = validate_returns(data)

    assert any("nonnumeric return" in issue for issue in issues)


def test_percentage_scale_warning_is_detected():
    data = valid_data()
    data.loc[0, "Fund_A"] = 2.5

    issues = validate_returns(data)

    assert any("WARNING" in issue for issue in issues)


def test_missing_fund_columns_are_detected():
    data = valid_data()[["Month"]]

    issues = validate_returns(data)

    assert any("at least one fund" in issue.lower() for issue in issues)
