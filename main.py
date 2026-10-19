
from pathlib import Path

from src.data_loader import load_excel
from src.validation import validate_returns


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

    # 4. Validate the loaded data
    issues = validate_returns(data)

    # 5. Display validation results
    print("\nVALIDATION REPORT")
    print("-" * 55)

    if not issues:
        print("No validation issues detected.")
        print("\nSTATUS: VALIDATION PASSED")

    else:
        for issue in issues:
            print(f"- {issue}")

        errors = [
            issue for issue in issues
            if issue.startswith("ERROR:")
        ]

        warnings = [
            issue for issue in issues
            if issue.startswith("WARNING:")
        ]

        if errors:
            print("\nSTATUS: VALIDATION FAILED")
            print("Resolve the reported errors before proceeding.")
        elif warnings:
            print("\nSTATUS: REVIEW REQUIRED")
            print("Review the warnings before proceeding.")
        else:
            print("\nSTATUS: REVIEW REQUIRED")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
