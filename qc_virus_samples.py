#!/usr/bin/env python3

# Task: to check the number of samples fails the QC check (using a set cut-off) from each origin


# import libraries

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {
    "sample",
    "pct_covered_bases",
    "qc_pass",
}

# load and inpect data
def load_data(filepath):

    data = pd.read_csv(
        filepath,
        true_values=["TRUE"],
        false_values=["FALSE"]
    )

    # Basic input validation
    missing_columns = REQUIRED_COLUMNS - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    if data.empty:
        raise ValueError("Input file contains no samples.")

    return data


# Extract sample origin and identify samples failing QC.
def identify_failures(data):

    data = data.copy()

    # Second character of sample name identifies origin. This keeps it dynamic for future origins.
    data["origin"] = data["sample"].str[1]

    data["failed"] = (
        (data["pct_covered_bases"] < 95)
        | (data["qc_pass"] == False)
    )

    return data

# Calculate QC failure statistics for each sample origin.
def calculate_summary(data):

    summary = (
        data.groupby("origin")
        .agg(
            total_samples=("sample", "count"),
            failed_samples=("failed", "sum")
        )
        .reset_index()
    )

    summary["failed_percentage"] = (
        summary["failed_samples"]
        / summary["total_samples"]
        * 100
    )

    return summary

# Print QC summary and warnings.
def report_results(summary):
   
    print("\nQC summary by origin:")
    print(summary.to_string(index=False))

    print("\nWarnings:")

    warnings_found = False

    for _, row in summary.iterrows():

        if row["failed_percentage"] > 10:

            warnings_found = True

            logging.warning(
                "Origin %s has %.1f%% failed samples (%d/%d).",
                row["origin"],
                row["failed_percentage"],
                row["failed_samples"],
                row["total_samples"]
            )

    if not warnings_found:
        print("No origin exceeded the 10% failure threshold.")


def main():

    parser = argparse.ArgumentParser(
        description="Monitor weekly virus sequencing QC results."
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        default="samples.txt",
        help="Path to QC metrics file (default: samples.txt)"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s"
    )

    data = load_data(args.input_file)

    data = identify_failures(data)

    summary = calculate_summary(data)

    report_results(summary)


if __name__ == "__main__":
    main()