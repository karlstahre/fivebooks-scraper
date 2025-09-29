#!/usr/bin/env python3
"""
merge_years.py

Merge new year data from an updted run into the original master TSV.

Usage: python3 merge_years.py books_with_year.tsv books_missing_year_updated.tsv merged_books_with_year.tsv
"""

import csv
import sys

if len(sys.argv) != 4:
    sys.exit("Usage: python3 merge_years.py original.tsv new_data.tsv output.tsv")

original_file, new_data_file, output_file = sys.argv[1:4]

# Load the new year values into a lookup dict
updates = {}
with open(new_data_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        year = row.get("Year", "").strip()
        if year:  # only keep rows that found a year
            key = (row["Title"].strip(), row["Author"].strip())
            updates[key] = year

updated_rows = 0

# Read the original file and update missing years
with open(original_file, newline="", encoding="utf-8") as fin, \
     open(output_file, "w", newline="", encoding="utf-8") as fout:
    
    reader = csv.DictReader(fin, delimiter="\t")
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()

    for row in reader:
        key = (row["Title"].strip(), row["Author"].strip())
        if (not row["Year"].strip()) and key in updates:
            row["Year"] = updates[key]
            updated_rows += 1
        writer.writerow(row)

print(f"✅ Merged data written to {output_file}")
print(f"    Filled {updated_rows} previously-missing Year values")