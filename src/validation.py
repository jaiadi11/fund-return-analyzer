
import pandas as pd


def validate_returns(data):
    """
    Validate monthly mutual fund return data.

    Returns a list of issues without modifying the original data.
    """
    issues = []

    # 1. Check for the required Month column
    if "Month" not in data.columns:
        return ["ERROR: Required column 'Month' is missing."]

    # Identify the fund columns
    fund_columns = [
        column for column in data.columns
        if column != "Month"
    ]

    # 2. Check that at least one fund column exists
    if not fund_columns:
        return ["ERROR: At least one fund column is required."]

    # 3. Check for invalid or missing dates
    dates = pd.to_datetime(data["Month"], errors="coerce")
    invalid_dates = dates.isna()

    if invalid_dates.any():
        issues.append(
            f"ERROR: {invalid_dates.sum()} invalid or missing month value(s)."
        )

    # 4. Check for duplicate monthly observations
    valid_dates = dates[~invalid_dates]
    monthly_periods = valid_dates.dt.to_period("M")

    if monthly_periods.duplicated().any():
        issues.append(
            "ERROR: Duplicate monthly observations found."
        )

    # 5 and 6. Check each fund's return values
    for fund in fund_columns:
        original = data[fund]
        numeric = pd.to_numeric(original, errors="coerce")

        missing = original.isna()
        nonnumeric = original.notna() & numeric.isna()

        if missing.any():
            issues.append(
                f"ERROR: {fund} has "
                f"{missing.sum()} missing return value(s)."
            )

        if nonnumeric.any():
            issues.append(
                f"ERROR: {fund} has "
                f"{nonnumeric.sum()} nonnumeric return value(s)."
            )

        # 7. Warn about possible return-scale problems
        valid_returns = numeric.dropna()

        if (valid_returns.abs() > 1).any():
            issues.append(
                f"WARNING: {fund} contains return values outside "
                "the usual decimal range. Check whether percentages "
                "were entered instead of decimals."
            )

    return issues
