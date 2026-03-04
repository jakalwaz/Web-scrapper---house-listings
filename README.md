# Web Scraper — House Listings & Real Estate Leads

Python web scrapers using Selenium to collect real estate agent and FSBO (For Sale By Owner) leads from Yellow Pages and Kijiji in London, ON.

## Scripts

| File | Source | Output |
|------|--------|--------|
| `scraper.py` | Yellow Pages — Real Estate Agents | `london_leads.csv` |
| `map_scrapper.py` | Yellow Pages — Multi-page scrape | `london_agents_mass_list.csv` |
| `kijiji_scraper.py` | Kijiji — FSBO listings | `london_fsbo_leads.csv` |

## Requirements

- Python 3.x
- Google Chrome installed
- `selenium`
- `webdriver-manager`

Install dependencies:
```
pip install selenium webdriver-manager
```

## Usage

Run any script directly:
```
python scraper.py
python map_scrapper.py
python kijiji_scraper.py
```

Each script outputs a `.csv` file with the collected leads. Configuration (target URL, output file, pages to scrape) is at the top of each file.

## Notes

- Scripts use Chrome in automated mode via `webdriver-manager` — no manual ChromeDriver setup needed
- `kijiji_scraper.py` includes anti-detection flags to reduce bot blocking
- `map_scrapper.py` supports multi-page scraping — adjust `PAGES_TO_SCRAPE` in the config
