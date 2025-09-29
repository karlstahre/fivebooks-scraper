#!/usr/bin/env python3
"""
filter_missing_year.py

Read books_with_year.tsv and write only the rows with no Year
to books_missing_year.tsv.
"""

import csv

input_file = "books_with_year.tsv"
output_file = "books_missing_year.tsv"

with open(input_file, newline="", encoding="utf-8") as inp, \
     open(output_file, "w", newline="", encoding="utf-8") as out:
    
    reader = csv.DictReader(inp, delimiter="\t")
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames, delimiter="\t")
    writer.writeheader()

    count = 0
    for row in reader:
        if not row["Year"].strip():
            writer.writerow(row)
            count += 1

print(f"✅ Wrote {count} rows to {output_file}")
