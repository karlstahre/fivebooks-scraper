#!/usr/bin/env python3
"""
add_publication_year.py

Enrich a tab-separated list of book titles and authors with first-publication
years from the Open Library API.

Usage:
    python3 add_publication_year.py input.tsv output.tsv

Input file:
    A TSV with at least two columns: "Title" and "Author".

Output file:
    A TSV with at least three columns: "Title", "Author", "Year".

The script applies several robustness strategies:
    * Normalises case and strips punctuation for searching.
    * Handles multiple authors (comma/and/& separators).
    * Falls back to title-only searches when needed.
    * Attempts a shortened title (before ':' or '-') if initial searches fail.
    * Handles leading "The " (tries again without it if not found).
    * Normalises/strips apostrophes for fallback queries.
    * Tries each listed author individually if primary author fails.
"""

from __future__ import annotations

import csv
import re
import sys
import time
from pathlib import Path
from typing import Iterator, Optional

import requests

OPENLIBRARY_SEACRH_URL = "https://openlibrary.org/search.json"
REQUEST_DELAY = 1.0  # seconds, to respect Open Library's polite use guidelines
MAX_RECURSION_DEPTH = 1  # max depth for short-title fallback 


# ---------- Text Normalisation ------------------------------------------------
def normalise(text: str) -> str:
    """
    Lowercase the string, remove most punctuation, and collapse whitespace.
    Retains letters, digits, and spaces for more forgivig Open Library matching.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text)      # collapse multiple spaces
    return text.strip()


def primary_author(author: str) -> str:
    """
    Return the first author's name, splitting on common spearators like
    'and', '&', or ','.
    """
    parts = re.split(r"\s*(?:,| and | & )\s*", author, maxsplit=1)
    return parts[0].strip()


def all_authors(author: str) -> list[str]:
    """Split an author field into a list of individual authors."""
    return [a.strip() for a in re.split(r"\s*(?:,| and | & )\s*", author) if a.strip()]


def strip_leading_the(title: str) -> str:
    """Remove a leading 'The ' (case-insensitive) if present."""
    return title[4:].strip() if title.lower().startswith("the ") else title


def normalise_apostrophes(title: str) -> str:
    """Replace curly quotes with straight and optionally remove them."""
    t = title.replace("’", "'").replace("‘", "'")
    return t, t.replace("'", "")


# ---------- Open Library Query ------------------------------------------------
def query_openlibrary(params: dict, return_docs: bool = False):
    """Perform a GET request to the Open Library search API."""
    try:
        print(f"    Querying Open Library. {params}")
        response = requests.get(OPENLIBRARY_SEACRH_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["docs"] if return_docs else (data["docs"][0] if data["docs"] else None)
    except requests.exceptions.Timeout:
        print(f"    [Timeout] for params: {params}")
    except requests.exceptions.RequestException as exc:
        print(f"    [Error] {exc} for params: {params}")
    return None


def fetch_first_year(title: str, author: str, depth: int = 0) -> Optional[int]:
    """
    Retrieve the first publication year for a given title/author using
    increasingly broad strategies.
    """
    norm_title = normalise(title)
    prim_author = normalise(primary_author(author))

    # 1. Title + primary author
    doc = query_openlibrary({"title": norm_title, "author": prim_author, "limit": 1})
    if doc and doc.get("first_publish_year"):
        return doc["first_publish_year"]
    
    # 2. Title only, then check authors locally
    docs = query_openlibrary({"title": norm_title, "limit": 5}, return_docs=True)
    for d in docs:
        authors = [normalise(a) for a in d.get("author_name", [])]
        if any(prim_author in a for a in authors) and d.get("first_publish_year"):
            return d["first_publish_year"]

    # 3. Try without leading "The "
    if title.lower(). startswith("the "):
        print("    Fallback: removing leading 'The'")
        yr = fetch_first_year(strip_leading_the(title), author, depth)
        if yr:
            return yr

    # 4. Try with apostrophes normalised/removed
    if "'" in title or "’" in title or "‘" in title:
        straight, stripped = normalise_apostrophes(title)
        for t in (straight, stripped):
            if t != title:
                print("    Fallback: apostrophe variant")
                yr = fetch_first_year(t, author, depth)
                if yr:
                    return yr
    
    # 5. Trye each author indiviually
    for a in all_authors(author):
        norm_a = normalise(a)
        print(f"    Fallback: trying indiviual author '{a}")
        doc = query_openlibrary({"title": norm_title, "author": norm_a, "limit": 1})
        if doc and doc.get("first_publish_year"):
            return doc["first_publish_year"]

    # 6. Short title (before colon or dash)
    if depth < MAX_RECURSION_DEPTH:
        short_title = re.split(r"[:\-]", title, 1)[0].strip()
        if short_title and short_title.lower() != norm_title:
            return fetch_first_year(short_title, author, depth=depth + 1)
    
    return None


# ---------- File handling -----------------------------------------------------
def read_books(path: Path) -> Iterator[tuple[str, str]]:
    """Yield (title, author) pairs from the input TSV."""
    with path.open(newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        for row in reader:
            title = row.get("Title")
            author = row.get("Author")
            if title and author:
                yield title.strip(), author.strip()


def write_books(path: Path, rows: list[tuple[str, str, Optional[int]]]) -> None:
    """Write enriched rows to the output TSV."""
    with path.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Title", "Author", "Year"])
        writer.writerows(rows)


# ---------- Main ---------------------------------------------------------------
def main(input_file: str, output_file: str) -> None:
    input_path = Path(input_file)
    output_path = Path(output_file)

    results: list[tuple[str, str, Optional[int]]] = []

    for title, author in read_books(input_path):
        print(f"Searching: {title} — {author}")
        try:
            year = fetch_first_year(title, author)
        except Exception as exc:  # catch network/HTTP errors
            print(f"  [Error] {exc}")
            year = None
        results.append((title, author, year))
        print(f"  Year: {year}")
        time.sleep(REQUEST_DELAY)

    write_books(output_path, results)
    print(f"\n✅ Finished. Wrote {len(results)} rows to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 add_publication_year.py input.tsv output.tsv")        
    main(sys.argv[1], sys.argv[2])
