# FiveBooks.com Book Scraper

A Python command-line tool to **extract all book titles and authors** from any [FiveBooks.com](https://fivebooks.com/) page.

FiveBooks pages often load additional books as you scroll.  
This scraper uses **Playwright** to render the page fully (including infinite scroll) and outputs a clean CSV with `Title` and `Author` columns.

---

## ✨ Features

- **Automatic scrolling** until every book is visible  
- **Smart parsing**: splits `Title` and `Author` even when `"by"` appears in the title  
- Saves results to a **UTF-8 CSV file**  
- Runs headless (no browser window required)  

---

## 📦 Requirements

- Python **3.8+**
- [Playwright](https://playwright.dev/python/)

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install
