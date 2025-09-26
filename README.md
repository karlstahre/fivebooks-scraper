# Book Scraper

A clean, robust Python script to scrape book titles and authors from a webpage where
books are represented by elements with the class `.book-title.-listbook`.  
Handles dynamic content (lazy-loading / infinite scroll) using [Playwright](https://playwright.dev/).

## Features

- Automatically scrolls to load all books on the page.
- Extracts both `Title` and `Author`, intelligently handling cases where `by` appears in the title.
- Outputs results to a CSV file.
- Headless browser mode — no GUI pop-ups.

## Installation

```bash
git clone <your-repo-url>
cd book-scraper
python3 -m pip install -r requirements.txt
python3 -m playwright install
