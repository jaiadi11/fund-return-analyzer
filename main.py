
from pathlib import Path

from src.data_loader import load_excel
from src.validation import validate_returns
from src.scale_review import find_scale_flags, apply_scale_decisions


def main():
    # 1. Locate the sample Excel workbook
    project_folder = Path(__file__).resolve().parent
    file_path = (
        project_folder
        / "sample_data"
        / "sample_monthly_returns.xlsx"
    )

    print("=" * 55)
    print("       MUTUAL FUND RETURN ANALYZER")
    print("=" * 55)

    # 2. Load the Excel workbook
    try:
        data = load_excel(
            file_path,
            sheet_name="Monthly_Returns"
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"\nDATA LOADING FAILED: {error}")
        return

    print("\nExcel workbook loaded successfully.")

    # 3. Display a preview of the data
    print("\nDATA PREVIEW")
    print("-" * 55)
    print(data.head().to_string(index=False))

    print(f"\nTotal rows: {len(data)}")
    print(f"Total columns: {len(data.columns)}")

    # 4. Validate the original data
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

    # 5. Identify suspicious return-scale values
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
            sum(v == "convert" for v in decisions.values())
        )
        print(
            "Values kept:",
            sum(v == "keep" for v in decisions.values())
        )
        print("Original Excel workbook remains unchanged.")

    else:
        print("\nNo return-scale values were flagged.")

    # 6. Validate the resulting working copy again
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

    print("\nFINAL DATA PREVIEW")
    print("-" * 55)
    print(working_data.head().to_string(index=False))

    print("\nSTATUS: DATA READY FOR THE NEXT STEP")
    print("No financial metrics have been calculated yet.")
    print("=" * 55)


if __name__ == "__main__":
    main()
