# Tayara Car Scraper

Web scraper for extracting car listings from Tayara.tn using Selenium with robust CSS selectors and fallback mechanisms.

## Prerequisites

- Python 3.7+
- Chrome browser installed
- ChromeDriver (automatically managed by selenium-manager in newer versions)

## Installation

```bash
pip install selenium
```

## Usage

### Basic Usage
```python
python scraper.py
```

### Configuration
Modify these variables in the script:
- `max_pages`: Number of pages to scrape (default: 20)
- `delay`: Delay between page loads in seconds (default: 3)
- `folder_path`: Output directory for CSV file
- `filename`: Output CSV filename

### Testing Selectors
Uncomment the test line to debug selectors:
```python
test_selectors(start_url)
```

## Features

- **Multiple fallback selectors** for each element type
- **Anti-detection measures** to avoid bot blocking
- **Robust error handling** continues scraping if individual elements fail
- **CSV export** with structured data
- **Headless mode** for background operation

## Output

CSV file with columns:
- `title`: Car listing title
- `url`: Link to the listing
- `price`: Price with currency
- `city`: Location

## Troubleshooting

**No cards found**: Run `test_selectors()` to check which selectors work on current page structure

**ChromeDriver issues**: Update Chrome browser or use selenium-manager

**Bot detection**: Script includes stealth measures, increase delays if needed

**Empty results**: Website structure may have changed, update selectors accordingly

## File Structure

```
project/
├── scraper.py          # Main scraper script
└── cars_final.csv      # Output file (generated)
```