
import math

import pytest

from src.metrics import (
    geometric_annualized_return,
    annualized_volatility,
    sharpe_ratio,
)


# Geometric annualized return

def test_constant_positive_monthly_returns():
    returns = [0.01] * 12
    assert geometric_annualized_return(returns) == pytest.approx(
        1.01**12 - 1
    )


def test_mixed_positive_and_negative_returns():
    returns = [0.10, -0.05, 0.02]
    expected = (1.10 * 0.95 * 1.02) ** 4 - 1
    assert geometric_annualized_return(returns) == pytest.approx(expected)


def test_all_zero_returns():
    assert geometric_annualized_return([0.0] * 12) == pytest.approx(0.0)


def test_empty_history_is_rejected():
    with pytest.raises(ValueError):
        geometric_annualized_return([])


def test_single_month_history_is_supported():
    assert geometric_annualized_return([0.02]) == pytest.approx(
        1.02**12 - 1
    )


def test_total_loss_returns_negative_one():
    assert geometric_annualized_return([0.05, -1.0, 0.10]) == -1.0


@pytest.mark.parametrize("returns", [[0.05, -1.01], [0.05, -1.50]])
def test_returns_below_total_loss_are_rejected(returns):
    with pytest.raises(ValueError):
        geometric_annualized_return(returns)


@pytest.mark.parametrize(
    "returns",
    [
        [0.05, float("nan")],
        [0.05, float("inf")],
        [0.05, float("-inf")],
        [0.05, "invalid"],
    ],
)
def test_invalid_returns_are_rejected(returns):
    with pytest.raises(ValueError):
        geometric_annualized_return(returns)


# Annualized volatility

def test_annualized_volatility_known_values():
    assert annualized_volatility([0.01, 0.02, 0.03]) == pytest.approx(
        0.01 * math.sqrt(12)
    )


def test_constant_returns_have_zero_volatility():
    assert annualized_volatility([0.02, 0.02, 0.02]) == pytest.approx(0.0)


def test_zero_returns_have_zero_volatility():
    assert annualized_volatility([0.0, 0.0, 0.0]) == pytest.approx(0.0)


@pytest.mark.parametrize("returns", [[], [0.02]])
def test_volatility_requires_two_observations(returns):
    with pytest.raises(ValueError):
        annualized_volatility(returns)


def test_volatility_rejects_invalid_values():
    with pytest.raises(ValueError):
        annualized_volatility([0.01, float("nan")])


# Sharpe ratio

def test_sharpe_ratio_uses_supplied_risk_free_rate():
    returns = [0.01, 0.02, 0.03]
    annual_return = geometric_annualized_return(returns)
    annual_volatility = annualized_volatility(returns)

    expected = (annual_return - 0.02) / annual_volatility

    assert sharpe_ratio(returns, 0.02) == pytest.approx(expected)


def test_higher_risk_free_rate_reduces_sharpe_ratio():
    returns = [0.01, 0.02, 0.03]

    assert sharpe_ratio(returns, 0.02) > sharpe_ratio(returns, 0.04)


def test_zero_risk_free_rate_is_supported():
    returns = [0.01, 0.02, 0.03]

    expected = (
        geometric_annualized_return(returns)
        / annualized_volatility(returns)
    )

    assert sharpe_ratio(returns, 0.0) == pytest.approx(expected)


def test_negative_risk_free_rate_is_supported():
    returns = [0.01, 0.02, 0.03]

    expected = (
        geometric_annualized_return(returns) + 0.01
    ) / annualized_volatility(returns)

    assert sharpe_ratio(returns, -0.01) == pytest.approx(expected)


def test_sharpe_ratio_rejects_zero_volatility():
    with pytest.raises(ValueError, match="volatility is zero"):
        sharpe_ratio([0.02, 0.02, 0.02], 0.03)


@pytest.mark.parametrize(
    "rate",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        "invalid",
        None,
        True,
    ],
)
def test_invalid_risk_free_rates_are_rejected(rate):
    with pytest.raises(ValueError):
        sharpe_ratio([0.01, 0.02, 0.03], rate)
