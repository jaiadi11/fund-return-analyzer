
import pandas as pd


def find_scale_flags(data):
    """
    Identify numeric return values whose absolute value exceeds 1.

    These are candidates for review, not confirmed errors.
    The original DataFrame is not modified.
    """
    flags = []

    if "Month" not in data.columns:
        raise ValueError("Required column 'Month' is missing.")

    fund_columns = [
        column for column in data.columns
        if column != "Month"
    ]

    for row_position in range(len(data)):
        for fund in fund_columns:
            value = data.iloc[row_position][fund]

            # Ignore missing and nonnumeric values.
            if pd.isna(value):
                continue

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue

            if abs(numeric_value) > 1:
                flags.append({
                    "row_position": row_position,
                    "month": data.iloc[row_position]["Month"],
                    "fund": fund,
                    "original_value": numeric_value,
                    "proposed_value": numeric_value / 100,
                })

    return flags


def apply_scale_decisions(data, decisions):
    """
    Apply explicitly approved conversions to a copy of the data.

    decisions maps (row_position, fund) to "convert" or "keep".
    The original DataFrame remains unchanged.
    """
    corrected_data = data.copy(deep=True)

    for (row_position, fund), decision in decisions.items():
        if fund not in corrected_data.columns or fund == "Month":
            raise ValueError(f"Invalid fund column: {fund}")

        if not isinstance(row_position, int):
            raise ValueError("Row position must be an integer.")

        if not 0 <= row_position < len(corrected_data):
            raise ValueError("Row position is out of range.")

        if decision not in ("convert", "keep"):
            raise ValueError(
                "Decision must be 'convert' or 'keep'."
            )

        if decision == "convert":
            original_value = corrected_data.iloc[
                row_position,
                corrected_data.columns.get_loc(fund)
            ]

            if pd.isna(original_value):
                raise ValueError("Cannot convert a missing value.")

            try:
                numeric_value = float(original_value)
            except (TypeError, ValueError):
                raise ValueError(
                    "Cannot convert a nonnumeric return value."
                ) from None

            if abs(numeric_value) <= 1:
                raise ValueError(
                    "Value is not flagged by the scale rule."
                )

            corrected_data.iloc[
                row_position,
                corrected_data.columns.get_loc(fund)
            ] = numeric_value / 100

    return corrected_data
