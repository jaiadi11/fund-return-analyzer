
import math


def _validate_returns(returns):
    """Validate monthly decimal returns and return a list of floats."""
    try:
        values = list(returns)
    except TypeError as exc:
        raise ValueError("Returns must be an iterable of numbers.") from exc

    if not values:
        raise ValueError("Returns cannot be empty.")

    validated = []

    for value in values:
        if isinstance(value, bool):
            raise ValueError("Boolean values are not valid returns.")

        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("All returns must be numeric.") from exc

        if not math.isfinite(value):
            raise ValueError("Returns must be finite numbers.")

        if value < -1.0:
            raise ValueError("A return cannot be below -100%.")

        validated.append(value)

    return validated


def geometric_annualized_return(returns):
    """
    Calculate geometric annualized return from monthly decimal returns.

    Formula:
        product(1 + monthly return) ** (12 / number of months) - 1

    Returns a decimal: 0.12 means 12%.
    """
    monthly_returns = _validate_returns(returns)

    if any(value == -1.0 for value in monthly_returns):
        return -1.0

    growth_factor = math.prod(1.0 + value for value in monthly_returns)

    return growth_factor ** (12.0 / len(monthly_returns)) - 1.0


def annualized_volatility(returns):
    """
    Calculate annualized volatility using sample standard deviation.

    Monthly standard deviation uses ddof=1.
    Annualized volatility = monthly standard deviation * sqrt(12).

    Returns a decimal: 0.15 means 15%.
    """
    monthly_returns = _validate_returns(returns)

    if len(monthly_returns) < 2:
        raise ValueError(
            "At least two monthly observations are required."
        )

    mean_return = sum(monthly_returns) / len(monthly_returns)

    squared_deviations = [
        (value - mean_return) ** 2
        for value in monthly_returns
    ]

    sample_variance = sum(squared_deviations) / (
        len(monthly_returns) - 1
    )

    return math.sqrt(sample_variance) * math.sqrt(12.0)


def sharpe_ratio(returns, annual_risk_free_rate):
    """
    Calculate the conventional annualized Sharpe ratio.

    annual_risk_free_rate must be a decimal:
        0.04 means 4% per year.

    Sharpe = (geometric annualized return - annual risk-free rate)
             / annualized volatility

    Raises ValueError when volatility is zero or inputs are invalid.
    """
    if isinstance(annual_risk_free_rate, bool):
        raise ValueError("Risk-free rate must be numeric.")

    try:
        risk_free_rate = float(annual_risk_free_rate)
    except (TypeError, ValueError) as exc:
        raise ValueError("Risk-free rate must be numeric.") from exc

    if not math.isfinite(risk_free_rate):
        raise ValueError("Risk-free rate must be finite.")

    annual_return = geometric_annualized_return(returns)
    annual_volatility = annualized_volatility(returns)

    if annual_volatility == 0.0:
        raise ValueError(
            "Sharpe ratio is undefined when volatility is zero."
        )

    return (annual_return - risk_free_rate) / annual_volatility
