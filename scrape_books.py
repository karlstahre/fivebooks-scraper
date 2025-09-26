#!/usr/bin/env python3
"""
FiveBooks.com Book Scraper
--------------------------

Scrapes all book titles and authors from a page on FiveBooks.com where book elements
have the class ".book-title.-listbook". Supports lazy-loaded content (infinit scroll)
using PlayWright.

Usage:
    python scrape_books.py <URL> [output_file]

Example:
    python scrape_books.py "https://fivebooks.com/best-books-on-science/" books.csv
"""

import sys
import time
import csv
from typing import List, Tuple
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def extract_books_from_html(html: str) -> List[Tuple[str, str]]:
    """
    Extracts book titles and authors from rendered HTML on FiveBooks.com

    Each book element has the class ".book-title.-listbook". Titles and authors are 
    separated by the last occurrence of "by " to handle titles containing "by ".

    Args:
        html (str): Rendered HTML content from a FiveBooks.com page.
    
    Returns:
        List of tuples: [(title, author), ...]
    """
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.select(".book-title.-listbook")
    books = []

    for tag in tags:
        full_text = tag.get_text(strip=True)
        if "by " in full_text:
            title, author = full_text.rsplit("by ", 1)
            title = title.strip()
            author = author.strip()
        else:
            title = full_text
            author = ""
        books.append((title, author))
    
    return books


def scroll_to_load_all_content(page, wait: float = 1.0):
    """
    Scrolls to the bottom of a FiveBooks.com page until no more content is loaded.

    Many FiveBooks.com pages use lazy-loaded / infinite scroll for book lists, so
    scrolling ensures all books are rendered in the DOM.

    Args:
        page: Playwright page object for the FiveBooks.com page.
        wait (float): Time in seconds to wait after each scroll.
    """
    previous_height = 0
    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(wait)
        current_height = page.evaluate("document.body.scrollHeight")
        if current_height == previous_height:
            break
        previous_height = current_height


def scrape_books(url: str) -> List[Tuple[str, str]]:
    """
    Scrapes all books from a given FiveBooks.com page URL.

    Args:
        url (str): The URL of a FiveBooks.com page.
    
    Returns:
        List of tuples: [(title, author), ...]
    """
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        print(f"Navigating to {url} ...")
        page.goto(url)

        print("Scrolling to load all books...")
        scroll_to_load_all_content(page)

        html = page.content()
        browser.close()
    
    books = extract_books_from_html(html)
    print(f"Found {len(books)} books.")
    return books


def save_books_to_csv(books: List[Tuple[str, str]], output_file: str):
    """
    Saves a list of books from FiveBooks.com to CSV file.

    Args:
        books: List of tuples (title, author)
        output_file: CSV file path
    """
    with open(output_file, "w", newline="", encoding="utf-8") as f_out:
        fieldnames = ["Title", "Author"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for title, author in books:
            writer.writerow({"Title": title, "Author": author})
    print(f"Saved books to {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_books.py <URL> [output_file]")
        sys.exit()

    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else "books.csv"

    books = scrape_books(url)
    save_books_to_csv(books, output_file)


if __name__ == "__main__":
    main()
