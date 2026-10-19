
import pandas as pd
import pytest

from src.scale_review import (
    find_scale_flags,
    apply_scale_decisions,
)


def sample_data():
    return pd.DataFrame({
        "Month": ["2025-01", "2025-02", "2025-03"],
        "Fund_A": [0.025, 2.5, -0.010],
        "Fund_B": [0.020, 0.015, -0.005],
    })


def test_suspicious_value_is_flagged():
    flags = find_scale_flags(sample_data())

    assert len(flags) == 1
    assert flags[0]["fund"] == "Fund_A"
    assert flags[0]["original_value"] == 2.5
    assert flags[0]["proposed_value"] == 0.025


def test_normal_decimal_returns_are_not_flagged():
    data = sample_data()
    data.loc[1, "Fund_A"] = 0.025

    assert find_scale_flags(data) == []


def test_approved_conversion_changes_working_copy():
    data = sample_data()

    corrected = apply_scale_decisions(
        data,
        {(1, "Fund_A"): "convert"},
    )

    assert corrected.iloc[1]["Fund_A"] == pytest.approx(0.025)
    assert data.iloc[1]["Fund_A"] == 2.5


def test_keep_decision_preserves_value():
    data = sample_data()

    corrected = apply_scale_decisions(
        data,
        {(1, "Fund_A"): "keep"},
    )

    assert corrected.iloc[1]["Fund_A"] == 2.5


def test_invalid_decision_is_rejected():
    with pytest.raises(ValueError, match="Decision must be"):
        apply_scale_decisions(
            sample_data(),
            {(1, "Fund_A"): "maybe"},
        )
