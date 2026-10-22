
from pathlib import Path
import math

from src.data_loader import load_excel
from src.validation import validate_returns
from src.scale_review import find_scale_flags, apply_scale_decisions
from src.metrics import (
    geometric_annualized_return,
    annualized_volatility,
    sharpe_ratio,
)


def get_annual_risk_free_rate():
    """Prompt for an annual risk-free rate entered as a percentage."""
    while True:
        raw_value = input(
            "\nEnter annual risk-free rate in % (example: 4.5): "
        ).strip()

        try:
            percentage = float(raw_value)
        except ValueError:
            print("Please enter a valid number, such as 4 or 4.5.")
            continue

        if not math.isfinite(percentage):
            print("Enter a finite number.")
            continue

        return percentage / 100.0


def display_metrics(working_data):
    """
    Calculate and display risk-return metrics for every fund.

    Returns remain decimal values internally.
    The Month column is excluded from calculations.
    """
    risk_free_rate = get_annual_risk_free_rate()

    print(f"\nAnnual risk-free rate used: {risk_free_rate:.2%}")

    headers = [
        "Fund",
        "Geometric Annualized Return",
        "Annualized Volatility",
        "Sharpe Ratio",
    ]

    rows = []

    for fund_name in working_data.columns:
        if fund_name == "Month":
            continue

        returns = working_data[fund_name].tolist()

        try:
            annual_return = geometric_annualized_return(returns)
            volatility = annualized_volatility(returns)
            ratio = sharpe_ratio(returns, risk_free_rate)

            rows.append(
                (
                    str(fund_name),
                    f"{annual_return:.2%}",
                    f"{volatility:.2%}",
                    f"{ratio:.2f}",
                )
            )

        except ValueError as error:
            rows.append(
                (str(fund_name), "N/A", "N/A", "N/A")
            )
            print(f"\nCould not calculate metrics for {fund_name}: {error}")

    print("\nFUND RISK-RETURN METRICS")
    print("=" * 105)
    print(
        f"{headers[0]:<20}"
        f"{headers[1]:>30}"
        f"{headers[2]:>27}"
        f"{headers[3]:>18}"
    )
    print("-" * 105)

    for row in rows:
        print(
            f"{row[0]:<20}"
            f"{row[1]:>30}"
            f"{row[2]:>27}"
            f"{row[3]:>18}"
        )

    print("=" * 105)


def main():
    """Run the complete Excel validation and metrics workflow."""
    project_folder = Path(__file__).resolve().parent
    file_path = (
        project_folder
        / "sample_data"
        / "sample_monthly_returns.xlsx"
    )

    print("=" * 55)
    print("       MUTUAL FUND RETURN ANALYZER")
    print("=" * 55)

    # 1. Load the Excel workbook.
    try:
        data = load_excel(
            file_path,
            sheet_name="Monthly_Returns",
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"\nDATA LOADING FAILED: {error}")
        return

    print("\nExcel workbook loaded successfully.")

    # 2. Preview the data.
    print("\nDATA PREVIEW")
    print("-" * 55)
    print(data.head().to_string(index=False))
    print(f"\nTotal rows: {len(data)}")
    print(f"Total columns: {len(data.columns)}")

    # 3. Validate the original data.
    issues = validate_returns(data)

    print("\nINITIAL VALIDATION")
    print("-" * 55)

    for issue in issues:
        print(f"- {issue}")

    errors = [
        issue for issue in issues
        if issue.startswith("ERROR:")
    ]

    if errors:
        print("\nSTATUS: VALIDATION FAILED")
        print("Resolve the errors before proceeding.")
        return

    # 4. Review suspicious return-scale values.
    flags = find_scale_flags(data)
    working_data = data.copy(deep=True)

    if flags:
        print("\nRETURN-SCALE REVIEW")
        print("-" * 55)

        for number, flag in enumerate(flags, start=1):
            print(
                f"{number}. Month: {flag['month']} | "
                f"Fund: {flag['fund']} | "
                f"Original: {flag['original_value']} | "
                f"Proposed: {flag['proposed_value']}"
            )

        print("\nChoose an action:")
        print("1. Convert all flagged values")
        print("2. Keep all original values")
        print("3. Review each value individually")

        while True:
            choice = input("Enter 1, 2, or 3: ").strip()

            if choice in {"1", "2", "3"}:
                break

            print("Invalid choice. Enter 1, 2, or 3.")

        decisions = {}

        for flag in flags:
            key = (flag["row_position"], flag["fund"])

            if choice == "1":
                decisions[key] = "convert"

            elif choice == "2":
                decisions[key] = "keep"

            else:
                print(
                    f"\nFund: {flag['fund']} | "
                    f"Month: {flag['month']}"
                )
                print(f"Original: {flag['original_value']}")
                print(f"Proposed: {flag['proposed_value']}")

                while True:
                    answer = input(
                        "Convert this value? (y/n): "
                    ).strip().lower()

                    if answer in {"y", "n"}:
                        decisions[key] = (
                            "convert" if answer == "y" else "keep"
                        )
                        break

                    print("Enter y or n.")

        try:
            working_data = apply_scale_decisions(data, decisions)
        except ValueError as error:
            print(f"\nSCALE REVIEW FAILED: {error}")
            return

        print("\nSCALE REVIEW SUMMARY")
        print(
            "Values converted:",
            sum(value == "convert" for value in decisions.values()),
        )
        print(
            "Values kept:",
            sum(value == "keep" for value in decisions.values()),
        )
        print("Original Excel workbook remains unchanged.")

    else:
        print("\nNo return-scale values were flagged.")

    # 5. Validate the resulting working copy.
    final_issues = validate_returns(working_data)

    print("\nFINAL VALIDATION")
    print("-" * 55)

    for issue in final_issues:
        print(f"- {issue}")

    final_errors = [
        issue for issue in final_issues
        if issue.startswith("ERROR:")
    ]

    final_warnings = [
        issue for issue in final_issues
        if issue.startswith("WARNING:")
    ]

    if final_errors:
        print("\nSTATUS: VALIDATION FAILED")
        print("Resolve the errors before proceeding.")
        return

    if final_warnings:
        print("\nWarnings remain. Review them before proceeding.")

        while True:
            answer = input(
                "Have you reviewed the remaining warnings? (y/n): "
            ).strip().lower()

            if answer in {"y", "n"}:
                break

            print("Enter y or n.")

        if answer != "y":
            print("Workflow stopped.")
            return

    # 6. Display the validated working data.
    print("\nFINAL DATA PREVIEW")
    print("-" * 55)
    print(working_data.head().to_string(index=False))

    print("\nSTATUS: DATA READY FOR FINANCIAL ANALYSIS")

    # 7. Calculate the metrics only after validation succeeds.
    display_metrics(working_data)

    print("\nAnalysis complete.")
    print("Original Excel workbook remains unchanged.")
    print("=" * 55)


if __name__ == "__main__":
    main()
